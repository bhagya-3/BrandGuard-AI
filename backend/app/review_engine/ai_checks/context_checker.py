
from typing import Any


class ContextChecker:

    def check(
        self,
        text: str,
        context: dict[str, Any] | None = None,
    ) -> dict:

        findings = []
        context = context or {}

        if not text or not text.strip():
            return self._result(findings)

        approved_terms = context.get("approved_terms", [])
        restricted_terms = context.get("restricted_terms", [])
        required_terms = context.get("required_terms", [])
        approved_claims = context.get("approved_claims", [])

        text_lower = text.lower()

        for term in restricted_terms:
            if not isinstance(term, str) or not term.strip():
                continue

            if term.lower() in text_lower:
                findings.append({
                    "category": "context",
                    "severity": "high",
                    "title": "Restricted term detected",
                    "description": (
                        "The document contains a term listed as restricted."
                    ),
                    "evidence": term,
                    "suggestion": (
                        "Check the applicable brand rule and "
                        "replace or remove the restricted wording."
                    ),
                })

        for term in required_terms:
            if not isinstance(term, str) or not term.strip():
                continue

            if term.lower() not in text_lower:
                findings.append({
                    "category": "context",
                    "severity": "medium",
                    "title": "Required term missing",
                    "description": (
                        "A term required by the supplied brand context "
                        "was not found."
                    ),
                    "evidence": term,
                    "suggestion": (
                        "Check whether this term should be included."
                    ),
                })

        for claim in approved_claims:
            if not isinstance(claim, str) or not claim.strip():
                continue

            if claim.lower() in text_lower:
                findings.append({
                    "category": "context",
                    "severity": "low",
                    "title": "Approved claim reference found",
                    "description": (
                        "This text matches a supplied approved claim."
                    ),
                    "evidence": claim,
                    "suggestion": (
                        "Retain the claim and verify that its "
                        "approved source version is still valid."
                    ),
                })

        return self._result(findings)

    @staticmethod
    def _result(findings: list[dict]) -> dict:
        return {
            "checker": "context_checker",
            "passed": not any(
                item["severity"] in {"high", "critical"}
                for item in findings
            ),
            "finding_count": len(findings),
            "findings": findings,
        }
