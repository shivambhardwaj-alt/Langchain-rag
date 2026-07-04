import logging
import uuid
from pathlib import Path



import os
import tempfile
import requests
from langchain_core.documents import Document
from loaders.pdf_loader import load_pdf
from loaders.text_loader import load_txt
from loaders.docs_loader import load_docx
from loaders.ppt_loader import load_ppt
from loaders.web_loader import load_web
from typing import List
logger  = logging.getLogger(__name__)


EXTENSION_LOADER_MAP = {
    ".pdf": load_pdf,
    ".txt": load_txt,
    ".docx": load_docx,
    ".pptx": load_ppt,
}

SUPPORTED_EXTENSIONS = set(EXTENSION_LOADER_MAP.keys()) | {"web"}



def generate_doc_id()-> str : 
    return str(uuid.uuid4())


def get_loader(source : str , doc_id : str) -> List[Document]:
    if not source or not source.strip():
        raise ValueError(f'Source/pathUrl cannot be empty')
    doc_id = doc_id or generate_doc_id()
    source = source.strip()
    if source.startswith("http://") or source.startswith("https://"):
        logger.info(f"Dispatching to web_loader for: {source}")
        return load_web(source, doc_id)
    path = Path(source)
    extension = path.suffix.lower()
    if extension not in EXTENSION_LOADER_MAP:
        supported = ", ".join(sorted(EXTENSION_LOADER_MAP.keys())) + ", web URLs"
        raise ValueError(
            f"Unsupported file type: '{extension}'. Supported types: {supported}"
        )
    loader_fn = EXTENSION_LOADER_MAP[extension]
    logger.info(f"Dispatching to {loader_fn.__name__} for path : {path.name}")
    return loader_fn(source, doc_id)    


def ingest_file(file_bytes: bytes, filename: str, doc_id: str | None = None) -> dict:
    """
    Saves uploaded file bytes to a temp path, loads + splits it,
    then pushes chunks into the vector store under a doc_id.
    """
    extension = os.path.splitext(filename)[1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}. Supported: {SUPPORTED_EXTENSIONS}")

    doc_id = doc_id or str(uuid.uuid4())

    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        raw_docs = _load_file(tmp_path, extension)
    finally:
        os.remove(tmp_path)

    if not raw_docs:
        raise ValueError("No content could be extracted from the file.")

    splitter = _get_splitter()
    chunks = splitter.split_documents(raw_docs)

    for chunk in chunks:
        chunk.metadata["doc_id"] = doc_id
        chunk.metadata["source"] = filename

    add_documents(doc_id=doc_id, chunks=chunks)

    logger.info(f"Ingested file '{filename}' as doc_id={doc_id} with {len(chunks)} chunks")

    return {
        "doc_id": doc_id,
        "source": filename,
        "chunks": len(chunks),
    }


def ingest_url(url: str, doc_id: str | None = None) -> dict:
    """
    Loads content from a URL, splits it, and pushes chunks into
    the vector store under a doc_id.
    """
    doc_id = doc_id or str(uuid.uuid4())

    try:
        raw_docs = WebBaseLoader(url).load()
    except Exception as e:
        logger.warning(f"WebBaseLoader failed for {url}: {e}. Trying UnstructuredURLLoader.")
        try:
            raw_docs = UnstructuredURLLoader(urls=[url]).load()
        except Exception as e2:
            logger.error(f"UnstructuredURLLoader also failed for {url}: {e2}")
            raise ValueError(f"Could not load content from URL: {url}")

    if not raw_docs:
        raise ValueError(f"No content extracted from URL: {url}")

    splitter = _get_splitter()
    chunks = splitter.split_documents(raw_docs)

    for chunk in chunks:
        chunk.metadata["doc_id"] = doc_id
        chunk.metadata["source"] = url

    add_documents(doc_id=doc_id, chunks=chunks)

    logger.info(f"Ingested URL '{url}' as doc_id={doc_id} with {len(chunks)} chunks")

    return {
        "doc_id": doc_id,
        "source": url,
        "chunks": len(chunks),
    }