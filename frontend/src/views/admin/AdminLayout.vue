<template>
  <div
    class="relative min-h-screen overflow-hidden bg-zinc-200/90 font-sans antialiased"
  >
    <div
      class="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_-10%,rgba(220,38,38,0.1),transparent_50%)]"
      aria-hidden="true"
    />
    <div
      class="pointer-events-none fixed inset-0 bg-admin-noise opacity-40"
      aria-hidden="true"
    />

    <div class="relative z-10 flex min-h-screen w-full">
      <aside
        class="flex w-[15rem] shrink-0 flex-col border-r border-zinc-800/90 bg-gradient-to-b from-zinc-900 via-zinc-900 to-zinc-950 shadow-[6px_0_32px_-8px_rgba(0,0,0,0.35)] sm:w-[15.5rem]"
      >
        <div class="border-b border-white/5 px-4 pb-4 pt-5 sm:px-5">
          <p class="text-[10px] font-semibold uppercase tracking-[0.26em] text-zinc-500">{{ t("admin.layout.console") }}</p>
          <h1
            class="mt-2 bg-gradient-to-br from-white via-zinc-100 to-zinc-400 bg-clip-text text-lg font-bold tracking-tight text-transparent"
          >
            AuraShift
          </h1>
          <p class="mt-1 text-[11px] font-medium text-zinc-500">{{ t("admin.layout.subtitle") }}</p>
        </div>
        <nav class="flex-1 space-y-0.5 overflow-y-auto px-2.5 py-3 text-[13px] leading-snug sm:px-3">
          <router-link
            v-for="item in primaryNav"
            :key="item.name"
            :to="{ name: item.name }"
            class="block rounded-lg px-3 py-2.5 text-zinc-400 transition-colors duration-150 hover:bg-white/[0.05] hover:text-zinc-100"
            active-class="bg-white/[0.06] font-medium text-zinc-100"
          >
            {{ item.label }}
          </router-link>

          <router-link
            :to="{ name: 'admin-config' }"
            class="block rounded-lg px-3 py-2.5 text-zinc-400 transition-colors duration-150 hover:bg-white/[0.05] hover:text-zinc-100"
            active-class="bg-white/[0.06] font-medium text-zinc-100"
          >
            {{ t("admin.layout.navConfig") }}
          </router-link>

          <router-link
            :to="{ name: 'admin-logs' }"
            class="block rounded-lg px-3 py-2.5 text-zinc-400 transition-colors duration-150 hover:bg-white/[0.05] hover:text-zinc-100"
            active-class="bg-white/[0.06] font-medium text-zinc-100"
          >
            {{ t("admin.layout.navLogs") }}
          </router-link>
        </nav>
        <AdminSidebarAuth />
      </aside>

      <main class="min-w-0 flex-1 overflow-auto py-2.5 pl-2 pr-3 sm:py-3 sm:pl-3 sm:pr-5">
        <div
          class="admin-main-panel relative min-h-[calc(100vh-1.25rem)] w-full max-w-[min(100%,1680px)] overflow-hidden rounded-xl border border-zinc-300/60 bg-white p-4 shadow-admin-panel ring-1 ring-zinc-900/[0.04] sm:rounded-2xl sm:p-5 md:p-6"
        >
          <div
            class="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blush/50 to-transparent"
            aria-hidden="true"
          />
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import { i18n } from "@/i18n";
import { ADMIN_FORCED_LOCALE } from "@/locales/languages";
import { applyDomLocale, applyVantLocale } from "@/utils/localeAdmin";
import AdminSidebarAuth from "@/components/admin/AdminSidebarAuth.vue";
// 系统配置页保留，但已隐藏数据库相关项；基础设施仍建议在 Railway Variables 管理。

/** 首屏即渲染侧栏：必须在任何 t() 之前把 locale 钉在 zh-CN（避免仍处 en 时仅显示键名） */
i18n.global.locale.value = ADMIN_FORCED_LOCALE;
applyDomLocale(ADMIN_FORCED_LOCALE);
applyVantLocale(ADMIN_FORCED_LOCALE);

useRoute();
useRouter();
const { t } = useI18n();

const primaryNav = computed(() => [
  { name: "admin-dash" as const, label: t("admin.layout.navDash") },
  { name: "admin-users" as const, label: t("admin.layout.navUsers") },
  { name: "admin-orders" as const, label: t("admin.layout.navOrders") },
  { name: "admin-affiliates" as const, label: t("admin.layout.navAffiliates") },
]);

</script>
