
def calculate_confidence(
    evidence_count: int,
    source_authority: float,
    evidence_relevance: float,
    source_agreement: float,
    ai_confidence: float = 0.5,
) -> float:
    """
    Calculate a confidence score between 0 and 1.

    All input scores must be between 0 and 1.
    """

    values = [
        source_authority,
        evidence_relevance,
        source_agreement,
        ai_confidence,
    ]

    if any(not 0 <= value <= 1 for value in values):
        raise ValueError("Confidence inputs must be between 0 and 1.")

    if evidence_count <= 0:
        return 0.0

    evidence_coverage = min(evidence_count / 3, 1.0)

    score = (
        evidence_coverage * 0.20
        + source_authority * 0.30
        + evidence_relevance * 0.25
        + source_agreement * 0.15
        + ai_confidence * 0.10
    )

    return round(max(0.0, min(score, 1.0)), 2)


def get_confidence_label(score: float) -> str:
    """Convert a confidence score into a readable label."""

    if not 0 <= score <= 1:
        raise ValueError("Score must be between 0 and 1.")

    if score >= 0.85:
        return "High"

    if score >= 0.60:
        return "Medium"

    return "Low"
