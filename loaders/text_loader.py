import logging
from pathlib import Path
import chardet 
from langchain_core.documents import Document
logger = logging.getLogger(__name__)


def load_txt(file_path : str , doc_id : str) -> list[Document]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f'Text file not Found at {file_path}')
    raw_bytes = path.read_bytes()
    if not raw_bytes:
        raise ValueError(f'File is empty at {file_path}')
    detected = chardet(raw_bytes)
    encoding = detected.get("encoding") or "utf-8"
    confidence = detected.get("confidence" , 0.0)
    if confidence <  0.5 : 
        logger.warning(
            f"Low confidence ({confidence:.2f}) detecting encoding for '{path.name}', "
            f"defaulting to utf-8 with error replacement"
        )
        encoding = "utf-8"
    try : 
        text = raw_bytes.decode(encoding=encoding,  errors= "replace")
        
    except (LookupError , UnicodeDecodeError) as e : 
        logger.error(f"Failed to decode '{path.name}' with detected encoding '{encoding}': {e}")
        text = raw_bytes.decode("utf-8", errors="replace")
    text = text.strip()
    if not text : 
        raise ValueError(f'Text file {file_path} not contains usable content after decoding')
    doc = Document(
        page_content=text,
        metadata={
            "source": path.name,
            "doc_id": doc_id,
            "file_type": "txt",
            "detected_encoding": encoding,
            "char_count": len(text),
        },
    )
    
    logger.info(f'Loaded TXT {path.name} : {len(text)}  chars : encoding = {encoding}')
    return [doc]
