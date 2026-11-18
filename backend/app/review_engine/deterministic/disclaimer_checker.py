
from typing import Any


class DisclaimerChecker:

    def check(
        self,
        text: str,
        rules: list[dict[str, Any]] | None = None,
    ) -> dict:

        findings = []
        rules = rules or []

        if not text or not text.strip():
            return self._result(findings)

        normalized_text = " ".join(text.lower().split())

        for rule in rules:
            if not rule.get("is_active", True):
                continue

            if rule.get("rule_type") != "disclaimer":
                continue

            config = rule.get("rule_config", {})

            if not isinstance(config, dict):
                continue

            required_text = config.get("required_text")
            prohibited_text = config.get("prohibited_text")
            severity = rule.get("severity", "high")

            if required_text:
                if not isinstance(required_text, str):
                    continue

                normalized_required = " ".join(
                    required_text.lower().split()
                )

                if normalized_required not in normalized_text:
                    findings.append({
                        "category": "disclaimer",
                        "severity": severity,
                        "title": "Required disclaimer missing",
                        "description": rule.get(
                            "description",
                            "A required disclaimer is missing.",
                        ),
                        "evidence": required_text,
                        "suggestion": (
                            "Add the exact approved disclaimer after "
                            "verifying its applicability."
                        ),
                        "rule_id": rule.get("id"),
                    })

            if prohibited_text:
                if not isinstance(prohibited_text, str):
                    continue

                normalized_prohibited = " ".join(
                    prohibited_text.lower().split()
                )

                if normalized_prohibited in normalized_text:
                    findings.append({
                        "category": "disclaimer",
                        "severity": severity,
                        "title": "Prohibited disclaimer wording detected",
                        "description": rule.get(
                            "description",
                            "The document contains prohibited disclaimer wording.",
                        ),
                        "evidence": prohibited_text,
                        "suggestion": (
                            "Replace the wording only with an "
                            "approved disclaimer."
                        ),
                        "rule_id": rule.get("id"),
                    })

        return self._result(findings)

    @staticmethod
    def _result(findings: list[dict]) -> dict:
        return {
            "checker": "disclaimer_checker",
            "passed": not any(
                item["severity"] in {"high", "critical"}
                for item in findings
            ),
            "finding_count": len(findings),
            "findings": findings,
        }
