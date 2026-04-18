import axios, { type AxiosError } from "axios";

import { FALLBACK_PUBLIC_CONFIG } from "@/data/fallbackConfig";
import { installAxiosHtmlResponseHint } from "@/utils/axiosHtmlHint";
import type { Scene, StyleItem } from "@/types/aura";

export type { Scene, StyleItem } from "@/types/aura";

export const api = axios.create({
  baseURL: "",
  withCredentials: true,
  timeout: 60000,
});
installAxiosHtmlResponseHint(api);

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

export async function fetchConfig(): Promise<{ scenes: Scene[]; styles: StyleItem[] }> {
  try {
    const { data } = await api.get<{ scenes: Scene[]; styles: StyleItem[] }>("/api/config");
    return data;
  } catch {
    return FALLBACK_PUBLIC_CONFIG;
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

export async function registerEmail(email: string, password: string) {
  await api.post("/api/auth/email/register", { email, password });
}

export async function loginEmail(email: string, password: string) {
  await api.post("/api/auth/email/login", { email, password });
}

export async function logoutAuth() {
  await api.post("/api/auth/logout");
}

export async function createTask(file: File, scene: string, style: string, ref?: string | null) {
  const fd = new FormData();
  fd.append("image", file);
  fd.append("scene", scene);
  fd.append("style", style);
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
