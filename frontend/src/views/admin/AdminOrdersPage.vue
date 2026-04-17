<template>
  <div>
    <div class="mb-8 border-b border-stone-200/80 pb-6">
      <h1 class="text-xl font-bold tracking-tight text-stone-950">{{ t("admin.orders.title") }}</h1>
      <p class="mt-1 text-xs text-stone-500">
        <code class="rounded bg-stone-100 px-1.5 py-0.5 font-mono text-[11px] text-stone-700">GET /api/admin/orders</code>
      </p>
    </div>

    <div
      v-if="!auth.token"
      class="mb-6 rounded-xl border border-amber-200/80 bg-gradient-to-r from-amber-50 to-amber-50/30 px-4 py-3 text-sm text-amber-950 shadow-admin-sm"
      v-html="t('admin.orders.authBanner')"
    />

    <div v-else class="mb-6 flex flex-wrap items-center gap-3">
      <label class="text-sm font-medium text-stone-600">{{ t("admin.orders.statusLabel") }}</label>
      <select
        v-model="statusFilter"
        class="rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm text-stone-800 shadow-sm focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
        @change="onFilterChange"
      >
        <option value="">{{ t("admin.orders.statusAll") }}</option>
        <option value="PENDING">PENDING</option>
        <option value="PAID">PAID</option>
      </select>
      <button
        type="button"
        class="rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-stone-700 shadow-sm transition hover:bg-stone-50"
        @click="reload"
      >
        {{ t("admin.orders.refresh") }}
      </button>
    </div>

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
            <th class="px-4 py-3 font-medium">{{ t("admin.orders.colOrderId") }}</th>
            <th class="px-4 py-3 font-medium">{{ t("admin.orders.colAmount") }}</th>
            <th class="px-4 py-3 font-medium">{{ t("admin.orders.colStatus") }}</th>
            <th class="px-4 py-3 font-medium">{{ t("admin.orders.colTaskId") }}</th>
            <th class="px-4 py-3 font-medium">{{ t("admin.orders.colUserId") }}</th>
            <th class="px-4 py-3 font-medium">{{ t("admin.orders.colTimes") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in items"
            :key="row.id"
            class="border-b border-stone-100/90 transition hover:bg-stone-50/80"
          >
            <td class="px-4 py-3 font-mono text-xs text-stone-800">{{ row.id }}</td>
            <td class="px-4 py-3 font-medium text-stone-900">{{ row.amount }} {{ row.currency }}</td>
            <td class="px-4 py-3">{{ row.status }}</td>
            <td class="max-w-[120px] truncate px-4 py-3 font-mono text-xs" :title="row.task_id">{{ row.task_id }}</td>
            <td class="max-w-[120px] truncate px-4 py-3 font-mono text-xs" :title="row.user_id">{{ row.user_id }}</td>
            <td class="px-4 py-3 text-xs text-stone-600">
              {{ row.created_at ?? "—" }}
              <span v-if="row.paid_at" class="mt-0.5 block text-stone-500">{{ t("common.paidAt", { time: row.paid_at }) }}</span>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="6" class="px-4 py-12 text-center text-sm text-stone-500">{{ t("common.noData") }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="total > 0" class="mt-6 flex flex-wrap items-center justify-between gap-3 text-sm text-stone-600">
      <span>{{ t("common.totalPage", { total, page }) }}</span>
      <div class="flex gap-2">
        <button
          type="button"
          class="rounded-xl border border-stone-200 bg-white px-3 py-1.5 text-sm font-medium shadow-sm transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="page <= 1"
          @click="page--; reload()"
        >
          {{ t("common.prev") }}
        </button>
        <button
          type="button"
          class="rounded-xl border border-stone-200 bg-white px-3 py-1.5 text-sm font-medium shadow-sm transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="page * pageSize >= total"
          @click="page++; reload()"
        >
          {{ t("common.next") }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useI18n } from "vue-i18n";

import { fetchAdminOrders, type AdminOrderRow } from "@/api/adminClient";
import { useAdminAuthStore } from "@/stores/adminAuth";

const { t } = useI18n();
const auth = useAdminAuthStore();
const loading = ref(false);
const error = ref("");
const items = ref<AdminOrderRow[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 20;
const statusFilter = ref("");

function formatErr(e: unknown): string {
  if (typeof e === "object" && e !== null && "response" in e) {
    const r = (e as { response?: { status?: number; data?: { detail?: string } } }).response;
    if (r?.status === 401) return t("admin.orders.err401");
    if (r?.data?.detail) return String(r.data.detail);
  }
  if (e instanceof Error) return e.message;
  return t("common.requestFailed");
}

function onFilterChange() {
  page.value = 1;
  reload();
}

async function reload() {
  if (!auth.token) {
    items.value = [];
    total.value = 0;
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    const data = await fetchAdminOrders({
      page: page.value,
      page_size: pageSize,
      status: statusFilter.value || undefined,
    });
    items.value = data.items;
    total.value = data.total;
  } catch (e) {
    error.value = formatErr(e);
    items.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

function onTokenChanged() {
  auth.loadFromStorage();
  page.value = 1;
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
