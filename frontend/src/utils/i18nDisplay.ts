import { unref } from "vue";

/**
 * 从已注册的 locale 消息里按 id 取文案，顺序：当前语言 → en → 接口兜底。
 * 不经过 t()，避免与 te/t 解析差异；不依赖接口语言。
 */
export type GetLocaleMessage = (locale: string) => unknown;

function asLocaleCode(preferredLocale: unknown): string {
  const v = unref(preferredLocale as never);
  if (typeof v === "string" && v.length > 0) return v;
  if (typeof v === "number") return String(v);
  return "";
}

function readScene(msgs: Record<string, unknown>, sceneId: string): string | undefined {
  const scene = msgs.scene;
  if (!scene || typeof scene !== "object") return undefined;
  const v = (scene as Record<string, unknown>)[sceneId];
  return typeof v === "string" && v.trim() !== "" ? v : undefined;
}

function readStyleBlock(msgs: Record<string, unknown>, styleId: string): { name?: string; proof?: string } | undefined {
  const styleItems = msgs.styleItems;
  if (!styleItems || typeof styleItems !== "object") return undefined;
  const block = (styleItems as Record<string, unknown>)[styleId];
  if (!block || typeof block !== "object") return undefined;
  return block as { name?: string; proof?: string };
}

/** 主题包风格 tp_xx_NN：与 styleItems 并列的扁平 packStyles[id] */
function readPackStyleBlock(msgs: Record<string, unknown>, styleId: string): { name?: string; proof?: string } | undefined {
  const packStyles = msgs.packStyles;
  if (!packStyles || typeof packStyles !== "object") return undefined;
  const block = (packStyles as Record<string, unknown>)[styleId];
  if (!block || typeof block !== "object") return undefined;
  return block as { name?: string; proof?: string };
}

function walkLocales(
  getLocaleMessage: GetLocaleMessage,
  preferredLocale: unknown,
  read: (msgs: Record<string, unknown>) => string | undefined,
  apiFallback: string,
): string {
  const code = asLocaleCode(preferredLocale);
  for (const loc of [code, "en"]) {
    const raw = getLocaleMessage(loc);
    if (!raw || typeof raw !== "object") continue;
    const v = read(raw as Record<string, unknown>);
    if (v !== undefined) return v;
  }
  return apiFallback;
}

export function sceneLabel(
  getLocaleMessage: GetLocaleMessage,
  preferredLocale: unknown,
  sceneId: string,
  apiLabel: string,
): string {
  return walkLocales(getLocaleMessage, preferredLocale, (m) => readScene(m, sceneId), apiLabel);
}

export function styleItemName(
  getLocaleMessage: GetLocaleMessage,
  preferredLocale: unknown,
  styleId: string,
  apiDisplayName: string,
): string {
  return walkLocales(
    getLocaleMessage,
    preferredLocale,
    (m) => {
      const pb = readPackStyleBlock(m, styleId);
      const pn = pb?.name;
      if (typeof pn === "string" && pn.trim() !== "") return pn;
      const b = readStyleBlock(m, styleId);
      const n = b?.name;
      return typeof n === "string" && n.trim() !== "" ? n : undefined;
    },
    apiDisplayName,
  );
}

export function styleItemProof(
  getLocaleMessage: GetLocaleMessage,
  preferredLocale: unknown,
  styleId: string,
  apiSocialProof: string,
): string {
  return walkLocales(
    getLocaleMessage,
    preferredLocale,
    (m) => {
      const pb = readPackStyleBlock(m, styleId);
      const pp = pb?.proof;
      if (typeof pp === "string" && pp.trim() !== "") return pp;
      const b = readStyleBlock(m, styleId);
      const p = b?.proof;
      return typeof p === "string" && p.trim() !== "" ? p : undefined;
    },
    apiSocialProof,
  );
}
