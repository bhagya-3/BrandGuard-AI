
import hashlib
import logging

from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.storage.factory import get_storage
from app.processors.text_extractor import extract_text

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="brandguard.documents.process_document",
    max_retries=3,
    default_retry_delay=30,
)
def process_document(self, document_id: str):
    """
    Download a document, extract its text and save the extracted text
    against its document version.
    """
    db = SessionLocal()

    try:
        document = db.execute(
            select(Document).where(Document.id == document_id)
        ).scalar_one_or_none()

        if document is None:
            return {
                "success": False,
                "message": "Document not found.",
                "document_id": document_id,
            }

        document.status = "processing"
        db.commit()

        # Use the configured storage provider (MinIO, S3, Azure or local).
        storage = get_storage()
        content = storage.download_file(document.storage_key)

        extracted = extract_text(
            filename=document.original_filename,
            content=content,
        )

        if isinstance(extracted, dict):
            extracted_text = extracted.get("text", "")
        else:
            extracted_text = str(extracted)

        if not extracted_text or not extracted_text.strip():
            raise ValueError("No readable text was extracted.")

        checksum = hashlib.sha256(content).hexdigest()

        version_number = document.current_version or 1

        version = db.execute(
            select(DocumentVersion).where(
                DocumentVersion.document_id == document.id,
                DocumentVersion.version_number == version_number,
            )
        ).scalar_one_or_none()

        if version is None:
            version = DocumentVersion(
                document_id=document.id,
                version_number=version_number,
                storage_key=document.storage_key,
                checksum=checksum,
                extracted_text=extracted_text,
                created_by=document.uploaded_by,
            )
            db.add(version)
        else:
            version.extracted_text = extracted_text
            version.checksum = checksum

        document.status = "processed"
        db.commit()

        logger.info(
            "Document %s processed successfully.",
            document_id,
        )

        return {
            "success": True,
            "document_id": document_id,
            "version_number": version_number,
            "character_count": len(extracted_text),
        }

    except Exception as exc:
        db.rollback()

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)

        document = db.execute(
            select(Document).where(Document.id == document_id)
        ).scalar_one_or_none()

        if document:
            document.status = "processing_failed"
            db.commit()

        logger.exception(
            "Document processing failed: %s",
            document_id,
        )

        raise

    finally:
        db.close()
