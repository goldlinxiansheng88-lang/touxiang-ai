import axios, { type AxiosError } from "axios";

import { FALLBACK_PUBLIC_CONFIG } from "@/data/fallbackConfig";
import { ALL_THEME_PACK_STYLE_ITEMS } from "@/data/themePackStyles";
import { installAxiosHtmlResponseHint } from "@/utils/axiosHtmlHint";
import type { Scene, StyleItem } from "@/types/aura";

export type { Scene, StyleItem } from "@/types/aura";

function normalizeBaseUrl(raw: unknown): string {
  const v = String(raw ?? "").trim();
  if (!v) return "";
  return v.endsWith("/") ? v.slice(0, -1) : v;
}

function coerceHttpsOnSecurePage(base: string): string {
  // If the SPA is served over HTTPS but API base is http://, browsers will block XHR (mixed content).
  // Upgrade to https:// automatically to reduce misconfiguration pain in production.
  if (typeof window === "undefined") return base;
  if (!base) return base;
  if (window.location.protocol !== "https:") return base;
  try {
    const u = new URL(base);
    if (u.protocol === "http:") {
      u.protocol = "https:";
      return u.toString().replace(/\/$/, "");
    }
  } catch {
    return base;
  }
  return base;
}

/** Production can set `VITE_API_BASE_URL=https://<your-backend-domain>` for cross-domain deploys. */
export const API_BASE_URL = coerceHttpsOnSecurePage(normalizeBaseUrl((import.meta as any).env?.VITE_API_BASE_URL));

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 60000,
});
installAxiosHtmlResponseHint(api);

/** Resolve an API path to a full URL (used for OAuth redirects). */
export function apiUrl(path: string): string {
  if (!path.startsWith("/")) path = `/${path}`;
  return API_BASE_URL ? `${API_BASE_URL}${path}` : `${window.location.origin}${path}`;
}

/** 优先使用 FastAPI 返回的 `detail`（503 时常为 Redis/Celery 说明），避免只显示 axios 默认英文。 */
export function getApiErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const ax = err as AxiosError<{ detail?: unknown }>;
    const raw = ax.response?.data;
    if (raw && typeof raw === "object" && raw !== null && "detail" in raw) {
      const det = (raw as { detail: unknown }).detail;
      if (typeof det === "string") return det;
      if (Array.isArray(det)) {
        return det
          .map((item) => {
            if (item && typeof item === "object" && item !== null && "msg" in item) {
              return String((item as { msg: unknown }).msg);
            }
            return JSON.stringify(item);
          })
          .join("; ");
      }
    }
    return ax.message || "Network error";
  }
  if (err instanceof Error) return err.message;
  return "Network error";
}

function mergeThemePackStyles(cfg: { scenes: Scene[]; styles: StyleItem[] }): {
  scenes: Scene[];
  styles: StyleItem[];
} {
  const have = new Set(cfg.styles.map((s) => s.id));
  const extra = ALL_THEME_PACK_STYLE_ITEMS.filter((s) => !have.has(s.id));
  if (extra.length === 0) return cfg;
  return { ...cfg, styles: [...cfg.styles, ...extra] };
}

export async function fetchConfig(): Promise<{ scenes: Scene[]; styles: StyleItem[] }> {
  try {
    const { data } = await api.get<{ scenes: Scene[]; styles: StyleItem[] }>("/api/config");
    return mergeThemePackStyles(data);
  } catch {
    return mergeThemePackStyles(FALLBACK_PUBLIC_CONFIG);
  }
}

export type ConfigRegistrySchemaItem = {
  key: string;
  label: string;
  group: string;
  description: string;
  readonly: boolean;
  is_secret: boolean;
  /** 填写类型提示：URL / Key / 数字 等，来自后端 VALUE_KIND_LABELS */
  value_kind?: string;
  /** 是否建议上线前必填（来自 ConfigEntry.required） */
  required?: boolean;
};

export async function fetchConfigRegistrySchema() {
  const { data } = await api.get<{
    groups: { id: string; label: string; hint?: string }[];
    items: ConfigRegistrySchemaItem[];
  }>("/api/meta/config-registry", { timeout: 12_000 });
  return data;
}

/** 数据库 / Redis / 主密钥脱敏预览，无需管理口令 */
export async function fetchInfrastructurePreview() {
  const { data } = await api.get<{
    database_url: string;
    redis_url: string;
    encryption_key: string;
  }>("/api/meta/infrastructure-preview");
  return data;
}

export type LocaleDetectResponse = {
  locale: string;
  country_code: string | null;
  source: string;
};

export async function fetchLocaleDetect() {
  const { data } = await api.get<LocaleDetectResponse>("/api/locale/detect");
  return data;
}

export type AuthMeResponse =
  | { authenticated: false }
  | {
      authenticated: true;
      user_id: string;
      email: string | null;
      display_name: string | null;
    };

export async function fetchAuthMe() {
  const { data } = await api.get<AuthMeResponse>("/api/auth/me");
  return data;
}

export type MyProfileResponse =
  | { authenticated: false; user: null }
  | {
      authenticated: boolean;
      user: {
        id: string;
        device_id: string;
        email: string | null;
        display_name: string | null;
        is_vip: boolean;
        vip_expires_at: string | null;
        created_at: string | null;
      };
    };

export async function fetchMyProfile() {
  const { data } = await api.get<MyProfileResponse>("/api/me");
  return data;
}

export type MyTaskRow = {
  id: string;
  status: string;
  scene: string;
  style: string;
  created_at: string | null;
};

export async function fetchMyTasks(params: { page?: number; page_size?: number }) {
  const { data } = await api.get<{ total: number; page: number; items: MyTaskRow[] }>("/api/me/tasks", { params });
  return data;
}

export async function registerEmail(email: string, password: string) {
  await api.post("/api/auth/email/register", { email, password });
}

export async function loginEmail(email: string, password: string) {
  await api.post("/api/auth/email/login", { email, password });
}

export async function logoutAuth() {
  await api.post("/api/auth/logout");
}

export async function createTask(
  file: File,
  scene: string,
  style: string,
  ref?: string | null,
  aspectRatio?: string | null,
  locale?: string | null,
  resolution?: number | null,
  removeBackground?: boolean | null,
) {
  const fd = new FormData();
  fd.append("image", file);
  fd.append("scene", scene);
  fd.append("style", style);
  fd.append("aspect_ratio", (aspectRatio || "auto").trim() || "auto");
  if (locale) fd.append("locale", String(locale).trim());
  if (resolution) fd.append("resolution", String(resolution));
  if (removeBackground != null) fd.append("remove_background", removeBackground ? "true" : "false");
  if (ref) fd.append("aff_ref", ref);
  const q = ref ? `?ref=${encodeURIComponent(ref)}` : "";
  const { data } = await api.post<{ task_id: string; status: string }>(`/api/tasks${q}`, fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getTask(taskId: string) {
  const { data } = await api.get<Record<string, unknown>>(`/api/tasks/${taskId}`);
  return data;
}

export type PaymentMethodsResponse = {
  methods: { id: string; enabled: boolean; label: string }[];
  checkout_amount_usd: string;
  checkout_amount_usdt: string;
  usdt_network: string;
  default_provider: string | null;
};

export type CreateCheckoutResponse =
  | { provider: "stripe"; checkout_url: string }
  | { provider: "creem"; checkout_url: string }
  | { provider: "lemon_squeezy"; checkout_url: string }
  | {
      provider: "usdt";
      checkout_url: null;
      usdt: { order_id: string; address: string; network: string; amount: string };
    };

export async function getPaymentMethods() {
  const { data } = await api.get<PaymentMethodsResponse>("/api/payments/methods");
  return data;
}

export async function createCheckout(taskId: string, provider?: string) {
  const { data } = await api.post<CreateCheckoutResponse>("/api/payments/create-checkout", {
    task_id: taskId,
    ...(provider ? { provider } : {}),
  });
  return data;
}
