
from abc import ABC, abstractmethod
from typing import Optional


class StorageInterface(ABC):
    """Common interface for file storage providers."""

    @abstractmethod
    def upload_file(
        self,
        storage_key: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload file bytes and return the storage key."""
        raise NotImplementedError

    @abstractmethod
    def download_file(self, storage_key: str) -> bytes:
        """Download a file and return its bytes."""
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, storage_key: str) -> bool:
        """Delete a stored file."""
        raise NotImplementedError

    @abstractmethod
    def file_exists(self, storage_key: str) -> bool:
        """Check whether a file exists."""
        raise NotImplementedError

    @abstractmethod
    def get_file_url(
        self,
        storage_key: str,
        expires_seconds: int = 3600,
    ) -> Optional[str]:
        """Return a temporary download URL when supported."""
        raise NotImplementedError
