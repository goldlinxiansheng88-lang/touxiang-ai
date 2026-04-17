import { Locale } from "vant";
import vantDeDE from "vant/es/locale/lang/de-DE";
import vantEnUS from "vant/es/locale/lang/en-US";
import vantEsES from "vant/es/locale/lang/es-ES";
import vantFrFR from "vant/es/locale/lang/fr-FR";
import vantJaJP from "vant/es/locale/lang/ja-JP";
import vantKoKR from "vant/es/locale/lang/ko-KR";
import vantPtBR from "vant/es/locale/lang/pt-BR";
import vantRuRU from "vant/es/locale/lang/ru-RU";
import vantZhCN from "vant/es/locale/lang/zh-CN";
import vantZhTW from "vant/es/locale/lang/zh-TW";

import { i18n } from "@/i18n";
import {
  ADMIN_FORCED_LOCALE,
  ADMIN_LOCALE_RESTORE_KEY,
  LOCALE_USER_KEY,
  SUPPORTED_LOCALE_SET,
} from "@/locales/languages";

/** 同步 html 根节点语言与排版方向 */
export function applyDomLocale(code: string): void {
  document.documentElement.setAttribute("dir", code === "ar" ? "rtl" : "ltr");
  document.documentElement.setAttribute("lang", code.split("-")[0] || "en");
}

/** Vant 组件（Toast 等）与当前界面语言对齐；无对应包时回退英文 */
export function applyVantLocale(code: string): void {
  const map: Record<string, [string, typeof vantEnUS]> = {
    "zh-CN": ["zh-CN", vantZhCN],
    "zh-TW": ["zh-TW", vantZhTW],
    ja: ["ja-JP", vantJaJP],
    ko: ["ko-KR", vantKoKR],
    es: ["es-ES", vantEsES],
    fr: ["fr-FR", vantFrFR],
    de: ["de-DE", vantDeDE],
    "pt-BR": ["pt-BR", vantPtBR],
    ru: ["ru-RU", vantRuRU],
  };
  const pair = map[code];
  if (pair) {
    Locale.use(pair[0], pair[1]);
  } else {
    Locale.use("en-US", vantEnUS);
  }
}

/** 进入 /admin：强制简体中文，并记住进入前的语言 */
export function lockAdminLocale(): void {
  const cur = String(i18n.global.locale.value);
  sessionStorage.setItem(ADMIN_LOCALE_RESTORE_KEY, cur);
  i18n.global.locale.value = ADMIN_FORCED_LOCALE;
  applyDomLocale(ADMIN_FORCED_LOCALE);
  applyVantLocale(ADMIN_FORCED_LOCALE);
}

/** 离开 /admin：恢复进入前语言或用户保存的语言 */
export function unlockAdminLocale(): void {
  const prev = sessionStorage.getItem(ADMIN_LOCALE_RESTORE_KEY);
  sessionStorage.removeItem(ADMIN_LOCALE_RESTORE_KEY);
  const saved = typeof localStorage !== "undefined" ? localStorage.getItem(LOCALE_USER_KEY)?.trim() : "";
  const next = (prev && SUPPORTED_LOCALE_SET.has(prev) ? prev : null) || (saved && SUPPORTED_LOCALE_SET.has(saved) ? saved : null) || "en";
  i18n.global.locale.value = next;
  applyDomLocale(next);
  applyVantLocale(next);
}
