from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.security.file_security import validate_storage_key
from app.storage.storage_interface import StorageInterface


class LocalStorage(StorageInterface):
    def __init__(self, root: str | None = None):
        self.root = Path(root or settings.FILE_STORAGE_PATH).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, storage_key: str) -> Path:
        key = validate_storage_key(storage_key)
        path = (self.root / Path(key)).resolve()
        if self.root not in path.parents:
            raise ValueError("Invalid storage key.")
        return path

    def upload_file(
        self,
        storage_key: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        if not isinstance(content, bytes):
            raise ValueError("File content must be bytes.")
        path = self._path(storage_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return validate_storage_key(storage_key)

    def download_file(self, storage_key: str) -> bytes:
        path = self._path(storage_key)
        if not path.is_file():
            raise FileNotFoundError("Stored document was not found.")
        return path.read_bytes()

    def delete_file(self, storage_key: str) -> bool:
        path = self._path(storage_key)
        if not path.is_file():
            return False
        path.unlink()
        return True

    def file_exists(self, storage_key: str) -> bool:
        return self._path(storage_key).is_file()

    def get_file_url(
        self,
        storage_key: str,
        expires_seconds: int = 3600,
    ) -> Optional[str]:
        self._path(storage_key)
        return None
