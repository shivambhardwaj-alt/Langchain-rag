import logging 
from pathlib import Path
from langchain_core.documents import Document
from typing import List
from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader


logger  = logging.getLogger(__name__)
def load_pdf(file_path : str , doc_id : str) -> List[Document]:
    path = Path(file_path)
    if not path.exists() :
        raise FileNotFoundError(f'File not found at : {file_path}')
    docs : List[Document] = []
    try : 
        loader  = PyMuPDFLoader(file_path=file_path)
        docs = loader.load()
        logger.info(f'Loaded pdf {file_path}  via PyMuPDFloader : {len(docs)} pages')
    except Exception as e : 
        try : 
            logger.warning(f'PyMuPdfLoader failed for {file_path} ,falling back to PyPDFLoader')
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            logger.info(f"Loaded PDF '{path.name}' via PyPDFLoader fallback: {len(docs)} pages")
        except Exception as fallback_error : 
            logger.error(f"Both PDF loaders failed for '{path.name}': {fallback_error}")
            raise ValueError(f"Could not extract content from PDF: {path.name}") from fallback_error
        if not docs : 
            raise ValueError(f'Pdf {path.name} produced zero pages')
    total_text_length = sum(len(d.page_content.strip()) for d in docs)
    avg_chars_per_page = total_text_length / max(len(docs), 1)
    
    if avg_chars_per_page < 20 : 
        logger.error(
                     f'PDF {path.name} has near zero-extractable text'
                     f"(avg {avg_chars_per_page:.1f} chars/page) — likely scanned/image-only, needs OCR"
                     )
        raise ValueError(
            f"PDF '{path.name}' appears to be a scanned/image-only document with no "
            f"extractable text. OCR processing is required but not supported by this loader."
        )
    totalPages = len(docs)
    for i , doc in enumerate(docs):
        doc.metadata.update({
            "source": path.name,
            "doc_id": doc_id,
            "page": doc.metadata.get("page", i) + 1,  
            "total_pages": totalPages, 
            "file_type": "pdf",
        })
        doc.page_content = " ".join(doc.page_content.split())
    return docs
