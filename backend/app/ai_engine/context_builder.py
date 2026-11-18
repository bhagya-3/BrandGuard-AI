
from typing import Any


def build_review_context(
    document_text: str,
    document_name: str,
    approved_sources: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Prepare document content and approved sources
    for the BrandGuard AI review process.
    """

    if not document_text or not document_text.strip():
        raise ValueError("Document content cannot be empty.")

    source_context = []

    for source in approved_sources:
        if not source.get("id") or not source.get("content"):
            continue

        source_context.append({
            "id": str(source["id"]),
            "title": source.get("title", "Untitled Source"),
            "source_type": source.get("source_type", "general"),
            "content": source["content"],
            "authority": source.get("authority", 0.8),
        })

    return {
        "document_name": document_name,
        "document_text": document_text.strip(),
        "approved_sources": source_context,
        "source_count": len(source_context),
    }
