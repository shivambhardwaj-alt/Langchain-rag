

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class KnowledgeGap(BaseModel):
    gap: str = Field(description="the specific concept/fact assumed but not explained")
    why_it_matters: str = Field(description="why understanding this is necessary to fully grasp the document")
    suggested_lookup: str = Field(description="a concrete search term or topic to research this gap")


class MissingKnowledgeOutput(BaseModel):
    gaps: list[KnowledgeGap] = Field(description="3-10 genuine knowledge gaps, no duplicates")
    user_likely_already_knows: list[str] = Field(
        description="concepts from prior_user_concepts that overlap with this document's prerequisites — "
                     "i.e. gaps the user has ALREADY closed based on history, so don't repeat these in 'gaps'"
    )


missing_knowledge_parser = PydanticOutputParser(pydantic_object=MissingKnowledgeOutput)

MISSING_KNOWLEDGE_SYSTEM_PROMPT = """You are an expert learning diagnostician. Your job is to find the gaps \
between what a document ASSUMES the reader knows and what the reader has ACTUALLY demonstrated knowing, based \
on their learning history from previous documents.

You will be given:
1. The current document's context.
2. A list of concepts the user has already learned from previous documents (prior_user_concepts) — this may be empty for a first-time user.

Rules:
- A "gap" is something the current document relies on (explicitly or implicitly) but does NOT itself explain, \
  AND that does not appear in prior_user_concepts.
- Cross-reference prior_user_concepts carefully — if the user already learned a prerequisite previously, do \
  NOT list it as a gap; instead list it in user_likely_already_knows.
- Do not list gaps that are trivial general knowledge (e.g. "what a sentence is") — only domain-relevant gaps.
- Each suggested_lookup should be a real, specific, searchable term — not a vague phrase.
- If prior_user_concepts is empty, treat this as the user's first document and identify all reasonable gaps.

{format_instructions}"""

MISSING_KNOWLEDGE_HUMAN_PROMPT = """Current document context:

{context}

User's prior learned concepts (from earlier documents, may be empty):
{prior_user_concepts}

Identify knowledge gaps following the schema."""

missing_knowledge_prompt = ChatPromptTemplate.from_messages([
    ("system", MISSING_KNOWLEDGE_SYSTEM_PROMPT),
    ("human", MISSING_KNOWLEDGE_HUMAN_PROMPT),
]).partial(format_instructions=missing_knowledge_parser.get_format_instructions())