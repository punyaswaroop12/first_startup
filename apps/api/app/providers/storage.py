from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.providers.base import StorageProvider, StoredFile

FILENAME_SAFE_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


class LocalStorageProvider:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or settings.local_storage_root
        self.root.mkdir(parents=True, exist_ok=True)

    def save_upload(self, file_bytes: bytes, filename: str, content_type: str | None) -> StoredFile:
        date_prefix = datetime.now(UTC).strftime("%Y/%m/%d")
        safe_name = FILENAME_SAFE_PATTERN.sub("-", filename).strip("-") or "upload.bin"
        relative_dir = Path(date_prefix)
        absolute_dir = self.root / relative_dir
        absolute_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid4()}-{safe_name}"
        absolute_path = absolute_dir / stored_name
        absolute_path.write_bytes(file_bytes)
        return StoredFile(
            absolute_path=absolute_path,
            relative_path=str(relative_dir / stored_name),
            original_name=filename,
            size_bytes=len(file_bytes),
            content_type=content_type,
        )

    def delete(self, relative_path: str) -> None:
        absolute_path = self.root / relative_path
        if absolute_path.exists():
            absolute_path.unlink()


def get_storage_provider() -> StorageProvider:
    return LocalStorageProvider()

