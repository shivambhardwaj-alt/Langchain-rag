from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
CONTEXTUALIZE_SYSTEM_PROMPT = """Given a chat history and the latest user question which might reference \
context in the chat history, formulate a standalone question which can be understood without the chat \
history. Do NOT answer the question, just reformulate it if needed, otherwise return it as-is."""


contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", CONTEXTUALIZE_SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])


CHAT_SYSTEM_PROMPT = """You are a knowledgeable study assistant helping the user understand their uploaded \
documents. Answer using ONLY the provided context below. If the context doesn't contain the answer, say so \
clearly instead of guessing or using outside knowledge.
If there is no context just make every  assumption by  yourself and search in your knowledgebase and try to find\
the answer give as much as explaination as possible.

Be conversational but precise. Reference specific parts of the document when relevant. If the user is asking \
about something covered in their earlier uploads (shown in prior learning context, if provided), connect the \
dots for them explicitly.
Context from relevant documents:
{context}

Prior learning context (concepts from earlier uploads, if relevant):
{prior_context}"""

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", CHAT_SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

chat_parser = StrOutputParser()
