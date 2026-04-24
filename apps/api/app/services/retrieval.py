from __future__ import annotations

import math
from dataclasses import dataclass

from sqlalchemy import select, text
from sqlalchemy.orm import Session, selectinload

from app.models.document import Document, DocumentChunk, DocumentStatus, DocumentVersion
from app.providers.embeddings import get_embedding_provider


@dataclass(slots=True)
class RetrievedChunk:
    chunk: DocumentChunk
    score: float


def retrieve_relevant_chunks(db: Session, query: str, limit: int = 5) -> list[RetrievedChunk]:
    query_embedding = get_embedding_provider().embed_texts([query])[0]

    if db.bind and db.bind.dialect.name == "postgresql":
        return _retrieve_postgres(db=db, query_embedding=query_embedding, limit=limit)
    return _retrieve_python(db=db, query_embedding=query_embedding, limit=limit)


def _retrieve_postgres(db: Session, query_embedding: list[float], limit: int) -> list[RetrievedChunk]:
    vector_literal = "[" + ",".join(f"{value:.8f}" for value in query_embedding) + "]"
    rows = db.execute(
        text(
            """
            SELECT dc.id, 1 - (dc.embedding <=> CAST(:embedding AS vector)) AS score
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            JOIN document_versions dv ON dv.id = dc.version_id
            WHERE d.status IN ('READY', 'FLAGGED')
              AND dv.is_current = TRUE
            ORDER BY dc.embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """
        ),
        {"embedding": vector_literal, "limit": limit},
    ).all()

    chunk_ids = [row.id for row in rows]
    if not chunk_ids:
        return []

    chunk_map = {
        chunk.id: chunk
        for chunk in db.scalars(
            select(DocumentChunk)
            .options(
                selectinload(DocumentChunk.document),
                selectinload(DocumentChunk.version),
            )
            .where(DocumentChunk.id.in_(chunk_ids))
        ).all()
    }
    return [
        RetrievedChunk(chunk=chunk_map[row.id], score=float(row.score))
        for row in rows
        if row.id in chunk_map
    ]


def _retrieve_python(db: Session, query_embedding: list[float], limit: int) -> list[RetrievedChunk]:
    chunks = db.scalars(
        select(DocumentChunk)
        .join(DocumentChunk.document)
        .join(DocumentChunk.version)
        .options(
            selectinload(DocumentChunk.document),
            selectinload(DocumentChunk.version),
        )
        .where(Document.status.in_([DocumentStatus.READY, DocumentStatus.FLAGGED]))
        .where(DocumentVersion.is_current.is_(True))
    ).all()

    scored_chunks = []
    for chunk in chunks:
        if not chunk.embedding:
            continue
        scored_chunks.append(
            RetrievedChunk(
                chunk=chunk,
                score=cosine_similarity(query_embedding, chunk.embedding),
            )
        )

    scored_chunks.sort(key=lambda item: item.score, reverse=True)
    return scored_chunks[:limit]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(left_value * right_value for left_value, right_value in zip(left, right, strict=False))
    left_magnitude = math.sqrt(sum(value * value for value in left)) or 1.0
    right_magnitude = math.sqrt(sum(value * value for value in right)) or 1.0
    return numerator / (left_magnitude * right_magnitude)
