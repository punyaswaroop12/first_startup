from __future__ import annotations

from collections.abc import Iterable
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.ingestion.chunker import chunk_text
from app.ingestion.parsers import UnsupportedDocumentTypeError, parse_document_bytes
from app.models.document import (
    Document,
    DocumentChunk,
    DocumentStatus,
    DocumentVersion,
    SourceType,
    Tag,
)
from app.models.user import User
from app.providers.embeddings import get_embedding_provider
from app.providers.storage import get_storage_provider
from app.schemas.document import DocumentListResponse, DocumentResponse, DocumentVersionResponse
from app.schemas.tag import TagResponse
from app.services.audit import create_audit_log
from app.services.tags import get_or_create_tags
from app.utils.text import sanitize_document_text

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv"}
ALLOWED_MIME_PREFIXES = {
    ".pdf": ("application/pdf", "application/octet-stream"),
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
        "application/octet-stream",
    ),
    ".txt": ("text/plain", "application/octet-stream"),
    ".csv": ("text/csv", "application/csv", "application/vnd.ms-excel", "application/octet-stream"),
}
MAX_UPLOAD_BYTES = settings.max_upload_size_mb * 1024 * 1024


def list_documents(db: Session, current_user: User, query: str | None = None) -> DocumentListResponse:
    statement = (
        select(Document)
        .options(
            selectinload(Document.owner),
            selectinload(Document.tags),
            selectinload(Document.versions),
            selectinload(Document.chunks),
        )
        .order_by(desc(Document.created_at))
    )

    if query:
        pattern = f"%{query.strip()}%"
        statement = (
            statement.outerjoin(Document.tags)
            .outerjoin(Document.chunks)
            .where(
                or_(
                    Document.name.ilike(pattern),
                    Tag.name.ilike(pattern),
                    DocumentChunk.content.ilike(pattern),
                )
            )
            .distinct()
        )

    documents = list(db.scalars(statement).all())
    items = [serialize_document(document, query=query) for document in documents]
    return DocumentListResponse(items=items, total=len(items))


def ingest_document_upload(
    db: Session,
    *,
    current_user: User,
    filename: str,
    content_type: str | None,
    file_bytes: bytes,
    tags_raw: str,
    version_label: str | None,
) -> DocumentResponse:
    return _ingest_document(
        db=db,
        current_user=current_user,
        filename=filename,
        content_type=content_type,
        file_bytes=file_bytes,
        tags=parse_tags(tags_raw),
        version_label=version_label,
        source_type=SourceType.UPLOAD,
        base_metadata={"original_filename": filename},
        existing_document=None,
        audit_event_type="document_uploaded",
        audit_message=f"Uploaded document {filename}",
        audit_details={},
    )


def ingest_external_document(
    db: Session,
    *,
    current_user: User | None,
    filename: str,
    content_type: str | None,
    file_bytes: bytes,
    tags: list[str],
    version_label: str | None,
    base_metadata: dict,
    existing_document: Document | None = None,
) -> DocumentResponse:
    acting_user = current_user or existing_document.owner if existing_document else current_user
    if acting_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A document owner is required for external ingestion.",
        )
    return _ingest_document(
        db=db,
        current_user=acting_user,
        filename=filename,
        content_type=content_type,
        file_bytes=file_bytes,
        tags=tags,
        version_label=version_label,
        source_type=SourceType.IMPORT,
        base_metadata=base_metadata,
        existing_document=existing_document,
        audit_event_type="document_synced",
        audit_message=f"Synced document {filename}",
        audit_details={"source_kind": base_metadata.get("external_source", {}).get("kind")},
    )


def _ingest_document(
    db: Session,
    *,
    current_user: User,
    filename: str,
    content_type: str | None,
    file_bytes: bytes,
    tags: list[str],
    version_label: str | None,
    source_type: SourceType,
    base_metadata: dict,
    existing_document: Document | None,
    audit_event_type: str,
    audit_message: str,
    audit_details: dict,
) -> DocumentResponse:
    validate_document_bytes(filename=filename, content_type=content_type, file_bytes=file_bytes)

    tags = get_or_create_tags(db, tags)
    storage_provider = get_storage_provider()
    embedding_provider = get_embedding_provider()
    stored_file = storage_provider.save_upload(file_bytes=file_bytes, filename=filename, content_type=content_type)
    document = existing_document
    if document is None:
        document = Document(
            name=filename,
            source_type=source_type,
            status=DocumentStatus.PROCESSING,
            owner=current_user,
            content_type=content_type,
            file_size_bytes=len(file_bytes),
            version_label=version_label,
            extra_metadata=base_metadata,
            tags=tags,
        )
        db.add(document)
        db.flush()
    else:
        document.name = filename
        document.source_type = source_type
        document.status = DocumentStatus.PROCESSING
        document.owner = current_user
        document.content_type = content_type
        document.file_size_bytes = len(file_bytes)
        document.version_label = version_label
        document.extra_metadata = {**document.extra_metadata, **base_metadata}
        document.tags = tags
        for prior_version in document.versions:
            prior_version.is_current = False

    try:
        parsed_document = parse_document_bytes(filename, file_bytes)
        normalized_text = sanitize_document_text(parsed_document.text)
        if not normalized_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No extractable text found in the document.",
            )

        version = DocumentVersion(
            document=document,
            version_label=version_label,
            file_path=stored_file.relative_path,
            parser_name=parsed_document.parser_name,
            extracted_text=normalized_text,
            extraction_notes=parsed_document.extraction_notes,
            content_hash=sha256(normalized_text.encode("utf-8")).hexdigest(),
        )
        db.add(version)
        db.flush()

        chunk_candidates = chunk_text(normalized_text, document_name=document.name)
        embeddings = embedding_provider.embed_texts([chunk.content for chunk in chunk_candidates])
        for candidate, embedding in zip(chunk_candidates, embeddings, strict=False):
            db.add(
                DocumentChunk(
                    document=document,
                    version=version,
                    chunk_index=candidate.chunk_index,
                    content=candidate.content,
                    excerpt=candidate.excerpt,
                    citation_label=candidate.citation_label,
                    token_count_estimate=candidate.token_count_estimate,
                    start_char=candidate.start_char,
                    end_char=candidate.end_char,
                    embedding=embedding,
                )
            )

        keyword_review = detect_review_flag(normalized_text)
        document.status = DocumentStatus.FLAGGED if keyword_review else DocumentStatus.READY
        document.requires_review = bool(keyword_review)
        document.review_reason = keyword_review

        create_audit_log(
            db,
            actor=current_user,
            event_type=audit_event_type,
            resource_type="document",
            resource_id=str(document.id),
            message=audit_message,
            details={
                "tags": [tag.name for tag in tags],
                "chunk_count": len(chunk_candidates),
                "parser_name": parsed_document.parser_name,
                "source_type": source_type.value,
                **audit_details,
            },
        )
        db.commit()
    except UnsupportedDocumentTypeError as exc:
        db.rollback()
        storage_provider.delete(stored_file.relative_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HTTPException:
        db.rollback()
        storage_provider.delete(stored_file.relative_path)
        raise
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        storage_provider.delete(stored_file.relative_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document ingestion failed.",
        ) from exc

    hydrated_document = db.get(
        Document,
        document.id,
        options=[
            selectinload(Document.owner),
            selectinload(Document.tags),
            selectinload(Document.versions),
            selectinload(Document.chunks),
        ],
    )
    from app.services.automations import evaluate_automation_rules

    evaluate_automation_rules(
        db,
        current_user=current_user,
        trigger_type="document_uploaded",
        resource_type="document",
        resource_id=str(document.id),
        event_payload={
            "name": hydrated_document.name,
            "tags": [tag.name for tag in hydrated_document.tags],
            "status": hydrated_document.status.value,
            "version_label": hydrated_document.version_label,
            "source_type": hydrated_document.source_type.value,
            "external_source_kind": hydrated_document.extra_metadata.get("external_source", {}).get("kind"),
        },
    )
    if hydrated_document.review_reason:
        evaluate_automation_rules(
            db,
            current_user=current_user,
            trigger_type="keyword_detected",
            resource_type="document",
            resource_id=str(document.id),
            event_payload={
                "name": hydrated_document.name,
                "tags": [tag.name for tag in hydrated_document.tags],
                "matched_keywords": [
                    hydrated_document.review_reason.split("'")[1]
                ]
                if "'" in hydrated_document.review_reason
                else [],
                "review_reason": hydrated_document.review_reason,
            },
        )

    hydrated_document = db.get(
        Document,
        document.id,
        options=[
            selectinload(Document.owner),
            selectinload(Document.tags),
            selectinload(Document.versions),
            selectinload(Document.chunks),
        ],
    )
    return serialize_document(hydrated_document)


def validate_document_bytes(*, filename: str, content_type: str | None, file_bytes: bytes) -> None:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed: PDF, DOCX, TXT, CSV.",
        )
    if content_type and not any(
        content_type.startswith(allowed) for allowed in ALLOWED_MIME_PREFIXES.get(extension, ())
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File MIME type does not match the allowed document types.",
        )
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds the current {settings.max_upload_size_mb}MB upload limit.",
        )


def delete_document(db: Session, *, document_id: UUID, current_user: User | None) -> None:
    document = db.get(
        Document,
        document_id,
        options=[
            selectinload(Document.versions),
            selectinload(Document.tags),
        ],
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    storage_provider = get_storage_provider()
    for version in document.versions:
        storage_provider.delete(version.file_path)

    create_audit_log(
        db,
        actor=current_user,
        event_type="document_deleted",
        resource_type="document",
        resource_id=str(document.id),
        message=f"Deleted document {document.name}",
        details={"tags": [tag.name for tag in document.tags]},
    )
    db.delete(document)
    db.commit()


def parse_tags(tags_raw: str) -> list[str]:
    return [tag.strip() for tag in tags_raw.split(",") if tag.strip()]


def detect_review_flag(text: str) -> str | None:
    review_keywords = ("incident", "violation", "escalate", "injury", "critical")
    lowered = text.lower()
    for keyword in review_keywords:
        if keyword in lowered:
            return f"Keyword '{keyword}' matched review criteria"
    return None


def serialize_document(document: Document, query: str | None = None) -> DocumentResponse:
    current_version = next((version for version in document.versions if version.is_current), None)
    matched_excerpt = find_matched_excerpt(document.chunks, query)
    external_source = document.extra_metadata.get("external_source", {})
    return DocumentResponse(
        id=document.id,
        name=document.name,
        source_type=document.source_type.value,
        status=document.status.value,
        owner_name=document.owner.full_name,
        owner_email=document.owner.email,
        content_type=document.content_type,
        file_size_bytes=document.file_size_bytes,
        version_label=document.version_label,
        requires_review=document.requires_review,
        review_reason=document.review_reason,
        tags=[TagResponse.model_validate(tag) for tag in document.tags],
        chunk_count=len(document.chunks),
        current_version=(
            DocumentVersionResponse.model_validate(current_version) if current_version else None
        ),
        connector_name=external_source.get("connector_name"),
        external_source_kind=external_source.get("kind"),
        source_label=external_source.get("source_label"),
        source_path=external_source.get("path"),
        source_url=external_source.get("source_url"),
        created_at=document.created_at,
        updated_at=document.updated_at,
        matched_excerpt=matched_excerpt,
    )


def find_matched_excerpt(chunks: Iterable[DocumentChunk], query: str | None) -> str | None:
    if not query:
        return None
    lowered_query = query.lower()
    for chunk in chunks:
        if lowered_query in chunk.content.lower():
            return chunk.excerpt
    return None
