import logging
from typing import List 
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
logger  = logging.getLogger(__name__)



CHUNK_CONFIG = {
    "pdf":  {"chunk_size": 1000, "chunk_overlap": 150},
    "docx": {"chunk_size": 1000, "chunk_overlap": 150},
    "pptx": {"chunk_size": 500,  "chunk_overlap": 50},
    "txt":  {"chunk_size": 1000, "chunk_overlap": 150},
    "web":  {"chunk_size": 1200, "chunk_overlap": 200},
}



DEFAULT_CONFIG = {"chunk_size" : 1000 , "chunk_overlap" : 150}

def chunk_document(docs : List[Document] , doc_id : str) -> List[Document]:
    if not docs : 
        raise ValueError(f'Cannot chunk empty list for doc_id = {doc_id}')
    
    mismatched = [d for d in docs if d.metadata.get("doc_id") != doc_id]
    
    if mismatched:
        raise ValueError(
        f'doc_id mismatch expected \'{doc_id}\' but found documents with '
        f'different doc_id in metadata. Check loader output before chunking.'
        )
    file_type = docs[0].metadata.get("file_type" , "unknown")
    
    config = CHUNK_CONFIG.get(file_type,DEFAULT_CONFIG)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = config['chunk_size'],
        chunk_overlap = config['chunk_overlap'],
        length_function = len,
        separators= ["\n\n" , "\n" , "." , " " , ""]
        
    )
    all_chunks : List[Document] = []
    global_chunk_index = 0 
    for parent_doc in docs : 
        if not parent_doc.page_content.strip():
            continue
        split_texts = splitter.split_text(parent_doc.page_content)
        
        
        
        for local_idx , text in enumerate(split_texts):
            chunk_metadata = dict(parent_doc.metadata)
            chunk_metadata.update({
                "chunk_index" : global_chunk_index ,
                "chunk_id" : f'{doc_id}_chunk_{global_chunk_index}',
                "chunk_char_count" : f'{len(text)}'
            })
            all_chunks.append(Document(page_content = text ,metadata =  chunk_metadata))
            global_chunk_index += 1
            
    if not all_chunks:
        raise ValueError(f"Chunking produced zero chunks for doc_id={doc_id} — all pages may be empty")

    logger.info(
        f"Chunked doc_id={doc_id} (file_type={file_type}): "
        f"{len(docs)} source units -> {len(all_chunks)} chunks "
        f"(chunk_size={config['chunk_size']}, overlap={config['chunk_overlap']})"
    )

    return all_chunks