
import re


class ReadabilityChecker:

    COMPLEX_WORDS = {
        "utilization",
        "implementation",
        "commencement",
        "approximately",
        "subsequently",
        "aforementioned",
        "facilitation",
        "methodology",
        "functionality",
        "optimization",
    }

    def check(
        self,
        text: str,
        max_sentence_words: int = 25,
        max_paragraph_words: int = 120,
    ) -> dict:

        findings = []

        if not text or not text.strip():
            return self._result(findings)

        paragraphs = [
            p.strip()
            for p in re.split(r"\n\s*\n", text)
            if p.strip()
        ]

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        for sentence in sentences:
            words = re.findall(r"\b[\w'-]+\b", sentence)

            if len(words) > max_sentence_words:
                findings.append({
                    "category": "readability",
                    "severity": "medium",
                    "title": "Long sentence",
                    "description": (
                        f"This sentence contains {len(words)} words, "
                        f"exceeding the recommended limit of "
                        f"{max_sentence_words}."
                    ),
                    "evidence": sentence[:300],
                    "suggestion": (
                        "Consider dividing this sentence into "
                        "shorter, clearer sentences."
                    ),
                })

        for paragraph in paragraphs:
            words = re.findall(r"\b[\w'-]+\b", paragraph)

            if len(words) > max_paragraph_words:
                findings.append({
                    "category": "readability",
                    "severity": "low",
                    "title": "Long paragraph",
                    "description": (
                        f"This paragraph contains {len(words)} words."
                    ),
                    "evidence": paragraph[:300],
                    "suggestion": (
                        "Break the paragraph into smaller sections."
                    ),
                })

        text_lower = text.lower()

        for word in self.COMPLEX_WORDS:
            pattern = rf"\b{re.escape(word)}\b"

            for match in re.finditer(pattern, text_lower):
                findings.append({
                    "category": "readability",
                    "severity": "low",
                    "title": "Potentially complex wording",
                    "description": (
                        "This word may be unnecessarily complex "
                        "for the intended audience."
                    ),
                    "evidence": match.group(),
                    "suggestion": (
                        "Consider using a simpler alternative "
                        "where appropriate."
                    ),
                })

        return self._result(findings)

    @staticmethod
    def _result(findings: list[dict]) -> dict:
        return {
            "checker": "readability_checker",
            "passed": not any(
                item["severity"] in {"high", "critical"}
                for item in findings
            ),
            "finding_count": len(findings),
            "findings": findings,
        }
