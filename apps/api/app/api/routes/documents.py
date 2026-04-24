from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, require_admin
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentResponse
from app.services.documents import delete_document, ingest_document_upload, list_documents

router = APIRouter()


@router.get("/", response_model=DocumentListResponse)
def list_documents_route(
    query: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentListResponse:
    return list_documents(db=db, current_user=current_user, query=query)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    tags: Annotated[str, Form()] = "",
    version_label: Annotated[str | None, Form()] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> DocumentResponse:
    file_bytes = await file.read()
    return ingest_document_upload(
        db=db,
        current_user=current_user,
        filename=file.filename or "document",
        content_type=file.content_type,
        file_bytes=file_bytes,
        tags_raw=tags,
        version_label=version_label,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_route(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    delete_document(db=db, document_id=document_id, current_user=current_user)

