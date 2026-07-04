from fastapi import APIRouter , UploadFile , File , Form , HTTPException 
from pydantic import BaseModel 

from loaders.loader_factory import get_loader