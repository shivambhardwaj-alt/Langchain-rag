from database.mongo_store import get_all_user_concepts, get_all_documents,get_document,find_related_documents
import logging


logger = logging.getLogger(__name__)
def get_learning_context(current_doc_concepts : list[str] | None = None):
    prior_concepts = get_all_user_concepts()
    prior_document = get_all_documents()
    related_docs = []
    if current_doc_concepts :   
        related_docs = find_related_documents(current_doc_concepts)
    return {
        "prior_user_concepts": prior_concepts,
        "prior_documents_summary": [
            {"filename": d["filename"], "summary": d.get("summary")} for d in prior_documents
        ],
        "related_documents": related_docs,
    }


def format_user_history_for_prompt(context : dict) -> str : 
    if not context["prior_documents_summary"]:
        return "(no prior documents — this is the user's first upload)"
    lines = []
    for doc in context["prior_documents_summary"]:
        summary_snippet = (doc.get("summary")  or "")[:200]
        lines.append(f"- {doc['filename']} : {summary_snippet}")
    concepts_line = f"\nConcepts already learned: {', '.join(context['prior_user_concepts'])}"
    return "\n".join(lines) + concepts_line



def link_related_documents(doc_id: str, related_docs: list[dict]) -> None:
    """
    Persist the related_doc_ids back onto the current document's Mongo record,
    so the relationship is queryable later without recomputing similarity.
    """
    from database.mongo_store import update_one_document

    related_ids = [d["doc_id"] for d in related_docs if d.get("doc_id") != doc_id]
    if related_ids:
        update_one_document(doc_id, "related_doc_ids", related_ids)
        logger.info(f"Linked {len(related_ids)} related documents to doc_id={doc_id}")
    
