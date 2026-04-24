"use client";

import { format } from "date-fns";
import { Download, FileText, Link2, Mail, Send, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/components/layout/auth-provider";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { documentsApi, reportsApi } from "@/lib/api";
import type {
  DocumentRecord,
  PowerBIReportReference,
  ReportRecord,
  SummaryTemplate,
  TeamsChannel
} from "@/lib/types";

const REPORT_TYPES = [
  { id: "executive", label: "Executive summary" },
  { id: "operational", label: "Operational summary" },
  { id: "document_changes", label: "Document changes summary" }
];

export default function ReportsPage() {
  const { token } = useAuth();
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [templates, setTemplates] = useState<SummaryTemplate[]>([]);
  const [reports, setReports] = useState<ReportRecord[]>([]);
  const [powerBIReports, setPowerBIReports] = useState<PowerBIReportReference[]>([]);
  const [teamsChannels, setTeamsChannels] = useState<TeamsChannel[]>([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  const [selectedPowerBIIds, setSelectedPowerBIIds] = useState<string[]>([]);
  const [emailRecipients, setEmailRecipients] = useState("");
  const [selectedTeamsChannelId, setSelectedTeamsChannelId] = useState("");
  const [reportType, setReportType] = useState("executive");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [deliveryMessage, setDeliveryMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [deliveryReportId, setDeliveryReportId] = useState<string | null>(null);

  const activeTemplates = useMemo(
    () => templates.filter((template) => template.report_type === reportType),
    [reportType, templates]
  );

  const loadData = async () => {
    if (!token) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const [
        documentsResponse,
        templatesResponse,
        reportsResponse,
        powerBIResponse,
        teamsChannelsResponse
      ] = await Promise.all([
        documentsApi.list(token),
        reportsApi.listTemplates(token),
        reportsApi.listReports(token),
        reportsApi.listPowerBIReferences(token),
        reportsApi.listTeamsChannels(token)
      ]);
      setDocuments(documentsResponse.items);
      setTemplates(templatesResponse);
      setReports(reportsResponse.items);
      setPowerBIReports(powerBIResponse);
      setTeamsChannels(teamsChannelsResponse);
      if (!selectedTeamsChannelId) {
        const defaultChannel =
          teamsChannelsResponse.find((channel) => channel.is_default) ?? teamsChannelsResponse[0];
        setSelectedTeamsChannelId(defaultChannel?.id ?? "");
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load reports.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const generateReport = async () => {
    if (!token) {
      return;
    }
    setIsGenerating(true);
    setError(null);
    try {
      await reportsApi.generate(token, {
        report_type: reportType,
        template_id: activeTemplates[0]?.id ?? null,
        document_ids: selectedDocumentIds,
        power_bi_report_ids: selectedPowerBIIds,
        notes
      });
      setNotes("");
      setDeliveryMessage(null);
      await loadData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Report generation failed.");
    } finally {
      setIsGenerating(false);
    }
  };

  const deliverReportEmail = async (reportId: string) => {
    if (!token) {
      return;
    }
    setDeliveryReportId(reportId);
    setError(null);
    setDeliveryMessage(null);
    try {
      const job = await reportsApi.deliverEmail(token, reportId, {
        recipients: emailRecipients
          .split(",")
          .map((value) => value.trim())
          .filter(Boolean)
      });
      setDeliveryMessage(`Email delivery queued with job ${job.id}.`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to queue email delivery.");
    } finally {
      setDeliveryReportId(null);
    }
  };

  const deliverReportTeams = async (reportId: string) => {
    if (!token) {
      return;
    }
    setDeliveryReportId(reportId);
    setError(null);
    setDeliveryMessage(null);
    try {
      const job = await reportsApi.deliverTeams(token, reportId, {
        channel_id: selectedTeamsChannelId || null
      });
      setDeliveryMessage(`Teams delivery queued with job ${job.id}.`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to queue Teams delivery.");
    } finally {
      setDeliveryReportId(null);
    }
  };

  const exportReport = async (reportId: string, exportFormat: "markdown" | "html") => {
    if (!token) {
      return;
    }
    const payload = await reportsApi.export(token, reportId, exportFormat);
    const blob = new Blob([payload.content], { type: payload.content_type });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = payload.filename;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <PageHeader
        eyebrow="Executive Reporting"
        title="Reports"
        description="Generate structured executive, operational, and document-change summaries from selected documents and recent system activity."
        tag="Executive summaries"
      />

      {error ? (
        <div className="mb-5 rounded-2xl border border-alert/20 bg-alert/5 px-4 py-3 text-sm text-alert">
          {error}
        </div>
      ) : null}

      {deliveryMessage ? (
        <div className="mb-5 rounded-2xl border border-signal/20 bg-signal/5 px-4 py-3 text-sm text-signal">
          {deliveryMessage}
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[0.92fr_1.08fr]">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-ink">Generate report</h2>
              <p className="mt-1 text-sm text-slate">Use saved templates and selected source docs.</p>
            </div>
            <Badge tone="signal">Structured output</Badge>
          </div>

          <div className="mt-6 grid gap-3">
            {REPORT_TYPES.map((option) => (
              <button
                key={option.id}
                className={`rounded-2xl border px-4 py-4 text-left transition ${
                  reportType === option.id ? "border-accent bg-accent/5" : "border-edge bg-mist"
                }`}
                onClick={() => setReportType(option.id)}
                type="button"
              >
                <p className="text-sm font-semibold text-ink">{option.label}</p>
                <p className="mt-1 text-xs text-slate">
                  {templates.find((template) => template.report_type === option.id)?.name ??
                    "Template available"}
                </p>
              </button>
            ))}
          </div>

          <div className="mt-6">
            <p className="text-sm font-semibold text-ink">Source documents</p>
            <div className="mt-3 max-h-[280px] space-y-2 overflow-y-auto rounded-2xl border border-edge bg-mist p-3">
              {documents.map((document) => {
                const isSelected = selectedDocumentIds.includes(document.id);
                return (
                  <label
                    key={document.id}
                    className="flex cursor-pointer items-start gap-3 rounded-2xl border border-white bg-white px-4 py-3"
                  >
                    <input
                      checked={isSelected}
                      onChange={(event) => {
                        if (event.target.checked) {
                          setSelectedDocumentIds((current) => [...current, document.id]);
                        } else {
                          setSelectedDocumentIds((current) =>
                            current.filter((value) => value !== document.id)
                          );
                        }
                      }}
                      type="checkbox"
                    />
                    <div>
                      <p className="text-sm font-semibold text-ink">{document.name}</p>
                      <p className="mt-1 text-xs text-slate">
                        {document.chunk_count} chunks · {document.tags.map((tag) => tag.name).join(", ") || "untagged"}
                      </p>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>

          <div className="mt-6">
            <p className="text-sm font-semibold text-ink">Linked Power BI context</p>
            <div className="mt-3 max-h-[220px] space-y-2 overflow-y-auto rounded-2xl border border-edge bg-mist p-3">
              {powerBIReports.length ? (
                powerBIReports.map((report) => {
                  const isSelected = selectedPowerBIIds.includes(report.id);
                  return (
                    <label
                      key={report.id}
                      className="flex cursor-pointer items-start gap-3 rounded-2xl border border-white bg-white px-4 py-3"
                    >
                      <input
                        checked={isSelected}
                        onChange={(event) => {
                          if (event.target.checked) {
                            setSelectedPowerBIIds((current) => [...current, report.id]);
                          } else {
                            setSelectedPowerBIIds((current) =>
                              current.filter((value) => value !== report.id)
                            );
                          }
                        }}
                        type="checkbox"
                      />
                      <div>
                        <p className="text-sm font-semibold text-ink">{report.name}</p>
                        <p className="mt-1 text-xs text-slate">
                          {report.workspace_name ?? "Power BI"} · {report.tags.join(", ") || "untagged"}
                        </p>
                      </div>
                    </label>
                  );
                })
              ) : (
                <div className="rounded-2xl border border-dashed border-edge px-4 py-8 text-sm text-slate">
                  No Power BI references are configured yet.
                </div>
              )}
            </div>
          </div>

          <div className="mt-6">
            <p className="text-sm font-semibold text-ink">Notes for this run</p>
            <textarea
              className="mt-3 min-h-[120px] w-full rounded-2xl border border-edge bg-mist px-4 py-3 text-sm text-ink outline-none"
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Optional context, priorities, or caveats for this week's report..."
              value={notes}
            />
          </div>

          <Button className="mt-6 w-full" disabled={isGenerating} onClick={() => void generateReport()}>
            <Sparkles className="mr-2 h-4 w-4" />
            {isGenerating ? "Generating..." : "Generate report"}
          </Button>

          <div className="mt-6 rounded-2xl border border-edge bg-mist p-4">
            <p className="text-sm font-semibold text-ink">Delivery defaults</p>
            <div className="mt-4 space-y-4">
              <div>
                <label className="text-sm font-medium text-ink">Email recipients</label>
                <input
                  className="mt-2 w-full rounded-2xl border border-edge bg-white px-4 py-3 text-sm text-ink outline-none"
                  onChange={(event) => setEmailRecipients(event.target.value)}
                  placeholder="ops-leadership@company.com"
                  value={emailRecipients}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-ink">Teams channel</label>
                <select
                  className="mt-2 w-full rounded-2xl border border-edge bg-white px-4 py-3 text-sm text-ink outline-none"
                  onChange={(event) => setSelectedTeamsChannelId(event.target.value)}
                  value={selectedTeamsChannelId}
                >
                  <option value="">Default configured channel</option>
                  {teamsChannels.map((channel) => (
                    <option key={channel.id} value={channel.id}>
                      {channel.channel_label ?? channel.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-ink">Report history</h2>
              <p className="mt-1 text-sm text-slate">
                {reports.length} generated report{reports.length === 1 ? "" : "s"}
              </p>
            </div>
            <Badge tone="accent">{activeTemplates[0]?.name ?? "Template ready"}</Badge>
          </div>

          <div className="mt-6 space-y-5">
            {isLoading ? (
              <div className="rounded-2xl border border-dashed border-edge px-5 py-12 text-sm text-slate">
                Loading reports...
              </div>
            ) : reports.length ? (
              reports.map((report) => (
                <div key={report.id} className="rounded-2xl border border-edge bg-mist p-5">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-lg font-semibold text-ink">{report.title}</h3>
                        <Badge tone="signal">{report.report_type.replace("_", " ")}</Badge>
                      </div>
                      <p className="mt-2 text-sm text-slate">
                        {report.template_name ?? "Default template"} ·{" "}
                        {format(new Date(report.created_at), "MMM d, yyyy HH:mm")}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2 lg:justify-end">
                      <Button
                        className="w-full sm:w-auto"
                        onClick={() => void exportReport(report.id, "markdown")}
                        variant="secondary"
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Markdown
                      </Button>
                      <Button
                        className="w-full sm:w-auto"
                        onClick={() => void exportReport(report.id, "html")}
                        variant="secondary"
                      >
                        <FileText className="mr-2 h-4 w-4" />
                        HTML
                      </Button>
                      <Button
                        className="w-full sm:w-auto"
                        disabled={deliveryReportId === report.id}
                        onClick={() => void deliverReportEmail(report.id)}
                        variant="secondary"
                      >
                        <Mail className="mr-2 h-4 w-4" />
                        Email
                      </Button>
                      <Button
                        className="w-full sm:w-auto"
                        disabled={deliveryReportId === report.id}
                        onClick={() => void deliverReportTeams(report.id)}
                        variant="secondary"
                      >
                        <Send className="mr-2 h-4 w-4" />
                        Teams
                      </Button>
                    </div>
                  </div>

                  <div className="mt-5 grid gap-4 md:grid-cols-2">
                    <Section title="Top themes" items={report.top_themes} />
                    <Section title="Risks/issues" items={report.risks} />
                    <Section title="Action items" items={report.action_items} />
                    <Section title="Notable updates" items={report.notable_updates} />
                  </div>

                  {report.linked_power_bi_reports.length ? (
                    <div className="mt-5 rounded-2xl border border-white bg-white p-4">
                      <div className="flex items-center gap-2">
                        <Link2 className="h-4 w-4 text-accent" />
                        <p className="text-sm font-semibold text-ink">Linked Power BI references</p>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-3">
                        {report.linked_power_bi_reports.map((item) => (
                          <a
                            key={item.id}
                            className="rounded-2xl border border-edge px-3 py-2 text-sm text-accent transition hover:border-accent"
                            href={item.report_url}
                            rel="noreferrer"
                            target="_blank"
                          >
                            {item.name}
                          </a>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>
              ))
            ) : (
              <div className="rounded-2xl border border-dashed border-edge px-5 py-12 text-sm text-slate">
                No reports generated yet. Use the panel on the left to create the first one.
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}

function Section({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-2xl border border-white bg-white p-4">
      <p className="text-sm font-semibold text-ink">{title}</p>
      <ul className="mt-3 space-y-2 text-sm leading-6 text-slate">
        {items.map((item) => (
          <li key={item} className="break-words">
            - {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
