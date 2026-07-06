import logging
from collections import defaultdict
from datetime import datetime, timedelta

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_community.chat_message_histories import ChatMessageHistory

logger = logging.getLogger(__name__)

_session_store: dict[str, ChatMessageHistory] = {}
_session_last_active: dict[str, datetime] = {}

SESSION_TTL_MINUTES = 60
MAX_MESSAGES = 20

def _is_expired(session_id: str) -> bool:
    if session_id not in _session_last_active:
        return True
    last_active = _session_last_active[session_id]
    return datetime.utcnow() - last_active > timedelta(minutes=SESSION_TTL_MINUTES)

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in _session_store or _is_expired(session_id):
        _session_store[session_id] = ChatMessageHistory()
        logger.info(f"Created new session: {session_id}")
    _session_last_active[session_id] = datetime.utcnow()
    return _session_store[session_id]

def clear_session(session_id: str) -> None:
    _session_store.pop(session_id, None)
    _session_last_active.pop(session_id, None)
    logger.info(f"Cleared session: {session_id}")


def get_session_messages(session_id: str) -> list[BaseMessage]:
    history = get_session_history(session_id)


    history.messages = history.messages[-MAX_MESSAGES:]

    return history.messages


def list_active_sessions() -> list[str]:
    return list(_session_store.keys())