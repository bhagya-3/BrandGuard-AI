
from typing import Any


class CitationBuilder:

    @staticmethod
    def build_citation(
        source_match: dict[str, Any],
    ) -> dict:

        if not source_match.get("source_id"):
            raise ValueError("Citation requires a source ID.")

        if not source_match.get("source_version_id"):
            raise ValueError("Citation requires a source version ID.")

        return {
            "source_id": source_match["source_id"],
            "source_version_id": source_match["source_version_id"],
            "source_title": source_match.get("source_title"),
            "quoted_text": source_match.get("content", ""),
            "relevance_score": source_match.get("relevance_score", 0.0),
            "chunk_index": source_match.get("chunk_index"),
            "source_status": source_match.get("source_status"),
        }

    def build_citations(
        self,
        source_matches: list[dict[str, Any]],
    ) -> list[dict]:

        citations = []

        for match in source_matches:
            try:
                citations.append(
                    self.build_citation(match)
                )
            except ValueError:
                continue

        return citations

    def attach_citations(
        self,
        finding: dict[str, Any],
        citations: list[dict],
    ) -> dict:

        result = finding.copy()

        result["evidence"] = citations
        result["has_evidence"] = len(citations) > 0

        if not citations:
            result["evidence_status"] = "unverified"
        else:
            result["evidence_status"] = "sources_found"

        return result

    @staticmethod
    def validate_citation(citation: dict) -> bool:

        required_fields = [
            "source_id",
            "source_version_id",
            "quoted_text",
        ]

        if not all(citation.get(field) for field in required_fields):
            return False

        score = citation.get("relevance_score", 0)

        return (
            isinstance(score, (int, float))
            and 0 <= score <= 1
        )
