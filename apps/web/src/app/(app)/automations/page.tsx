"use client";

import { format } from "date-fns";
import { Bolt, Mail, Send, ShieldAlert } from "lucide-react";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/layout/auth-provider";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { adminApi, automationsApi } from "@/lib/api";
import type { AutomationRule, AutomationRun, TeamsChannel } from "@/lib/types";

export default function AutomationsPage() {
  const { token, user } = useAuth();
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [runs, setRuns] = useState<AutomationRun[]>([]);
  const [name, setName] = useState("Safety upload summary + notify");
  const [description, setDescription] = useState(
    "When a safety-tagged document is uploaded, generate an operational summary and notify leadership."
  );
  const [triggerType, setTriggerType] = useState("document_uploaded");
  const [tagFilter, setTagFilter] = useState("safety");
  const [keywordFilter, setKeywordFilter] = useState("incident");
  const [reportType, setReportType] = useState("operational");
  const [recipients, setRecipients] = useState("");
  const [teamsChannels, setTeamsChannels] = useState<TeamsChannel[]>([]);
  const [teamsChannelId, setTeamsChannelId] = useState("");
  const [flagReason, setFlagReason] = useState("Flagged by automation rule");
  const [enableSummary, setEnableSummary] = useState(true);
  const [enableNotify, setEnableNotify] = useState(true);
  const [enableTeamsPost, setEnableTeamsPost] = useState(false);
  const [enableFlag, setEnableFlag] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const isAdmin = user?.role === "admin";

  const loadData = async () => {
    if (!token || !isAdmin) {
      return;
    }
    setError(null);
    try {
      const [rulesResponse, runsResponse, teamsChannelsResponse] = await Promise.all([
        automationsApi.listRules(token),
        automationsApi.listRuns(token),
        adminApi.listTeamsChannels(token)
      ]);
      setRules(rulesResponse);
      setRuns(runsResponse);
      setTeamsChannels(teamsChannelsResponse);
      if (!teamsChannelId) {
        const defaultChannel =
          teamsChannelsResponse.find((channel) => channel.is_default) ?? teamsChannelsResponse[0];
        setTeamsChannelId(defaultChannel?.id ?? "");
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load automations.");
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
          eyebrow="Workflow Rules"
          title="Automations"
          description="Automation rule configuration is restricted to admin users."
          tag="Admin only"
        />
        <Card>
          <div className="rounded-2xl border border-dashed border-edge px-5 py-14 text-sm text-slate">
            Sign in as an admin user to manage rules and automation history.
          </div>
        </Card>
      </div>
    );
  }

  const saveRule = async () => {
    if (!token) {
      return;
    }
    setIsSaving(true);
    setError(null);
    const conditionConfig: Record<string, unknown> = {};
    if (triggerType === "document_uploaded" && tagFilter.trim()) {
      conditionConfig.tags_any = tagFilter
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);
    }
    if (triggerType === "keyword_detected" && keywordFilter.trim()) {
      conditionConfig.keywords_any = keywordFilter
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);
    }
    if (triggerType === "report_generated") {
      conditionConfig.report_type = reportType;
    }

    const actionConfig: Array<Record<string, unknown>> = [];
    if (enableSummary && triggerType !== "report_generated") {
      actionConfig.push({ type: "generate_summary", report_type: reportType });
    }
    if (enableNotify) {
      actionConfig.push(
        triggerType === "report_generated"
          ? {
              type: "deliver_report_email",
              recipients: recipients
                .split(",")
                .map((value) => value.trim())
                .filter(Boolean)
            }
          : {
              type: "notify_recipients",
              recipients: recipients
                .split(",")
                .map((value) => value.trim())
                .filter(Boolean)
            }
      );
    }
    if (enableTeamsPost) {
      actionConfig.push(
        triggerType === "report_generated"
          ? {
              type: "deliver_report_teams",
              channel_id: teamsChannelId || undefined
            }
          : {
              type: "post_to_teams",
              channel_id: teamsChannelId || undefined
            }
      );
    }
    if (enableFlag && triggerType !== "report_generated") {
      actionConfig.push({ type: "flag_for_review", reason: flagReason });
    }

    try {
      await automationsApi.createRule(token, {
        name,
        description,
        trigger_type: triggerType,
        condition_config: conditionConfig,
        action_config: actionConfig,
        is_active: true
      });
      await loadData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to save rule.");
    } finally {
      setIsSaving(false);
    }
  };

  const toggleRule = async (rule: AutomationRule) => {
    if (!token) {
      return;
    }
    await automationsApi.updateRule(token, rule.id, {
      name: rule.name,
      description: rule.description ?? "",
      trigger_type: rule.trigger_type,
      condition_config: rule.condition_config,
      action_config: rule.action_config,
      is_active: !rule.is_active
    });
    await loadData();
  };

  return (
    <div>
      <PageHeader
        eyebrow="Workflow Rules"
        title="Automations"
        description="Configure lightweight operational rules like summarizing safety uploads, flagging keyword hits, and notifying report recipients."
        tag="Rules engine"
      />

      {error ? (
        <div className="mb-5 rounded-2xl border border-alert/20 bg-alert/5 px-4 py-3 text-sm text-alert">
          {error}
        </div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-ink">Create rule</h2>
              <p className="mt-1 text-sm text-slate">Explicit triggers, explicit conditions, explicit actions.</p>
            </div>
            <Badge tone="signal">Rules-based</Badge>
          </div>

          <div className="mt-6 space-y-4">
            <div>
              <label className="text-sm font-medium text-ink">Rule name</label>
              <Input className="mt-2" onChange={(event) => setName(event.target.value)} value={name} />
            </div>
            <div>
              <label className="text-sm font-medium text-ink">Description</label>
              <textarea
                className="mt-2 min-h-[100px] w-full rounded-2xl border border-edge bg-mist px-4 py-3 text-sm text-ink outline-none"
                onChange={(event) => setDescription(event.target.value)}
                value={description}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-ink">Trigger</label>
              <select
                className="mt-2 w-full rounded-2xl border border-edge bg-mist px-4 py-3 text-sm text-ink outline-none"
                onChange={(event) => setTriggerType(event.target.value)}
                value={triggerType}
              >
                <option value="document_uploaded">Document uploaded</option>
                <option value="report_generated">Report generated</option>
                <option value="keyword_detected">Keyword detected</option>
              </select>
            </div>

            {triggerType === "document_uploaded" ? (
              <div>
                <label className="text-sm font-medium text-ink">Tags any-match</label>
                <Input className="mt-2" onChange={(event) => setTagFilter(event.target.value)} value={tagFilter} />
              </div>
            ) : null}

            {triggerType === "keyword_detected" ? (
              <div>
                <label className="text-sm font-medium text-ink">Keywords any-match</label>
                <Input
                  className="mt-2"
                  onChange={(event) => setKeywordFilter(event.target.value)}
                  value={keywordFilter}
                />
              </div>
            ) : null}

            {(triggerType === "report_generated" || enableSummary) && triggerType !== "keyword_detected" ? (
              <div>
                <label className="text-sm font-medium text-ink">Summary/report type</label>
                <select
                  className="mt-2 w-full rounded-2xl border border-edge bg-mist px-4 py-3 text-sm text-ink outline-none"
                  onChange={(event) => setReportType(event.target.value)}
                  value={reportType}
                >
                  <option value="executive">Executive</option>
                  <option value="operational">Operational</option>
                  <option value="document_changes">Document changes</option>
                </select>
              </div>
            ) : null}

            <div className="grid gap-3">
              <label className="flex items-center gap-3 rounded-2xl border border-edge bg-mist px-4 py-3">
                <input
                  checked={enableSummary}
                  disabled={triggerType === "report_generated"}
                  onChange={(event) => setEnableSummary(event.target.checked)}
                  type="checkbox"
                />
                <Bolt className="h-4 w-4 text-accent" />
                <span className="text-sm text-ink">
                  {triggerType === "report_generated" ? "Report already generated for this trigger" : "Generate summary report"}
                </span>
              </label>
              <label className="flex items-center gap-3 rounded-2xl border border-edge bg-mist px-4 py-3">
                <input checked={enableNotify} onChange={(event) => setEnableNotify(event.target.checked)} type="checkbox" />
                <Mail className="h-4 w-4 text-signal" />
                <span className="text-sm text-ink">
                  {triggerType === "report_generated" ? "Email generated report" : "Notify recipients"}
                </span>
              </label>
              <label className="flex items-center gap-3 rounded-2xl border border-edge bg-mist px-4 py-3">
                <input checked={enableTeamsPost} onChange={(event) => setEnableTeamsPost(event.target.checked)} type="checkbox" />
                <Send className="h-4 w-4 text-accent" />
                <span className="text-sm text-ink">
                  {triggerType === "report_generated" ? "Post generated report to Teams" : "Post notification to Teams"}
                </span>
              </label>
              <label className="flex items-center gap-3 rounded-2xl border border-edge bg-mist px-4 py-3">
                <input
                  checked={enableFlag}
                  disabled={triggerType === "report_generated"}
                  onChange={(event) => setEnableFlag(event.target.checked)}
                  type="checkbox"
                />
                <ShieldAlert className="h-4 w-4 text-alert" />
                <span className="text-sm text-ink">
                  {triggerType === "report_generated" ? "Review flags apply to documents only" : "Flag for review"}
                </span>
              </label>
            </div>

            {enableNotify ? (
              <div>
                <label className="text-sm font-medium text-ink">Recipients</label>
                <Input
                  className="mt-2"
                  onChange={(event) => setRecipients(event.target.value)}
                  placeholder="ops-leadership@company.com"
                  value={recipients}
                />
              </div>
            ) : null}

            {enableTeamsPost ? (
              <div>
                <label className="text-sm font-medium text-ink">Teams channel</label>
                <select
                  className="mt-2 w-full rounded-2xl border border-edge bg-mist px-4 py-3 text-sm text-ink outline-none"
                  onChange={(event) => setTeamsChannelId(event.target.value)}
                  value={teamsChannelId}
                >
                  <option value="">Default Teams channel</option>
                  {teamsChannels.map((channel) => (
                    <option key={channel.id} value={channel.id}>
                      {channel.channel_label ?? channel.name}
                    </option>
                  ))}
                </select>
              </div>
            ) : null}

            {enableFlag && triggerType !== "report_generated" ? (
              <div>
                <label className="text-sm font-medium text-ink">Flag reason</label>
                <Input
                  className="mt-2"
                  onChange={(event) => setFlagReason(event.target.value)}
                  value={flagReason}
                />
              </div>
            ) : null}
          </div>

          <Button className="mt-6 w-full" disabled={isSaving} onClick={() => void saveRule()}>
            {isSaving ? "Saving rule..." : "Save automation rule"}
          </Button>
        </Card>

        <div className="space-y-5">
          <Card>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Active rules</h2>
              <Badge tone="accent">{rules.length} configured</Badge>
            </div>
            <div className="mt-5 space-y-4">
              {rules.length ? (
                rules.map((rule) => (
                  <div key={rule.id} className="rounded-2xl border border-edge bg-mist p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-ink">{rule.name}</p>
                        <p className="mt-1 text-sm text-slate">{rule.description}</p>
                      </div>
                      <Button onClick={() => void toggleRule(rule)} variant="secondary">
                        {rule.is_active ? "Disable" : "Enable"}
                      </Button>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <Badge tone="signal">{rule.trigger_type}</Badge>
                      {rule.is_active ? <Badge tone="accent">active</Badge> : <Badge>paused</Badge>}
                    </div>
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-edge px-4 py-10 text-sm text-slate">
                  No automation rules configured yet.
                </div>
              )}
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Recent runs</h2>
              <Badge tone="signal">{runs.length} tracked</Badge>
            </div>
            <div className="mt-5 space-y-3">
              {runs.length ? (
                runs.map((run) => (
                  <div key={run.id} className="rounded-2xl border border-edge bg-mist p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-ink">{run.rule_name}</p>
                        <p className="mt-1 text-xs text-slate">
                          {run.resource_type} {run.resource_id} · {format(new Date(run.created_at), "MMM d, HH:mm")}
                        </p>
                      </div>
                      <Badge tone={run.status === "failed" ? "alert" : "signal"}>{run.status}</Badge>
                    </div>
                    {run.error_message ? (
                      <p className="mt-3 text-sm text-alert">{run.error_message}</p>
                    ) : null}
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-edge px-4 py-10 text-sm text-slate">
                  Runs will appear after a rule fires on document upload, keyword detection, or report generation.
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
