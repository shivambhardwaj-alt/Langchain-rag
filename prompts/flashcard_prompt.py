

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Flashcard(BaseModel):
    front: str = Field(description="question or term, concise")
    back: str = Field(description="answer or definition, concise but complete")
    card_type: str = Field(description="one of: definition, fact, concept, comparison, application")
    difficulty: str = Field(description="one of: easy, medium, hard")


class FlashcardsOutput(BaseModel):
    flashcards: list[Flashcard] = Field(description="12-20 flashcards, no duplicate fronts")


flashcards_parser = PydanticOutputParser(pydantic_object=FlashcardsOutput)

FLASHCARDS_SYSTEM_PROMPT = """You are an expert at writing flashcards for spaced-repetition learning systems \
(like Anki), generated from a document.

Rules:
- "front" must be answerable from memory in a few seconds — no compound questions.
- "back" must be self-contained: someone reading only the back, with no other context, should fully \
  understand the answer.
- Avoid yes/no fronts. Avoid fronts that give away the answer in the question itself.
- card_type "comparison" cards should contrast two related concepts from the document (e.g. "X vs Y: key difference?").
- card_type "application" cards should test using a concept, not just recalling it.
- No duplicate or near-duplicate fronts.
- Cover the breadth of the document, not just the first section.

{format_instructions}"""

FLASHCARDS_HUMAN_PROMPT = """Document context:

{context}

Generate flashcards following the schema."""

flashcards_prompt = ChatPromptTemplate.from_messages([
    ("system", FLASHCARDS_SYSTEM_PROMPT),
    ("human", FLASHCARDS_HUMAN_PROMPT),
]).partial(format_instructions=flashcards_parser.get_format_instructions())