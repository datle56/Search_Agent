from typing import List, Dict, Optional, Any, Callable
import json
from datetime import datetime
import uuid
from app.services.search.search_manager import SearchManager
from app.models.base import Source, Node, Edge, IdeaGraph
from app.services.llm.base import BaseChatClient
from app.services.llm.schemas import (
    CREATE_NODE_SCHEMA,
    CREATE_EDGE_SCHEMA,
    JUDGE_INFORMATION_SCHEMA,
    MERGE_NODES_SCHEMA,
    GENERATE_NEXT_QUERY_SCHEMA,
)
from app.services.llm.base import BaseChatClient
class SearchAgent:
    def __init__(
        self,
        chat_client: BaseChatClient,
        search_manager: SearchManager,
        min_nodes: int = 3,
        max_nodes: int = 5,
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

    async def research_concept(self, concept: str) -> IdeaGraph:
        try:
            self.graph.concept = concept
            self._emit_update("start", {"concept": concept})

            self.current_query = concept
            self._emit_update("query", {"query": self.current_query})
        except:
            print("error")

        

        
