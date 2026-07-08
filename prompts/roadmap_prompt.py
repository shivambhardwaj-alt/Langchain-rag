from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class RoadmapStep(BaseModel):
    step_number: int = Field(
        description="Sequential step number starting from 1"
    )

    title: str = Field(
        description="Short title of this learning step"
    )

    description: str = Field(
        description="Explain what the learner should study in this step and why."
    )

    estimated_time: str = Field(
        description="Estimated time to complete this step."
    )

    depends_on_steps: list[int] = Field(
        default_factory=list,
        description="List of prerequisite step numbers."
    )

    resources_to_revisit: list[str] = Field(
        default_factory=list,
        description="ONLY filenames or document IDs from the user's previous uploaded documents. Never return objects or URLs."
    )


class RoadmapOutput(BaseModel):
    goal: str = Field(
        description="The overall learning goal."
    )

    current_position_step: int = Field(
        description="The step number where the user currently stands."
    )

    steps: list[RoadmapStep] = Field(
        description="A sequenced learning roadmap."
    )


roadmap_parser = PydanticOutputParser(
    pydantic_object=RoadmapOutput
)

ROADMAP_SYSTEM_PROMPT = """
You are an expert learning path designer.If the Information is not available in the document fields then you  can generate your intelligence to create information but make response better
You are a genius who can work without information provided by the user so generate response by yourself and make those better.

Create a personalized roadmap using:

1. Current document.
2. User's previous learning history.

Rules:

- Return ONLY valid JSON matching the schema.
- Do NOT add markdown.
- Do NOT explain anything outside JSON.

Roadmap Rules:

- Goal should summarize what the learner will achieve.
- Create between 4 and 10 learning steps.
- Steps must be ordered logically.
- step_number starts from 1.
- depends_on_steps may reference ONLY previous step numbers.
- current_position_step should reflect the learner's existing knowledge.
- estimated_time should be realistic.

IMPORTANT:

resources_to_revisit MUST be an array of strings.

Each string must be ONLY a filename or document ID from the user's previous uploaded documents.

If there are no previous relevant documents, return:

[]

Never generate:

- articles
- videos
- URLs
- dictionaries
- objects

Correct:

"resources_to_revisit": [
    "dp_notes.pdf",
    "graph_summary.md"
]

Correct:

"resources_to_revisit": []

Incorrect:

{{
    "resources_to_revisit": [
        {{
            "title": "Introduction to DP",
            "url": "https://..."
        }}
    ]
}}

{format_instructions}
"""


ROADMAP_HUMAN_PROMPT = """
Current document:

{context}

User learning history:

{user_history}

Generate the personalized roadmap.
"""
roadmap_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ROADMAP_SYSTEM_PROMPT),
        ("human", ROADMAP_HUMAN_PROMPT),
    ]
).partial(
    format_instructions=roadmap_parser.get_format_instructions()
)