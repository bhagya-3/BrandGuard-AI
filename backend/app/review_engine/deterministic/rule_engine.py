
from typing import Any

from app.review_engine.deterministic.terminology_checker import (
    TerminologyChecker,
)
from app.review_engine.deterministic.disclaimer_checker import (
    DisclaimerChecker,
)
from app.review_engine.deterministic.claims_checker import (
    ClaimsChecker,
)


class RuleEngine:

    def __init__(self):
        self.terminology_checker = TerminologyChecker()
        self.disclaimer_checker = DisclaimerChecker()
        self.claims_checker = ClaimsChecker()

    def run(
        self,
        text: str,
        rules: list[dict[str, Any]] | None = None,
        approved_claims: list[dict[str, Any]] | None = None,
        require_claim_evidence: bool = True,
    ) -> dict:

        rules = rules or []
        approved_claims = approved_claims or []

        terminology_result = self.terminology_checker.check(
            text=text,
            rules=rules,
        )

        disclaimer_result = self.disclaimer_checker.check(
            text=text,
            rules=rules,
        )

        claims_result = self.claims_checker.check(
            text=text,
            approved_claims=approved_claims,
            require_evidence=require_claim_evidence,
        )

        results = [
            terminology_result,
            disclaimer_result,
            claims_result,
        ]

        all_findings = []

        for result in results:
            all_findings.extend(result["findings"])

        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for finding in all_findings:
            severity = finding.get("severity", "low")

            if severity in severity_counts:
                severity_counts[severity] += 1

        return {
            "engine": "deterministic_rule_engine",
            "status": "completed",
            "passed": not any(
                finding.get("severity") in {"critical", "high"}
                for finding in all_findings
            ),
            "total_findings": len(all_findings),
            "severity_counts": severity_counts,
            "results": results,
            "findings": all_findings,
        }
