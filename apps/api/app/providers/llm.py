from __future__ import annotations

import json
import re
from dataclasses import dataclass

from openai import OpenAI

from app.core.config import settings


@dataclass(slots=True)
class ChatProviderResponse:
    answer: str
    follow_up_questions: list[str]


@dataclass(slots=True)
class ReportProviderResponse:
    top_themes: list[str]
    risks: list[str]
    action_items: list[str]
    notable_updates: list[str]


class FakeLLMProvider:
    def generate_chat_response(
        self,
        *,
        question: str,
        retrieved_chunks: list[dict],
        conversation_history: list[dict],
    ) -> ChatProviderResponse:
        if not retrieved_chunks:
            return ChatProviderResponse(
                answer=(
                    "I’m not fully confident based on the current document set. I couldn’t find "
                    "enough supporting material to answer that reliably."
                ),
                follow_up_questions=[
                    "Which document should I search next?",
                    "Is there a related SOP or policy version to upload?",
                    "Do you want a summary of the closest matching documents?"
                ],
            )

        supporting_lines = []
        for chunk in retrieved_chunks[:2]:
            supporting_lines.append(
                f"{chunk['document_name']}: {first_sentence(chunk['excerpt'])}"
            )

        answer = (
            f"Based on the retrieved documents, {first_sentence(' '.join(supporting_lines)).lower()}"
        )
        return ChatProviderResponse(
            answer=answer[0].upper() + answer[1:],
            follow_up_questions=[
                f"What operational action follows from {keyword_from_question(question)}?",
                "Which source document should I inspect more closely?",
                "Do you want a short executive summary of these findings?",
            ],
        )

    def generate_report_response(
        self,
        *,
        system_prompt: str,
        instruction_prompt: str,
        report_type: str,
        document_context: str,
        activity_context: str,
        notes: str,
    ) -> ReportProviderResponse:
        del system_prompt, instruction_prompt
        lines = [line.strip() for line in document_context.splitlines() if line.strip()]
        activity_lines = [line.strip("- ").strip() for line in activity_context.splitlines() if line.strip()]
        top_themes = derive_items(lines, prefix="Document:", fallback=f"{report_type.title()} update prepared")
        risks = derive_items(
            [line for line in lines if "Review flag:" in line and "none" not in line.lower()],
            prefix="Review flag:",
            fallback="No critical risks surfaced beyond current uploaded material",
        )
        action_items = derive_items(
            [line for line in lines if "Excerpt:" not in line][:6] + ([notes] if notes else []),
            prefix="",
            fallback="Review notable updates and assign owners for follow-up",
        )
        notable_updates = derive_items(
            activity_lines,
            prefix="",
            fallback="Recent system activity is limited; more uploads and reports will enrich this view",
        )
        return ReportProviderResponse(
            top_themes=top_themes[:4],
            risks=risks[:4],
            action_items=action_items[:4],
            notable_updates=notable_updates[:4],
        )


class OpenAILLMProvider:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        )

    def generate_chat_response(
        self,
        *,
        system_prompt: str,
        instruction_prompt: str,
        question: str,
        retrieved_chunks: list[dict],
        conversation_history: list[dict],
    ) -> ChatProviderResponse:
        history_block = "\n".join(
            f"{message['role']}: {message['content']}" for message in conversation_history[-6:]
        )
        context_block = "\n\n".join(
            f"[{chunk['citation_label']}]\n{chunk['content']}" for chunk in retrieved_chunks
        )
        user_prompt = (
            f"{instruction_prompt}\n\n"
            f"Conversation history:\n{history_block or 'No prior history'}\n\n"
            f"Question:\n{question}\n\n"
            f"Retrieved document excerpts:\n{context_block or 'No excerpts found'}\n\n"
            "Return strict JSON with keys `answer` and `follow_up_questions`."
        )
        response = self.client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        payload = json.loads(response.choices[0].message.content or "{}")
        return ChatProviderResponse(
            answer=payload.get("answer", "I’m not confident enough to answer from the retrieved material."),
            follow_up_questions=payload.get("follow_up_questions", []),
        )

    def generate_report_response(
        self,
        *,
        system_prompt: str,
        instruction_prompt: str,
        report_type: str,
        document_context: str,
        activity_context: str,
        notes: str,
    ) -> ReportProviderResponse:
        user_prompt = (
            f"{instruction_prompt}\n\n"
            f"Report type: {report_type}\n\n"
            f"Document context:\n{document_context}\n\n"
            f"Recent activity:\n{activity_context}\n\n"
            f"User notes:\n{notes or 'None'}\n\n"
            "Return JSON with keys: top_themes, risks, action_items, notable_updates."
        )
        response = self.client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        payload = json.loads(response.choices[0].message.content or "{}")
        return ReportProviderResponse(
            top_themes=payload.get("top_themes", []),
            risks=payload.get("risks", []),
            action_items=payload.get("action_items", []),
            notable_updates=payload.get("notable_updates", []),
        )


def get_llm_provider():
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return OpenAILLMProvider()
    return FakeLLMProvider()


def first_sentence(text: str) -> str:
    match = re.split(r"(?<=[.!?])\s+", text.strip())
    return match[0] if match and match[0] else text.strip()


def keyword_from_question(question: str) -> str:
    tokens = [token for token in re.findall(r"[A-Za-z0-9-]+", question.lower()) if len(token) > 3]
    return tokens[0] if tokens else "this topic"


def derive_items(lines: list[str], *, prefix: str, fallback: str) -> list[str]:
    items = []
    for line in lines:
        candidate = line
        if prefix and prefix in candidate:
            candidate = candidate.split(prefix, maxsplit=1)[-1].strip()
        candidate = candidate.strip(" -")
        if candidate:
            items.append(candidate)
    if not items:
        items.append(fallback)
    return items
