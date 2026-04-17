import { createI18n } from "vue-i18n";

import { messages } from "@/locales";

export const i18n = createI18n({
  legacy: false,
  locale: "en",
  fallbackLocale: "en",
  globalInjection: true,
  messages: messages as Record<string, Record<string, unknown>>,
});

export type AppLocale = keyof typeof messages;
