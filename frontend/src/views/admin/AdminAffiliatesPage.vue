<template>
  <div>
    <div class="mb-8 border-b border-stone-200/80 pb-6">
      <h1 class="text-xl font-bold tracking-tight text-stone-950">{{ t("admin.affiliates.title") }}</h1>
      <p class="mt-1 text-xs text-stone-500">
        <code class="rounded bg-stone-100 px-1.5 py-0.5 font-mono text-[11px] text-stone-700">GET /api/admin/affiliates</code>
      </p>
    </div>

    <div
      v-if="!auth.token"
      class="mb-6 rounded-xl border border-amber-200/80 bg-gradient-to-r from-amber-50 to-amber-50/30 px-4 py-3 text-sm text-amber-950 shadow-admin-sm"
      v-html="t('admin.affiliates.authBanner')"
    />

    <template v-else>
      <div class="mb-6 max-w-xl space-y-4 rounded-2xl border border-stone-200/70 bg-gradient-to-b from-white to-stone-50/50 p-5 text-sm shadow-admin-sm">
        <p class="text-[13px] font-semibold text-stone-900">{{ t("admin.affiliates.createTitle") }}</p>
        <div class="grid gap-3 sm:grid-cols-2">
          <label class="text-stone-600"
            >{{ t("admin.affiliates.name") }}
            <input
              v-model="createName"
              type="text"
              class="mt-1.5 w-full rounded-xl border border-stone-200 bg-white px-3 py-2 text-stone-900 shadow-sm focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
              :placeholder="t('admin.affiliates.placeholderOptional')"
          /></label>
          <label class="text-stone-600"
            >{{ t("admin.affiliates.code") }}
            <input
              v-model="createCode"
              type="text"
              class="mt-1.5 w-full rounded-xl border border-stone-200 bg-white px-3 py-2 text-stone-900 shadow-sm focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
              :placeholder="t('admin.affiliates.placeholderRandom')"
          /></label>
          <label class="sm:col-span-2 text-stone-600"
            >{{ t("admin.affiliates.rate") }}
            <input
              v-model.number="createRate"
              type="number"
              step="0.01"
              min="0"
              max="1"
              class="mt-1.5 w-full max-w-xs rounded-xl border border-stone-200 bg-white px-3 py-2 text-stone-900 shadow-sm focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
          /></label>
        </div>
        <button
          type="button"
          class="rounded-xl bg-stone-900 px-5 py-2.5 text-sm font-medium text-white shadow-admin-sm transition hover:bg-stone-800 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="creating"
          @click="createAff"
        >
          {{ creating ? t("admin.affiliates.submitting") : t("admin.affiliates.submit") }}
        </button>
        <p v-if="createMsg" class="text-xs text-stone-600">{{ createMsg }}</p>
      </div>
      <div class="mb-6">
        <button
          type="button"
          class="rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-stone-700 shadow-sm transition hover:bg-stone-50"
          @click="reload"
        >
          {{ t("admin.affiliates.refreshList") }}
        </button>
      </div>
    </template>

    <div v-if="loading" class="py-12 text-center text-sm text-stone-500">{{ t("common.loading") }}</div>
    <div
      v-else-if="error"
      class="mb-6 rounded-xl border border-red-200/80 bg-red-50 px-4 py-3 text-sm text-red-800 shadow-admin-sm whitespace-pre-wrap"
    >
      {{ error }}
    </div>

    <div v-else class="overflow-hidden rounded-2xl border border-stone-200/70 bg-white shadow-admin-sm">
      <table class="min-w-full text-left text-sm">
        <thead class="border-b border-stone-200/80 bg-stone-50/90 text-[11px] font-semibold uppercase tracking-wide text-stone-500">
          <tr>
            <th class="px-4 py-3 font-medium">{{ t("admin.affiliates.colCode") }}</th>
            <th class="px-4 py-3 font-medium">{{ t("admin.affiliates.colName") }}</th>
            <th class="px-4 py-3 font-medium">{{ t("admin.affiliates.colRate") }}</th>
            <th class="px-4 py-3 font-medium">{{ t("admin.affiliates.colBalance") }}</th>
            <th class="px-4 py-3 font-medium">{{ t("admin.affiliates.colCreated") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in items"
            :key="row.id"
            class="border-b border-stone-100/90 transition hover:bg-stone-50/80"
          >
            <td class="px-4 py-3 font-mono font-semibold text-stone-900">{{ row.code }}</td>
            <td class="px-4 py-3">{{ row.name ?? "—" }}</td>
            <td class="px-4 py-3">{{ row.commission_rate }}</td>
            <td class="px-4 py-3 text-stone-800">{{ row.wallet_balance }} / {{ row.total_earned }}</td>
            <td class="px-4 py-3 text-xs text-stone-600">{{ row.created_at ?? "—" }}</td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="5" class="px-4 py-12 text-center text-sm text-stone-500">{{ t("common.noData") }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useI18n } from "vue-i18n";

import { createAdminAffiliate, fetchAdminAffiliates, type AdminAffiliateRow } from "@/api/adminClient";
import { useAdminAuthStore } from "@/stores/adminAuth";

const { t } = useI18n();
const auth = useAdminAuthStore();
const loading = ref(false);
const error = ref("");
const items = ref<AdminAffiliateRow[]>([]);
const creating = ref(false);
const createName = ref("");
const createCode = ref("");
const createRate = ref(0.3);
const createMsg = ref("");

function formatErr(e: unknown): string {
  const ax = e as { response?: unknown; code?: string; message?: string };
  if (!ax.response && (ax.code === "ERR_NETWORK" || /Network Error/i.test(ax.message ?? ""))) {
    return t("admin.errors.networkNoResponse");
  }
  if (typeof e === "object" && e !== null && "response" in e) {
    const r = (e as {
      response?: { status?: number; data?: { detail?: unknown }; headers?: Record<string, string> };
    }).response;
    if (r?.status === 401) {
      return t("admin.affiliates.err401");
    }
    const raw = r?.data?.detail;
    if (raw !== undefined && raw !== null) {
      if (Array.isArray(raw)) {
        return raw.map((x: { msg?: string }) => x?.msg ?? JSON.stringify(x)).join("；");
      }
      return String(raw);
    }
    if (r?.status === 503) {
      return t("admin.errors.e503");
    }
    if (r?.status === 500) {
      const ct = r.headers?.["content-type"] ?? "";
      const hint =
        ct.includes("application/json") || !ct ? t("admin.errors.e500json") : t("admin.errors.e500html");
      return t("admin.errors.e500body", { hint });
    }
  }
  const msg =
    typeof e === "object" && e !== null && "message" in e
      ? String((e as { message?: string }).message ?? "")
      : "";
  if (/timeout of \d+ms exceeded|ECONNABORTED|timeout/i.test(msg)) {
    return t("admin.errors.timeoutHint", { msg });
  }
  if (e instanceof Error) return e.message;
  return t("admin.errors.requestFailed");
}

async function reload() {
  if (!auth.token) {
    items.value = [];
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    const data = await fetchAdminAffiliates();
    items.value = data.items;
  } catch (e) {
    error.value = formatErr(e);
    items.value = [];
  } finally {
    loading.value = false;
  }
}

async function createAff() {
  if (!auth.token) return;
  creating.value = true;
  createMsg.value = "";
  try {
    const res = await createAdminAffiliate({
      name: createName.value || undefined,
      code: createCode.value || undefined,
      commission_rate: createRate.value,
    });
    createMsg.value = t("admin.affiliates.createdOk", { code: res.code, link: res.link });
    createName.value = "";
    createCode.value = "";
    await reload();
  } catch (e) {
    createMsg.value = formatErr(e);
  } finally {
    creating.value = false;
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
