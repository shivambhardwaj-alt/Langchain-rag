import logging

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from database.vector_store import get_retriever
from memory.conversation_memory import get_session_history

from config import llm_1 , llm_2 ,llm_3 ,llm_4, LLM_TEMPERATURE

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
from langchain_core.runnables import (
    RunnableParallel, 
    RunnableLambda,
    RunnablePassthrough,
)

from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

logger = logging.getLogger(__name__)


_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = llm_1
        logger.info(f"Initialized model: {_llm}")
    return _llm



def _format_docs(docs) -> str:
    return "\n\n--\n\n".join(doc.page_content for doc in docs)


UNIVERSAL_FALLBACK_CHAIN = (
                                UNIVERSAL_FALLBACK_PROMPT | get_llm() | universal_fallback_parser
    )


def get_smart_context(doc_id: str | None, query: str):
    
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
    "counterargs":  (counter_args_prompt, counter_args_parser),
    "missing_knowledge": (missing_knowledge_prompt, missing_knowledge_parser),
    "roadmap": (roadmap_prompt, roadmap_parser),
    "explain_simple": (explain_simple_prompt, StrOutputParser()),
    "explain_technical": (explain_technical_prompt, StrOutputParser()),
}

branch_a_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You refine draft content. Given the draft below, improve clarity, "
     "fix gaps, and keep the SAME structure/format as the draft. And make a good quality  Prompt which generates possibility "
     "Do not add commentary, only output the improved content."),
    ("human", "{stage1_output}")
])

branch_b_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You cross-check draft content for accuracy and completeness. Given the "
     "draft below, correct errors and fill missing pieces, keeping the SAME "
     "structure/format as the draft. Do not add commentary, only output the "
     "corrected content."),
    ("human", "{stage1_output}")
])

master_combine_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are the final editor. Merge Version A and Version B below into ONE "
     "final output. Preserve the required structure/format implied by both "
     "versions (e.g. if they look like JSON, output valid JSON; if they are "
     "plain text, output plain text). Do not include any preamble, only the "
     "final merged content."),
    ("human", "Version A:\n{branch_a}\n\nVersion B:\n{branch_b}")
])


_parallel_stage = RunnableParallel(
    branch_a=branch_a_prompt | llm_2 | StrOutputParser(),
    branch_b=branch_b_prompt | llm_3 | StrOutputParser(),
)


def llm_merge(prompt, parser, input: dict, chain_type):
    stage1_chain = prompt | llm_1 | StrOutputParser()
    stage1_output = stage1_chain.invoke(input)

    parallel_result = _parallel_stage.invoke({
        "stage1_output": stage1_output
    })
    

    _combine_chain = master_combine_prompt | llm_4 | parser

    final_output = _combine_chain.invoke({
        "branch_a": stage1_output,
        "branch_b": parallel_result["branch_b"]
    })

    return final_output

def run_chain(
    chain_type,
    doc_id: str | None = None,
    query: str = "",
    sessionId: str | None = None,
    user_history: str | None = None,
):

    chat_history = []
    if sessionId:
        history = get_session_history(sessionId)
        chat_history = history.messages

    if chain_type not in CHAIN_MAP:
        return {"response": "Invalid chain type", "sessionId": sessionId}

    retriever = get_retriever(doc_id=doc_id)

    history_aware_retriever = create_history_aware_retriever(
        llm_1,
        retriever,
        contextualize_prompt,
    )

    docs = history_aware_retriever.invoke({
        "input": query,
        "chat_history": chat_history,
    })

    context = _format_docs(docs)

    
    inputs = {
    "context": context,
    "input": query,
    "chat_history": chat_history,
    "prior_context": user_history or "(none)"
}

    prompt, parser = CHAIN_MAP[chain_type]

    
    if chain_type.startswith("explain"):
        inputs["specific_topic_instruction"] = query

    if chain_type == "missing_knowledge":
        inputs["prior_user_concepts"] = user_history or "(none)"

    if chain_type == "roadmap":
        inputs["user_history"] = user_history or "(none)"

   
    result = llm_merge(
        prompt=prompt,
        parser=parser,
        input=inputs,
        chain_type=chain_type,
    )

    return {
        "response": result,
        "session_id": sessionId,
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


