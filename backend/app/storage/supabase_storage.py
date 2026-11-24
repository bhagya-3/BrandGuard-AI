

from typing import Optional
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.security.file_security import validate_storage_key
from app.storage.storage_interface import StorageInterface


class SupabaseStorage(StorageInterface):
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_SECRET_KEY:
            raise ValueError("Supabase Storage credentials are not configured.")

        self.base_url = settings.SUPABASE_URL.rstrip("/") + "/storage/v1"
        self.bucket = settings.SUPABASE_BUCKET
        self.headers = {
            "apikey": settings.SUPABASE_SECRET_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SECRET_KEY}",
        }
        self.timeout = 60.0

    def _object_url(self, storage_key: str) -> str:
        key = validate_storage_key(storage_key)
        return (
            f"{self.base_url}/object/"
            f"{quote(self.bucket, safe='')}/{quote(key, safe='/')}"
        )

       
    def upload_file(
        self,
        storage_key: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        if not isinstance(content, bytes):
            raise ValueError("File content must be bytes.")

        response = httpx.post(
            self._object_url(storage_key),
            headers={
                **self.headers,
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            content=content,
            timeout=self.timeout,
        )

        if response.is_error:
            print(
                "SUPABASE UPLOAD ERROR:",
                response.status_code,
                response.text,
            )

        response.raise_for_status()
        return validate_storage_key(storage_key)


    def download_file(self, storage_key: str) -> bytes:
        response = httpx.get(
            self._object_url(storage_key),
            headers=self.headers,
            timeout=self.timeout,
        )
        if response.status_code == 404:
            raise FileNotFoundError("Stored document was not found.")
        response.raise_for_status()
        return response.content

    def delete_file(self, storage_key: str) -> bool:
        key = validate_storage_key(storage_key)
        response = httpx.request(
            "DELETE",
            f"{self.base_url}/object/{quote(self.bucket, safe='')}",
            headers=self.headers,
            json={"prefixes": [key]},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return True

    def file_exists(self, storage_key: str) -> bool:
        key = validate_storage_key(storage_key)
        url = (
            f"{self.base_url}/object/info/"
            f"{quote(self.bucket, safe='')}/{quote(key, safe='/')}"
        )
        response = httpx.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
        )
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True

    def get_file_url(
        self,
        storage_key: str,
        expires_seconds: int = 3600,
    ) -> Optional[str]:
        response = httpx.post(
            f"{self.base_url}/object/sign/"
            f"{quote(self.bucket, safe='')}/{quote(validate_storage_key(storage_key), safe='/')}",
            headers=self.headers,
            json={"expiresIn": expires_seconds},
            timeout=self.timeout,
        )
        response.raise_for_status()
        signed_path = response.json()["signedURL"]
        if signed_path.startswith("http"):
            return signed_path
        return self.base_url + signed_path
