from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.chat import ChatConversation, ChatMessage, ChatMessageRole
from app.models.user import User
from app.providers.llm import FakeLLMProvider, get_llm_provider
from app.schemas.chat import (
    ChatConversationResponse,
    ChatConversationSummaryResponse,
    ChatMessageResponse,
    CitationResponse,
)
from app.services.prompts import load_prompt
from app.services.retrieval import retrieve_relevant_chunks


def list_conversations(db: Session, current_user: User) -> list[ChatConversationSummaryResponse]:
    conversations = db.scalars(
        select(ChatConversation)
        .where(ChatConversation.created_by_id == current_user.id)
        .options(selectinload(ChatConversation.messages))
        .order_by(desc(ChatConversation.updated_at))
    ).all()
    return [
        ChatConversationSummaryResponse(
            id=conversation.id,
            title=conversation.title,
            updated_at=conversation.updated_at,
            message_count=len(conversation.messages),
        )
        for conversation in conversations
    ]


def create_conversation(
    db: Session,
    *,
    current_user: User,
    title: str | None,
) -> ChatConversationResponse:
    conversation = ChatConversation(
        title=title or "New conversation",
        created_by=current_user,
    )
    db.add(conversation)
    db.commit()
    return get_conversation(db=db, current_user=current_user, conversation_id=conversation.id)


def get_conversation(
    db: Session,
    *,
    current_user: User,
    conversation_id: UUID,
) -> ChatConversationResponse:
    conversation = _load_conversation(db=db, current_user=current_user, conversation_id=conversation_id)
    return serialize_conversation(conversation)


def send_message(
    db: Session,
    *,
    current_user: User,
    conversation_id: UUID,
    content: str,
) -> ChatConversationResponse:
    if not content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message content is required.")

    conversation = _load_conversation(db=db, current_user=current_user, conversation_id=conversation_id)
    if conversation.title == "New conversation":
        conversation.title = content[:60].strip()

    user_message = ChatMessage(
        conversation=conversation,
        role=ChatMessageRole.USER,
        content=content.strip(),
        citations=[],
        suggested_follow_ups=[],
    )
    db.add(user_message)
    db.flush()

    retrieved = retrieve_relevant_chunks(db=db, query=content, limit=5)
    llm_provider = get_llm_provider()
    conversation_history = [
        {"role": message.role.value, "content": message.content}
        for message in conversation.messages
    ] + [{"role": "user", "content": content.strip()}]

    if isinstance(llm_provider, FakeLLMProvider):
        provider_response = llm_provider.generate_chat_response(
            question=content.strip(),
            retrieved_chunks=[format_retrieved_chunk(item) for item in retrieved],
            conversation_history=conversation_history,
        )
    else:
        provider_response = llm_provider.generate_chat_response(
            system_prompt=load_prompt("chat/system.md"),
            instruction_prompt=load_prompt("chat/answer.md"),
            question=content.strip(),
            retrieved_chunks=[format_retrieved_chunk(item) for item in retrieved],
            conversation_history=conversation_history,
        )

    assistant_message = ChatMessage(
        conversation=conversation,
        role=ChatMessageRole.ASSISTANT,
        content=provider_response.answer,
        citations=[serialize_citation(item).model_dump(mode="json") for item in retrieved],
        suggested_follow_ups=provider_response.follow_up_questions[:3],
    )
    conversation.updated_at = datetime.now(UTC)
    db.add(assistant_message)
    db.commit()

    return get_conversation(db=db, current_user=current_user, conversation_id=conversation_id)


def _load_conversation(db: Session, *, current_user: User, conversation_id: UUID) -> ChatConversation:
    conversation = db.scalar(
        select(ChatConversation)
        .where(
            ChatConversation.id == conversation_id,
            ChatConversation.created_by_id == current_user.id,
        )
        .options(selectinload(ChatConversation.messages))
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return conversation


def serialize_conversation(conversation: ChatConversation) -> ChatConversationResponse:
    messages = sorted(conversation.messages, key=lambda item: item.created_at)
    return ChatConversationResponse(
        id=conversation.id,
        title=conversation.title,
        updated_at=conversation.updated_at,
        messages=[
            ChatMessageResponse(
                id=message.id,
                role=message.role.value,
                content=message.content,
                citations=[CitationResponse.model_validate(citation) for citation in message.citations],
                suggested_follow_ups=message.suggested_follow_ups,
                created_at=message.created_at,
            )
            for message in messages
        ],
    )


def serialize_citation(item) -> CitationResponse:  # noqa: ANN001
    chunk = item.chunk
    external_source = chunk.document.extra_metadata.get("external_source", {})
    return CitationResponse(
        chunk_id=chunk.id,
        document_id=chunk.document.id,
        document_name=chunk.document.name,
        version_label=chunk.version.version_label,
        citation_label=chunk.citation_label,
        excerpt=chunk.excerpt,
        score=round(item.score, 4),
        connector_name=external_source.get("connector_name"),
        external_source_kind=external_source.get("kind"),
        source_label=external_source.get("source_label"),
        source_path=external_source.get("path"),
        source_url=external_source.get("source_url"),
    )


def format_retrieved_chunk(item) -> dict:  # noqa: ANN001
    chunk = item.chunk
    return {
        "chunk_id": str(chunk.id),
        "document_id": str(chunk.document.id),
        "document_name": chunk.document.name,
        "version_label": chunk.version.version_label,
        "citation_label": chunk.citation_label,
        "excerpt": chunk.excerpt,
        "content": chunk.content,
        "score": item.score,
    }
