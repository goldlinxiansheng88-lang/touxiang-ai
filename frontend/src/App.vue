<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { fetchLocaleDetect } from "@/api/client";
import { i18n } from "@/i18n";
import { LOCALE_USER_KEY, SUPPORTED_LOCALE_SET } from "@/locales/languages";
import { applyVantLocale } from "@/utils/localeAdmin";

const route = useRoute();
const { locale, t } = useI18n();

function applyLocale(code: string) {
  if (!SUPPORTED_LOCALE_SET.has(code)) return;
  locale.value = code;
  i18n.global.locale.value = code;
  document.documentElement.setAttribute("dir", code === "ar" ? "rtl" : "ltr");
  document.documentElement.setAttribute("lang", code.split("-")[0] || "en");
  applyVantLocale(code);
}

/** 前台页标题随语言变化；管理后台固定走路由守卫里的 zh-CN，用中文标题 */
watch(
  () => [route.path, locale.value] as const,
  () => {
    if (route.path.startsWith("/admin")) {
      document.title = t("meta.adminTitle");
      return;
    }
    document.title = t("meta.pageTitle");
  },
  { immediate: true },
);

watch(
  () => locale.value,
  (code) => {
    if (!route.path.startsWith("/admin")) {
      applyVantLocale(code);
    }
  },
);

onMounted(async () => {
  applyVantLocale(String(locale.value));

  /** 管理后台仅中文：勿用本地偏好 / IP 推断覆盖路由守卫已设的 zh-CN（否则会退回 en 且无 admin 文案） */
  if (route.path.startsWith("/admin")) {
    return;
  }

  const user = localStorage.getItem(LOCALE_USER_KEY)?.trim();
  if (user && SUPPORTED_LOCALE_SET.has(user)) {
    applyLocale(user);
    return;
  }
  try {
    const d = await fetchLocaleDetect();
    if (d.locale && SUPPORTED_LOCALE_SET.has(d.locale)) {
      applyLocale(d.locale);
    }
  } catch {
    /* 离线或后端不可用时保持默认 en */
  }
});
</script>
