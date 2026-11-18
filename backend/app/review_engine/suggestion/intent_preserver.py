
import re
from typing import Any


class IntentPreserver:

    @staticmethod
    def extract_protected_elements(
        text: str,
        protected_terms: list[str] | None = None,
    ) -> set[str]:

        protected = set()

        # Numbers, percentages and currency values.
        patterns = [
            r"\b\d+(?:,\d{3})*(?:\.\d+)?\s*%",
            r"[$₹€£]\s?\d+(?:,\d{3})*(?:\.\d+)?",
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b\d+(?:,\d{3})*(?:\.\d+)?\b",
            r"https?://\S+",
            r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
            r'"[^"]+"',
            r"'[^']+'",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text):
                protected.add(match.group())

        # User-configured product names or other protected terms.
        for term in protected_terms or []:
            if term and term.lower() in text.lower():
                protected.add(term)

        return protected

    def check(
        self,
        original_text: str,
        suggested_text: str,
        protected_terms: list[str] | None = None,
        required_phrases: list[str] | None = None,
    ) -> dict[str, Any]:

        if not original_text or not suggested_text:
            return {
                "preserved": False,
                "issues": ["Original and suggested text are required."],
                "protected_elements": [],
            }

        original_elements = self.extract_protected_elements(
            original_text,
            protected_terms,
        )

        suggested_elements = self.extract_protected_elements(
            suggested_text,
            protected_terms,
        )

        issues = []

        missing_elements = original_elements - suggested_elements

        if missing_elements:
            issues.append({
                "type": "protected_element_missing",
                "message": "Some protected information is missing.",
                "elements": sorted(missing_elements),
            })

        for phrase in required_phrases or []:
            if phrase.lower() in original_text.lower():
                if phrase.lower() not in suggested_text.lower():
                    issues.append({
                        "type": "required_phrase_missing",
                        "message": (
                            "A required phrase was not preserved."
                        ),
                        "phrase": phrase,
                    })

        preserved = len(issues) == 0
        result = {
            "preserved": preserved,
            "valid": preserved,
            "issues": issues,
            "protected_elements": sorted(original_elements),
        }
        return result
