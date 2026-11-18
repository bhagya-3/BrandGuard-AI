from datetime import datetime, timedelta, timezone
from typing import Optional

from azure.core.exceptions import AzureError, ResourceExistsError
from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    ContentSettings,
    generate_blob_sas,
)

from app.core.config import settings
from app.storage.access_control import validate_storage_key
from app.storage.storage_interface import StorageInterface


class AzureBlobStorageError(Exception):
    """Raised when an Azure Blob Storage operation fails."""


class AzureBlobStorage(StorageInterface):
    def __init__(self):
        if not settings.AZURE_STORAGE_CONNECTION_STRING:
            raise AzureBlobStorageError(
                "AZURE_STORAGE_CONNECTION_STRING is not configured."
            )
        if not settings.AZURE_STORAGE_CONTAINER:
            raise AzureBlobStorageError(
                "AZURE_STORAGE_CONTAINER is not configured."
            )

        self.container_name = settings.AZURE_STORAGE_CONTAINER
        self.service = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.container = self.service.get_container_client(
            self.container_name
        )
        try:
            self.container.create_container()
        except ResourceExistsError:
            pass
        except AzureError as exc:
            raise AzureBlobStorageError(
                "Unable to initialize the Azure Blob container."
            ) from exc

    def upload_file(
        self,
        storage_key: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        key = validate_storage_key(storage_key)
        if not isinstance(content, bytes):
            raise AzureBlobStorageError("File content must be bytes.")
        try:
            self.container.upload_blob(
                name=key,
                data=content,
                overwrite=True,
                content_settings=ContentSettings(
                    content_type=content_type
                ),
            )
            return key
        except AzureError as exc:
            raise AzureBlobStorageError(
                "Azure Blob upload failed."
            ) from exc

    def download_file(self, storage_key: str) -> bytes:
        key = validate_storage_key(storage_key)
        try:
            return self.container.download_blob(key).readall()
        except AzureError as exc:
            raise AzureBlobStorageError(
                "Azure Blob download failed."
            ) from exc

    def delete_file(self, storage_key: str) -> bool:
        key = validate_storage_key(storage_key)
        try:
            self.container.delete_blob(key, delete_snapshots="include")
            return True
        except AzureError as exc:
            raise AzureBlobStorageError(
                "Azure Blob deletion failed."
            ) from exc

    def file_exists(self, storage_key: str) -> bool:
        key = validate_storage_key(storage_key)
        try:
            return self.container.get_blob_client(key).exists()
        except AzureError as exc:
            raise AzureBlobStorageError(
                "Azure Blob existence check failed."
            ) from exc

    def get_file_url(
        self,
        storage_key: str,
        expires_seconds: int = 3600,
    ) -> Optional[str]:
        key = validate_storage_key(storage_key)
        if not 1 <= expires_seconds <= 7 * 24 * 60 * 60:
            raise AzureBlobStorageError(
                "URL expiry must be between 1 second and 7 days."
            )
        if not settings.AZURE_STORAGE_ACCOUNT_NAME or not settings.AZURE_STORAGE_ACCOUNT_KEY:
            raise AzureBlobStorageError(
                "Azure account name and key are required to sign download URLs."
            )
        try:
            token = generate_blob_sas(
                account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
                container_name=self.container_name,
                blob_name=key,
                account_key=settings.AZURE_STORAGE_ACCOUNT_KEY,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc)
                + timedelta(seconds=expires_seconds),
            )
            return f"{self.container.get_blob_client(key).url}?{token}"
        except AzureError as exc:
            raise AzureBlobStorageError(
                "Unable to generate an Azure Blob download URL."
            ) from exc
