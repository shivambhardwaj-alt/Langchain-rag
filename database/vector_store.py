import logging
from pathlib import Path
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

PERSIST_DIRECTORY = "data/vector_db"
COLLECTION_NAME = "ai_knowledge_studio"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_embeddings = None
_vector_store = None



def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings



def get_vector_store() -> Chroma:
    global _vector_store

    if _vector_store is None:
        Path(PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)

        _vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=_get_embeddings(),
            persist_directory=PERSIST_DIRECTORY,
        )

        logger.info(f"Initialized Chroma Vector Store at {PERSIST_DIRECTORY}")

    return _vector_store



def add_chunks(chunks: list[Document]) -> list[str]:
    if not chunks:
        raise ValueError("Cannot add empty chunk list to vector store")

   
    for c in chunks:
        if "doc_id" not in c.metadata:
            raise ValueError("Missing doc_id in chunk metadata")
        if "chunk_id" not in c.metadata:
            raise ValueError("Missing chunk_id in chunk metadata")

    store = get_vector_store()

    chunk_ids = [
        f"{c.metadata['doc_id']}_{c.metadata['chunk_id']}"
        for c in chunks
    ]

  
    for c in chunks:
        c.metadata["doc_id"] = str(c.metadata["doc_id"])
        c.metadata["chunk_id"] = str(c.metadata["chunk_id"])

    ids = store.add_documents(documents=chunks, ids=chunk_ids)

    logger.info(f"Added {len(ids)} chunks to vector store")

    return ids



def get_retriever(doc_id: str | None = None, k: int = 5):
  
    store = get_vector_store()

    search_kwargs = {"k": k}

    if doc_id:
    
        search_kwargs["where"] = {"doc_id": doc_id}
    else:
        logger.warning("No doc_id provided → global retrieval enabled")

    return store.as_retriever(search_kwargs=search_kwargs)



def similarity_search(
    query: str,
    k: int = 5,
    doc_id: str | None = None
) -> list[Document]:

    store = get_vector_store()

    where_filter = {"doc_id": doc_id} if doc_id else None

    return store.similarity_search(
        query,
        k=k,
        filter=where_filter   
    )



def delete_document(doc_id: str) -> None:
    store = get_vector_store()

    store.delete(where={"doc_id": doc_id})

    logger.info(f"Deleted all chunks for doc_id={doc_id}")