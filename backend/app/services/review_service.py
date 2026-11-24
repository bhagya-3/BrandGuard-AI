from asyncio.log import logger
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.finding import Finding
from app.models.evidence import Evidence
from app.models.suggestion import Suggestion

from app.repositories.document_repository import DocumentRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.source_repository import SourceRepository

from app.review_engine.review_pipeline import ReviewPipeline
from app.services.source_service import SourceService


class ReviewServiceError(Exception):
    logger = logging.getLogger(__name__)
    pass


class ReviewService:

    def __init__(
        self,
        db: Session,
        pipeline=None,
    ):
        self.db = db
        self.documents = DocumentRepository(db)
        self.reviews = ReviewRepository(db)
        self.sources = SourceRepository(db)
        self.source_service = SourceService(db)
        self.pipeline = pipeline or ReviewPipeline(
            enable_suggestions=True
        )

    def run_review(
        self,
        document_id: str,
        organization_id: str,
        workspace_id: str,
        requested_by: str,
        extracted_text: str,
        rules: list[dict] | None = None,
        approved_claims: list[dict] | None = None,
        brand_guidelines: dict | None = None,
        generate_suggestions: bool = True,
    ) -> Review:

        document = self.documents.get_by_id_and_org(
            document_id,
            organization_id,
        )

        if not document:
            raise ReviewServiceError("Document not found.")

        if document.workspace_id != workspace_id:
            raise ReviewServiceError(
                "Document does not belong to this workspace."
            )

        review = Review(
            organization_id=organization_id,
            workspace_id=workspace_id,
            document_id=document_id,
            requested_by=requested_by,
            status="in_progress",
            started_at=datetime.now(timezone.utc),
        )

        self.db.add(review)
        self.db.flush()

        try:
            approved_sources = (
                self.source_service.get_approved_sources(
                    organization_id
                )
            )

            result = self.pipeline.run_review(
                text=extracted_text,
                rules=rules or [],
                approved_claims=approved_claims or [],
                approved_sources=approved_sources,
                brand_guidelines=brand_guidelines or {},
                generate_suggestions=generate_suggestions,
            )

            for item in result["findings"]:
                suggestion_result = item.get("suggestion_result") or {}

                suggested_text = (
                    suggestion_result.get("suggested_text") or ""
                ).strip()

                original_text = (
                    suggestion_result.get("original_text")
                    or item.get("evidence_text")
                    or ""
                ).strip()

                if suggested_text and original_text:
                    generation_status = "generated"
                elif suggestion_result.get("status") == "insufficient_context":
                    generation_status = "insufficient_context"
                else:
                    generation_status = "unavailable"

                generation_message = (
                    suggestion_result.get("rationale")
                    or suggestion_result.get("message")
                    or (
                        "Correction suggestion is ready for human review."
                        if generation_status == "generated"
                        else "A reviewer can correct this finding manually."
                    )
                )

                finding = Finding(
                    review_id=review.id,
                    document_id=document_id,
                    category=item["category"],
                    severity=item["severity"],
                    title=item["title"],
                    description=item["description"],
                    location=str(item.get("position") or ""),
                    status="open",
                    suggestion_generation_status=generation_status,
                    suggestion_generation_message=generation_message,
                )

                self.db.add(finding)
                self.db.flush()

                for citation in item.get("citations", []):
                    self.db.add(
                        Evidence(
                            finding_id=finding.id,
                            source_id=citation.get("source_id"),
                            source_version_id=citation.get(
                                "source_version_id"
                            ),
                            quote=citation.get("quoted_text", ""),
                            source_reference=str(
                                citation.get("chunk_index", "")
                            ),
                            relevance_score=citation.get(
                                "relevance_score"
                            ),
                        )
                    )

                document_quote = (
                    item.get("evidence_text") or ""
                ).strip()

                existing_quotes = {
                    (citation.get("quoted_text") or "").strip()
                    for citation in item.get("citations", [])
                }

                if document_quote and document_quote not in existing_quotes:
                    self.db.add(
                        Evidence(
                            finding_id=finding.id,
                            quote=document_quote,
                            source_reference="Uploaded document",
                        )
                    )

                if generation_status == "generated":
                    self.db.add(
                        Suggestion(
                            finding_id=finding.id,
                            created_by=requested_by,
                            original_text=original_text,
                            suggested_text=suggested_text,
                            rationale=suggestion_result.get(
                                "rationale", ""
                            ),
                            status="pending",
                        )
                    )


                self.db.add(finding)
                self.db.flush()

                for citation in item.get("citations", []):
                    self.db.add(
                        Evidence(
                            finding_id=finding.id,
                            source_id=citation.get("source_id"),
                            source_version_id=citation.get(
                                "source_version_id"
                            ),
                            quote=citation.get("quoted_text", ""),
                            source_reference=str(
                                citation.get("chunk_index", "")
                            ),
                            relevance_score=citation.get(
                                "relevance_score"
                            ),
                        )
                    )

                document_quote = (item.get("evidence_text") or "").strip()
                existing_quotes = {
                    (citation.get("quoted_text") or "").strip()
                    for citation in item.get("citations", [])
                }

                if document_quote and document_quote not in existing_quotes:
                    self.db.add(
                        Evidence(
                            finding_id=finding.id,
                            quote=document_quote,
                            source_reference="Uploaded document",
                        )
                    )
                suggestion_result = item.get("suggestion_result")

                if (
                    suggestion_result
                    and suggestion_result.get("suggested_text")
                ):
                    self.db.add(
                        Suggestion(
                            finding_id=finding.id,
                            created_by=requested_by,
                            original_text=suggestion_result.get(
                                "original_text",
                                item.get("evidence_text", ""),
                            ),
                            suggested_text=suggestion_result[
                                "suggested_text"
                            ],
                            rationale=suggestion_result.get(
                                "rationale", ""
                            ),
                            status="pending",
                        )
                    )

            review.status = "completed"
            review.summary = (
                f"Review completed with "
                f"{result['total_findings']} findings."
            )
            review.completed_at = datetime.now(timezone.utc)

            self.db.flush()
            return review

        except Exception as exc:
            logger.exception("Document review failed: %s", exc)
            review.status = "failed"
            review.summary = "Review processing failed."
            review.completed_at = datetime.now(timezone.utc)

            self.db.flush()

            raise ReviewServiceError(
                "Unable to complete document review."
            ) from exc

    def get_review(
        self,
        review_id: str,
        organization_id: str,
    ):
        review = self.reviews.get_by_id_and_org(
            review_id,
            organization_id,
        )

        if not review:
            raise ReviewServiceError("Review not found.")

        return review

    def list_reviews(self, organization_id: str):
        return self.reviews.list_by_organization(
            organization_id
        )
