from __future__ import annotations

import re

INSTRUCTION_LIKE_PATTERN = re.compile(
    r"(ignore (all|previous) instructions|system prompt|act as|developer message)",
    flags=re.IGNORECASE,
)


def sanitize_document_text(text: str) -> str:
    normalized = text.replace("\x00", " ").replace("\r\n", "\n").replace("\r", "\n")
    cleaned_lines = []
    for line in normalized.splitlines():
        stripped = line.strip()
        if INSTRUCTION_LIKE_PATTERN.search(stripped) and len(stripped) < 300:
            cleaned_lines.append("[potentially instruction-like content removed]")
        else:
            cleaned_lines.append(stripped)
    sanitized = "\n".join(cleaned_lines)
    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)
    return sanitized.strip()
