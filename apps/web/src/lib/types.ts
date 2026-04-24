export type UserRole = "admin" | "user";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AuthProviderStatus {
  key: string;
  label: string;
  enabled: boolean;
}

export interface AuthProvidersResponse {
  providers: AuthProviderStatus[];
}

export interface MetricCard {
  label: string;
  value: string;
  trend?: string | null;
}

export interface ActivityItem {
  timestamp: string;
  title: string;
  description: string;
}

export interface DashboardOverview {
  metrics: MetricCard[];
  activity: ActivityItem[];
  power_bi_reports: PowerBIReportCard[];
}

export interface PowerBIReportCard {
  id: string;
  name: string;
  workspace_name?: string | null;
  report_url: string;
  description?: string | null;
}

export interface Tag {
  id: string;
  name: string;
  description: string | null;
  color: string | null;
  created_at: string;
}

export interface DocumentVersion {
  id: string;
  version_label: string | null;
  parser_name: string;
  extraction_notes: string | null;
  created_at: string;
}

export interface DocumentRecord {
  id: string;
  name: string;
  source_type: string;
  status: string;
  owner_name: string;
  owner_email: string;
  content_type: string | null;
  file_size_bytes: number;
  version_label: string | null;
  requires_review: boolean;
  review_reason: string | null;
  tags: Tag[];
  chunk_count: number;
  current_version: DocumentVersion | null;
  connector_name?: string | null;
  external_source_kind?: string | null;
  source_label?: string | null;
  source_path?: string | null;
  source_url?: string | null;
  created_at: string;
  updated_at: string;
  matched_excerpt?: string | null;
}

export interface DocumentListResponse {
  items: DocumentRecord[];
  total: number;
}

export interface Citation {
  chunk_id: string;
  document_id: string;
  document_name: string;
  version_label: string | null;
  citation_label: string;
  excerpt: string;
  score: number;
  connector_name?: string | null;
  external_source_kind?: string | null;
  source_label?: string | null;
  source_path?: string | null;
  source_url?: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  citations: Citation[];
  suggested_follow_ups: string[];
  created_at: string;
}

export interface ChatConversationSummary {
  id: string;
  title: string;
  updated_at: string;
  message_count: number;
}

export interface ChatConversation {
  id: string;
  title: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface SummaryTemplate {
  id: string;
  name: string;
  report_type: string;
  template_key: string;
  description: string | null;
  instructions_override?: string | null;
  is_default: boolean;
}

export interface PowerBIReportReference {
  id: string;
  name: string;
  description: string | null;
  workspace_name: string | null;
  workspace_id: string | null;
  report_id: string | null;
  report_url: string;
  embed_url: string | null;
  tags: string[];
  is_active: boolean;
  created_at: string;
}

export interface TeamsChannel {
  id: string;
  name: string;
  description: string | null;
  channel_label: string | null;
  delivery_type: string;
  has_webhook: boolean;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
}

export interface ReportRecord {
  id: string;
  title: string;
  report_type: string;
  status: string;
  template_name: string | null;
  top_themes: string[];
  risks: string[];
  action_items: string[];
  notable_updates: string[];
  linked_power_bi_reports: PowerBIReportReference[];
  markdown_content: string;
  html_content: string;
  created_at: string;
}

export interface ReportListResponse {
  items: ReportRecord[];
  total: number;
}

export interface ReportExport {
  filename: string;
  export_format: string;
  content_type: string;
  content: string;
}

export interface AutomationRule {
  id: string;
  name: string;
  description: string | null;
  trigger_type: string;
  condition_config: Record<string, unknown>;
  action_config: Array<Record<string, unknown>>;
  is_active: boolean;
  created_at: string;
}

export interface AutomationRun {
  id: string;
  rule_name: string;
  trigger_type: string;
  status: string;
  resource_type: string;
  resource_id: string;
  error_message: string | null;
  created_at: string;
  event_payload: Record<string, unknown>;
  result_payload: Record<string, unknown>;
}

export interface AuditLogRecord {
  id: string;
  event_type: string;
  resource_type: string;
  resource_id: string | null;
  message: string;
  actor_name: string | null;
  created_at: string;
  details: Record<string, unknown>;
}

export interface MicrosoftTenantSummary {
  id: string;
  tenant_id: string;
  display_name: string | null;
  primary_domain: string | null;
  last_seen_at: string;
}

export interface MicrosoftOverview {
  microsoft_auth_enabled: boolean;
  microsoft_graph_app_configured: boolean;
  configured_tenant_id: string;
  email_provider: string;
  teams_provider: string;
  microsoft_outlook_sender?: string | null;
  admin_emails: string[];
  admin_domains: string[];
  tenants: MicrosoftTenantSummary[];
  connector_count: number;
  teams_channel_count: number;
  power_bi_report_count: number;
  queued_job_count: number;
  default_teams_channel_name?: string | null;
}

export interface MicrosoftConnector {
  id: string;
  name: string;
  description: string | null;
  connector_type: string;
  status: string;
  is_active: boolean;
  microsoft_tenant_id: string;
  tenant_label: string;
  source_url: string | null;
  source_label: string;
  default_tags: string[];
  sync_frequency_minutes: number;
  last_synced_at: string | null;
  next_sync_at: string | null;
  last_error: string | null;
  document_count: number;
  synced_item_count: number;
  resolved_target: Record<string, unknown>;
  permissions_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface BackgroundJobRecord {
  id: string;
  job_type: string;
  status: string;
  resource_type: string;
  resource_id: string | null;
  created_by_name: string | null;
  scheduled_for: string | null;
  started_at: string | null;
  finished_at: string | null;
  attempt_count: number;
  payload: Record<string, unknown>;
  result_payload: Record<string, unknown>;
  error_message: string | null;
  created_at: string;
}
