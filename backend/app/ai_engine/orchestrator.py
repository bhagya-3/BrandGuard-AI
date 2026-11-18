
import logging
from typing import Any

from app.ai_engine.confidence import calculate_confidence
from app.ai_engine.context_builder import build_review_context
from app.ai_engine.evidence_retriever import retrieve_evidence
from app.ai_engine.explainability import build_explanation
from app.ai_engine.hallucination_guard import validate_findings
from app.ai_engine.llm_client import LLMClient
from app.ai_engine.prompt_manager import build_review_messages


logger = logging.getLogger(__name__)


class ReviewOrchestrator:

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()

    async def review_document(
        self,
        document_text: str,
        document_name: str,
        approved_sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Execute the complete BrandGuard AI review.
        """

        # Step 1: Prepare document and source information
        context = build_review_context(
            document_text=document_text,
            document_name=document_name,
            approved_sources=approved_sources,
        )

        # Step 2: Retrieve relevant approved evidence
        evidence = retrieve_evidence(
            document_text=context["document_text"],
            approved_sources=context["approved_sources"],
        )

        # Step 3: Build AI review instructions
        messages = build_review_messages(
            context=context,
            evidence=evidence,
        )

        # Step 4: Ask the AI to identify possible issues
        ai_response = await self.llm_client.generate_json(
            messages=messages
        )

        findings = ai_response.get("findings", [])

        if not isinstance(findings, list):
            raise ValueError(
                "AI response must contain a findings list."
            )

        # Step 5: Validate AI findings
        validation = validate_findings(
            findings=findings,
            document_text=context["document_text"],
            evidence=evidence,
        )

        # Step 6: Calculate confidence and explain findings
        explained_findings = []

        for finding in validation["valid_findings"]:
            finding_evidence = [
                item for item in evidence
                if str(item["evidence_id"]) in {
                    str(evidence_id)
                    for evidence_id in finding.get("evidence_ids", [])
                }
            ]

            average_relevance = (
                sum(item["relevance"] for item in finding_evidence)
                / len(finding_evidence)
                if finding_evidence
                else 0.0
            )

            average_authority = (
                sum(item["authority"] for item in finding_evidence)
                / len(finding_evidence)
                if finding_evidence
                else 0.0
            )

            ai_confidence = finding.get("ai_confidence", 0.5)

            if not isinstance(ai_confidence, (int, float)):
                ai_confidence = 0.5

            ai_confidence = max(0.0, min(float(ai_confidence), 1.0))

            score = calculate_confidence(
                evidence_count=len(finding_evidence),
                source_authority=average_authority,
                evidence_relevance=average_relevance,
                source_agreement=0.5,
                ai_confidence=ai_confidence,
            )

            finding["confidence"] = score

            explained_findings.append(
                build_explanation(
                    finding=finding,
                    evidence=evidence,
                )
            )

        # Step 7: Return review results
        return {
            "document_name": document_name,
            "status": "completed",
            "total_findings": len(explained_findings),
            "findings": explained_findings,
            "rejected_findings": validation["rejected_findings"],
            "evidence_used": len(evidence),
            "human_review_required": (
                len(validation["rejected_findings"]) > 0
                or any(
                    item["verification_status"]
                    == "Needs Human Verification"
                    for item in validation["valid_findings"]
                )
            ),
            "approval_status": "Not Approved",
            "message": (
                "AI review completed. Human review and approval "
                "are still required."
            ),
        }
