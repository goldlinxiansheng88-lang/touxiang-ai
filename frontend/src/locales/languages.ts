/** 用户手动选择语言后写入 localStorage；有值时不再用 IP 推断 */
export const LOCALE_USER_KEY = "aurashift_locale_user_choice";

/** 进入管理后台前暂存界面语言，离开 /admin 时恢复（管理后台固定简体中文） */
export const ADMIN_LOCALE_RESTORE_KEY = "aurashift_locale_before_admin";

/** 管理后台固定使用的语言 */
export const ADMIN_FORCED_LOCALE = "zh-CN" as const;

/** 与 i18n locale 代码一致；展示名为各语言自称 */
export const LANGUAGE_OPTIONS: { code: string; label: string }[] = [
  { code: "en", label: "English" },
  { code: "zh-CN", label: "简体中文" },
  { code: "zh-TW", label: "繁體中文" },
  { code: "ja", label: "日本語" },
  { code: "ko", label: "한국어" },
  { code: "es", label: "Español" },
  { code: "fr", label: "Français" },
  { code: "de", label: "Deutsch" },
  { code: "pt-BR", label: "Português (Brasil)" },
  { code: "ru", label: "Русский" },
  { code: "ar", label: "العربية" },
  { code: "hi", label: "हिन्दी" },
  { code: "id", label: "Bahasa Indonesia" },
  { code: "th", label: "ไทย" },
  { code: "vi", label: "Tiếng Việt" },
  { code: "tr", label: "Türkçe" },
  { code: "pl", label: "Polski" },
  { code: "nl", label: "Nederlands" },
  { code: "it", label: "Italiano" },
  { code: "uk", label: "Українська" },
  { code: "ms", label: "Bahasa Melayu" },
];

export const SUPPORTED_LOCALE_SET = new Set(LANGUAGE_OPTIONS.map((o) => o.code));
