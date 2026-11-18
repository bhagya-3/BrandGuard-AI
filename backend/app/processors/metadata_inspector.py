
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256


def inspect_metadata(
    filename: str,
    content: bytes,
    file_format: str,
) -> dict:
    extension = Path(filename).suffix.lower()

    return {
        "filename": filename,
        "extension": extension,
        "format": file_format,
        "size_bytes": len(content),
        "size_kb": round(len(content) / 1024, 2),
        "checksum_sha256": sha256(content).hexdigest(),
        "inspected_at": datetime.now(timezone.utc).isoformat(),
    }
