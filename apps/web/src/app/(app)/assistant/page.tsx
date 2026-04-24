"use client";

import { formatDistanceToNow } from "date-fns";
import { MessageSquarePlus, SendHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/components/layout/auth-provider";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { chatApi } from "@/lib/api";
import type { ChatConversation, ChatConversationSummary, ChatMessage } from "@/lib/types";

export default function AssistantPage() {
  const { token } = useAuth();
  const [conversations, setConversations] = useState<ChatConversationSummary[]>([]);
  const [activeConversation, setActiveConversation] = useState<ChatConversation | null>(null);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [selectedAssistantMessageId, setSelectedAssistantMessageId] = useState<string | null>(null);

  const selectedAssistantMessage = useMemo(() => {
    if (!activeConversation) {
      return null;
    }
    return (
      activeConversation.messages.find((message) => message.id === selectedAssistantMessageId) ??
      [...activeConversation.messages].reverse().find((message) => message.role === "assistant") ??
      null
    );
  }, [activeConversation, selectedAssistantMessageId]);

  const loadConversations = async () => {
    if (!token) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const summaries = await chatApi.listConversations(token);
      setConversations(summaries);
      if (summaries[0]) {
        const detail = await chatApi.getConversation(token, summaries[0].id);
        setActiveConversation(detail);
        setSelectedAssistantMessageId(
          [...detail.messages].reverse().find((message) => message.role === "assistant")?.id ?? null
        );
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load assistant history.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const createConversation = async () => {
    if (!token) {
      return;
    }
    const conversation = await chatApi.createConversation(token);
    const summaries = await chatApi.listConversations(token);
    setConversations(summaries);
    setActiveConversation(conversation);
    setSelectedAssistantMessageId(null);
  };

  const openConversation = async (conversationId: string) => {
    if (!token) {
      return;
    }
    const detail = await chatApi.getConversation(token, conversationId);
    setActiveConversation(detail);
    setSelectedAssistantMessageId(
      [...detail.messages].reverse().find((message) => message.role === "assistant")?.id ?? null
    );
  };

  const sendMessage = async (content: string) => {
    if (!token || !content.trim()) {
      return;
    }
    setIsSending(true);
    setError(null);
    try {
      let conversationId = activeConversation?.id;
      if (!conversationId) {
        const newConversation = await chatApi.createConversation(token, content.slice(0, 60));
        conversationId = newConversation.id;
      }
      const detail = await chatApi.sendMessage(token, conversationId, content);
      const summaries = await chatApi.listConversations(token);
      setConversations(summaries);
      setActiveConversation(detail);
      setDraft("");
      const latestAssistant = [...detail.messages].reverse().find((message) => message.role === "assistant");
      setSelectedAssistantMessageId(latestAssistant?.id ?? null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to send message.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div>
      <PageHeader
        eyebrow="Knowledge Assistant"
        title="Chat Assistant"
        description="Ask questions over uploaded SOPs and policies. Answers cite supporting source chunks and keep the source excerpts visible for review."
        tag="Cited answers"
      />

      {error ? (
        <div className="mb-5 rounded-2xl border border-alert/20 bg-alert/5 px-4 py-3 text-sm text-alert">
          {error}
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[280px_minmax(0,1fr)_340px]">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-ink">Conversations</p>
              <p className="mt-1 text-xs text-slate">Saved assistant threads</p>
            </div>
            <Button onClick={() => void createConversation()} variant="secondary">
              <MessageSquarePlus className="h-4 w-4" />
            </Button>
          </div>

          <div className="mt-4 space-y-2">
            {isLoading ? (
              <div className="rounded-2xl border border-dashed border-edge px-4 py-10 text-sm text-slate">
                Loading conversations...
              </div>
            ) : conversations.length ? (
              conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  className={`w-full rounded-2xl border px-4 py-4 text-left transition ${
                    activeConversation?.id === conversation.id
                      ? "border-accent bg-accent/5"
                      : "border-edge bg-mist hover:bg-white"
                  }`}
                  onClick={() => void openConversation(conversation.id)}
                >
                  <p className="text-sm font-semibold text-ink">{conversation.title}</p>
                  <p className="mt-2 text-xs text-slate">
                    {conversation.message_count} messages ·{" "}
                    {formatDistanceToNow(new Date(conversation.updated_at), { addSuffix: true })}
                  </p>
                </button>
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-edge px-4 py-10 text-sm text-slate">
                Start your first conversation after documents are uploaded.
              </div>
            )}
          </div>
        </Card>

        <Card className="flex min-h-[720px] flex-col">
          <div className="border-b border-edge pb-4">
            <h2 className="text-lg font-semibold text-ink">
              {activeConversation?.title ?? "Ask the operations assistant"}
            </h2>
            <p className="mt-1 text-sm text-slate">
              Answers are grounded in uploaded documents and surface the exact source excerpts.
            </p>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto py-6">
            {activeConversation?.messages.length ? (
              activeConversation.messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  isSelected={selectedAssistantMessageId === message.id}
                  message={message}
                  onSelect={() =>
                    setSelectedAssistantMessageId(message.role === "assistant" ? message.id : null)
                  }
                  onSuggestionClick={(suggestion) => void sendMessage(suggestion)}
                />
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-edge px-5 py-14 text-sm text-slate">
                Ask about a safety protocol, maintenance SOP, escalation path, or any uploaded
                policy.
              </div>
            )}
          </div>

          <form
            className="border-t border-edge pt-4"
            onSubmit={(event) => {
              event.preventDefault();
              void sendMessage(draft);
            }}
          >
            <div className="rounded-3xl border border-edge bg-mist p-3">
              <textarea
                className="min-h-[100px] w-full resize-none border-0 bg-transparent p-2 text-sm text-ink outline-none"
                onChange={(event) => setDraft(event.target.value)}
                placeholder="Ask a question about your uploaded documents..."
                value={draft}
              />
              <div className="mt-2 flex items-center justify-between">
                <p className="text-xs text-slate">
                  The assistant cites sources and states uncertainty when evidence is thin.
                </p>
                <Button disabled={isSending || !draft.trim()} type="submit">
                  <SendHorizontal className="mr-2 h-4 w-4" />
                  {isSending ? "Answering..." : "Send"}
                </Button>
              </div>
            </div>
          </form>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-ink">Source panel</p>
              <p className="mt-1 text-xs text-slate">Evidence behind the selected answer</p>
            </div>
            {selectedAssistantMessage?.citations.length ? (
              <Badge tone="signal">{selectedAssistantMessage.citations.length} sources</Badge>
            ) : null}
          </div>

          <div className="mt-5 space-y-4">
            {selectedAssistantMessage?.citations.length ? (
              selectedAssistantMessage.citations.map((citation) => (
                <div key={citation.chunk_id} className="rounded-2xl border border-edge bg-mist p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold text-ink">{citation.document_name}</p>
                    <Badge tone="accent">{Math.round(citation.score * 100)}% match</Badge>
                  </div>
                  <p className="mt-2 text-xs uppercase tracking-[0.2em] text-slate">
                    {citation.citation_label}
                  </p>
                  {citation.source_label ? (
                    <p className="mt-2 text-xs text-slate">
                      {citation.source_label}
                      {citation.source_path ? ` · ${citation.source_path}` : ""}
                    </p>
                  ) : null}
                  <p className="mt-3 text-sm leading-6 text-slate">{citation.excerpt}</p>
                  {citation.source_url ? (
                    <a
                      className="mt-3 inline-block text-xs font-semibold text-accent underline-offset-4 hover:underline"
                      href={citation.source_url}
                      rel="noreferrer"
                      target="_blank"
                    >
                      Open source
                    </a>
                  ) : null}
                </div>
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-edge px-4 py-12 text-sm text-slate">
                Select an assistant response to inspect its supporting chunks.
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}

function MessageBubble({
  message,
  isSelected,
  onSelect,
  onSuggestionClick
}: {
  message: ChatMessage;
  isSelected: boolean;
  onSelect: () => void;
  onSuggestionClick: (value: string) => void;
}) {
  const isAssistant = message.role === "assistant";
  return (
    <div className={`flex ${isAssistant ? "justify-start" : "justify-end"}`}>
      <div
        className={`max-w-[85%] rounded-3xl px-5 py-4 text-left ${
          isAssistant
            ? isSelected
              ? "border border-accent bg-accent/5"
              : "border border-edge bg-mist"
            : "bg-ink text-white"
        }`}
        onClick={() => {
          if (isAssistant) {
            onSelect();
          }
        }}
      >
        <div className="flex items-center justify-between gap-3">
          <p
            className={`text-xs font-semibold uppercase tracking-[0.2em] ${
              isAssistant ? "text-slate" : "text-white/60"
            }`}
          >
            {message.role}
          </p>
          {isAssistant && message.citations.length ? (
            <Badge tone="signal">{message.citations.length} citations</Badge>
          ) : null}
        </div>
        <p className={`mt-3 text-sm leading-7 ${isAssistant ? "text-ink" : "text-white"}`}>
          {message.content}
        </p>
        {isAssistant && message.suggested_follow_ups.length ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {message.suggested_follow_ups.map((suggestion) => (
              <button
                key={suggestion}
                className="rounded-full border border-edge bg-white px-3 py-1.5 text-xs font-semibold text-slate"
                onClick={(event) => {
                  event.stopPropagation();
                  onSuggestionClick(suggestion);
                }}
                type="button"
              >
                {suggestion}
              </button>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}
