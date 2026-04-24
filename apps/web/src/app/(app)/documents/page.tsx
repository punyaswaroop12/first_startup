"use client";

import { format } from "date-fns";
import { Search, Trash2, UploadCloud } from "lucide-react";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/layout/auth-provider";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { documentsApi, tagsApi } from "@/lib/api";
import type { DocumentRecord, Tag } from "@/lib/types";

export default function DocumentsPage() {
  const { token, user } = useAuth();
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [query, setQuery] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [tagsInput, setTagsInput] = useState("safety");
  const [versionLabel, setVersionLabel] = useState("1.0");
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const canManageDocuments = user?.role === "admin";

  const loadDocuments = async (activeQuery = query) => {
    if (!token) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const [documentsResponse, tagsResponse] = await Promise.all([
        documentsApi.list(token, activeQuery),
        tagsApi.list(token)
      ]);
      setDocuments(documentsResponse.items);
      setAvailableTags(tagsResponse);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load documents.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadDocuments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const submitUpload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token || !selectedFile) {
      return;
    }
    setError(null);
    setIsUploading(true);
    const payload = new FormData();
    payload.append("file", selectedFile);
    payload.append("tags", tagsInput);
    payload.append("version_label", versionLabel);

    try {
      await documentsApi.upload(token, payload);
      setSelectedFile(null);
      setTagsInput("safety");
      setVersionLabel("1.0");
      await loadDocuments();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const deleteDocument = async (documentId: string) => {
    if (!token) {
      return;
    }
    try {
      await documentsApi.remove(token, documentId);
      await loadDocuments();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Delete failed.");
    }
  };

  return (
    <div>
      <PageHeader
        eyebrow="Knowledge Base"
        title="Documents"
        description="Upload policies, SOPs, checklists, and CSV exports. Each document is validated, parsed, chunked, tagged, and prepared for retrieval."
        tag="Indexed content"
      />

      {error ? (
        <div className="mb-5 rounded-2xl border border-alert/20 bg-alert/5 px-4 py-3 text-sm text-alert">
          {error}
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-ink">Upload pipeline</h2>
            <Badge tone={canManageDocuments ? "signal" : "neutral"}>
              {canManageDocuments ? "Admin enabled" : "Read only"}
            </Badge>
          </div>
          <p className="mt-4 text-sm leading-7 text-slate">
            Supported formats: PDF, DOCX, TXT, and CSV. Uploads are capped at 15MB and stored with
            version metadata, tags, owner attribution, and ingest status.
          </p>

          <form className="mt-6 space-y-4" onSubmit={submitUpload}>
            <div className="rounded-2xl border border-edge bg-mist p-4">
              <label className="text-sm font-medium text-ink">Document file</label>
              <input
                accept=".pdf,.docx,.txt,.csv"
                className="mt-3 block w-full rounded-xl border border-edge bg-white px-3 py-3 text-sm text-slate"
                disabled={!canManageDocuments}
                onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                type="file"
              />
              <p className="mt-3 text-xs text-slate">
                {selectedFile ? selectedFile.name : "Choose a document to ingest."}
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-sm font-medium text-ink">Tags</label>
                <Input
                  className="mt-2"
                  disabled={!canManageDocuments}
                  onChange={(event) => setTagsInput(event.target.value)}
                  placeholder="safety, compliance"
                  value={tagsInput}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-ink">Version label</label>
                <Input
                  className="mt-2"
                  disabled={!canManageDocuments}
                  onChange={(event) => setVersionLabel(event.target.value)}
                  placeholder="3.2"
                  value={versionLabel}
                />
              </div>
            </div>

            <Button
              className="w-full"
              disabled={!canManageDocuments || !selectedFile || isUploading}
              type="submit"
            >
              <UploadCloud className="mr-2 h-4 w-4" />
              {isUploading ? "Ingesting..." : "Upload and index document"}
            </Button>
          </form>

          <div className="mt-6 rounded-2xl border border-edge bg-mist p-4">
            <p className="text-sm font-semibold text-ink">Available tags</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {availableTags.map((tag) => (
                <Badge key={tag.id} tone="accent">
                  {tag.name}
                </Badge>
              ))}
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 className="text-lg font-semibold text-ink">Document inventory</h2>
              <p className="mt-1 text-sm text-slate">
                {documents.length} document{documents.length === 1 ? "" : "s"} indexed
              </p>
            </div>
            <form
              className="flex w-full max-w-md items-center gap-2"
              onSubmit={(event) => {
                event.preventDefault();
                setQuery(searchTerm);
                void loadDocuments(searchTerm);
              }}
            >
              <Input
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Search by file name, tag, or content"
                value={searchTerm}
              />
              <Button type="submit" variant="secondary">
                <Search className="h-4 w-4" />
              </Button>
            </form>
          </div>

          <div className="mt-6 space-y-4">
            {isLoading ? (
              <div className="rounded-2xl border border-dashed border-edge px-5 py-12 text-sm text-slate">
                Loading document inventory...
              </div>
            ) : documents.length ? (
              documents.map((document) => (
                <div key={document.id} className="rounded-2xl border border-edge bg-mist p-5">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-lg font-semibold text-ink">{document.name}</h3>
                        <Badge tone={document.status === "flagged" ? "alert" : "signal"}>
                          {document.status}
                        </Badge>
                        {document.requires_review ? <Badge tone="alert">review flagged</Badge> : null}
                      </div>
                      <p className="mt-2 text-sm text-slate">
                        Owned by {document.owner_name} · Uploaded{" "}
                        {format(new Date(document.created_at), "MMM d, yyyy HH:mm")}
                      </p>
                      <p className="mt-2 text-sm text-slate">
                        {document.chunk_count} chunks · {document.current_version?.parser_name ?? "parser"} ·{" "}
                        {document.version_label ? `Version ${document.version_label}` : "No version label"}
                      </p>
                      {document.source_label ? (
                        <p className="mt-2 text-sm text-slate">
                          Source: {document.source_label}
                          {document.source_path ? ` · ${document.source_path}` : ""}
                        </p>
                      ) : null}
                    </div>

                    {canManageDocuments ? (
                      <Button onClick={() => void deleteDocument(document.id)} variant="ghost">
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </Button>
                    ) : null}
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {document.tags.map((tag) => (
                      <Badge key={tag.id} tone="accent">
                        {tag.name}
                      </Badge>
                    ))}
                    {document.external_source_kind ? (
                      <Badge tone="signal">{document.external_source_kind}</Badge>
                    ) : null}
                  </div>

                  {document.source_url ? (
                    <div className="mt-4">
                      <a
                        className="text-sm font-medium text-accent underline-offset-4 hover:underline"
                        href={document.source_url}
                        rel="noreferrer"
                        target="_blank"
                      >
                        Open source document
                      </a>
                    </div>
                  ) : null}

                  {document.review_reason ? (
                    <p className="mt-4 rounded-xl border border-alert/20 bg-alert/5 px-3 py-3 text-sm text-alert">
                      {document.review_reason}
                    </p>
                  ) : null}

                  {document.matched_excerpt ? (
                    <p className="mt-4 rounded-xl border border-edge bg-white px-3 py-3 text-sm leading-6 text-slate">
                      {document.matched_excerpt}
                    </p>
                  ) : null}
                </div>
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-edge px-5 py-12 text-sm text-slate">
                No documents found. Seed data appears after running the backend seed command.
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
