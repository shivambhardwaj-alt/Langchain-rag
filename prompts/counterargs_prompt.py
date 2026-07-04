

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class CounterArgument(BaseModel):
    original_claim: str = Field(description="the specific claim from the document being challenged")
    counter_argument: str = Field(description="a substantive, good-faith counter-argument")
    strength: str = Field(description="one of: weak, moderate, strong — how damaging this counter is to the original claim")
    supporting_reasoning: str = Field(description="why this counter-argument holds, 1-2 sentences")


class CounterArgumentsOutput(BaseModel):
    document_thesis: str = Field(description="the main argument/position of the document, if it has one")
    counter_arguments: list[CounterArgument] = Field(description="4-8 counter-arguments to distinct claims")
    has_clear_argumentative_thesis: bool = Field(
        description="false if the document is purely descriptive/factual with no arguable thesis"
    )


counter_args_parser = PydanticOutputParser(pydantic_object=CounterArgumentsOutput)

COUNTER_ARGS_SYSTEM_PROMPT = """You are a rigorous critical-thinking partner. Your job is to steelman opposing \
views to the document's claims — not to nitpick wording, but to genuinely challenge the substance.

Rules:
- First determine if the document actually makes arguable claims (has_clear_argumentative_thesis). If it's \
  purely factual/descriptive (e.g. a recipe, a glossary), set this to false and return an empty \
  counter_arguments list — do not force counter-arguments onto neutral content.
- Each counter-argument must target a SPECIFIC claim, quoted/paraphrased precisely as original_claim — never \
  vague claims like "the document oversimplifies things".
- Be intellectually honest: rate strength accurately, including "weak" if that's genuinely the case. Do not \
  inflate every counter to "strong" to seem more rigorous.
- Ground counter-arguments in established reasoning, evidence, or well-known opposing schools of thought — \
  do not fabricate statistics or studies.
- Avoid ad hominem or attacking tone/style — attack the substance of the claim only.

{format_instructions}"""

COUNTER_ARGS_HUMAN_PROMPT = """Document context:

{context}

Generate counter-arguments following the schema."""

counter_args_prompt = ChatPromptTemplate.from_messages([
    ("system", COUNTER_ARGS_SYSTEM_PROMPT),
    ("human", COUNTER_ARGS_HUMAN_PROMPT),
]).partial(format_instructions=counter_args_parser.get_format_instructions())