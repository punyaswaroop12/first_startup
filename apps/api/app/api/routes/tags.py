from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, require_admin
from app.models.user import User
from app.schemas.tag import TagCreateRequest, TagResponse
from app.services.tags import create_tag, delete_tag, list_tags

router = APIRouter()


@router.get("/", response_model=list[TagResponse])
def list_tags_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TagResponse]:
    return [TagResponse.model_validate(tag) for tag in list_tags(db)]


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag_route(
    payload: TagCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> TagResponse:
    tag = create_tag(db=db, name=payload.name, description=payload.description, color=payload.color)
    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag_route(
    tag_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    delete_tag(db=db, tag_id=tag_id)
