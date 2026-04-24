import type {
  AuditLogRecord,
  AuthProviderStatus,
  AuthProvidersResponse,
  BackgroundJobRecord,
  ChatConversation,
  ChatConversationSummary,
  DashboardOverview,
  DocumentListResponse,
  DocumentRecord,
  LoginResponse,
  AutomationRule,
  AutomationRun,
  MicrosoftConnector,
  MicrosoftOverview,
  PowerBIReportReference,
  ReportExport,
  ReportListResponse,
  ReportRecord,
  SummaryTemplate,
  Tag,
  TeamsChannel,
  User
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

const API_ORIGIN = API_BASE_URL.replace(/\/api\/v1$/, "");

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers = new Headers(options.headers ?? undefined);
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...Object.fromEntries(headers.entries())
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new ApiError(payload.detail ?? "Request failed", response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const authApi = {
  providers: async (): Promise<AuthProviderStatus[]> =>
    apiRequest<AuthProvidersResponse>("/auth/providers").then((response) => response.providers),
  login: async (email: string, password: string): Promise<LoginResponse> =>
    apiRequest<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),
  me: async (token: string): Promise<User> => apiRequest<User>("/auth/me", {}, token),
  microsoftStartUrl: (redirectTo = "/dashboard"): string =>
    `${API_ORIGIN}/api/v1/auth/microsoft/start?redirect_to=${encodeURIComponent(redirectTo)}`
};

export const dashboardApi = {
  overview: async (token: string): Promise<DashboardOverview> =>
    apiRequest<DashboardOverview>("/dashboard/overview", {}, token)
};

export const tagsApi = {
  list: async (token: string): Promise<Tag[]> => apiRequest<Tag[]>("/tags", {}, token),
  create: async (
    token: string,
    payload: { name: string; description?: string; color?: string }
  ): Promise<Tag> =>
    apiRequest<Tag>(
      "/tags",
      {
        method: "POST",
        body: JSON.stringify(payload)
      },
      token
    ),
  remove: async (token: string, tagId: string): Promise<void> => {
    await apiRequest<void>(
      `/tags/${tagId}`,
      {
        method: "DELETE"
      },
      token
    );
  }
};

export const documentsApi = {
  list: async (token: string, query?: string): Promise<DocumentListResponse> => {
    const suffix = query ? `?query=${encodeURIComponent(query)}` : "";
    return apiRequest<DocumentListResponse>(`/documents${suffix}`, {}, token);
  },
  upload: async (token: string, payload: FormData): Promise<DocumentRecord> =>
    apiRequest<DocumentRecord>(
      "/documents/upload",
      {
        method: "POST",
        body: payload
      },
      token
    ),
  remove: async (token: string, documentId: string): Promise<void> => {
    await apiRequest<void>(
      `/documents/${documentId}`,
      {
        method: "DELETE"
      },
      token
    );
  }
};

export const chatApi = {
  listConversations: async (token: string): Promise<ChatConversationSummary[]> =>
    apiRequest<ChatConversationSummary[]>("/chat/conversations", {}, token),
  createConversation: async (token: string, title?: string): Promise<ChatConversation> =>
    apiRequest<ChatConversation>(
      "/chat/conversations",
      {
        method: "POST",
        body: JSON.stringify({ title })
      },
      token
    ),
  getConversation: async (token: string, conversationId: string): Promise<ChatConversation> =>
    apiRequest<ChatConversation>(`/chat/conversations/${conversationId}`, {}, token),
  sendMessage: async (
    token: string,
    conversationId: string,
    content: string
  ): Promise<ChatConversation> =>
    apiRequest<ChatConversation>(
      `/chat/conversations/${conversationId}/messages`,
      {
        method: "POST",
        body: JSON.stringify({ content })
      },
      token
    )
};

export const reportsApi = {
  listTemplates: async (token: string): Promise<SummaryTemplate[]> =>
    apiRequest<SummaryTemplate[]>("/reports/templates", {}, token),
  listReports: async (token: string): Promise<ReportListResponse> =>
    apiRequest<ReportListResponse>("/reports", {}, token),
  listPowerBIReferences: async (token: string): Promise<PowerBIReportReference[]> =>
    apiRequest<PowerBIReportReference[]>("/reports/power-bi-references", {}, token),
  listTeamsChannels: async (token: string): Promise<TeamsChannel[]> =>
    apiRequest<TeamsChannel[]>("/reports/teams-channels", {}, token),
  generate: async (
    token: string,
    payload: {
      report_type: string;
      template_id?: string | null;
      document_ids: string[];
      power_bi_report_ids?: string[];
      notes?: string;
    }
  ): Promise<ReportRecord> =>
    apiRequest<ReportRecord>(
      "/reports/generate",
      {
        method: "POST",
        body: JSON.stringify(payload)
      },
      token
    ),
  deliverEmail: async (
    token: string,
    reportId: string,
    payload: { recipients: string[]; subject?: string | null }
  ): Promise<BackgroundJobRecord> =>
    apiRequest<BackgroundJobRecord>(
      `/reports/${reportId}/deliver/email`,
      {
        method: "POST",
        body: JSON.stringify(payload)
      },
      token
    ),
  deliverTeams: async (
    token: string,
    reportId: string,
    payload: { channel_id?: string | null }
  ): Promise<BackgroundJobRecord> =>
    apiRequest<BackgroundJobRecord>(
      `/reports/${reportId}/deliver/teams`,
      {
        method: "POST",
        body: JSON.stringify(payload)
      },
      token
    ),
  export: async (
    token: string,
    reportId: string,
    exportFormat: "markdown" | "html"
  ): Promise<ReportExport> =>
    apiRequest<ReportExport>(
      `/reports/${reportId}/export?export_format=${exportFormat}`,
      {},
      token
    )
};

export const automationsApi = {
  listRules: async (token: string): Promise<AutomationRule[]> =>
    apiRequest<AutomationRule[]>("/automations/rules", {}, token),
  listRuns: async (token: string): Promise<AutomationRun[]> =>
    apiRequest<AutomationRun[]>("/automations/runs", {}, token),
  createRule: async (
    token: string,
    payload: {
      name: string;
      description?: string;
      trigger_type: string;
      condition_config: Record<string, unknown>;
      action_config: Array<Record<string, unknown>>;
      is_active: boolean;
    }
  ): Promise<AutomationRule> =>
    apiRequest<AutomationRule>(
      "/automations/rules",
      {
        method: "POST",
        body: JSON.stringify(payload)
      },
      token
    ),
  updateRule: async (
    token: string,
    ruleId: string,
    payload: {
      name: string;
      description?: string;
      trigger_type: string;
      condition_config: Record<string, unknown>;
      action_config: Array<Record<string, unknown>>;
      is_active: boolean;
    }
  ): Promise<AutomationRule> =>
    apiRequest<AutomationRule>(
      `/automations/rules/${ruleId}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload)
      },
      token
    )
};

export const adminApi = {
  listAuditLogs: async (token: string): Promise<AuditLogRecord[]> =>
    apiRequest<AuditLogRecord[]>("/admin/audit-logs", {}, token),
  microsoftOverview: async (token: string): Promise<MicrosoftOverview> =>
    apiRequest<MicrosoftOverview>("/admin/microsoft/overview", {}, token),
  listMicrosoftConnectors: async (token: string): Promise<MicrosoftConnector[]> =>
    apiRequest<MicrosoftConnector[]>("/admin/microsoft/connectors", {}, token),
  createMicrosoftConnector: async (
    token: string,
    payload: {
      name: string;
      description?: string | null;
      connector_type: string;
      microsoft_tenant_id?: string | null;
      site_hostname?: string | null;
      site_path?: string | null;
      drive_name?: string | null;
      user_principal_name?: string | null;
      folder_path?: string | null;
      default_tags: string[];
      sync_frequency_minutes: number;
      is_active: boolean;
      run_initial_sync: boolean;
    }
  ): Promise<MicrosoftConnector> =>
    apiRequest<MicrosoftConnector>(
      "/admin/microsoft/connectors",
      {
        method: "POST",
        body: JSON.stringify(payload)
      },
      token
    ),
  updateMicrosoftConnector: async (
    token: string,
    connectorId: string,
    payload: {
      name?: string | null;
      description?: string | null;
      default_tags?: string[] | null;
      sync_frequency_minutes?: number | null;
      is_active?: boolean | null;
    }
  ): Promise<MicrosoftConnector> =>
    apiRequest<MicrosoftConnector>(
      `/admin/microsoft/connectors/${connectorId}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload)
      },
      token
    ),
  syncMicrosoftConnector: async (token: string, connectorId: string): Promise<BackgroundJobRecord> =>
    apiRequest<BackgroundJobRecord>(
      `/admin/microsoft/connectors/${connectorId}/sync`,
      {
        method: "POST"
      },
      token
    ),
  listBackgroundJobs: async (token: string): Promise<BackgroundJobRecord[]> =>
    apiRequest<BackgroundJobRecord[]>("/admin/microsoft/jobs", {}, token),
  runDueMicrosoftJobs: async (token: string): Promise<BackgroundJobRecord[]> =>
    apiRequest<BackgroundJobRecord[]>(
      "/admin/microsoft/jobs/run-due",
      {
        method: "POST"
      },
      token
    ),
  listTeamsChannels: async (token: string): Promise<TeamsChannel[]> =>
    apiRequest<TeamsChannel[]>("/admin/microsoft/teams/channels", {}, token),
  createTeamsChannel: async (
    token: string,
    payload: {
      name: string;
      description?: string | null;
      channel_label?: string | null;
      delivery_type: string;
      webhook_url?: string | null;
      is_active: boolean;
      is_default: boolean;
    }
  ): Promise<TeamsChannel> =>
    apiRequest<TeamsChannel>(
      "/admin/microsoft/teams/channels",
      {
        method: "POST",
        body: JSON.stringify(payload)
      },
      token
    ),
  updateTeamsChannel: async (
    token: string,
    channelId: string,
    payload: {
      name: string;
      description?: string | null;
      channel_label?: string | null;
      delivery_type: string;
      webhook_url?: string | null;
      is_active: boolean;
      is_default: boolean;
    }
  ): Promise<TeamsChannel> =>
    apiRequest<TeamsChannel>(
      `/admin/microsoft/teams/channels/${channelId}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload)
      },
      token
    ),
  listPowerBIReports: async (token: string): Promise<PowerBIReportReference[]> =>
    apiRequest<PowerBIReportReference[]>("/admin/microsoft/power-bi/reports", {}, token),
  createPowerBIReport: async (
    token: string,
    payload: {
      name: string;
      description?: string | null;
      workspace_name?: string | null;
      workspace_id?: string | null;
      report_id?: string | null;
      report_url: string;
      embed_url?: string | null;
      tags: string[];
      is_active: boolean;
    }
  ): Promise<PowerBIReportReference> =>
    apiRequest<PowerBIReportReference>(
      "/admin/microsoft/power-bi/reports",
      {
        method: "POST",
        body: JSON.stringify(payload)
      },
      token
    ),
  updatePowerBIReport: async (
    token: string,
    reportId: string,
    payload: {
      name: string;
      description?: string | null;
      workspace_name?: string | null;
      workspace_id?: string | null;
      report_id?: string | null;
      report_url: string;
      embed_url?: string | null;
      tags: string[];
      is_active: boolean;
    }
  ): Promise<PowerBIReportReference> =>
    apiRequest<PowerBIReportReference>(
      `/admin/microsoft/power-bi/reports/${reportId}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload)
      },
      token
    ),
  updateTemplate: async (
    token: string,
    templateId: string,
    payload: {
      description?: string | null;
      instructions_override?: string | null;
      is_default?: boolean | null;
    }
  ): Promise<SummaryTemplate> =>
    apiRequest<SummaryTemplate>(
      `/admin/summary-templates/${templateId}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload)
      },
      token
    )
};

export { ApiError };
