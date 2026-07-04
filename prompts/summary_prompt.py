from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel , Field
from langchain_core.output_parsers import PydanticOutputParser 
from typing import List



class SummaryOutput(BaseModel):
    tldr : str  = Field(description="1-2 sentence summary max 40 words")
    summary : str  = Field( description= "Full Summary , 200-400 words , well-structured")
    key_takeaways : List[str] = Field(description= "3-6 bullet point takeaways")
    document_type : str  = Field(description= "e.g. research paper, lecture notes, business report, tutorial")
    
    estimated_reading_time_minutes: int  = Field(description="Original document's estimated reading time")
summaryParse = PydanticOutputParser(pydantic_object = SummaryOutput)
SUMMARY_SYSTEM_PROMPT =  """You are an expert document analyst. Your job is to produce summaries that someone \
could use INSTEAD of reading the original document, not just a vague gist.

Rules:
- Ground every claim strictly in the provided context. Never add external knowledge or assumptions.
- If the document is technical, preserve technical precision in the summary — do not oversimplify.
- If the document contains conflicting statements internally, mention the conflict rather than picking one side.
- Do not summarize formatting artifacts (e.g. "this document has 3 sections") — summarize content.
- If the provided context appears incomplete (e.g. cut off mid-sentence), note this in document_type field \
  as "partial extraction" but still summarize what's available.

{format_instructions}"""



SUMMARY_HUMAN_PROMPT = """Document context (may be multiple chunks, possibly out of order):

{context}

Produce a summary following the required schema."""

summary_prompt = ChatPromptTemplate([
    ("system" , SUMMARY_SYSTEM_PROMPT),
    ("human" , SUMMARY_HUMAN_PROMPT)
]).partial(format_instructions = summaryParse.get_format_instructions())