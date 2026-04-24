from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.chat import (
    ChatConversationResponse,
    ChatConversationSummaryResponse,
    CreateConversationRequest,
    SendChatMessageRequest,
)
from app.services.chat import (
    create_conversation,
    get_conversation,
    list_conversations,
    send_message,
)

router = APIRouter()


@router.get("/conversations", response_model=list[ChatConversationSummaryResponse])
def list_conversations_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChatConversationSummaryResponse]:
    return list_conversations(db=db, current_user=current_user)


@router.post(
    "/conversations",
    response_model=ChatConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation_route(
    payload: CreateConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatConversationResponse:
    return create_conversation(db=db, current_user=current_user, title=payload.title)


@router.get("/conversations/{conversation_id}", response_model=ChatConversationResponse)
def get_conversation_route(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatConversationResponse:
    return get_conversation(db=db, current_user=current_user, conversation_id=conversation_id)


@router.post("/conversations/{conversation_id}/messages", response_model=ChatConversationResponse)
def send_message_route(
    conversation_id: UUID,
    payload: SendChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatConversationResponse:
    return send_message(
        db=db,
        current_user=current_user,
        conversation_id=conversation_id,
        content=payload.content,
    )

