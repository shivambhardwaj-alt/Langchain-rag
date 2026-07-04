from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

universal_fallback_parser = StrOutputParser()

UNIVERSAL_FALLBACK_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     """
You are a highly intelligent AI assistant.

You must answer the user's question using your general knowledge.

Rules:
- Be accurate and helpful
- If the question is a concept → explain clearly with examples
- If it is a summary request → give structured bullet summary
- If it is a how/why question → explain step by step
- If unsure → say you are not certain instead of hallucinating
- Keep response clean and structured
"""),
    ("human", "{question}")
])



