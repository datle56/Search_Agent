from typing import List, Dict, Optional, Any, Callable
import json
from datetime import datetime
import uuid
from app.services.search.search_manager import SearchManager
from app.models.base import Source, Edge, IdeaGraph
from app.services.llm.base import BaseChatClient
from app.services.llm.schemas import (
    CREATE_NODE_SCHEMA,
    CREATE_EDGE_SCHEMA,
    JUDGE_INFORMATION_SCHEMA,
    SUMMARY_TEMPLATE,
    QUERY_UPDATE_PROMPT,
    MERGE_NODES_SCHEMA,
    PROCESS_SOURCES_PROMPT,
    GENERATE_NEXT_QUERY_SCHEMA,
)
from app.models.base import Source, Node, Edge, IdeaGraph
from app.models.responses import ChatCompletion

class SearchAgent:
    def __init__(
        self,
        chat_client: BaseChatClient,
        search_manager: SearchManager,
        min_nodes: int = 5,
        max_nodes: int = 10,
        on_update: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.chat_client = chat_client
        self.search_manager = search_manager
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
        self.collected_sources: List[Source] = []
        self.graph = IdeaGraph(concept="", nodes=[], edges=[])
        self.current_query = ""
        self.on_update = on_update

    def _emit_update(self, event_type: str, data: Dict[str, Any]):
        # If an update callback is provided, send the update event along with the current graph data
        if self.on_update:
            graph_data = self.graph.model_dump()
            self.on_update({"type": event_type, "data": data, "graph": graph_data})

    async def _perform_search(self, query: str) -> List[Source]:
        # Execute the search using the search manager
        return await self.search_manager.search(query)

    async def _process_sources(self, sources: List[Source], is_original: bool = False):
        try:
            graph_summary = self._format_graph_for_llm()
            sources_text = "\n\n".join(
                [
                    f"Source: {source.title}\nURL: {source.url}\nContent: {source.snippet}"
                    for source in sources
                ]
            )

            # Choose a different prompt if this is the initial (root) node versus an expansion node
            if is_original:
                node_prompt = PROCESS_SOURCES_PROMPT["initial_node"].format(
                    concept=self.graph.concept,
                    graph_summary=graph_summary,
                    sources_text=sources_text,
                )
            else:
                node_prompt = PROCESS_SOURCES_PROMPT["nodes"].format(
                    concept=self.graph.concept,
                    graph_summary=graph_summary,
                    sources_text=sources_text,
                )

            # Call LLM to create a node based on the sources
            node_response = await self._call_llm(
                messages=[{"role": "user", "content": node_prompt}],
                functions=[CREATE_NODE_SCHEMA],
                function_call="auto",
            )

            for choice in node_response.choices:
                if choice.message.function_call:
                    try:
                        if choice.message.function_call.name == "create_node":
                            node_data = json.loads(choice.message.function_call.arguments)
                            # Add the is_original flag: True for the root node, False for expansion nodes
                            node = Node(is_original=is_original, **node_data, sources=sources)
                            self.graph.nodes.append(node)
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Error processing node: {str(e)}")
                        continue

            # Process edge creation as before
            graph_summary = self._format_graph_for_llm()
            edge_prompt = PROCESS_SOURCES_PROMPT["edges"].format(
                concept=self.graph.concept,
                graph_summary=graph_summary,
                sources_text=sources_text,
            )

            edge_response = await self._call_llm(
                messages=[{"role": "user", "content": edge_prompt}],
                functions=[CREATE_EDGE_SCHEMA],
                function_call="auto",
            )

            for choice in edge_response.choices:
                if choice.message.function_call:
                    try:
                        if choice.message.function_call.name == "create_edge":
                            edge_data = json.loads(choice.message.function_call.arguments)
                            if edge_data["source_node_id"] != edge_data["target_node_id"]:
                                edge = Edge(**edge_data)
                                self.graph.edges.append(edge)
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Error processing edge: {str(e)}")
                        continue

                        
        except Exception as e:
            print(f"Error processing sources: {str(e)}")
            raise

    async def research_concept(self, concept: str) -> IdeaGraph:
        try:
            self.graph.concept = concept
            self._emit_update("start", {"concept": concept})
            self.current_query = concept
            self._emit_update("query", {"query": self.current_query})

            # Initial search for the root node
            initial_sources = await self._perform_search(self.current_query)
            if not initial_sources:
                raise ValueError("No initial sources found")
            self.collected_sources.extend(initial_sources)
            self._emit_update(
                "sources_found",
                {"count": len(initial_sources), "query": self.current_query},
            )

            # Use a specialized prompt for the first node that contains the definition of the concept
            await self._process_sources(initial_sources, is_original=True)
            self._emit_update(
                "graph_updated",
                {"nodes": len(self.graph.nodes), "edges": len(self.graph.edges)},
            )

            # Expand the search (expansion nodes)
            while not await self._has_sufficient_information():
                query = await self._generate_next_query()
                if not query:
                    raise ValueError("Failed to generate next query")

                self.current_query = query
                self._emit_update("query", {"query": query})
                print(f"Searching for: {query}")
                sources = await self._perform_search(query)
                if sources:
                    self.collected_sources.extend(sources)
                    self._emit_update(
                        "sources_found", {"count": len(sources), "query": query}
                    )
                    # Expansion nodes are created with is_original set to False
                    await self._process_sources(sources, is_original=False)
                    self._emit_update(
                        "graph_updated",
                        {
                            "nodes": len(self.graph.nodes),
                            "edges": len(self.graph.edges),
                        },
                    )
                else:
                    print("No additional sources found")
                    break

            print("Starting graph finalization...")
            print("Merging similar expansion nodes")
            await self._merge_similar_nodes()
            print("Merged similar expansion nodes")
            await self._validate_graph()
            print("Graph validated")
            self._emit_update(
                "complete",
                {"nodes": len(self.graph.nodes), "edges": len(self.graph.edges)},
            )
            if not self.graph.nodes:
                raise ValueError("Failed to construct graph - no nodes created")
            return self.graph

        except Exception as e:
            print(f"Error in research_concept: {str(e)}")
            raise

    def _format_graph_for_llm(self) -> str:
        nodes_info = []
        for node in self.graph.nodes:
            node_type = "Initial Node" if node.is_original else "Expansion Node"
            sources_str = ", ".join(source.url for source in node.sources) if node.sources else "None"
            node_str = (
                f"Node ID: {node.id}\n"
                f"Type: {node_type}\n"
                f"Component Name: {node.name}\n"
                f"Related Fields/Domains: {node.origin}\n"
                f"Influential Sources: {sources_str}\n"
                f"Component Description: {node.description}\n"
            )
            nodes_info.append(node_str)

        edges_info = []
        for edge in self.graph.edges:
            edge_str = (
                f"From Node ID: {edge.source_node_id}\n"
                f"To Node ID: {edge.target_node_id}\n"
                f"Relationship: {edge.change_description}\n"
            )
            edges_info.append(edge_str)

        node_info = ("\n" + "-" * 50 + "\n").join(nodes_info) if nodes_info else "No components recorded yet"
        edge_info = ("\n" + "-" * 50 + "\n").join(edges_info) if edges_info else "No relationships recorded yet"
        summary = SUMMARY_TEMPLATE.format(
            concept=self.graph.concept,
            node_info=node_info,
            edge_info=edge_info,
        )
        return summary

    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict]] = None,
        function_call: Optional[Dict] = None,
    ) -> Any:
        try:
            response = await self.chat_client.chat_completion(
                messages=messages, functions=functions, function_call=function_call
            )
            return response
        except Exception as e:
            print(f"LLM API error: {str(e)}")
            raise

    async def _has_sufficient_information(self) -> bool:
        try:
            if len(self.graph.nodes) >= self.max_nodes:
                return True
            if len(self.graph.nodes) < self.min_nodes:
                return False

            prompt = f"""
            Evaluate if we have sufficient information about the evolution of '{self.graph.concept}'.
            Current nodes: {len(self.graph.nodes)}
            Current edges: {len(self.graph.edges)}
            Node summaries: {[node.description for node in self.graph.nodes]}
            """

            response = await self._call_llm(
                messages=[{"role": "user", "content": prompt}],
                functions=[JUDGE_INFORMATION_SCHEMA],
                function_call={"name": JUDGE_INFORMATION_SCHEMA["name"]},
            )

            try:
                result = json.loads(response.choices[0].message.function_call.arguments)
                return result["is_sufficient"]
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"Error parsing LLM response: {str(e)}")
                return False

        except Exception as e:
            print(f"Error checking information sufficiency: {str(e)}")
            return False

    async def _generate_next_query(self) -> str:
        try:
            summary = self._format_graph_for_llm()
            prompt = QUERY_UPDATE_PROMPT.format(
                concept=self.graph.concept,
                summary=summary,
                previous_query=self.current_query,
            )
            print(f"Prompt: {prompt}")

            response: ChatCompletion = await self._call_llm(
                messages=[{"role": "user", "content": prompt}],
                functions=[GENERATE_NEXT_QUERY_SCHEMA],
                function_call={"name": "generate_next_query"},
            )

            try:
                query = json.loads(response.choices[0].message.function_call.arguments)["query"]
                return query
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"Error parsing LLM response for next query: {str(e)}")
                return f"More information about {self.graph.concept}"

        except Exception as e:
            print(f"Error generating next query: {str(e)}")
            return f"History and development of {self.graph.concept}"

    async def _merge_similar_nodes(self):
        try:
            # Filter to include only expansion nodes (excluding the root node)
            expansion_nodes = [node for node in self.graph.nodes if not node.is_original]
            if len(expansion_nodes) < 2:
                return  # Not enough expansion nodes to merge

            nodes_data = [node.model_dump() for node in expansion_nodes]
            prompt = f"""
            Analyze these nodes representing developments in the concept of '{self.graph.concept}'.
            Identify any nodes that represent the same conceptual expansion and should be merged.
            Consider:
            - Similar key contributors
            - Similar main ideas

            Nodes: {nodes_data}
            """
            print("Calling LLM for node merging")
            response: ChatCompletion = await self._call_llm(
                messages=[{"role": "user", "content": prompt}],
                functions=[MERGE_NODES_SCHEMA],
                function_call={"name": "merge_nodes"},
            )

            if response.choices and response.choices[0].message.function_call:
                merge_data = json.loads(response.choices[0].message.function_call.arguments)
            else:
                print("No function call found in response")
                return

            if merge_data.get("node_ids"):
                print("Executing node merge")
                await self._execute_node_merge(
                    node_ids=merge_data["node_ids"],
                    reasoning=merge_data.get("reasoning", "No reasoning provided"),
                    merged_summary=merge_data.get("merged_summary", "No summary provided"),
                )
        except Exception as e:
            print(f"Error in merge_similar_nodes: {str(e)}")

    def _create_merged_node(self, nodes: List["Node"], merged_summary: str, reasoning: str) -> "Node":
        # Combine the names of the nodes to form the merged name
        merged_name = " / ".join(node.name for node in nodes)
        merged_description = f"{merged_summary}\nMerge Reasoning: {reasoning}"
        merged_origin = nodes[0].origin if nodes else ""
        merged_related_terms = list({term for node in nodes for term in node.related_terms})
        merged_sources = []
        for node in nodes:
            merged_sources.extend(node.sources)
        # The merged node is always considered an expansion node
        return Node(
            name=merged_name,
            description=merged_description,
            origin=merged_origin,
            related_terms=merged_related_terms,
            sources=merged_sources,
            is_original=False,
        )

    def _update_edges_for_merged_node(self, old_node_ids: List[str], merged_node_id: str):
        new_edges = []
        seen_connections = set()
        for edge in self.graph.edges:
            # Replace the IDs of merged nodes with the new merged node ID
            source_id = merged_node_id if edge.source_node_id in old_node_ids else edge.source_node_id
            target_id = merged_node_id if edge.target_node_id in old_node_ids else edge.target_node_id
            if source_id == target_id:
                continue
            connection = (source_id, target_id)
            if connection in seen_connections:
                continue
            seen_connections.add(connection)
            new_edge = Edge(
                source_node_id=source_id,
                target_node_id=target_id,
                change_description=edge.change_description,
                weight=edge.weight,
                sources=edge.sources,
            )
            new_edges.append(new_edge)
        self.graph.edges = new_edges

    async def _execute_node_merge(self, node_ids: List[str], reasoning: str, merged_summary: str):
        try:
            if not node_ids:
                raise ValueError("No node IDs provided for merging")
            if not reasoning:
                raise ValueError("No reasoning provided for merge")
            if not merged_summary:
                raise ValueError("No merged summary provided")

            print("Finding nodes to merge")
            # Merge only expansion nodes (do not merge the original/root node)
            nodes_to_merge = [node for node in self.graph.nodes if node.id in node_ids and not node.is_original]
            if not nodes_to_merge:
                raise ValueError(f"No expansion nodes found matching provided IDs: {node_ids}")

            print("Creating merged node")
            merged_node = self._create_merged_node(nodes_to_merge, merged_summary, reasoning)

            print("Updating edges")
            self._update_edges_for_merged_node(old_node_ids=node_ids, merged_node_id=merged_node.id)

            print("Removing old nodes and adding merged node")
            self.graph.nodes = [node for node in self.graph.nodes if node.id not in node_ids]
            self.graph.nodes.append(merged_node)

            try:
                print("Adding merge info to graph metadata")
                if "merge_history" not in self.graph.metadata:
                    self.graph.metadata["merge_history"] = []
                self.graph.metadata["merge_history"].append({
                    "merged_node_ids": node_ids,
                    "new_node_id": merged_node.id,
                    "reasoning": reasoning,
                    "timestamp": datetime.now().isoformat(),
                })
            except Exception as e:
                print(f"Warning: Failed to update merge history: {str(e)}")
        except Exception as e:
            print(f"Error executing node merge: {str(e)}")
            raise

    async def _validate_graph(self):
        try:
            self.graph.edges = self._remove_duplicate_edges(self.graph.edges)
            self.graph.edges = self._enforce_temporal_order(self.graph.edges)
        except Exception as e:
            print(f"Error validating graph: {str(e)}")
            raise

    def _remove_duplicate_edges(self, edges):
        seen = set()
        unique_edges = []
        for edge in edges:
            key = (edge.source_node_id, edge.target_node_id)
            if key not in seen:
                seen.add(key)
                unique_edges.append(edge)
        return unique_edges

    def _enforce_temporal_order(self, edges: List[Edge]) -> List[Edge]:
        # This function can be extended to enforce chronological ordering if needed
        return edges

    def _get_node_by_id(self, node_id: str) -> Optional["Node"]:
        return next((node for node in self.graph.nodes if node.id == node_id), None)
