from __future__ import annotations

import hashlib
import math

from openai import OpenAI

from app.core.config import settings
from app.providers.base import EmbeddingProvider


class FakeEmbeddingProvider:
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            weight = 1 + (digest[4] / 255)
            vector[index] += weight

        magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / magnitude for value in vector]


class OpenAIEmbeddingProvider:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]


def get_embedding_provider() -> EmbeddingProvider:
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbeddingProvider()
    return FakeEmbeddingProvider(dimension=settings.embedding_dimension)

