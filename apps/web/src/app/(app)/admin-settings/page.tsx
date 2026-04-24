"use client";

import { format } from "date-fns";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/layout/auth-provider";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { adminApi, reportsApi, tagsApi } from "@/lib/api";
import type {
  AuditLogRecord,
  BackgroundJobRecord,
  MicrosoftConnector,
  MicrosoftOverview,
  PowerBIReportReference,
  SummaryTemplate,
  Tag,
  TeamsChannel
} from "@/lib/types";

const DEFAULT_CONNECTOR_FORM = {
  name: "Safety SharePoint Library",
  description: "Enterprise document sync for safety policies and operating procedures.",
  connector_type: "sharepoint",
  microsoft_tenant_id: "",
  site_hostname: "contoso.sharepoint.com",
  site_path: "sites/Operations",
  drive_name: "Documents",
  user_principal_name: "ops-admin@contoso.com",
  folder_path: "Shared Documents/Safety",
  default_tags: "safety, operations",
  sync_frequency_minutes: "1440",
  is_active: true,
  run_initial_sync: true
};

const DEFAULT_TEAMS_FORM = {
  name: "Operations Leadership",
  description: "Default Teams destination for weekly summaries and review flags.",
  channel_label: "Operations Leadership",
  delivery_type: "preview",
  webhook_url: "",
  is_active: true,
  is_default: true
};

const DEFAULT_POWER_BI_FORM = {
  name: "Operations KPI Board",
  description: "Executive metrics board linked into report generation.",
  workspace_name: "Ops Executive Analytics",
  workspace_id: "",
  report_id: "",
  report_url: "https://app.powerbi.com/groups/me/reports/operations-kpi-board",
  embed_url: "",
  tags: "operations, weekly",
  is_active: true
};

export default function AdminSettingsPage() {
  const { token, user } = useAuth();
  const [tags, setTags] = useState<Tag[]>([]);
  const [templates, setTemplates] = useState<SummaryTemplate[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogRecord[]>([]);
  const [overview, setOverview] = useState<MicrosoftOverview | null>(null);
  const [connectors, setConnectors] = useState<MicrosoftConnector[]>([]);
  const [backgroundJobs, setBackgroundJobs] = useState<BackgroundJobRecord[]>([]);
  const [teamsChannels, setTeamsChannels] = useState<TeamsChannel[]>([]);
  const [powerBIReports, setPowerBIReports] = useState<PowerBIReportReference[]>([]);
  const [templateDrafts, setTemplateDrafts] = useState<Record<string, string>>({});
  const [newTag, setNewTag] = useState("compliance");
  const [connectorForm, setConnectorForm] = useState(DEFAULT_CONNECTOR_FORM);
  const [teamsForm, setTeamsForm] = useState(DEFAULT_TEAMS_FORM);
  const [powerBIForm, setPowerBIForm] = useState(DEFAULT_POWER_BI_FORM);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingConnector, setIsSavingConnector] = useState(false);
  const [isSavingTeamsChannel, setIsSavingTeamsChannel] = useState(false);
  const [isSavingPowerBI, setIsSavingPowerBI] = useState(false);
  const [isRunningDueJobs, setIsRunningDueJobs] = useState(false);

  const isAdmin = user?.role === "admin";

  const loadData = async () => {
    if (!token || !isAdmin) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const [
        tagsResponse,
        templatesResponse,
        auditResponse,
        microsoftOverview,
        microsoftConnectors,
        jobsResponse,
        teamsChannelsResponse,
        powerBIReportsResponse
      ] = await Promise.all([
        tagsApi.list(token),
        reportsApi.listTemplates(token),
        adminApi.listAuditLogs(token),
        adminApi.microsoftOverview(token),
        adminApi.listMicrosoftConnectors(token),
        adminApi.listBackgroundJobs(token),
        adminApi.listTeamsChannels(token),
        adminApi.listPowerBIReports(token)
      ]);
      setTags(tagsResponse);
      setTemplates(templatesResponse);
      setAuditLogs(auditResponse);
      setOverview(microsoftOverview);
      setConnectors(microsoftConnectors);
      setBackgroundJobs(jobsResponse);
      setTeamsChannels(teamsChannelsResponse);
      setPowerBIReports(powerBIReportsResponse);
      setTemplateDrafts(
        Object.fromEntries(
          templatesResponse.map((template) => [template.id, template.instructions_override ?? ""])
        )
      );
      setConnectorForm((current) => ({
        ...current,
        microsoft_tenant_id:
          current.microsoft_tenant_id || microsoftOverview.tenants[0]?.id || current.microsoft_tenant_id
      }));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load admin settings.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, isAdmin]);

  if (!isAdmin) {
    return (
      <div>
        <PageHeader
          eyebrow="Administration"
          title="Admin Settings"
          description="Tag management, Microsoft integrations, template configuration, and audit visibility are restricted to admins."
          tag="Admin only"
        />
        <Card>
          <div className="rounded-2xl border border-dashed border-edge px-5 py-14 text-sm text-slate">
            Sign in as an admin user to manage system settings and review audit activity.
          </div>
        </Card>
      </div>
    );
  }

  const createTag = async () => {
    if (!token || !newTag.trim()) {
      return;
    }
    await tagsApi.create(token, { name: newTag.trim() });
    setNewTag("");
    await loadData();
  };

  const deleteTag = async (tagId: string) => {
    if (!token) {
      return;
    }
    await tagsApi.remove(token, tagId);
    await loadData();
  };

  const toggleTemplateDefault = async (template: SummaryTemplate) => {
    if (!token) {
      return;
    }
    await adminApi.updateTemplate(token, template.id, { is_default: true });
    await loadData();
  };

  const saveTemplateOverride = async (template: SummaryTemplate) => {
    if (!token) {
      return;
    }
    await adminApi.updateTemplate(token, template.id, {
      instructions_override: templateDrafts[template.id] ?? ""
    });
    await loadData();
  };

  const createConnector = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) {
      return;
    }
    setIsSavingConnector(true);
    setError(null);
    try {
      await adminApi.createMicrosoftConnector(token, {
        name: connectorForm.name,
        description: connectorForm.description || null,
        connector_type: connectorForm.connector_type,
        microsoft_tenant_id: connectorForm.microsoft_tenant_id || null,
        site_hostname:
          connectorForm.connector_type === "sharepoint" ? connectorForm.site_hostname || null : null,
        site_path:
          connectorForm.connector_type === "sharepoint" ? connectorForm.site_path || null : null,
        drive_name:
          connectorForm.connector_type === "sharepoint" ? connectorForm.drive_name || null : null,
        user_principal_name:
          connectorForm.connector_type === "onedrive" ? connectorForm.user_principal_name || null : null,
        folder_path: connectorForm.folder_path || null,
        default_tags: connectorForm.default_tags
          .split(",")
          .map((value) => value.trim())
          .filter(Boolean),
        sync_frequency_minutes: Number.parseInt(connectorForm.sync_frequency_minutes, 10) || 1440,
        is_active: connectorForm.is_active,
        run_initial_sync: connectorForm.run_initial_sync
      });
      setConnectorForm((current) => ({ ...DEFAULT_CONNECTOR_FORM, microsoft_tenant_id: current.microsoft_tenant_id }));
      await loadData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to create connector.");
    } finally {
      setIsSavingConnector(false);
    }
  };

  const syncConnector = async (connectorId: string) => {
    if (!token) {
      return;
    }
    try {
      await adminApi.syncMicrosoftConnector(token, connectorId);
      await loadData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to queue connector sync.");
    }
  };

  const toggleConnectorStatus = async (connector: MicrosoftConnector) => {
    if (!token) {
      return;
    }
    try {
      await adminApi.updateMicrosoftConnector(token, connector.id, {
        is_active: !connector.is_active
      });
      await loadData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to update connector.");
    }
  };

  const runDueJobs = async () => {
    if (!token) {
      return;
    }
    setIsRunningDueJobs(true);
    try {
      await adminApi.runDueMicrosoftJobs(token);
      await loadData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to dispatch due jobs.");
    } finally {
      setIsRunningDueJobs(false);
    }
  };

  const createTeamsChannel = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) {
      return;
    }
    setIsSavingTeamsChannel(true);
    setError(null);
    try {
      await adminApi.createTeamsChannel(token, {
        name: teamsForm.name,
        description: teamsForm.description || null,
        channel_label: teamsForm.channel_label || null,
        delivery_type: teamsForm.delivery_type,
        webhook_url: teamsForm.delivery_type === "webhook" ? teamsForm.webhook_url || null : null,
        is_active: teamsForm.is_active,
        is_default: teamsForm.is_default
      });
      setTeamsForm(DEFAULT_TEAMS_FORM);
      await loadData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to create Teams channel.");
    } finally {
      setIsSavingTeamsChannel(false);
    }
  };

  const setDefaultTeamsChannel = async (channel: TeamsChannel) => {
    if (!token || channel.delivery_type !== "preview") {
      return;
    }
    await adminApi.updateTeamsChannel(token, channel.id, {
      name: channel.name,
      description: channel.description,
      channel_label: channel.channel_label,
      delivery_type: channel.delivery_type,
      webhook_url: null,
      is_active: true,
      is_default: true
    });
    await loadData();
  };

  const toggleTeamsChannel = async (channel: TeamsChannel) => {
    if (!token || channel.delivery_type !== "preview") {
      return;
    }
    await adminApi.updateTeamsChannel(token, channel.id, {
      name: channel.name,
      description: channel.description,
      channel_label: channel.channel_label,
      delivery_type: channel.delivery_type,
      webhook_url: null,
      is_active: !channel.is_active,
      is_default: channel.is_default && channel.is_active ? false : channel.is_default
    });
    await loadData();
  };

  const createPowerBIReference = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) {
      return;
    }
    setIsSavingPowerBI(true);
    setError(null);
    try {
      await adminApi.createPowerBIReport(token, {
        name: powerBIForm.name,
        description: powerBIForm.description || null,
        workspace_name: powerBIForm.workspace_name || null,
        workspace_id: powerBIForm.workspace_id || null,
        report_id: powerBIForm.report_id || null,
        report_url: powerBIForm.report_url,
        embed_url: powerBIForm.embed_url || null,
        tags: powerBIForm.tags
          .split(",")
          .map((value) => value.trim())
          .filter(Boolean),
        is_active: powerBIForm.is_active
      });
      setPowerBIForm(DEFAULT_POWER_BI_FORM);
      await loadData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to create Power BI reference.");
    } finally {
      setIsSavingPowerBI(false);
    }
  };

  const togglePowerBIReference = async (report: PowerBIReportReference) => {
    if (!token) {
      return;
    }
    await adminApi.updatePowerBIReport(token, report.id, {
      name: report.name,
      description: report.description,
      workspace_name: report.workspace_name,
      workspace_id: report.workspace_id,
      report_id: report.report_id,
      report_url: report.report_url,
      embed_url: report.embed_url,
      tags: report.tags,
      is_active: !report.is_active
    });
    await loadData();
  };

  return (
    <div>
      <PageHeader
        eyebrow="Administration"
        title="Admin Settings"
        description="Manage enterprise Microsoft connections, sync operations, summary templates, tags, and audit visibility from a single admin surface."
        tag="Enterprise admin"
      />

      {error ? (
        <div className="mb-5 rounded-2xl border border-alert/20 bg-alert/5 px-4 py-3 text-sm text-alert">
          {error}
        </div>
      ) : null}

      <div className="space-y-5">
        <div className="grid gap-5 xl:grid-cols-[0.85fr_1.15fr]">
          <Card>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Microsoft readiness</h2>
              <Badge tone={overview?.microsoft_graph_app_configured ? "signal" : "alert"}>
                {overview?.microsoft_graph_app_configured ? "Graph ready" : "Config needed"}
              </Badge>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <InfoPill
                label="Sign-in"
                value={overview?.microsoft_auth_enabled ? "Enabled" : "Disabled"}
              />
              <InfoPill
                label="Graph app"
                value={overview?.microsoft_graph_app_configured ? "Configured" : "Missing secret/client"}
              />
              <InfoPill label="Tenant mode" value={overview?.configured_tenant_id ?? "organizations"} />
              <InfoPill
                label="Tenants discovered"
                value={String(overview?.tenants.length ?? 0)}
              />
              <InfoPill label="Email delivery" value={overview?.email_provider ?? "preview"} />
              <InfoPill label="Teams delivery" value={overview?.teams_provider ?? "preview"} />
            </div>

            <div className="mt-5 rounded-2xl border border-edge bg-mist p-4">
              <p className="text-sm font-semibold text-ink">Role mapping scaffold</p>
              <p className="mt-2 text-sm text-slate">
                Admin emails:{" "}
                {overview?.admin_emails.length ? overview.admin_emails.join(", ") : "No explicit email overrides"}
              </p>
              <p className="mt-2 text-sm text-slate">
                Admin domains:{" "}
                {overview?.admin_domains.length ? overview.admin_domains.join(", ") : "No domain overrides"}
              </p>
              <p className="mt-2 text-sm text-slate">
                Outlook sender: {overview?.microsoft_outlook_sender ?? "Not configured"}
              </p>
              <p className="mt-2 text-sm text-slate">
                Default Teams channel: {overview?.default_teams_channel_name ?? "Not configured"}
              </p>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Add connector</h2>
              <Badge tone="accent">
                {overview?.connector_count ?? 0} source{(overview?.connector_count ?? 0) === 1 ? "" : "s"}
              </Badge>
            </div>

            <form className="mt-5 space-y-4" onSubmit={createConnector}>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-sm font-medium text-ink">Name</label>
                  <Input
                    className="mt-2"
                    onChange={(event) =>
                      setConnectorForm((current) => ({ ...current, name: event.target.value }))
                    }
                    value={connectorForm.name}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-ink">Connector type</label>
                  <select
                    className="mt-2 w-full rounded-2xl border border-edge bg-white px-4 py-3 text-sm text-ink outline-none"
                    onChange={(event) =>
                      setConnectorForm((current) => ({ ...current, connector_type: event.target.value }))
                    }
                    value={connectorForm.connector_type}
                  >
                    <option value="sharepoint">SharePoint document library</option>
                    <option value="onedrive">OneDrive folder</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-ink">Description</label>
                <textarea
                  className="mt-2 min-h-[84px] w-full rounded-2xl border border-edge bg-white px-4 py-3 text-sm text-ink outline-none"
                  onChange={(event) =>
                    setConnectorForm((current) => ({ ...current, description: event.target.value }))
                  }
                  value={connectorForm.description}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-sm font-medium text-ink">Tenant</label>
                  <select
                    className="mt-2 w-full rounded-2xl border border-edge bg-white px-4 py-3 text-sm text-ink outline-none"
                    onChange={(event) =>
                      setConnectorForm((current) => ({
                        ...current,
                        microsoft_tenant_id: event.target.value
                      }))
                    }
                    value={connectorForm.microsoft_tenant_id}
                  >
                    <option value="">Select tenant</option>
                    {overview?.tenants.map((tenant) => (
                      <option key={tenant.id} value={tenant.id}>
                        {tenant.display_name || tenant.primary_domain || tenant.tenant_id}
                      </option>
                    ))}
                  </select>
                  <p className="mt-2 text-xs text-slate">
                    Sign in with Microsoft first if no tenant appears here.
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-ink">Sync cadence</label>
                  <Input
                    className="mt-2"
                    onChange={(event) =>
                      setConnectorForm((current) => ({
                        ...current,
                        sync_frequency_minutes: event.target.value
                      }))
                    }
                    placeholder="1440"
                    value={connectorForm.sync_frequency_minutes}
                  />
                </div>
              </div>

              {connectorForm.connector_type === "sharepoint" ? (
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <label className="text-sm font-medium text-ink">Site hostname</label>
                    <Input
                      className="mt-2"
                      onChange={(event) =>
                        setConnectorForm((current) => ({
                          ...current,
                          site_hostname: event.target.value
                        }))
                      }
                      value={connectorForm.site_hostname}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-ink">Site path</label>
                    <Input
                      className="mt-2"
                      onChange={(event) =>
                        setConnectorForm((current) => ({ ...current, site_path: event.target.value }))
                      }
                      value={connectorForm.site_path}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-ink">Library name</label>
                    <Input
                      className="mt-2"
                      onChange={(event) =>
                        setConnectorForm((current) => ({ ...current, drive_name: event.target.value }))
                      }
                      value={connectorForm.drive_name}
                    />
                  </div>
                </div>
              ) : (
                <div>
                  <label className="text-sm font-medium text-ink">User principal name</label>
                  <Input
                    className="mt-2"
                    onChange={(event) =>
                      setConnectorForm((current) => ({
                        ...current,
                        user_principal_name: event.target.value
                      }))
                    }
                    value={connectorForm.user_principal_name}
                  />
                </div>
              )}

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-sm font-medium text-ink">Folder path</label>
                  <Input
                    className="mt-2"
                    onChange={(event) =>
                      setConnectorForm((current) => ({ ...current, folder_path: event.target.value }))
                    }
                    value={connectorForm.folder_path}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-ink">Default tags</label>
                  <Input
                    className="mt-2"
                    onChange={(event) =>
                      setConnectorForm((current) => ({ ...current, default_tags: event.target.value }))
                    }
                    placeholder="safety, operations"
                    value={connectorForm.default_tags}
                  />
                </div>
              </div>

              <div className="flex flex-wrap gap-6 text-sm text-slate">
                <label className="flex items-center gap-2">
                  <input
                    checked={connectorForm.is_active}
                    onChange={(event) =>
                      setConnectorForm((current) => ({ ...current, is_active: event.target.checked }))
                    }
                    type="checkbox"
                  />
                  Active connector
                </label>
                <label className="flex items-center gap-2">
                  <input
                    checked={connectorForm.run_initial_sync}
                    onChange={(event) =>
                      setConnectorForm((current) => ({
                        ...current,
                        run_initial_sync: event.target.checked
                      }))
                    }
                    type="checkbox"
                  />
                  Run initial sync immediately
                </label>
              </div>

              <Button disabled={isSavingConnector || !overview?.tenants.length} type="submit">
                {isSavingConnector ? "Saving connector..." : "Create connector"}
              </Button>
            </form>
          </Card>
        </div>

        <div className="grid gap-5 xl:grid-cols-[1.05fr_0.95fr]">
          <Card>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Connector sources</h2>
              <Button disabled={isRunningDueJobs || isLoading} onClick={() => void runDueJobs()} variant="secondary">
                {isRunningDueJobs ? "Dispatching..." : "Run due syncs"}
              </Button>
            </div>

            <div className="mt-5 space-y-3">
              {connectors.length ? (
                connectors.map((connector) => (
                  <div key={connector.id} className="rounded-2xl border border-edge bg-mist p-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="text-sm font-semibold text-ink">{connector.name}</p>
                          <Badge
                            tone={
                              connector.status === "error"
                                ? "alert"
                                : connector.status === "syncing"
                                  ? "accent"
                                  : "signal"
                            }
                          >
                            {connector.status}
                          </Badge>
                          <Badge tone="accent">{connector.connector_type}</Badge>
                        </div>
                        <p className="mt-2 text-sm text-slate">
                          {connector.source_label} · {connector.tenant_label}
                        </p>
                        <p className="mt-2 text-sm text-slate">
                          {connector.document_count} indexed document
                          {connector.document_count === 1 ? "" : "s"} · sync every{" "}
                          {connector.sync_frequency_minutes} minutes
                        </p>
                        <p className="mt-2 text-xs text-slate">
                          Last sync:{" "}
                          {connector.last_synced_at
                            ? format(new Date(connector.last_synced_at), "MMM d, HH:mm")
                            : "Never"}
                          {" · "}
                          Next sync:{" "}
                          {connector.next_sync_at
                            ? format(new Date(connector.next_sync_at), "MMM d, HH:mm")
                            : "Not scheduled"}
                        </p>
                      </div>

                      <div className="flex gap-2">
                        <Button onClick={() => void syncConnector(connector.id)} variant="secondary">
                          Sync now
                        </Button>
                        <Button onClick={() => void toggleConnectorStatus(connector)} variant="ghost">
                          {connector.is_active ? "Pause" : "Resume"}
                        </Button>
                      </div>
                    </div>

                    {connector.default_tags.length ? (
                      <div className="mt-4 flex flex-wrap gap-2">
                        {connector.default_tags.map((tag) => (
                          <Badge key={tag} tone="accent">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    ) : null}

                    {connector.last_error ? (
                      <p className="mt-4 rounded-xl border border-alert/20 bg-alert/5 px-3 py-3 text-sm text-alert">
                        {connector.last_error}
                      </p>
                    ) : null}

                    {connector.source_url ? (
                      <a
                        className="mt-4 inline-block text-xs font-semibold text-accent underline-offset-4 hover:underline"
                        href={connector.source_url}
                        rel="noreferrer"
                        target="_blank"
                      >
                        Open configured source
                      </a>
                    ) : null}
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-edge px-4 py-12 text-sm text-slate">
                  No Microsoft connectors configured yet.
                </div>
              )}
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Sync jobs</h2>
              <Badge tone="signal">{backgroundJobs.length} recent</Badge>
            </div>

            <div className="mt-5 space-y-3">
              {backgroundJobs.length ? (
                backgroundJobs.map((job) => (
                  <div key={job.id} className="rounded-2xl border border-edge bg-mist p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="text-sm font-semibold text-ink">{job.job_type}</p>
                          <Badge
                            tone={
                              job.status === "failed"
                                ? "alert"
                                : job.status === "running"
                                  ? "accent"
                                  : "signal"
                            }
                          >
                            {job.status}
                          </Badge>
                        </div>
                        <p className="mt-2 text-xs text-slate">
                          {job.created_by_name ?? "system"} · attempts {job.attempt_count}
                        </p>
                      </div>
                      <span className="text-xs text-slate">
                        {format(new Date(job.created_at), "MMM d, HH:mm")}
                      </span>
                    </div>
                    {job.error_message ? (
                      <p className="mt-3 text-sm text-alert">{job.error_message}</p>
                    ) : null}
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-edge px-4 py-12 text-sm text-slate">
                  Sync jobs will appear here after initial or manual connector runs.
                </div>
              )}
            </div>
          </Card>
        </div>

        <div className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
          <Card>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Teams delivery channels</h2>
              <Badge tone="accent">{overview?.teams_channel_count ?? teamsChannels.length} configured</Badge>
            </div>

            <form className="mt-5 space-y-4" onSubmit={createTeamsChannel}>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-sm font-medium text-ink">Name</label>
                  <Input
                    className="mt-2"
                    onChange={(event) =>
                      setTeamsForm((current) => ({ ...current, name: event.target.value }))
                    }
                    value={teamsForm.name}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-ink">Channel label</label>
                  <Input
                    className="mt-2"
                    onChange={(event) =>
                      setTeamsForm((current) => ({ ...current, channel_label: event.target.value }))
                    }
                    value={teamsForm.channel_label}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-ink">Description</label>
                <textarea
                  className="mt-2 min-h-[84px] w-full rounded-2xl border border-edge bg-white px-4 py-3 text-sm text-ink outline-none"
                  onChange={(event) =>
                    setTeamsForm((current) => ({ ...current, description: event.target.value }))
                  }
                  value={teamsForm.description}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-sm font-medium text-ink">Delivery type</label>
                  <select
                    className="mt-2 w-full rounded-2xl border border-edge bg-white px-4 py-3 text-sm text-ink outline-none"
                    onChange={(event) =>
                      setTeamsForm((current) => ({ ...current, delivery_type: event.target.value }))
                    }
                    value={teamsForm.delivery_type}
                  >
                    <option value="preview">Preview file</option>
                    <option value="webhook">Incoming webhook</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-ink">Webhook URL</label>
                  <Input
                    className="mt-2"
                    onChange={(event) =>
                      setTeamsForm((current) => ({ ...current, webhook_url: event.target.value }))
                    }
                    placeholder="Required for webhook delivery"
                    value={teamsForm.webhook_url}
                  />
                </div>
              </div>

              <div className="flex flex-wrap gap-6 text-sm text-slate">
                <label className="flex items-center gap-2">
                  <input
                    checked={teamsForm.is_active}
                    onChange={(event) =>
                      setTeamsForm((current) => ({ ...current, is_active: event.target.checked }))
                    }
                    type="checkbox"
                  />
                  Active
                </label>
                <label className="flex items-center gap-2">
                  <input
                    checked={teamsForm.is_default}
                    onChange={(event) =>
                      setTeamsForm((current) => ({ ...current, is_default: event.target.checked }))
                    }
                    type="checkbox"
                  />
                  Default channel
                </label>
              </div>

              <Button disabled={isSavingTeamsChannel} type="submit">
                {isSavingTeamsChannel ? "Saving channel..." : "Add Teams channel"}
              </Button>
            </form>

            <div className="mt-5 space-y-3">
              {teamsChannels.length ? (
                teamsChannels.map((channel) => (
                  <div key={channel.id} className="rounded-2xl border border-edge bg-mist p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="text-sm font-semibold text-ink">{channel.channel_label ?? channel.name}</p>
                          <Badge tone="signal">{channel.delivery_type}</Badge>
                          {channel.is_default ? <Badge tone="accent">default</Badge> : null}
                        </div>
                        <p className="mt-2 text-sm text-slate">{channel.description ?? "No description"}</p>
                        <p className="mt-2 text-xs text-slate">
                          {channel.has_webhook ? "Webhook configured" : "Preview delivery"}
                        </p>
                      </div>
                      {channel.delivery_type === "preview" ? (
                        <div className="flex gap-2">
                          {!channel.is_default ? (
                            <Button onClick={() => void setDefaultTeamsChannel(channel)} variant="secondary">
                              Make default
                            </Button>
                          ) : null}
                          <Button onClick={() => void toggleTeamsChannel(channel)} variant="ghost">
                            {channel.is_active ? "Pause" : "Resume"}
                          </Button>
                        </div>
                      ) : (
                        <span className="text-xs text-slate">Webhook channels currently support create-only management.</span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-edge px-4 py-10 text-sm text-slate">
                  No Teams channels configured yet.
                </div>
              )}
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Power BI references</h2>
              <Badge tone="accent">{overview?.power_bi_report_count ?? powerBIReports.length} linked</Badge>
            </div>

            <form className="mt-5 space-y-4" onSubmit={createPowerBIReference}>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-sm font-medium text-ink">Name</label>
                  <Input
                    className="mt-2"
                    onChange={(event) =>
                      setPowerBIForm((current) => ({ ...current, name: event.target.value }))
                    }
                    value={powerBIForm.name}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-ink">Workspace</label>
                  <Input
                    className="mt-2"
                    onChange={(event) =>
                      setPowerBIForm((current) => ({ ...current, workspace_name: event.target.value }))
                    }
                    value={powerBIForm.workspace_name}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-ink">Description</label>
                <textarea
                  className="mt-2 min-h-[84px] w-full rounded-2xl border border-edge bg-white px-4 py-3 text-sm text-ink outline-none"
                  onChange={(event) =>
                    setPowerBIForm((current) => ({ ...current, description: event.target.value }))
                  }
                  value={powerBIForm.description}
                />
              </div>

              <div>
                <label className="text-sm font-medium text-ink">Report URL</label>
                <Input
                  className="mt-2"
                  onChange={(event) =>
                    setPowerBIForm((current) => ({ ...current, report_url: event.target.value }))
                  }
                  value={powerBIForm.report_url}
                />
              </div>

              <div>
                <label className="text-sm font-medium text-ink">Tags</label>
                <Input
                  className="mt-2"
                  onChange={(event) =>
                    setPowerBIForm((current) => ({ ...current, tags: event.target.value }))
                  }
                  value={powerBIForm.tags}
                />
              </div>

              <label className="flex items-center gap-2 text-sm text-slate">
                <input
                  checked={powerBIForm.is_active}
                  onChange={(event) =>
                    setPowerBIForm((current) => ({ ...current, is_active: event.target.checked }))
                  }
                  type="checkbox"
                />
                Active reference
              </label>

              <Button disabled={isSavingPowerBI} type="submit">
                {isSavingPowerBI ? "Saving reference..." : "Add Power BI reference"}
              </Button>
            </form>

            <div className="mt-5 space-y-3">
              {powerBIReports.length ? (
                powerBIReports.map((report) => (
                  <div key={report.id} className="rounded-2xl border border-edge bg-mist p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-ink">{report.name}</p>
                        <p className="mt-1 text-xs text-slate">
                          {report.workspace_name ?? "Power BI"} · {report.tags.join(", ") || "untagged"}
                        </p>
                        <p className="mt-2 text-sm text-slate">{report.description ?? "No description"}</p>
                      </div>
                      <Button onClick={() => void togglePowerBIReference(report)} variant="ghost">
                        {report.is_active ? "Disable" : "Enable"}
                      </Button>
                    </div>
                    <a
                      className="mt-3 inline-block text-xs font-semibold text-accent underline-offset-4 hover:underline"
                      href={report.report_url}
                      rel="noreferrer"
                      target="_blank"
                    >
                      Open Power BI report
                    </a>
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-edge px-4 py-10 text-sm text-slate">
                  No Power BI references configured yet.
                </div>
              )}
            </div>
          </Card>
        </div>

        <div className="grid gap-5 xl:grid-cols-[0.92fr_1.08fr]">
          <div className="space-y-5">
            <Card>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-ink">Tags</h2>
                <Badge tone="signal">{tags.length} configured</Badge>
              </div>

              <div className="mt-5 flex gap-3">
                <Input onChange={(event) => setNewTag(event.target.value)} value={newTag} />
                <Button onClick={() => void createTag()} variant="secondary">
                  Add tag
                </Button>
              </div>

              <div className="mt-5 space-y-3">
                {tags.map((tag) => (
                  <div
                    key={tag.id}
                    className="flex items-center justify-between rounded-2xl border border-edge bg-mist px-4 py-3"
                  >
                    <div>
                      <p className="text-sm font-semibold text-ink">{tag.name}</p>
                      <p className="mt-1 text-xs text-slate">{tag.description ?? "No description"}</p>
                    </div>
                    <Button onClick={() => void deleteTag(tag.id)} variant="ghost">
                      Delete
                    </Button>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-ink">Summary templates</h2>
                <Badge tone="accent">{templates.length} available</Badge>
              </div>

              <div className="mt-5 space-y-3">
                {templates.map((template) => (
                  <div key={template.id} className="rounded-2xl border border-edge bg-mist p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-ink">{template.name}</p>
                        <p className="mt-1 text-xs text-slate">
                          {template.report_type} · {template.template_key}
                        </p>
                      </div>
                      {template.is_default ? (
                        <Badge tone="signal">default</Badge>
                      ) : (
                        <Button onClick={() => void toggleTemplateDefault(template)} variant="secondary">
                          Make default
                        </Button>
                      )}
                    </div>
                    <p className="mt-3 text-sm text-slate">{template.description ?? "No description"}</p>
                    <textarea
                      className="mt-3 min-h-[96px] w-full rounded-2xl border border-white bg-white px-4 py-3 text-sm text-ink outline-none"
                      onChange={(event) =>
                        setTemplateDrafts((current) => ({
                          ...current,
                          [template.id]: event.target.value
                        }))
                      }
                      placeholder="Optional admin override instructions for this template..."
                      value={templateDrafts[template.id] ?? ""}
                    />
                    <div className="mt-3 flex justify-end">
                      <Button onClick={() => void saveTemplateOverride(template)} variant="secondary">
                        Save override
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <Card>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Audit log</h2>
              <Badge tone="signal">{auditLogs.length} recent events</Badge>
            </div>

            <div className="mt-5 space-y-3">
              {auditLogs.map((log) => (
                <div key={log.id} className="rounded-2xl border border-edge bg-mist p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-sm font-semibold text-ink">{log.message}</p>
                      <p className="mt-1 text-xs text-slate">
                        {log.event_type} · {log.actor_name ?? "system"}
                      </p>
                    </div>
                    <span className="text-xs text-slate">
                      {format(new Date(log.created_at), "MMM d, HH:mm")}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function InfoPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-edge bg-mist px-4 py-4">
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate">{label}</p>
      <p className="mt-2 text-sm font-semibold text-ink">{value}</p>
    </div>
  );
}
