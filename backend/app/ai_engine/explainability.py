
from typing import Any


def build_explanation(
    finding: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create an explainable review result."""

    evidence_map = {
        item["evidence_id"]: item
        for item in evidence
    }

    supporting_sources = []

    for evidence_id in finding.get("evidence_ids", []):
        item = evidence_map.get(str(evidence_id))

        if item:
            supporting_sources.append({
                "evidence_id": item["evidence_id"],
                "source_title": item["source_title"],
                "source_text": item["evidence_text"],
            })

    return {
        "issue": finding.get("title", "Review issue"),
        "category": finding.get("category", "General"),
        "severity": finding.get("severity", "medium"),
        "original_text": finding.get("quoted_text", ""),
        "reason": finding.get(
            "description",
            "This content may need further review."
        ),
        "suggested_correction": finding.get(
            "suggested_correction"
        ),
        "supporting_sources": supporting_sources,
        "required_action": (
            "Required Action"
            if finding.get("severity") == "high"
            else "Review Recommended"
        ),
        "confidence": finding.get("confidence", 0.0),
    }
