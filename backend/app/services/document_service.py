
import hashlib
import uuid

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.repositories.document_repository import DocumentRepository
from app.security.file_security import (
    validate_upload,
    validate_storage_key,
)
from app.security.malware_scanner import (
    MalwareScanner,
    MalwareScannerError,
)


class DocumentServiceError(Exception):
    pass


class DocumentService:

    def __init__(
        self,
        db: Session,
        storage=None,
        malware_scanner=None,
    ):
        self.db = db
        self.repository = DocumentRepository(db)
        self.storage = storage
        self.scanner = malware_scanner or MalwareScanner()

    def upload_document(
        self,
        filename: str,
        content: bytes,
        organization_id: str,
        workspace_id: str,
        uploader_id: str,
    ) -> Document:

        if not self.storage:
            raise DocumentServiceError(
                "File storage is not configured."
            )

        validation = validate_upload(filename, content)

        try:
            scan_result = self.scanner.scan_bytes(
                content,
                validation["filename"],
            )
        except MalwareScannerError as exc:
            raise DocumentServiceError(
                "Upload blocked because malware scanning failed."
            ) from exc

        if scan_result.get("infected") is True:
            raise DocumentServiceError(
                "The uploaded file was identified as malicious."
            )

        storage_key = (
            f"{organization_id}/documents/{uuid.uuid4().hex}/"
            f"{validation['filename']}"
        )

        storage_key = validate_storage_key(storage_key)

        try:
            self.storage.upload_file(
                storage_key,
                content,
                content_type=self._content_type(
                    validation["extension"]
                ),
            )
        except Exception as exc:
            raise DocumentServiceError(
                "Unable to store the uploaded document."
            ) from exc

        document = Document(
            organization_id=organization_id,
            workspace_id=workspace_id,
            uploaded_by=uploader_id,
            title=validation["filename"],
            original_filename=validation["filename"],
            mime_type=self._content_type(
                validation["extension"]
            ),
            file_size=len(content),
            storage_key=storage_key,
            status="uploaded",
            current_version=1,
        )

        self.db.add(document)
        self.db.flush()
        self.db.add(
            DocumentVersion(
                document_id=document.id,
                version_number=1,
                storage_key=storage_key,
                checksum=hashlib.sha256(content).hexdigest(),
                created_by=uploader_id,
            )
        )
        self.db.flush()

        return document

    def get_document(
        self,
        document_id: str,
        organization_id: str,
    ):
        document = self.repository.get_by_id_and_org(
            document_id,
            organization_id,
        )

        if not document:
            raise DocumentServiceError("Document not found.")

        return document

    def list_documents(
        self,
        organization_id: str,
        workspace_id: str | None = None,
    ):
        if workspace_id:
            return self.repository.list_by_workspace(
                workspace_id
            )

        return self.repository.list_by_organization(
            organization_id
        )

    def update_document(
        self,
        document_id: str,
        organization_id: str,
        title: str | None = None,
    ):
        document = self.get_document(
            document_id,
            organization_id,
        )

        if title:
            document.title = title.strip()

        self.db.flush()
        return document

    @staticmethod
    def _content_type(extension: str) -> str:
        content_types = {
            ".pdf": "application/pdf",
            ".docx": (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            ".pptx": (
                "application/vnd.openxmlformats-officedocument."
                "presentationml.presentation"
            ),
            ".txt": "text/plain",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }

        return content_types.get(
            extension,
            "application/octet-stream",
        )
