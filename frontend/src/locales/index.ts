import enBase from "./en.base.json";
import jaPartial from "./ja.json";
import koPartial from "./ko.json";
import zhCNAdmin from "./zh-CN.admin.json";
import zhCNBase from "./zh-CN.base.json";
import zhTWPartial from "./zh-TW.json";

import { CLONE_PACKS } from "./clonePacks";
import { PACK_STYLE_I18N } from "./packStyleMessages";
import { deepMerge } from "./merge";

import type enShape from "./en.base.json";

type Messages = typeof enShape;

/**
 * 前台用 en.base；管理后台文案只维护 zh-CN.admin 一份。
 * 同时将 zh-CN.admin 并入 en 与各克隆语言包：若 locale 仍停在 en（时序/回退），fallback 也能解析 admin.*，避免界面显示键名。
 */
const enJson = deepMerge(
  deepMerge(enBase as Record<string, unknown>, zhCNAdmin as Record<string, unknown>),
  { packStyles: PACK_STYLE_I18N.en as unknown as Record<string, unknown> },
) as Messages;
const zhCN = deepMerge(
  deepMerge(zhCNBase as Record<string, unknown>, zhCNAdmin as Record<string, unknown>),
  { packStyles: PACK_STYLE_I18N["zh-CN"] as unknown as Record<string, unknown> },
) as Messages;

function cloneEn(): Messages {
  return JSON.parse(JSON.stringify(enJson)) as Messages;
}

/** 克隆英文后再合并完整前台包（与 en.base 同结构，含 styleItems、flow、loading 等） */
function cloneWithOverlay(localeCode: string): Messages {
  const pack = CLONE_PACKS[localeCode];
  if (!pack) return cloneEn();
  return deepMerge(cloneEn() as Record<string, unknown>, pack as Record<string, unknown>) as Messages;
}

/** 语言包：en/zh-CN 为完整 JSON；ja/ko/zh-TW 为英文底稿 + 补丁；其余 16 语为 clonePacks 全覆盖前台键 */
export const messages: Record<string, Messages> = {
  en: enJson,
  "zh-CN": zhCN,
  ja: deepMerge(enJson as Record<string, unknown>, jaPartial as Record<string, unknown>) as Messages,
  ko: deepMerge(enJson as Record<string, unknown>, koPartial as Record<string, unknown>) as Messages,
  "zh-TW": deepMerge(
    deepMerge(enJson as Record<string, unknown>, {
      packStyles: PACK_STYLE_I18N["zh-CN"] as unknown as Record<string, unknown>,
    }),
    zhTWPartial as Record<string, unknown>,
  ) as Messages,
  es: cloneWithOverlay("es"),
  fr: cloneWithOverlay("fr"),
  de: cloneWithOverlay("de"),
  "pt-BR": cloneWithOverlay("pt-BR"),
  ru: cloneWithOverlay("ru"),
  ar: cloneWithOverlay("ar"),
  hi: cloneWithOverlay("hi"),
  id: cloneWithOverlay("id"),
  th: cloneWithOverlay("th"),
  vi: cloneWithOverlay("vi"),
  tr: cloneWithOverlay("tr"),
  pl: cloneWithOverlay("pl"),
  nl: cloneWithOverlay("nl"),
  it: cloneWithOverlay("it"),
  uk: cloneWithOverlay("uk"),
  ms: cloneWithOverlay("ms"),
};
