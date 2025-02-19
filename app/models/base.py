from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import List, Dict
import json

class Source(BaseModel):
    url: str
    title: str
    snippet: str


from pydantic import BaseModel, Field
import uuid
from typing import List

class Source(BaseModel):
    url: str
    title: str
    snippet: str
    source_type: str = Field(..., description="Either 'google' or 'wikipedia'")
    retrieved_at: datetime = Field(default_factory=datetime.now)

class Node(BaseModel):
    """Represents a component (constituent term) of a concept."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    description: str
    origin: str = ""  # Ví dụ: nguồn gốc hay bối cảnh hình thành thành phần này
    related_terms: List[str] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    is_original: bool = False  # True nếu đây là node ban đầu, False nếu là node mở rộng

class Edge(BaseModel):
    """Represents an evolution or influence between two idea snapshots"""

    source_node_id: str
    target_node_id: str
    change_description: str
    weight: float = 1.0
    sources: List[Source] = Field(default_factory=list)


class IdeaGraph(BaseModel):
    """Represents the complete evolution of an idea"""

    concept: str
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)  # For future extensibility

    def to_json(self) -> str:
        """Serialize the graph to JSON string"""
        return json.dumps(
            self.model_dump(), indent=2, default=str  # Handles datetime serialization
        )

    @classmethod
    def from_json(cls, json_str: str) -> "IdeaGraph":
        """Create an IdeaGraph instance from a JSON string"""
        data = json.loads(json_str)
        return cls(**data)