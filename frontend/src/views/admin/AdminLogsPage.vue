<template>
  <div>
    <div class="mb-8 border-b border-stone-200/80 pb-6">
      <h1 class="text-xl font-bold tracking-tight text-stone-950">{{ t("admin.logs.title") }}</h1>
      <p class="mt-1 text-xs text-stone-500">
        <code class="rounded bg-stone-100 px-1.5 py-0.5 font-mono text-[11px] text-stone-700">GET /api/admin/runtime-logs/stream</code>
        {{ t("admin.logs.hintSse") }}
        <code class="rounded bg-stone-100 px-1.5 py-0.5 font-mono text-[11px] text-stone-700">GET /api/admin/runtime-logs</code>
      </p>
    </div>

    <div
      v-if="!auth.token"
      class="mb-6 rounded-xl border border-amber-200/80 bg-gradient-to-r from-amber-50 to-amber-50/30 px-4 py-3 text-sm text-amber-950 shadow-admin-sm"
      v-html="t('admin.logs.authBanner')"
    />

    <div v-else class="mb-4 flex flex-wrap items-center gap-3">
      <label class="flex items-center gap-2 text-sm text-stone-700">
        <input v-model="liveStream" type="checkbox" class="rounded border-stone-300" />
        {{ t("admin.logs.modeLive") }}
      </label>
      <label v-if="!liveStream" class="flex items-center gap-2 text-sm text-stone-700">
        <input v-model="autoRefresh" type="checkbox" class="rounded border-stone-300" />
        {{ t("admin.logs.modePoll") }}
      </label>
      <button
        type="button"
        class="rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-stone-700 shadow-sm transition hover:bg-stone-50 disabled:opacity-50"
        :disabled="loading"
        @click="loadOnce"
      >
        {{ loading ? t("admin.logs.loading") : t("admin.logs.refreshSnap") }}
      </button>
      <span v-if="liveStream && streamConnected" class="text-xs font-medium text-emerald-700">{{ t("admin.logs.connected") }}</span>
      <span v-else-if="liveStream && auth.token" class="text-xs text-stone-500">{{ t("admin.logs.connecting") }}</span>
    </div>

    <p v-if="hint" class="mb-3 rounded-lg border border-amber-200/80 bg-amber-50/90 px-3 py-2 text-xs leading-relaxed text-amber-950">
      {{ hint }}
    </p>
    <p v-if="logPath" class="mb-2 break-all font-mono text-[11px] text-stone-500">
      {{ t("admin.logs.currentFile") }}<span class="text-stone-800">{{ logPath }}</span>
    </p>

    <div
      v-if="error"
      class="mb-4 rounded-xl border border-red-200/80 bg-red-50 px-4 py-3 text-sm text-red-800 shadow-admin-sm whitespace-pre-wrap"
    >
      {{ error }}
    </div>

    <div
      class="overflow-hidden rounded-2xl border border-stone-200/70 bg-zinc-950 shadow-admin-sm"
      :class="lines.length ? '' : 'min-h-[12rem]'"
    >
      <pre
        ref="preEl"
        class="max-h-[min(70vh,720px)] overflow-auto p-4 font-mono text-[11px] leading-relaxed text-zinc-100 selection:bg-zinc-700"
        >{{ bodyText || t("admin.logs.emptyLog") }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import { fetchAdminRuntimeLogs } from "@/api/adminClient";
import { useAdminAuthStore } from "@/stores/adminAuth";

const { t } = useI18n();

const MAX_LINES = 12_000;

const auth = useAdminAuthStore();
const loading = ref(false);
const error = ref("");
const lines = ref<string[]>([]);
const hint = ref<string | null>(null);
const logPath = ref<string | null>(null);
const autoRefresh = ref(false);
const liveStream = ref(true);
const streamConnected = ref(false);
const preEl = ref<HTMLElement | null>(null);

let pollTimer: ReturnType<typeof setInterval> | null = null;
let es: EventSource | null = null;

const bodyText = computed(() => lines.value.join("\n"));

function formatErr(e: unknown): string {
  if (typeof e === "object" && e !== null && "response" in e) {
    const r = (e as { response?: { status?: number; data?: { detail?: string } } }).response;
    if (r?.status === 401) return t("admin.logs.err401");
    if (r?.data?.detail) return String(r.data.detail);
  }
  if (e instanceof Error) return e.message;
  return t("admin.logs.errConnect");
}

function trimLines() {
  if (lines.value.length > MAX_LINES) {
    lines.value = lines.value.slice(-MAX_LINES);
  }
}

async function scrollToBottom() {
  await nextTick();
  const el = preEl.value;
  if (el) el.scrollTop = el.scrollHeight;
}

async function loadOnce() {
  if (!auth.token) return;
  loading.value = true;
  error.value = "";
  try {
    const data = await fetchAdminRuntimeLogs({ tail_lines: 1200 });
    lines.value = data.lines ?? [];
    hint.value = data.hint ?? null;
    logPath.value = data.path ?? null;
    await scrollToBottom();
  } catch (e) {
    error.value = formatErr(e);
    lines.value = [];
    hint.value = null;
    logPath.value = null;
  } finally {
    loading.value = false;
  }
}

function stopPoll() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

function stopStream() {
  if (es) {
    es.close();
    es = null;
  }
  streamConnected.value = false;
}

function startPoll() {
  stopPoll();
  if (!autoRefresh.value || !auth.token || liveStream.value) return;
  pollTimer = setInterval(() => loadOnce(), 5000);
}

function handleSsePayload(raw: string) {
  let d: {
    type?: string;
    hint?: string;
    path?: string;
    lines?: string[];
    line?: string;
  };
  try {
    d = JSON.parse(raw) as typeof d;
  } catch {
    return;
  }
  if (d.type === "error") {
    hint.value = d.hint ?? t("admin.logs.streamFail");
    lines.value = [];
    logPath.value = null;
    streamConnected.value = false;
    return;
  }
  if (d.type === "init") {
    error.value = "";
    hint.value = null;
    logPath.value = d.path ?? null;
    lines.value = d.lines ?? [];
    trimLines();
    streamConnected.value = true;
    void scrollToBottom();
    return;
  }
  if (d.type === "reset") {
    lines.value = [];
    hint.value = t("admin.logs.rotated");
    void scrollToBottom();
    return;
  }
  if (d.type === "append" && typeof d.line === "string") {
    lines.value.push(d.line);
    trimLines();
    void scrollToBottom();
  }
}

function startStream() {
  stopStream();
  if (!auth.token?.trim() || !liveStream.value) return;
  const token = encodeURIComponent(auth.token.trim());
  const url = `/api/admin/runtime-logs/stream?admin_token=${token}`;
  es = new EventSource(url);
  es.onopen = () => {
    streamConnected.value = true;
  };
  es.onmessage = (ev) => {
    handleSsePayload(ev.data);
  };
  es.onerror = () => {
    streamConnected.value = false;
  };
}

function syncTransport() {
  stopPoll();
  stopStream();
  error.value = "";
  if (!auth.token) {
    lines.value = [];
    hint.value = null;
    logPath.value = null;
    return;
  }
  if (liveStream.value) {
    startStream();
  } else {
    void loadOnce();
    startPoll();
  }
}

watch(
  () => auth.token,
  () => syncTransport(),
);

watch(liveStream, () => syncTransport());

watch(autoRefresh, () => startPoll());

onMounted(() => syncTransport());

onUnmounted(() => {
  stopPoll();
  stopStream();
});
</script>
