
from typing import Any

from app.review_engine.deterministic import RuleEngine

from app.review_engine.ai_checks import (
    ToneChecker,
    ContextChecker,
    ReadabilityChecker,
    AccessibilityChecker,
    VisualChecker,
)

from app.review_engine.evidence import (
    SourceMatcher,
    CitationBuilder,
)

from app.review_engine.suggestion import (
    CorrectionGenerator,
)


class ReviewPipeline:

    def __init__(
        self,
        enable_suggestions: bool = False,
    ):
        self.rule_engine = RuleEngine()

        self.tone_checker = ToneChecker()
        self.context_checker = ContextChecker()
        self.readability_checker = ReadabilityChecker()
        self.accessibility_checker = AccessibilityChecker()
        self.visual_checker = VisualChecker()

        self.source_matcher = SourceMatcher()
        self.citation_builder = CitationBuilder()

        self.correction_generator = (
            CorrectionGenerator()
            if enable_suggestions
            else None
        )

    def run_review(
        self,
        text: str,
        rules: list[dict] | None = None,
        approved_claims: list[dict] | None = None,
        approved_sources: list[dict] | None = None,
        brand_guidelines: dict | None = None,
        context: dict | None = None,
        visual_data: dict | None = None,
        metadata: dict | None = None,
        expected_tone: str = "professional",
        generate_suggestions: bool = False,
        protected_terms: list[str] | None = None,
    ) -> dict[str, Any]:

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Document text cannot be empty.")

        rules = rules or []
        approved_claims = approved_claims or []
        approved_sources = approved_sources or []
        brand_guidelines = brand_guidelines or {}
        context = context or {}
        visual_data = visual_data or {}
        metadata = metadata or {}
        protected_terms = protected_terms or []

        # --------------------------------------------------
        # STEP 1: Run deterministic checks
        # --------------------------------------------------

        deterministic_result = self.rule_engine.run(
            text=text,
            rules=rules,
            approved_claims=approved_claims,
        )

        # --------------------------------------------------
        # STEP 2: Run AI-related content checks
        # --------------------------------------------------

        tone_result = self.tone_checker.check(
            text=text,
            expected_tone=expected_tone,
            brand_guidelines=brand_guidelines,
        )

        context_result = self.context_checker.check(
            text=text,
            context=context,
        )

        readability_result = self.readability_checker.check(
            text=text,
        )

        accessibility_result = self.accessibility_checker.check(
            text=text,
            metadata=metadata,
        )

        visual_result = self.visual_checker.check(
            visual_data=visual_data,
            brand_guidelines=brand_guidelines,
        )

        checker_results = [
            deterministic_result,
            tone_result,
            context_result,
            readability_result,
            accessibility_result,
            visual_result,
        ]

        # --------------------------------------------------
        # STEP 3: Combine all findings
        # --------------------------------------------------

        all_findings = []

        for result in checker_results:
            for finding in result.get("findings", []):
                normalized = self._normalize_finding(
                    finding,
                    result.get("checker", result.get("engine")),
                )
                all_findings.append(normalized)

        # --------------------------------------------------
        # STEP 4: Find supporting approved-source evidence
        # --------------------------------------------------

        for finding in all_findings:

            evidence_text = finding.get("evidence_text", "")

            finding["citations"] = []
            finding["evidence_status"] = "unverified"

            if not evidence_text or not approved_sources:
                continue

            matches = self.source_matcher.match_sources(
                query=evidence_text,
                sources=approved_sources,
                top_k=3,
            )

            citations = self.citation_builder.build_citations(
                matches
            )

            finding["citations"] = citations

            if citations:
                finding["evidence_status"] = "sources_found"

        # --------------------------------------------------
        # STEP 5: Generate optional correction suggestions
        # --------------------------------------------------

        if generate_suggestions and self.correction_generator:

            for finding in all_findings:

                finding["suggestion_result"] = None

                if not finding.get("evidence_text"):
                    continue

                try:
                    suggestion_result = self.correction_generator.generate(
                        original_text=finding["evidence_text"],
                        finding=finding,
                        brand_guidelines=brand_guidelines,
                        evidence=finding.get("citations", []),
                        protected_terms=protected_terms,
                    )

                    finding["suggestion_result"] = suggestion_result

                except Exception:
                    finding["suggestion_result"] = {
                        "status": "unavailable",
                        "suggested_text": None,
                        "requires_human_review": True,
                        "automatically_applied": False,
                    }

        # --------------------------------------------------
        # STEP 6: Calculate severity summary
        # --------------------------------------------------

        severity_counts = self._count_severities(
            all_findings
        )

        critical_findings = severity_counts["critical"]
        high_findings = severity_counts["high"]

        # --------------------------------------------------
        # STEP 7: Build final review response
        # --------------------------------------------------

        return {
            "pipeline": "BrandGuard AI Review Pipeline",
            "status": "completed",
            "total_findings": len(all_findings),
            "severity_counts": severity_counts,
            "passed": critical_findings == 0 and high_findings == 0,
            "results": {
                "deterministic": deterministic_result,
                "tone": tone_result,
                "context": context_result,
                "readability": readability_result,
                "accessibility": accessibility_result,
                "visual": visual_result,
            },
            "findings": all_findings,
            "human_review_required": True,
            "automatically_approved": False,
            "automatically_published": False,
            "document_modified": False,
        }

    @staticmethod
    def _normalize_finding(
        finding: dict,
        checker_name: str | None = None,
    ) -> dict:

        return {
            "category": finding.get("category", "general"),
            "severity": finding.get("severity", "low"),
            "title": finding.get("title", "Review finding"),
            "description": finding.get("description", ""),
            "evidence_text": (
                finding.get("evidence")
                if isinstance(finding.get("evidence"), str)
                else ""
            ),
            "suggestion": finding.get("suggestion"),
            "rule_id": finding.get("rule_id"),
            "position": finding.get("position"),
            "checker": checker_name,
            "citations": [],
            "evidence_status": "unverified",
        }

    @staticmethod
    def _count_severities(
        findings: list[dict],
    ) -> dict:

        counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for finding in findings:
            severity = finding.get("severity", "low")

            if severity in counts:
                counts[severity] += 1

        return counts
