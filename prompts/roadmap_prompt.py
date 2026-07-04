

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class RoadmapStep(BaseModel):
    step_number: int
    title: str = Field(description="short title for this learning step")
    description: str = Field(description="what to learn/do in this step and why it comes at this point in the sequence")
    resources_to_revisit: list[str] = Field(
        default_factory=list,
        description="doc_ids or filenames from the user's prior documents relevant to this step, if any"
    )
    estimated_time: str = Field(description="rough time estimate, e.g. '30 minutes', '2-3 days'")
    depends_on_steps: list[int] = Field(default_factory=list, description="step_numbers that must be completed first")


class RoadmapOutput(BaseModel):
    goal: str = Field(description="inferred or stated overall learning goal")
    steps: list[RoadmapStep] = Field(description="4-10 sequenced steps forming a coherent learning path")
    current_position_step: int = Field(
        description="the step_number representing where the user currently stands, based on prior_user_concepts and the current document"
    )


roadmap_parser = PydanticOutputParser(pydantic_object=RoadmapOutput)

ROADMAP_SYSTEM_PROMPT = """You are an expert learning path designer. Build a personalized, sequenced learning \
roadmap using the user's full learning history plus the current document.

You will be given:
1. The current document's context and extracted concepts.
2. The user's prior learned concepts and prior document topics/summaries across their whole history.

Rules:
- The roadmap must be a logical DAG: depends_on_steps must only reference earlier or parallel steps, never \
  create cycles.
- Use prior_user_concepts to determine current_position_step accurately — do not start the user at step 1 if \
  they've already covered foundational material in earlier documents.
- resources_to_revisit should reference actual prior documents/filenames given to you, not invented ones — \
  leave empty if nothing prior is relevant to that step.
- Steps should be genuinely sequenced (prerequisite-driven), not just a flat list of topics in document order.
- estimated_time should be realistic for a self-directed learner, not overly optimistic.
- If the user's history shows they're clearly already advanced in this topic, keep the roadmap short and \
  start near the end — do not pad with steps they don't need.

{format_instructions}"""

ROADMAP_HUMAN_PROMPT = """Current document context:

{context}

User's learning history (prior concepts and document summaries, may be empty for new users):
{user_history}

Build the personalized roadmap following the schema."""

roadmap_prompt = ChatPromptTemplate.from_messages([
    ("system", ROADMAP_SYSTEM_PROMPT),
    ("human", ROADMAP_HUMAN_PROMPT),
]).partial(format_instructions=roadmap_parser.get_format_instructions())