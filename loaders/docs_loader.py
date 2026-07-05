

import logging
from pathlib import Path

from docx import Document as DocxDocument
from docx.table import Table
from docx.text.paragraph import Paragraph
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def load_docx(file_path: str, doc_id: str) -> list[Document]:
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"DOCX not found at: {file_path}")

    try:
        docx_file = DocxDocument(file_path)
    except Exception as e:
        logger.error(f"Failed to open DOCX '{path.name}': {e}")
        raise ValueError(f"'{path.name}' is not a valid .docx file or is corrupted") from e

    sections: list[dict] = []
    current_section = {"heading": "Document Start", "level": 0, "content": []}

   
    for element in _iter_block_items(docx_file):
        if isinstance(element, Paragraph):
            style_name = (element.style.name or "").lower()
            is_heading = style_name.startswith("heading") or style_name == "title"

            if is_heading and element.text.strip():
                if current_section["content"]:
                    sections.append(current_section)
                level = 0
                if style_name.startswith("heading"):
                    try:
                        level = int(style_name.replace("heading", "").strip())
                    except ValueError:
                        level = 1
                current_section = {"heading": element.text.strip(), "level": level, "content": []}
            elif element.text.strip():
                current_section["content"].append(element.text.strip())

        elif isinstance(element, Table):
            table_text = _table_to_text(element)
            if table_text:
                current_section["content"].append(f"[TABLE]\n{table_text}\n[/TABLE]")

    if current_section["content"]:
        sections.append(current_section)

    if not sections:
        raise ValueError(f"DOCX '{path.name}' contains no extractable text content")

    docs: list[Document] = []
    for i, section in enumerate(sections):
        body_text = "\n\n".join(section["content"]).strip()
        if not body_text:
            continue
        docs.append(
            Document(
                page_content=f"{section['heading']}\n\n{body_text}" if section["heading"] != "Document Start" else body_text,
                metadata={
                    "source": path.name,
                    "doc_id": doc_id,
                    "section_index": i,
                    "section_heading": section["heading"],
                    "heading_level": section["level"],
                    "file_type": "docx",
                },
            )
        )

    if not docs:
        raise ValueError(f"DOCX '{path.name}' produced no non-empty sections")

    logger.info(f"Loaded DOCX '{path.name}': {len(docs)} sections")
    return docs


def _iter_block_items(docx_file: DocxDocument):
    """Yield paragraphs and tables in the order they appear in the document body."""
    from docx.oxml.ns import qn
    parent_elm = docx_file.element.body
    for child in parent_elm.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, docx_file)
        elif child.tag == qn("w:tbl"):
            yield Table(child, docx_file)


def _table_to_text(table: Table) -> str:
    """Convert a docx table into pipe-delimited readable text, skipping fully empty rows."""
    rows_text = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        if any(cells):
            rows_text.append(" | ".join(cells))
    return "\n".join(rows_text)