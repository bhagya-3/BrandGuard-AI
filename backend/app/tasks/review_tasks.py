
import logging

from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.services.review_service import ReviewService

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="brandguard.reviews.run_review",
    max_retries=2,
    default_retry_delay=60,
)
def run_review_task(
    self,
    document_id: str,
    organization_id: str,
    workspace_id: str,
    requested_by: str,
    rules: list = None,
    approved_claims: list = None,
    brand_guidelines: dict = None,
    generate_suggestions: bool = True,
):
    """Run a BrandGuard compliance review asynchronously."""
    db = SessionLocal()

    try:
        document = db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.organization_id == organization_id,
            )
        ).scalar_one_or_none()

        if document is None:
            return {
                "success": False,
                "message": "Document not found in this organization.",
            }

        version_number = document.current_version or 1

        version = db.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == document.id,
                DocumentVersion.version_number == version_number,
            )
        ).scalar_one_or_none()

        if version is None or not version.extracted_text:
            raise ValueError(
                "Document text is not available. Process the document first."
            )

        review_service = ReviewService(db)

        result = review_service.run_review(
            document_id=document_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            requested_by=requested_by,
            extracted_text=version.extracted_text,
            rules=rules or [],
            approved_claims=approved_claims or [],
            brand_guidelines=brand_guidelines or {},
            generate_suggestions=generate_suggestions,
        )

        logger.info(
            "Review completed for document %s.",
            document_id,
        )

        return {
            "success": True,
            "document_id": document_id,
            "review_id": str(result.id),
            "status": result.status,
        }

    except Exception as exc:
        db.rollback()

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)

        logger.exception(
            "Review task failed for document %s.",
            document_id,
        )
        raise

    finally:
        db.close()
