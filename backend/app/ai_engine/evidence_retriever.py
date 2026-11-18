
import re
from typing import Any


def tokenize(text: str) -> set[str]:
    """Extract searchable words from text."""

    return {
        word.lower()
        for word in re.findall(r"\b[a-zA-Z0-9]+\b", text)
        if len(word) > 2
    }


def retrieve_evidence(
    document_text: str,
    approved_sources: list[dict[str, Any]],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Retrieve relevant passages from approved sources.

    Only approved sources passed to this function are considered.
    """

    document_words = tokenize(document_text)

    results = []

    for source in approved_sources:
        content = source.get("content", "")
        source_words = tokenize(content)

        if not source_words:
            continue

        common_words = document_words.intersection(source_words)

        relevance = len(common_words) / max(len(document_words), 1)

        if relevance <= 0:
            continue

        results.append({
            "evidence_id": str(source["id"]),
            "source_title": source.get("title", "Untitled Source"),
            "source_type": source.get("source_type", "general"),
            "evidence_text": content,
            "relevance": round(min(relevance, 1.0), 3),
            "authority": source.get("authority", 0.8),
        })

    results.sort(
        key=lambda item: item["relevance"],
        reverse=True,
    )

    return results[:limit]
