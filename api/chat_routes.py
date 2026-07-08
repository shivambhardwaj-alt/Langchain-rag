from fastapi import APIRouter, UploadFile, File , HTTPException
from schemas.chat_schema import ChatRequest, ChatResponse
from chains.feautres_chain import run_chain
import shutil
import os

router = APIRouter(prefix="/chat", tags=["Chat"])



@router.post("/model", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    result = run_chain(
        chain_type=payload.chain_type,
        sessionId=payload.session_id,
        query=payload.query,
        doc_id=payload.doc_id,
    )
    return {
        "response": result["response"],
        "sessionId": result["session_id"],
    }

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    filename = os.path.basename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # now get the file and add that to the vector database 
    # only url is left now    

    return {
        "message": "File uploaded successfully",
        "filename": filename,
        "path": file_path,
    }