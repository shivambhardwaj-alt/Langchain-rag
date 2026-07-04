from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    chain_type: str
    session_id: str
    query: str
    doc_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str