import logging 
from datetime import datetime , timezone
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from config import MONGO_URI ,MONGO_DB_NAME
from langchain_core.documents import Document
logger = logging.getLogger(__name__)
_client = None
_db = None

def get_db():
    global _client , _db
    if _db is None :
        _client  = MongoClient(MONGO_URI)
        _db = _client[MONGO_DB_NAME]
        logger.info(f'Connected to Database {MONGO_DB_NAME}')
    return _db

def save_document_record(doc_id : str , filename : str, file_type : str , summary : str |None = None , concepts : list[dict] | None =  None ,prerequisite_concepts : list[str] | None= None) -> str : 
    db = get_db()
    collection = db['documents']
    record = {
        "doc_id": doc_id,
        "filename": filename,
        "file_type": file_type,
        "upload_date": datetime.now(timezone.utc),
        "summary": summary,
        "concepts": concepts or [],
        "prerequisite_concepts": prerequisite_concepts or [],
        "related_doc_ids": [],
    }

    try : 
        collection.update_one(
            {doc_id : doc_id}, 
            {"$set" : record},
            upsert= True,
        )
        logger.info(f'Saved Document record for document id {doc_id}')
    except  PyMongoError as e  :
        logger.error(f'Failed to save the document record for document id {doc_id}')
        raise
    return doc_id
def update_one_document(doc_id : str , field: str , value ) -> dict | None : 
    db = get_db()
    db["documents"].update_one({"doc_id": doc_id}, {"$set": {field: value}})

def get_document(doc_id : str ) -> dict | None : 
    db = get_db()
    return db["documents"].find_one({"doc_id" : doc_id} , {"_id" : 0})

def get_all_documents() -> list[Document]:
    db = get_db()
    return list(db["documents"].find({}, {"_id": 0}).sort("upload_date", -1))
def get_all_user_concepts() -> list[Document]:
    db = get_db()
    allconcepts = set()
    for doc in db['documents'].find({} , {"_id" : 0  , "concepts" : 1}):
        for concept in doc.get("concepts" , []):
            name = concept.get("name") if isinstance (concept , dict) else None 
            if name : 
                allconcepts.add(name)
    return sorted(allconcepts)


def delete_document_record(doc_id : str) -> bool : 
    db = get_db()
    result = db['documents'].delete_one({"doc_id" : doc_id})
    return result.deleted_count > 0 
def find_related_documents(concept_names : list[str] , exclude_doc_id : str | None = None) -> list[dict]:
    if not concept_names:
        return []
    db = get_db()
    query = {"concepts.name": {"$in": concept_names}}
    results = db['documents'].find(
        query , 
        {"_id": 0, "doc_id": 1, "filename": 1, "summary": 1, "concepts": 1},
        
    )
    return list[results]

    
