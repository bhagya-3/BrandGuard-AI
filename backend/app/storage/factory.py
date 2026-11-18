from app.core.config import settings
from app.storage.azure_storage import AzureBlobStorage
from app.storage.local_storage import LocalStorage
from app.storage.s3_storage import S3Storage
from app.storage.storage_interface import StorageInterface


def get_storage() -> StorageInterface:
    backend = settings.STORAGE_BACKEND.strip().lower()
    if backend == "local":
        return LocalStorage()
    if backend == "minio":
        from app.storage.minio_storage import MinIOStorage

        return MinIOStorage()
    if backend in {"s3", "aws_s3"}:
        return S3Storage()
    if backend in {"azure", "azure_blob"}:
        return AzureBlobStorage()
    raise ValueError(f"Unsupported storage backend: {settings.STORAGE_BACKEND}")
