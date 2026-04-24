from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Tag


def normalize_tag_name(name: str) -> str:
    return name.strip().lower().replace(" ", "-")


def list_tags(db: Session) -> list[Tag]:
    return list(db.scalars(select(Tag).order_by(Tag.name)).all())


def create_tag(db: Session, *, name: str, description: str | None, color: str | None) -> Tag:
    normalized_name = normalize_tag_name(name)
    existing = db.scalar(select(Tag).where(Tag.name == normalized_name))
    if existing:
        return existing

    tag = Tag(name=normalized_name, description=description, color=color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, *, tag_id) -> None:  # noqa: ANN001
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found.")
    db.delete(tag)
    db.commit()


def get_or_create_tags(db: Session, tag_names: list[str]) -> list[Tag]:
    normalized = [normalize_tag_name(name) for name in tag_names if normalize_tag_name(name)]
    if not normalized:
        return []

    existing_tags = {
        tag.name: tag for tag in db.scalars(select(Tag).where(Tag.name.in_(normalized))).all()
    }
    tags = []
    for name in normalized:
        tag = existing_tags.get(name)
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
            existing_tags[name] = tag
        tags.append(tag)
    return tags
