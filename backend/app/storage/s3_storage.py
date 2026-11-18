
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from typing import Optional

from app.core.config import settings
from app.storage.storage_interface import StorageInterface
from app.storage.access_control import validate_storage_key


class S3StorageError(Exception):
    """Raised when an Amazon S3 operation fails."""


class S3Storage(StorageInterface):
    def __init__(self):
        self.bucket_name = settings.AWS_S3_BUCKET

        if not self.bucket_name:
            raise S3StorageError("AWS_S3_BUCKET is not configured.")

        client_options = {
            "service_name": "s3",
            "region_name": settings.AWS_REGION,
        }

        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            client_options["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            client_options["aws_secret_access_key"] = (
                settings.AWS_SECRET_ACCESS_KEY
            )

        self.client = boto3.client(**client_options)

    def upload_file(
        self,
        storage_key: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        key = validate_storage_key(storage_key)

        if not isinstance(content, bytes):
            raise S3StorageError("File content must be bytes.")

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type,
                ServerSideEncryption="AES256",
            )
            return key
        except (ClientError, BotoCoreError) as exc:
            raise S3StorageError("S3 upload failed.") from exc

    def download_file(self, storage_key: str) -> bytes:
        key = validate_storage_key(storage_key)

        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return response["Body"].read()
        except (ClientError, BotoCoreError) as exc:
            raise S3StorageError("S3 download failed.") from exc

    def delete_file(self, storage_key: str) -> bool:
        key = validate_storage_key(storage_key)

        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return True
        except (ClientError, BotoCoreError) as exc:
            raise S3StorageError("S3 deletion failed.") from exc

    def file_exists(self, storage_key: str) -> bool:
        key = validate_storage_key(storage_key)

        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return True
        except ClientError as exc:
            status_code = exc.response.get(
                "ResponseMetadata", {}
            ).get("HTTPStatusCode")

            if status_code == 404:
                return False

            raise S3StorageError("S3 existence check failed.") from exc
        except BotoCoreError as exc:
            raise S3StorageError("S3 existence check failed.") from exc

    def get_file_url(
        self,
        storage_key: str,
        expires_seconds: int = 3600,
    ) -> Optional[str]:
        key = validate_storage_key(storage_key)

        if not 1 <= expires_seconds <= 7 * 24 * 60 * 60:
            raise S3StorageError(
                "URL expiry must be between 1 second and 7 days."
            )

        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                },
                ExpiresIn=expires_seconds,
            )
        except (ClientError, BotoCoreError) as exc:
            raise S3StorageError(
                "Unable to generate S3 download URL."
            ) from exc
