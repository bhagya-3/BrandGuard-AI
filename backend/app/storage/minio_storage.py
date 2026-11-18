
from io import BytesIO
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.storage.storage_interface import StorageInterface
from app.storage.access_control import validate_storage_key


class MinIOStorageError(Exception):
    """Raised when a MinIO operation fails."""


class MinIOStorage(StorageInterface):
    def __init__(self):
        endpoint = settings.MINIO_ENDPOINT

        if not endpoint:
            raise MinIOStorageError("MINIO_ENDPOINT is not configured.")

        self.bucket_name = settings.MINIO_BUCKET

        if not self.bucket_name:
            raise MinIOStorageError("MINIO_BUCKET is not configured.")

        self.client = Minio(
            endpoint=endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Create the bucket if it does not already exist."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as exc:
            raise MinIOStorageError(
                f"Unable to initialize MinIO bucket: {exc.code}"
            ) from exc

    def upload_file(
        self,
        storage_key: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        key = validate_storage_key(storage_key)

        if not isinstance(content, bytes):
            raise MinIOStorageError("File content must be bytes.")

        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=key,
                data=BytesIO(content),
                length=len(content),
                content_type=content_type,
            )
            return key
        except S3Error as exc:
            raise MinIOStorageError(
                f"MinIO upload failed: {exc.code}"
            ) from exc

    def download_file(self, storage_key: str) -> bytes:
        key = validate_storage_key(storage_key)
        response = None

        try:
            response = self.client.get_object(
                self.bucket_name,
                key,
            )
            return response.read()
        except S3Error as exc:
            raise MinIOStorageError(
                f"MinIO download failed: {exc.code}"
            ) from exc
        finally:
            if response is not None:
                response.close()
                response.release_conn()

    def delete_file(self, storage_key: str) -> bool:
        key = validate_storage_key(storage_key)

        try:
            self.client.remove_object(self.bucket_name, key)
            return True
        except S3Error as exc:
            raise MinIOStorageError(
                f"MinIO deletion failed: {exc.code}"
            ) from exc

    def file_exists(self, storage_key: str) -> bool:
        key = validate_storage_key(storage_key)

        try:
            self.client.stat_object(self.bucket_name, key)
            return True
        except S3Error as exc:
            if exc.code in {"NoSuchKey", "NoSuchObject", "NotFound"}:
                return False
            raise MinIOStorageError(
                f"MinIO existence check failed: {exc.code}"
            ) from exc

    def get_file_url(
        self,
        storage_key: str,
        expires_seconds: int = 3600,
    ) -> Optional[str]:
        key = validate_storage_key(storage_key)

        if not 1 <= expires_seconds <= 7 * 24 * 60 * 60:
            raise MinIOStorageError(
                "URL expiry must be between 1 second and 7 days."
            )

        try:
            from datetime import timedelta

            return self.client.presigned_get_object(
                self.bucket_name,
                key,
                expires=timedelta(seconds=expires_seconds),
            )
        except S3Error as exc:
            raise MinIOStorageError(
                f"Unable to generate MinIO URL: {exc.code}"
            ) from exc
