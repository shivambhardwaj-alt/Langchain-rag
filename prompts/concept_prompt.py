
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field



class Concept(BaseModel):
    name: str = Field(description="Concept name, short and precise")
    definition: str = Field(description="1-3 sentence definition grounded in the document")
    importance: str = Field(description="why this concept matters in context, 1 sentence")
    difficulty: str = Field(description="one of: beginner, intermediate, advanced")
    related_concepts: list[str] = Field(default_factory=list, description="names of related concepts from this same list")


class ConceptsOutput(BaseModel):
    concepts: list[Concept] = Field(description="5-15 key concepts, ordered by importance, no duplicates")
    prerequisite_concepts: list[str] = Field(
        description="Concepts the reader should already know that are NOT explained in this document"
    )


concepts_parser = PydanticOutputParser(pydantic_object=ConceptsOutput)

CONCEPTS_SYSTEM_PROMPT = """You are an expert curriculum designer extracting key concepts from a document for a \
spaced-repetition learning system. These concepts will be stored long-term and reused when the user uploads \
related documents in the future, so precision and atomicity matter.

Rules:
- Each concept must be atomic — one idea per concept, not a bundled topic.
- Do not invent concepts not present or implied in the document.
- difficulty should reflect how much background knowledge is needed to understand it, not how complex the wording is.
- related_concepts must only reference concept names that also appear in your own concepts list.
- prerequisite_concepts are things assumed by the document but never defined in it — flag these explicitly, \
  they matter for downstream "missing knowledge" detection.
- Avoid generic concepts (e.g. "introduction", "conclusion") — only substantive domain concepts.

{format_instructions}"""

CONCEPTS_HUMAN_PROMPT = """Document context:

{context}

Extract concepts following the schema."""

concepts_prompt = ChatPromptTemplate.from_messages([
    ("system", CONCEPTS_SYSTEM_PROMPT),
    ("human", CONCEPTS_HUMAN_PROMPT),
]).partial(format_instructions=concepts_parser.get_format_instructions())


