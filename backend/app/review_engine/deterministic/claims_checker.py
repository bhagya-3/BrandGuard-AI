
import re
from typing import Any


class ClaimsChecker:

    def check(
        self,
        text: str,
        approved_claims: list[dict[str, Any]] | None = None,
        require_evidence: bool = True,
    ) -> dict:

        findings = []
        approved_claims = approved_claims or []

        if not text or not text.strip():
            return self._result(findings)

        normalized_text = self._normalize(text)

        matched_claims = set()

        for claim in approved_claims:
            if not isinstance(claim, dict):
                continue

            claim_text = claim.get("claim")

            if not isinstance(claim_text, str) or not claim_text.strip():
                continue

            normalized_claim = self._normalize(claim_text)

            if normalized_claim and normalized_claim in normalized_text:
                matched_claims.add(normalized_claim)

        # Identify potentially factual or numerical statements.
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            if not self._looks_like_claim(sentence):
                continue

            normalized_sentence = self._normalize(sentence)

            matched = any(
                claim in normalized_sentence
                or normalized_sentence in claim
                for claim in matched_claims
            )

            if not matched and require_evidence:
                findings.append({
                    "category": "claims",
                    "severity": self._classify_severity(sentence),
                    "title": "Claim requires source verification",
                    "description": (
                        "This statement appears to make a factual "
                        "or numerical claim, but no matching approved "
                        "claim was supplied to this checker."
                    ),
                    "evidence": sentence[:500],
                    "suggestion": (
                        "Verify this statement against an approved "
                        "brand source and attach supporting evidence."
                    ),
                    "rule_id": None,
                })

        return self._result(findings)

    @staticmethod
    def _looks_like_claim(sentence: str) -> bool:
        claim_indicators = [
            r"\b\d+(?:\.\d+)?\s*%",
            r"\b\d+(?:,\d{3})*(?:\.\d+)?\b",
            r"\bguarantees?\b",
            r"\bproves?\b",
            r"\bcertified\b",
            r"\bclinically tested\b",
            r"\bnumber one\b",
            r"\bno\.?\s*1\b",
            r"\bfirst\b",
            r"\bbest\b",
            r"\bfastest\b",
            r"\bmost effective\b",
            r"\bimproves?\b",
            r"\breduces?\b",
            r"\bincreases?\b",
            r"\bsaves?\b",
            r"\btrusted by\b",
        ]

        return any(
            re.search(pattern, sentence, re.IGNORECASE)
            for pattern in claim_indicators
        )
    @staticmethod
    def _classify_severity(sentence: str) -> str:
        high_risk_patterns = [
            r"\bguarantees?\b",
            r"\bclinically proven\b",
            r"\bclinically tested\b",
            r"\bcures?\b",
            r"\bdiagnoses?\b",
            r"\bno side effects?\b",
            r"\b100\s*%\s*(?:safe|effective|guaranteed)\b",
            r"\bguaranteed returns?\b",
            r"\b(?:HIPAA|GDPR|SOC\s*2)\s+certified\b",
        ]

        for pattern in high_risk_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return "high"

        return "medium"
    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(
            re.sub(r"[^\w\s%]", " ", text.lower()).split()
        )

    @staticmethod
    def _result(findings: list[dict]) -> dict:
        return {
            "checker": "claims_checker",
            "passed": not any(
                item["severity"] in {"high", "critical"}
                for item in findings
            ),
            "finding_count": len(findings),
            "findings": findings,
        }
