from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional


class MindMapNode(BaseModel):
    id: str = Field(description="unique short slug id , e.g 'node_1'")
    label: str = Field(description="short node text , max 6 words ")
    parent_id: Optional[str] = Field(description="id of parent node, null for root node")
    level: int = Field(description="0 for root, 1 for main branches, 2+ for sub-branches")


class MindMapOutput(BaseModel):
    title: str = Field(description="overall document title for root node")
    nodes: List[MindMapNode] = Field(
        default_factory=list,
        description="flat list for all nodes including root, forming tree via parent_id"
    )


mindmap_parser = PydanticOutputParser(pydantic_object=MindMapOutput)

MINDMAP_SYSTEM_PROMPT = """You are an expert at converting dense documents into hierarchical mind maps that
will be rendered visually (e.g. as a tree diagram in a frontend).

Rules:
- Build a tree: exactly one root node (level 0, parent_id null), 4-8 main branches (level 1),
  and sub-branches (level 2-3) only where the document has genuine sub-structure.
- Every node's parent_id must reference an existing id (except root).
- Labels must be short (max 6 words).
- No cycles or orphan nodes.
- Prefer breadth over depth.

{format_instructions}"""

MINDMAP_HUMAN_PROMPT = """Document context:

{context}

Build the mind map following the schema."""

mindmap_prompt = ChatPromptTemplate.from_messages([
    ("system", MINDMAP_SYSTEM_PROMPT),
    ("human", MINDMAP_HUMAN_PROMPT),
]).partial(format_instructions=mindmap_parser.get_format_instructions())