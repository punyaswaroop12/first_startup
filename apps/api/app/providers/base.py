from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(slots=True)
class StoredFile:
    absolute_path: Path
    relative_path: str
    original_name: str
    size_bytes: int
    content_type: str | None


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class StorageProvider(Protocol):
    def save_upload(self, file_bytes: bytes, filename: str, content_type: str | None) -> StoredFile: ...

    def delete(self, relative_path: str) -> None: ...

