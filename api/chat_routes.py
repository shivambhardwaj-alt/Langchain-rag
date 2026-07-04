from fastapi import APIRouter, Depends
from schemas.chat_schema import ChatRequest , ChatResponse
from auth.dependencies import get_current_user
from chains.feautres_chain import run_chain

router = APIRouter(prefix="/chat", tags=["Chat"])

#user=Depends(get_current_user)
@router.post("/model", response_model=ChatResponse)
def chat(payload: ChatRequest):
    result = run_chain(
        chain_type=payload.chain_type,
        sessionId=payload.session_id,
        query=payload.query,
        doc_id=payload.doc_id,
    )

    return result