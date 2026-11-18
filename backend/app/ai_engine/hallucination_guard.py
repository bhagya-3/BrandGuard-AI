
from typing import Any


def validate_findings(
    findings: list[dict[str, Any]],
    document_text: str,
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Validate AI findings against the uploaded document
    and retrieved evidence.

    Invalid findings are rejected, not silently approved.
    """

    valid_evidence_ids = {
        str(item["evidence_id"])
        for item in evidence
    }

    valid_findings = []
    rejected_findings = []

    normalized_document = document_text.casefold()

    for finding in findings:
        evidence_ids = [
            str(item)
            for item in finding.get("evidence_ids", [])
        ]

        quoted_text = finding.get("quoted_text", "").strip()

        unknown_ids = [
            item for item in evidence_ids
            if item not in valid_evidence_ids
        ]

        if unknown_ids:
            rejected_findings.append({
                "finding": finding,
                "reason": "Unknown evidence reference."
            })
            continue

        if quoted_text and quoted_text.casefold() not in normalized_document:
            rejected_findings.append({
                "finding": finding,
                "reason": "Quoted text was not found in the document."
            })
            continue

        if not evidence_ids:
            finding["verification_status"] = "Needs Human Verification"
        else:
            finding["verification_status"] = "Evidence Referenced"

        valid_findings.append(finding)

    return {
        "valid_findings": valid_findings,
        "rejected_findings": rejected_findings,
        "total_checked": len(findings),
    }
