

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class GeneratedQuestion(BaseModel):
    question: str
    type: str = Field(description="one of: factual, conceptual, analytical, application")
    answer: str = Field(description="grounded answer, cite the relevant part of the document conceptually")
    bloom_level: str = Field(description="one of: remember, understand, apply, analyze, evaluate, create")


class QuestionsOutput(BaseModel):
    questions: list[GeneratedQuestion] = Field(description="8-12 questions spanning multiple bloom levels and types")


questions_parser = PydanticOutputParser(pydantic_object=QuestionsOutput)

QUESTIONS_SYSTEM_PROMPT = """You are an expert educator generating study questions from a document, modeled on \
Bloom's Taxonomy to ensure a range of cognitive depth — not just recall questions.

Rules:
- Distribute questions across bloom_levels: include at least 2 at "remember/understand", at least 2 at \
  "apply/analyze", and at least 1 at "evaluate/create" if the document supports it.
- "factual" questions test specific facts/details from the text.
- "conceptual" questions test understanding of underlying ideas.
- "analytical" questions require connecting multiple parts of the document.
- "application" questions ask the reader to apply the document's content to a new scenario.
- Every answer must be answerable strictly from the provided context — do not write questions whose \
  answers require outside knowledge.
- Do not write trivially obvious or yes/no questions.

{format_instructions}"""

QUESTIONS_HUMAN_PROMPT = """Document context:

{context}

Generate study questions following the schema."""

questions_prompt = ChatPromptTemplate.from_messages([
    ("system", QUESTIONS_SYSTEM_PROMPT),
    ("human", QUESTIONS_HUMAN_PROMPT),
]).partial(format_instructions=questions_parser.get_format_instructions())