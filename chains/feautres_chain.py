import logging

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from database.vector_store import get_retriever
from memory.conversation_memory import get_session_history

from config import LLM_MODEL, LLM_TEMPERATURE

from typing import Literal
from prompts.summary_prompt import summary_prompt, summaryParse
from prompts.concept_prompt import concepts_prompt, concepts_parser
from prompts.questions_prompt import questions_prompt, questions_parser
from prompts.mindmap_prompt import mindmap_prompt, mindmap_parser
from prompts.quiz_prompt import quiz_prompt, quiz_parser
from prompts.flashcard_prompt import flashcards_parser, flashcards_prompt
from prompts.counterargs_prompt import counter_args_parser, counter_args_prompt
from prompts.explainsimple_prompt import explain_simple_prompt
from prompts.explaintechnical_prompt import explain_technical_prompt
from prompts.missingKnowledge_prompt import missing_knowledge_parser, missing_knowledge_prompt
from prompts.roadmap_prompt import roadmap_prompt, roadmap_parser
from prompts.chat_prompt import contextualize_prompt, chat_prompt ,chat_parser
from prompts.fallback_prompt import UNIVERSAL_FALLBACK_PROMPT, universal_fallback_parser
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
        logger.info(f"Initialized model: {_llm}")
    return _llm



def _format_docs(docs) -> str:
    return "\n\n--\n\n".join(doc.page_content for doc in docs)


UNIVERSAL_FALLBACK_CHAIN = (
                                UNIVERSAL_FALLBACK_PROMPT | get_llm() | universal_fallback_parser
    )


def get_smart_context(doc_id: str | None, query: str):
    """
    Returns:
        context (str)
        found (bool)
    """
    retriever = get_retriever(doc_id=doc_id, k=5)    
    docs = retriever.invoke(query)


    try:
        docs = retriever.invoke(query)
       
    except Exception as e:
        logger.error(f"Retriever failed: {e}")
        return "", False

    if not docs:
        return "", False

    return _format_docs(docs), True
   


def _safe_context(doc_id: str, query: str):
    context, found = get_smart_context(doc_id, query)
    if not found:
        context = ""
    return context


CHAIN_MAP = {
    "chat" : (chat_prompt,chat_parser),
    "summary": (summary_prompt, summaryParse),
    "concepts": (concepts_prompt, concepts_parser),
    "questions": (questions_prompt, questions_parser),
    "mindmap": (mindmap_prompt, mindmap_parser),
    "quiz": (quiz_prompt, quiz_parser),
    "flashcards": (flashcards_prompt, flashcards_parser),
    "counterargs": (counter_args_prompt, counter_args_parser),
    "missing_knowledge": (missing_knowledge_prompt, missing_knowledge_parser),
    "roadmap": (roadmap_prompt, roadmap_parser),
    "explain_simple": (explain_simple_prompt, StrOutputParser()),
    "explain_technical": (explain_technical_prompt, StrOutputParser()),
}





def run_chain(
    chain_type,
    doc_id: str | None = None,
    query: str = "",
    sessionId: str | None = None,
    user_history: str | None = None,
):
    llm = get_llm()

   
    chat_history: list[BaseMessage] = []

    if sessionId:
        history_obj = get_session_history(session_id=sessionId)
        chat_history = history_obj.messages

    if  chain_type != "chat":
        retriever = get_retriever(doc_id=doc_id)

        history_aware_retriever = create_history_aware_retriever(
            llm,
            retriever,
            contextualize_prompt
        )

        
        docs = history_aware_retriever.invoke({
            "input": query,
            "chat_history": chat_history  
        })

        context = _format_docs(docs)
        found = len(docs) > 0
        if chain_type not in CHAIN_MAP:
            return {
                "response": "Invalid chain type",
                "session_id": sessionId
            }

        prompt, parser = CHAIN_MAP[chain_type]
        chain = prompt | llm | parser

        if not found:
            if chain_type == "summary":
                result = UNIVERSAL_FALLBACK_CHAIN.invoke({"question": query})

            elif chain_type in ["quiz", "questions", "flashcards", "counterargs"]:
                result = []

            elif chain_type == "mindmap":
                result = {"nodes": []}

            elif chain_type.startswith("explain"):
                result = "No relevant content found in document."

            elif chain_type == "roadmap":
                result = {"steps": []}

            else:
                result = ""


        else:
            inputs = {
                "context": context,
                "question": query
            }

            if chain_type.startswith("explain"):
                inputs["specific_topic_instruction"] = f"Focus specifically on: {query}"

            if chain_type == "missing_knowledge":
                inputs["prior_user_concepts"] = user_history or "(none)"

            if chain_type == "roadmap":
                inputs["user_history"] = user_history or "(none)"

            result = chain.invoke(inputs)
            
        


            if hasattr(result, "model_dump"):
                result = str(result.model_dump())
            elif hasattr(result, "dict"):
                result = str(result.dict())
    else:
        
        prompt , parser = CHAIN_MAP["chat"] 
        chain = prompt | llm |parser
        result = chain.invoke(inputs)
        

    return {
        "response": result,
        "session_id": sessionId
    }

def get_chat_chain():
    
    llm = get_llm()
    retriever = get_retriever()

    history_aware_retriever = create_history_aware_retriever(
        llm,
        retriever,
        contextualize_prompt
    )

    qa_chain = create_stuff_documents_chain(llm, chat_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

    conversational_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return conversational_chain


_chat_chain = None

def get_chat_chain_singleton():
    global _chat_chain
    if _chat_chain is None:
        _chat_chain = get_chat_chain()
    return _chat_chain