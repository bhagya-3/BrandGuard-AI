
import re
from typing import Any


class TerminologyChecker:

    def check(
        self,
        text: str,
        rules: list[dict[str, Any]] | None = None,
    ) -> dict:

        findings = []
        rules = rules or []

        if not text or not text.strip():
            return self._result(findings)

        for rule in rules:
            if not rule.get("is_active", True):
                continue

            rule_type = rule.get("rule_type", "terminology")
            match_type = rule.get("match_type", "exact")
            config = rule.get("rule_config", {})

            if not isinstance(config, dict):
                continue

            term = config.get("term") or config.get("incorrect_term")
            preferred = config.get("preferred_term")
            severity = rule.get("severity", "medium")

            if not isinstance(term, str) or not term.strip():
                continue

            pattern = self._build_pattern(term, match_type)

            if not pattern:
                continue

            matches = list(re.finditer(pattern, text, re.IGNORECASE))

            for match in matches:
                if rule_type == "required_term":
                    continue

                if rule_type == "prohibited_term" or rule_type == "terminology":
                    findings.append({
                        "category": "terminology",
                        "severity": severity,
                        "title": rule.get(
                            "name",
                            "Terminology inconsistency",
                        ),
                        "description": rule.get(
                            "description",
                            "A term conflicts with an approved brand rule.",
                        ),
                        "evidence": match.group(),
                        "suggestion": (
                            f"Consider using '{preferred}'."
                            if preferred
                            else "Review this term against the approved terminology."
                        ),
                        "rule_id": rule.get("id"),
                        "position": match.start(),
                    })

            if rule_type == "required_term":
                if not matches:
                    findings.append({
                        "category": "terminology",
                        "severity": severity,
                        "title": rule.get(
                            "name",
                            "Required terminology missing",
                        ),
                        "description": rule.get(
                            "description",
                            "A required brand term was not found.",
                        ),
                        "evidence": term,
                        "suggestion": (
                            f"Consider including '{term}' where appropriate."
                        ),
                        "rule_id": rule.get("id"),
                    })

        return self._result(findings)

    @staticmethod
    def _build_pattern(term: str, match_type: str):
        escaped = re.escape(term)

        if match_type == "exact":
            return rf"\b{escaped}\b"

        if match_type == "contains":
            return escaped

        if match_type == "case_sensitive":
            return rf"\b{escaped}\b"

        return None

    @staticmethod
    def _result(findings: list[dict]) -> dict:
        return {
            "checker": "terminology_checker",
            "passed": not any(
                item["severity"] in {"high", "critical"}
                for item in findings
            ),
            "finding_count": len(findings),
            "findings": findings,
        }
