import axios from "axios";

import { installAxiosHtmlResponseHint } from "@/utils/axiosHtmlHint";

const KEY = "aurashift_admin_token";

export const adminHttp = axios.create({
  baseURL: "",
  timeout: 60000,
});
installAxiosHtmlResponseHint(adminHttp);

adminHttp.interceptors.request.use((config) => {
  const t = localStorage.getItem(KEY)?.trim();
  if (t) {
    config.headers["X-Admin-Token"] = t;
  }
  return config;
});

export type AdminDashboard = {
  visitors_today: number;
  queued_tasks: number;
  success_rate: number;
  revenue_today_usd: number;
  compute_cost_usd: number;
};

export async function fetchAdminDashboard() {
  const { data } = await adminHttp.get<AdminDashboard>("/api/admin/dashboard");
  return data;
}

export type AdminUserRow = {
  id: string;
  device_id: string;
  ip_address: string | null;
  is_vip: boolean;
  vip_expires_at: string | null;
  created_at: string | null;
};

export async function fetchAdminUsers(params: { page?: number; page_size?: number }) {
  const { data } = await adminHttp.get<{ total: number; page: number; items: AdminUserRow[] }>(
    "/api/admin/users",
    { params },
  );
  return data;
}

export type AdminOrderRow = {
  id: string;
  task_id: string;
  user_id: string;
  amount: number;
  currency: string;
  status: string;
  affiliate_id: string | null;
  commission_earned: number | null;
  created_at: string | null;
  paid_at: string | null;
  payment_channel: string | null;
};

export async function fetchAdminOrders(params: {
  page?: number;
  page_size?: number;
  status?: string;
}) {
  const { data } = await adminHttp.get<{ total: number; page: number; items: AdminOrderRow[] }>(
    "/api/admin/orders",
    { params },
  );
  return data;
}

export async function markAdminOrderPaid(orderId: string) {
  const { data } = await adminHttp.post<{ ok: boolean; already_paid?: boolean }>(
    `/api/admin/orders/${orderId}/mark-paid`,
  );
  return data;
}

export type AdminAffiliateRow = {
  id: string;
  code: string;
  name: string | null;
  commission_rate: number;
  wallet_balance: number;
  total_earned: number;
  created_at: string | null;
};

export async function fetchAdminAffiliates() {
  const { data } = await adminHttp.get<{ items: AdminAffiliateRow[] }>("/api/admin/affiliates");
  return data;
}

export async function createAdminAffiliate(body: { name?: string; code?: string; commission_rate?: number }) {
  const { data } = await adminHttp.post<{ id: string; code: string; link: string }>("/api/admin/affiliates", body);
  return data;
}

export type AdminConfigItem = {
  key: string;
  label: string;
  group: string;
  value: string;
  value_type: string;
  description: string | null;
  is_encrypted: boolean;
  readonly: boolean;
  source: string;
  /** 与 schema 同步：填写 URL / Key 等提示 */
  value_kind?: string;
  /** 与 schema 同步：必填 / 选填 */
  required?: boolean;
};

export async function fetchAdminConfigs() {
  const { data } = await adminHttp.get<{
    items: AdminConfigItem[];
    groups: { id: string; label: string; hint?: string }[];
  }>("/api/admin/configs");
  return data;
}

export async function patchAdminConfigs(items: { key: string; value: string }[]) {
  const { data } = await adminHttp.patch<{
    ok: boolean;
    env_synced?: boolean;
    hint?: string;
    db_unavailable?: boolean;
    deferred_keys?: string[];
  }>("/api/admin/configs", { items });
  return data;
}

export async function postAdminConfigTestConnection(body: {
  key: string;
  value?: string;
  related?: Record<string, string>;
}) {
  const { data } = await adminHttp.post<{ ok: boolean; message: string }>(
    "/api/admin/configs/test-connection",
    body,
    { timeout: 120000 },
  );
  return data;
}

export type AdminRuntimeLogs = {
  lines: string[];
  path: string | null;
  hint: string | null;
};

export async function fetchAdminRuntimeLogs(params?: { tail_lines?: number }) {
  const { data } = await adminHttp.get<AdminRuntimeLogs>("/api/admin/runtime-logs", { params });
  return data;
}
