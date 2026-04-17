<template>
  <div>
    <div class="mb-8 border-b border-stone-200/80 pb-6">
      <h1 class="text-xl font-bold tracking-tight text-stone-950">{{ t("admin.dashboard.title") }}</h1>
      <p class="mt-1 text-xs text-stone-500">
        <code class="rounded bg-stone-100 px-1.5 py-0.5 font-mono text-[11px] text-stone-700">GET /api/admin/dashboard</code>
        {{ t("admin.dashboard.hintHeaders") }}
        <code class="rounded bg-stone-100 px-1.5 py-0.5 font-mono text-[11px] text-stone-700">X-Admin-Token</code>
      </p>
    </div>

    <div
      v-if="!auth.token"
      class="mb-6 rounded-xl border border-amber-200/80 bg-gradient-to-r from-amber-50 to-amber-50/30 px-4 py-3 text-sm text-amber-950 shadow-admin-sm"
      v-html="t('admin.dashboard.authBanner')"
    />

    <div v-if="loading" class="py-12 text-center text-sm text-stone-500">{{ t("common.loading") }}</div>
    <div
      v-else-if="error"
      class="mb-6 rounded-xl border border-red-200/80 bg-red-50 px-4 py-3 text-sm text-red-800 shadow-admin-sm whitespace-pre-wrap"
    >
      {{ error }}
    </div>

    <div v-else class="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-5 lg:gap-4">
      <div
        v-for="(card, i) in statCards"
        :key="i"
        class="group relative overflow-hidden rounded-2xl border border-stone-200/60 bg-gradient-to-br from-white to-stone-50/90 p-4 shadow-admin-sm transition before:pointer-events-none before:absolute before:inset-x-0 before:top-0 before:h-px before:bg-gradient-to-r before:from-blush/50 before:via-transparent before:to-transparent hover:border-stone-300/70 hover:shadow-md"
      >
        <div class="absolute right-0 top-0 h-20 w-20 rounded-bl-full bg-gradient-to-br from-blush/[0.07] to-transparent transition group-hover:from-blush/[0.12]" />
        <p class="relative text-[11px] font-medium uppercase tracking-wide text-stone-500">{{ card.label }}</p>
        <p class="relative mt-2 text-2xl font-semibold tabular-nums tracking-tight text-stone-900">{{ card.value }}</p>
      </div>
    </div>

    <button
      v-if="auth.token && !loading"
      type="button"
      class="mt-8 rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-stone-700 shadow-sm transition hover:bg-stone-50"
      @click="reload"
    >
      {{ t("admin.dashboard.refresh") }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useI18n } from "vue-i18n";

import { fetchAdminDashboard, type AdminDashboard } from "@/api/adminClient";
import { useAdminAuthStore } from "@/stores/adminAuth";

const { t } = useI18n();
const auth = useAdminAuthStore();
const loading = ref(false);
const error = ref("");
const dash = ref<AdminDashboard | null>(null);

const statCards = computed(() => {
  const d = dash.value;
  return [
    { label: t("admin.dashboard.metricTasks"), value: d ? String(d.visitors_today) : "—" },
    { label: t("admin.dashboard.metricQueued"), value: d ? String(d.queued_tasks) : "—" },
    { label: t("admin.dashboard.metricSuccess"), value: d ? (d.success_rate * 100).toFixed(1) + "%" : "—" },
    { label: t("admin.dashboard.metricRevenue"), value: d ? d.revenue_today_usd.toFixed(2) : "—" },
    { label: t("admin.dashboard.metricCost"), value: d ? d.compute_cost_usd.toFixed(2) : "—" },
  ];
});

function formatErr(e: unknown): string {
  if (typeof e === "object" && e !== null && "response" in e) {
    const r = (e as { response?: { status?: number; data?: { detail?: string } } }).response;
    if (r?.status === 401) return t("admin.dashboard.err401");
    if (r?.data?.detail) return String(r.data.detail);
  }
  if (e instanceof Error) return e.message;
  return t("admin.dashboard.errConnect");
}

async function reload() {
  if (!auth.token) {
    dash.value = null;
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    dash.value = await fetchAdminDashboard();
  } catch (e) {
    error.value = formatErr(e);
    dash.value = null;
  } finally {
    loading.value = false;
  }
}

function onTokenChanged() {
  auth.loadFromStorage();
  reload();
}

onMounted(() => {
  reload();
  window.addEventListener("aurashift-admin-token-changed", onTokenChanged);
});

onUnmounted(() => {
  window.removeEventListener("aurashift-admin-token-changed", onTokenChanged);
});
</script>
