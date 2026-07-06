from pydantic import BaseModel
from typing import Optional, Any   

class ChatRequest(BaseModel):
    chain_type: str
    session_id: str
    query: str
    doc_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: Any
    session_id: str