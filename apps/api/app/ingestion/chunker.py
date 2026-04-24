from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class ChunkCandidate:
    chunk_index: int
    content: str
    excerpt: str
    citation_label: str
    token_count_estimate: int
    start_char: int
    end_char: int


def _split_long_segment(segment: str, max_chars: int, overlap: int) -> list[str]:
    pieces: list[str] = []
    start = 0
    while start < len(segment):
        end = min(start + max_chars, len(segment))
        pieces.append(segment[start:end])
        if end == len(segment):
            break
        start = max(end - overlap, start + 1)
    return pieces


def chunk_text(
    text: str,
    document_name: str,
    max_chars: int = 1100,
    overlap: int = 120,
) -> list[ChunkCandidate]:
    normalized = text.strip()
    if not normalized:
        return []

    raw_segments = [segment.strip() for segment in re.split(r"\n{2,}", normalized) if segment.strip()]
    segments: list[str] = []
    for segment in raw_segments:
        if len(segment) > max_chars:
            segments.extend(_split_long_segment(segment, max_chars=max_chars, overlap=overlap))
        else:
            segments.append(segment)

    chunks: list[ChunkCandidate] = []
    current_segments: list[str] = []
    current_start = 0
    cursor = 0

    def flush(buffer_end: int) -> None:
        if not current_segments:
            return
        content = "\n\n".join(current_segments).strip()
        chunk_index = len(chunks)
        chunks.append(
            ChunkCandidate(
                chunk_index=chunk_index,
                content=content,
                excerpt=content[:260],
                citation_label=f"{document_name} · chunk {chunk_index + 1}",
                token_count_estimate=max(1, len(content.split())),
                start_char=current_start,
                end_char=buffer_end,
            )
        )

    buffer_end = 0
    for segment in segments:
        segment_start = normalized.find(segment, cursor)
        if segment_start == -1:
            segment_start = cursor
        segment_end = segment_start + len(segment)
        cursor = segment_end

        candidate = "\n\n".join([*current_segments, segment]).strip()
        if current_segments and len(candidate) > max_chars:
            flush(buffer_end)
            current_segments.clear()
            current_start = segment_start

        if not current_segments:
            current_start = segment_start
        current_segments.append(segment)
        buffer_end = segment_end

    flush(buffer_end)
    return chunks

