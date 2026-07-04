from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, field_validator
from typing import List


class QuizQuestion(BaseModel):
    question: str

    options: List[str] = Field(
        description="exactly 4 options, only one correct"
    )

    correctIndex: int = Field(
        description="0-indexed position of the correct option in 'options'"
    )

    explanation: str = Field(
        description="why correct answer is correct AND why others are wrong briefly"
    )

    difficulty: str = Field(
        description="one of: easy, medium, hard"
    )

    @field_validator("options")
    @classmethod
    def must_have_four(cls, v):
        if len(v) != 4:
            raise ValueError("options must contain exactly 4 items")
        return v


class QuizOutput(BaseModel):
    questions: List[QuizQuestion] = Field(
        description="10 MCQs, mix of easy/medium/hard (30/40/30 split)"
    )


quiz_parser = PydanticOutputParser(pydantic_object=QuizOutput)


QUIZ_SYSTEM_PROMPT = """You are an expert assessment designer creating a multiple-choice quiz from a document.

Rules:
- Exactly 4 options per question, exactly one correct.
- Wrong options must be plausible and based on document misconceptions.
- No "all of the above" or "none of the above".
- correctIndex must match final option order.
- Difficulty mix: 3 easy, 4 medium, 3 hard.
- Every question must be strictly based on context.

{format_instructions}"""


QUIZ_HUMAN_PROMPT = """Document context:

{context}

Generate the quiz following the schema."""


quiz_prompt = ChatPromptTemplate.from_messages([
    ("system", QUIZ_SYSTEM_PROMPT),
    ("human", QUIZ_HUMAN_PROMPT),
]).partial(format_instructions=quiz_parser.get_format_instructions())