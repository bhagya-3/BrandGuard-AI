
import re
from typing import Any


class ToneChecker:

    def __init__(self):
        self.formal_patterns = [
            r"\bhereby\b",
            r"\bpursuant to\b",
            r"\baforementioned\b",
            r"\bshall be\b",
        ]

        self.casual_patterns = [
            r"\bya\b",
            r"\bgonna\b",
            r"\bwanna\b",
            r"\bkinda\b",
            r"\bsuper cool\b",
        ]

        self.aggressive_patterns = [
            r"\byou must buy\b",
            r"\bguaranteed success\b",
            r"\bno excuses\b",
            r"\bact now or lose\b",
        ]

    def check(
        self,
        text: str,
        expected_tone: str = "professional",
        brand_guidelines: dict[str, Any] | None = None,
    ) -> dict:

        if not text or not text.strip():
            return self._result([])

        guidelines = brand_guidelines or {}
        allowed_tones = guidelines.get("allowed_tones", [])

        findings = []
        normalized_tone = expected_tone.lower().strip()

        if normalized_tone not in {
            "professional",
            "friendly",
            "confident",
            "conversational",
            "formal",
            "empathetic",
            "persuasive",
        }:
            normalized_tone = "professional"

        if normalized_tone in {"professional", "formal"}:
            findings.extend(
                self._find_patterns(
                    text,
                    self.casual_patterns,
                    "Informal wording may not match the expected tone.",
                    "medium",
                )
            )

        if normalized_tone in {"friendly", "conversational"}:
            findings.extend(
                self._find_patterns(
                    text,
                    self.aggressive_patterns,
                    "Aggressive wording may conflict with a friendly tone.",
                    "medium",
                )
            )

        if normalized_tone in {"professional", "friendly"}:
            findings.extend(
                self._find_patterns(
                    text,
                    self.aggressive_patterns,
                    "The wording may sound overly forceful.",
                    "high",
                )
            )

        if allowed_tones and normalized_tone not in allowed_tones:
            findings.append({
                "category": "tone",
                "severity": "medium",
                "title": "Tone configuration mismatch",
                "description": (
                    "The requested tone is not included in the "
                    "configured brand tone guidelines."
                ),
                "evidence": normalized_tone,
                "suggestion": (
                    "Select a tone approved by the brand guidelines."
                ),
            })

        for pattern in self.formal_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                if normalized_tone in {"friendly", "conversational"}:
                    findings.append({
                        "category": "tone",
                        "severity": "low",
                        "title": "Potentially overly formal wording",
                        "description": (
                            "This phrase may sound too formal "
                            "for the expected communication style."
                        ),
                        "evidence": match.group(),
                        "suggestion": (
                            "Consider using simpler, more natural wording."
                        ),
                    })

        return self._result(findings)

    @staticmethod
    def _find_patterns(
        text: str,
        patterns: list[str],
        description: str,
        severity: str,
    ) -> list[dict]:

        findings = []

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "category": "tone",
                    "severity": severity,
                    "title": "Tone inconsistency",
                    "description": description,
                    "evidence": match.group(),
                    "suggestion": (
                        "Review this phrase against the approved "
                        "brand voice guidelines."
                    ),
                })

        return findings

    @staticmethod
    def _result(findings: list[dict]) -> dict:
        return {
            "checker": "tone_checker",
            "passed": len(findings) == 0,
            "finding_count": len(findings),
            "findings": findings,
        }
