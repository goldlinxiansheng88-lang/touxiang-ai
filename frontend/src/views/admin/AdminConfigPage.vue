<template>
  <div>
    <div class="mb-8 flex flex-wrap items-baseline gap-x-3 gap-y-2 border-b border-stone-200/80 pb-6">
      <div>
        <h1 class="text-xl font-bold tracking-tight text-stone-950">{{ t("admin.config.title") }}</h1>
        <p class="mt-1 max-w-2xl text-xs leading-relaxed text-stone-500" v-html="t('admin.config.intro')" />
      </div>
      <template v-if="activeGroupFromHash">
        <span class="hidden text-stone-300 sm:inline" aria-hidden="true">/</span>
        <span class="text-sm font-medium text-stone-800">{{ groupLabel(activeGroupFromHash.id, activeGroupFromHash.label) }}</span>
        <button
          type="button"
          class="rounded-full border border-stone-200 bg-white px-3 py-1 text-xs font-medium text-stone-600 shadow-sm transition hover:border-stone-300 hover:bg-stone-50"
          @click="showAllConfigGroups"
        >
          {{ t("admin.config.showAllGroups") }}
        </button>
      </template>
    </div>

    <div
      v-if="!auth.token"
      class="mb-4 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-xl border border-amber-200/80 bg-gradient-to-r from-amber-50 to-amber-50/30 px-4 py-3 text-xs text-amber-950 shadow-admin-sm"
    >
      <span v-html="t('admin.config.authBanner')" />
      <a href="#admin-auth-anchor" class="shrink-0 font-medium text-stone-900 underline decoration-stone-400 underline-offset-2 hover:decoration-stone-600">{{ t("admin.config.goAuth") }}</a>
    </div>

    <div
      v-if="schemaWarn"
      class="mb-4 rounded-xl border border-amber-200/80 bg-amber-50/90 px-4 py-3 text-xs leading-relaxed text-amber-950 shadow-admin-sm whitespace-pre-wrap"
    >
      {{ schemaWarn }}
    </div>

    <div
      v-if="schemaFatal"
      class="mb-4 rounded-xl border border-red-200/80 bg-red-50 px-4 py-3 text-sm text-red-800 whitespace-pre-wrap shadow-admin-sm"
    >
      {{ schemaFatal }}
    </div>

    <template v-else>
      <p
        v-if="schemaSyncing"
        class="mb-3 text-xs text-stone-500"
      >
        {{ t("admin.config.schemaSyncing") }}
      </p>
      <div v-if="valuesLoading" class="mb-4 text-sm text-stone-500">{{ t("admin.config.valuesLoading") }}</div>
      <div
        v-if="valuesError"
        class="mb-4 rounded-xl border border-red-200/80 bg-red-50/90 px-4 py-3 text-sm text-red-800 shadow-admin-sm whitespace-pre-wrap"
      >
        {{ valuesError }}
      </div>

      <div class="mb-6 flex flex-wrap items-center gap-3">
        <button
          type="button"
          class="rounded-xl bg-stone-900 px-5 py-2.5 text-sm font-medium text-white shadow-admin-sm transition hover:bg-stone-800 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="saving"
          @click="save"
        >
          {{ saving ? t("admin.config.saving") : t("admin.config.save") }}
        </button>
        <button
          type="button"
          class="rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-medium text-stone-700 shadow-sm transition hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="valuesLoading"
          @click="reloadValues(true)"
        >
          {{ t("admin.config.discardReload") }}
        </button>
      </div>
      <p v-if="infoBanner" class="mb-4 text-sm text-stone-600">{{ infoBanner }}</p>

      <!-- 按分类卡片展示：displayGroups 在带 hash 时仅一项，实现右侧内容归档 -->
      <div
        v-for="g in displayGroups"
        :key="g.id"
        :id="configGroupAnchorId(g.id)"
        class="scroll-mt-24 relative mb-8 overflow-hidden rounded-2xl border border-stone-200/50 bg-gradient-to-b from-white via-white to-stone-50/90 shadow-admin-sm before:pointer-events-none before:absolute before:inset-x-0 before:top-0 before:z-10 before:h-[2px] before:bg-gradient-to-r before:from-blush before:via-stone-400/50 before:to-stone-200/30"
      >
        <div class="border-b border-stone-200/70 bg-stone-50/80 px-5 py-4 backdrop-blur-[2px]">
          <h2 class="text-[15px] font-semibold tracking-tight text-stone-900">{{ groupLabel(g.id, g.label) }}</h2>
          <p v-if="g.hint" class="mt-1.5 text-xs leading-relaxed text-stone-600" v-html="groupHint(g.id, g.hint)" />
        </div>
        <div class="space-y-3 p-4 sm:p-5">
          <div
            v-for="row in itemsByGroup[g.id] || []"
            :key="row.key"
            class="rounded-xl border border-stone-200/60 bg-white p-4 text-sm shadow-[0_1px_3px_rgba(28,25,23,0.04)] sm:p-5"
          >
            <div class="space-y-3">
              <div class="space-y-2">
                <div class="flex flex-wrap items-center gap-2">
                  <div class="text-[15px] font-medium text-stone-900">{{ itemLabel(row) }}</div>
                  <span
                    class="inline-flex shrink-0 rounded-md border px-2 py-0.5 text-[10px] font-semibold leading-tight"
                    :class="
                      isRowRequired(row)
                        ? 'border-amber-300/90 bg-amber-50 text-amber-950'
                        : 'border-stone-200 bg-stone-50 text-stone-600'
                    "
                    :title="isRowRequired(row) ? t('admin.badge.requiredFlow') : t('admin.badge.optionalFlow')"
                  >
                    {{ isRowRequired(row) ? t("admin.config.required") : t("admin.config.optional") }}
                  </span>
                  <span
                    v-if="showValueKindChip(row)"
                    class="inline-flex shrink-0 rounded-md border border-stone-200 bg-stone-50 px-2 py-0.5 text-[10px] font-medium leading-tight text-stone-600"
                    :title="t('admin.config.valueKindTitle') + ' ' + valueKindLabel(row)"
                  >
                    {{ valueKindLabel(row) }}
                  </span>
                </div>
                <p class="text-xs leading-relaxed text-stone-500">{{ itemDesc(row) }}</p>
                <p class="text-[11px] font-medium uppercase tracking-wide text-stone-400">{{ t("admin.config.sourcePrefix") }} {{ sourceLabelTranslated(row.source) }}</p>
              </div>

              <!-- 键名单独行，输入与「连接」同一行并垂直居中，避免键名把按钮顶偏 -->
              <p class="break-all font-mono text-[10px] leading-snug text-stone-400">{{ row.key }}</p>

              <div
                class="flex flex-col gap-3 sm:gap-3"
                :class="isTestableKey(row.key) ? 'sm:flex-row sm:items-center' : ''"
              >
                <div class="min-w-0 flex-1">
                  <div v-if="row.readonly">
                    <input
                      type="text"
                      readonly
                      :value="readonlyDisplayValue(row)"
                      :placeholder="
                        row.source === 'pending_auth'
                          ? t('admin.config.readonlyPlaceholderAuth')
                          : t('admin.config.readonlyPlaceholderEmpty')
                      "
                      class="w-full cursor-text rounded-xl border border-stone-200 bg-stone-50/50 px-3 py-2.5 font-mono text-xs text-stone-800 shadow-admin-inset selection:bg-indigo-100 focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
                      @click="selectReadonly($event)"
                      @focus="selectReadonly($event)"
                    />
                  </div>
                  <template v-else>
                    <div
                      v-if="row.key === 'database_url' || row.key === 'redis_url'"
                      class="space-y-2"
                    >
                      <p class="text-[11px] leading-relaxed text-stone-600">
                        {{ row.key === "database_url" ? t("admin.config.dbUrlHelp") : t("admin.config.redisUrlHelp") }}
                      </p>
                      <textarea
                        v-model="edits[row.key]"
                        rows="4"
                        spellcheck="false"
                        autocomplete="off"
                        :disabled="!canEdit"
                        :placeholder="row.key === 'database_url' ? t('admin.config.phDb') : t('admin.config.phRedis')"
                        class="w-full resize-y rounded-xl border border-stone-200 bg-white px-3 py-2.5 font-mono text-xs leading-relaxed text-stone-900 shadow-sm placeholder:text-stone-400 focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10 disabled:cursor-not-allowed disabled:bg-stone-100 disabled:text-stone-500"
                        :class="fieldAccentClass(isRowRequired(row))"
                      />
                    </div>
                    <template v-else>
                      <input
                        v-if="!row.is_encrypted"
                        v-model="edits[row.key]"
                        type="text"
                        :disabled="!canEdit"
                        :aria-required="isRowRequired(row)"
                        class="w-full rounded-xl border border-stone-200 bg-white px-3 py-2.5 font-mono text-sm text-stone-900 shadow-sm transition focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10 disabled:cursor-not-allowed disabled:bg-stone-100 disabled:text-stone-500"
                        :class="fieldAccentClass(isRowRequired(row))"
                      />
                      <AdminSecretInput
                        v-else
                        v-model="edits[row.key]"
                        :mark="isRowRequired(row) ? 'required' : 'optional'"
                        :disabled="!canEdit"
                        :placeholder="maskedPlaceholder(row)"
                      />
                    </template>
                  </template>
                </div>

                <div
                  v-if="isTestableKey(row.key)"
                  class="flex w-full shrink-0 border-t border-stone-100 pt-3 sm:w-[10.25rem] sm:items-center sm:border-l sm:border-t-0 sm:border-stone-200/70 sm:pl-3 sm:pt-0"
                >
                  <button
                    type="button"
                    class="w-full rounded-lg border border-stone-200 bg-stone-50 px-3 py-1.5 text-center text-xs font-medium text-stone-800 shadow-sm transition hover:bg-white hover:shadow disabled:cursor-not-allowed disabled:opacity-50"
                    :disabled="!auth.token || connectionBusy(row.key)"
                    @click="runConnectionTest(row)"
                  >
                    {{ connectionBusy(row.key) ? t("admin.config.connecting") : t("admin.config.connect") }}
                  </button>
                </div>
              </div>

              <p v-if="row.readonly" class="text-[11px] leading-snug text-stone-500" v-html="t('admin.config.readonlyHelp')" />

              <p
                v-if="isTestableKey(row.key) && connectionHint(row.key)"
                class="text-[11px] leading-snug"
                :class="connectionHintClass(row.key)"
              >
                {{ connectionHint(row.key) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { onBeforeRouteLeave, useRoute, useRouter } from "vue-router";

import {
  fetchConfigRegistrySchema,
  fetchInfrastructurePreview,
  type ConfigRegistrySchemaItem,
} from "@/api/client";
import {
  getFallbackConfigRegistry,
  ADMIN_GROUP_ORDER,
  CONFIG_TESTABLE_KEYS,
  CONFIG_VALUE_KIND_BY_KEY,
  configItemRequired,
  configGroupAnchorId,
} from "@/data/adminConfigFallbackSchema";
import {
  fetchAdminConfigs,
  patchAdminConfigs,
  postAdminConfigTestConnection,
  type AdminConfigItem,
} from "@/api/adminClient";
import { useAdminAuthStore } from "@/stores/adminAuth";
import AdminSecretInput from "@/components/admin/AdminSecretInput.vue";
import { fieldAccentClass } from "@/utils/configFieldUi";
import { adminGroupPath, adminItemField, adminValueKindKey, tr } from "@/locales/adminI18n";

const { t, te } = useI18n();
const auth = useAdminAuthStore();
const route = useRoute();
const router = useRouter();
/** 首屏使用内置分类立即渲染，避免等 /api/meta 时整页空白 */
const _fbInit = getFallbackConfigRegistry();
const schemaFatal = ref("");
const schemaWarn = ref("");
const schemaSyncing = ref(false);
const registryGroups = ref<{ id: string; label: string; hint?: string }[]>(_fbInit.groups);
const schemaItems = ref<ConfigRegistrySchemaItem[]>(_fbInit.items);

const valuesLoading = ref(false);
/** 并发拉取时只让最后一次请求负责结束 loading，避免先完成的请求把 loading 置 false、按钮却看似永远不可点 */
let valuesFetchGeneration = 0;
const valuesError = ref("");
const valueItems = ref<AdminConfigItem[]>([]);

const saving = ref(false);
const infoBanner = ref("");
const edits = ref<Record<string, string>>({});
/** 刷新或返回本页时恢复未提交的输入（与「合并项」监听解耦，避免异步刷新把正在编辑的内容冲掉） */
const DRAFT_STORAGE_KEY = "aurashift-admin-config-drafts-v1";
let persistDraftTimer: ReturnType<typeof setTimeout> | null = null;
/** 连接检测：idle | testing | ok | fail */
const connectionStatus = ref<Record<string, { phase: string; message: string }>>({});
/** 未授权时只读项的脱敏预览（来自公开接口） */
const infraPreview = ref<Record<string, string>>({});

/** 分类结构加载完即可编辑；配置值拉取失败/重试中不禁用表单，避免「保存更改」与输入框长期灰显 */
const canEdit = computed(() => !schemaFatal.value);

const mergedItems = computed<AdminConfigItem[]>(() => {
  const fromServer = new Map(valueItems.value.map((i) => [i.key, i]));
  return schemaItems.value.map((s) => {
    const v = fromServer.get(s.key);
    const valueKind = s.value_kind ?? CONFIG_VALUE_KIND_BY_KEY[s.key];
    const required = typeof s.required === "boolean" ? s.required : configItemRequired(s.key);
    if (v) return { ...v, value_kind: valueKind, required };
    return {
      key: s.key,
      label: s.label,
      group: s.group,
      value: "",
      value_type: "string",
      description: s.description,
      is_encrypted: s.is_secret,
      readonly: s.readonly,
      source: auth.token ? "env_default" : "pending_auth",
      value_kind: valueKind,
      required,
    };
  });
});

const itemsByGroup = computed(() => {
  const m: Record<string, AdminConfigItem[]> = {};
  for (const row of mergedItems.value) {
    const g = row.group || "其它";
    if (!m[g]) m[g] = [];
    m[g].push(row);
  }
  return m;
});

/** 按 ADMIN_GROUP_ORDER 排序，保证分类顺序固定、与后端一致 */
const visibleGroups = computed(() => {
  const present = new Set(mergedItems.value.map((r) => r.group));
  const base =
    registryGroups.value.length > 0 ? registryGroups.value : getFallbackConfigRegistry().groups;
  return [...base]
    .filter((g) => present.has(g.id))
    .sort((a, b) => ADMIN_GROUP_ORDER.indexOf(a.id) - ADMIN_GROUP_ORDER.indexOf(b.id));
});

/** 与 URL #hash 对应的一条分类；有则右侧只展示该归档，否则展示全部分类 */
const activeGroupFromHash = computed(() => {
  const raw = route.hash.replace(/^#/, "");
  if (!raw) return null;
  return visibleGroups.value.find((g) => configGroupAnchorId(g.id) === raw) ?? null;
});

const displayGroups = computed(() => {
  const g = activeGroupFromHash.value;
  if (g) return [g];
  return visibleGroups.value;
});

const isDirty = computed(() => {
  for (const row of mergedItems.value) {
    if (row.readonly) continue;
    const v = edits.value[row.key] ?? "";
    if (row.is_encrypted && v === "") continue;
    const orig =
      row.is_encrypted && row.value === "••••••••"
        ? ""
        : row.value === "••••••••"
          ? ""
          : row.value;
    if (v !== orig) return true;
  }
  return false;
});

function showAllConfigGroups() {
  router.replace({ path: "/admin/config" });
}

function scrollConfigHashIntoView() {
  const raw = route.hash.replace(/^#/, "");
  if (!raw) return;
  requestAnimationFrame(() => {
    const el = document.getElementById(raw);
    el?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

watch(
  () => [schemaFatal.value, visibleGroups.value.length, route.hash] as const,
  () => {
    if (schemaFatal.value) return;
    if (activeGroupFromHash.value) return;
    scrollConfigHashIntoView();
  },
  { flush: "post" },
);

function groupLabel(id: string, fallback: string): string {
  const p = adminGroupPath(id, "label");
  return tr(te, t, p, fallback);
}

function groupHint(id: string, fallback: string): string {
  const p = adminGroupPath(id, "hint");
  return tr(te, t, p, fallback);
}

function itemLabel(row: AdminConfigItem): string {
  const p = adminItemField(row.key, "label");
  return tr(te, t, p, row.label);
}

function itemDesc(row: AdminConfigItem): string {
  const p = adminItemField(row.key, "description");
  return tr(te, t, p, row.description);
}

function valueKindLabel(row: AdminConfigItem): string {
  const fallback = (row.value_kind ?? CONFIG_VALUE_KIND_BY_KEY[row.key] ?? "").trim();
  const p = adminValueKindKey(row.key);
  return p && te(p) ? t(p) : fallback;
}

function showValueKindChip(row: AdminConfigItem): boolean {
  return !!valueKindLabel(row);
}

function isRowRequired(row: AdminConfigItem): boolean {
  return row.required === true;
}

function sourceLabelTranslated(s: string) {
  const p = `admin.config.sources.${s}`;
  return te(p) ? t(p) : s;
}

function maskedPlaceholder(row: AdminConfigItem) {
  if (row.value === "••••••••") return t("admin.config.maskedPlaceholderSet");
  return t("admin.config.maskedPlaceholderOptional");
}

function readonlyDisplayValue(row: AdminConfigItem): string {
  if (row.source !== "pending_auth") return row.value ?? "";
  const p = infraPreview.value[row.key];
  if (p) return p;
  return "";
}

function selectReadonly(ev: Event) {
  const el = ev.target as HTMLInputElement | null;
  if (el) el.select();
}

function isTestableKey(key: string): boolean {
  return CONFIG_TESTABLE_KEYS.has(key);
}

function valueForTest(k: string): string | undefined {
  const row = mergedItems.value.find((r) => r.key === k);
  if (!row) return undefined;
  const ed = edits.value[k];
  if (ed !== undefined && String(ed).trim() !== "") return String(ed);
  if (row.readonly) {
    const d = readonlyDisplayValue(row);
    if (d && !d.includes("•")) return d;
    return undefined;
  }
  const raw = row.value ?? "";
  if (raw && !String(raw).includes("••")) return String(raw);
  return undefined;
}

function relatedForTest(primary: string): Record<string, string> | undefined {
  if (primary === "image_api_key") {
    const ep = valueForTest("image_api_endpoint");
    return ep ? { image_api_endpoint: ep } : undefined;
  }
  const s3keys = ["s3_access_key", "s3_secret_key", "s3_bucket_name", "s3_region"];
  if (s3keys.includes(primary)) {
    const o: Record<string, string> = {};
    for (const sk of s3keys) {
      const v = valueForTest(sk);
      if (v) o[sk] = v;
    }
    return Object.keys(o).length ? o : undefined;
  }
  if (primary === "lemon_squeezy_api_key") {
    const sid = valueForTest("lemon_squeezy_store_id");
    return sid ? { lemon_squeezy_store_id: sid } : undefined;
  }
  return undefined;
}

function connectionBusy(key: string): boolean {
  return connectionStatus.value[key]?.phase === "testing";
}

function connectionHint(key: string): string {
  return connectionStatus.value[key]?.message ?? "";
}

function connectionHintClass(key: string): string {
  const p = connectionStatus.value[key]?.phase;
  if (p === "ok") return "text-emerald-700";
  if (p === "fail") return "text-red-600";
  return "text-stone-500";
}

async function runConnectionTest(row: AdminConfigItem) {
  if (!auth.token) {
    infoBanner.value = t("admin.config.saveAuthFirstShort");
    return;
  }
  connectionStatus.value = {
    ...connectionStatus.value,
    [row.key]: { phase: "testing", message: t("admin.config.connecting") },
  };
  try {
    const v = valueForTest(row.key);
    const payload: { key: string; value?: string; related?: Record<string, string> } = {
      key: row.key,
    };
    if (v !== undefined) payload.value = v;
    const rel = relatedForTest(row.key);
    if (rel) payload.related = rel;
    const data = await postAdminConfigTestConnection(payload);
    connectionStatus.value = {
      ...connectionStatus.value,
      [row.key]: { phase: data.ok ? "ok" : "fail", message: data.message },
    };
  } catch (e: unknown) {
    connectionStatus.value = {
      ...connectionStatus.value,
      [row.key]: { phase: "fail", message: formatErr(e) },
    };
  }
}

function formatErr(e: unknown): string {
  if (typeof e === "object" && e !== null && "response" in e) {
    const r = (e as {
      response?: { status?: number; data?: { detail?: unknown }; headers?: Record<string, string> };
    }).response;
    if (r?.status === 401) {
      return t("admin.errors.e401");
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

function loadDraft(): Record<string, string> | null {
  try {
    const raw = sessionStorage.getItem(DRAFT_STORAGE_KEY);
    if (!raw) return null;
    const o = JSON.parse(raw) as unknown;
    if (!o || typeof o !== "object" || Array.isArray(o)) return null;
    return o as Record<string, string>;
  } catch {
    return null;
  }
}

function initEdits(rows: AdminConfigItem[], opts?: { skipDraft?: boolean }) {
  const next: Record<string, string> = {};
  for (const row of rows) {
    if (row.readonly) continue;
    if (row.source === "pending_auth") {
      next[row.key] = "";
      continue;
    }
    if (row.is_encrypted && row.value === "••••••••") next[row.key] = "";
    else next[row.key] = row.value;
  }
  if (!opts?.skipDraft) {
    const draft = loadDraft();
    if (draft) {
      for (const row of rows) {
        if (row.readonly) continue;
        const k = row.key;
        if (Object.prototype.hasOwnProperty.call(draft, k) && typeof draft[k] === "string") {
          next[k] = draft[k];
        }
      }
    }
  }
  edits.value = next;
}

watch(
  edits,
  () => {
    if (persistDraftTimer) clearTimeout(persistDraftTimer);
    persistDraftTimer = setTimeout(() => {
      persistDraftTimer = null;
      try {
        sessionStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(edits.value));
      } catch {
        /* 存储配额等 */
      }
    }, 400);
  },
  { deep: true },
);

function applyFallback(reason: string) {
  const fb = getFallbackConfigRegistry();
  registryGroups.value = fb.groups;
  schemaItems.value = fb.items;
  schemaWarn.value = reason;
}

async function loadSchema() {
  schemaSyncing.value = true;
  schemaFatal.value = "";
  schemaWarn.value = "";
  try {
    const data = await fetchConfigRegistrySchema();
    if (!data.items?.length) {
      applyFallback(t("admin.errors.schemaFallback"));
    } else {
      registryGroups.value = data.groups;
      schemaItems.value = data.items;
    }
  } catch (e) {
    applyFallback(t("admin.errors.schemaFallbackErr", { err: formatErr(e) }));
  } finally {
    schemaSyncing.value = false;
  }
}

async function reloadValues(clearDraft = false) {
  valuesError.value = "";
  infoBanner.value = "";
  if (clearDraft) {
    try {
      sessionStorage.removeItem(DRAFT_STORAGE_KEY);
    } catch {
      /* empty */
    }
  }
  if (!auth.token) {
    valueItems.value = [];
    valuesLoading.value = false;
    await nextTick();
    initEdits(mergedItems.value, { skipDraft: clearDraft });
    return;
  }
  const gen = ++valuesFetchGeneration;
  valuesLoading.value = true;
  try {
    const data = await fetchAdminConfigs();
    if (gen !== valuesFetchGeneration) return;
    valueItems.value = data.items;
    if (data.groups?.length) registryGroups.value = data.groups;
    await nextTick();
    initEdits(mergedItems.value, { skipDraft: clearDraft });
  } catch (e) {
    if (gen !== valuesFetchGeneration) return;
    valuesError.value = formatErr(e);
    // 不清空 valueItems：保留上一次成功结果；无缓存时 merged 仍可由 schema 生成占位行
  } finally {
    if (gen === valuesFetchGeneration) {
      valuesLoading.value = false;
    }
  }
}

async function save() {
  if (!auth.token) {
    infoBanner.value = t("admin.config.saveAuthFirst");
    return;
  }
  saving.value = true;
  valuesError.value = "";
  infoBanner.value = "";
  try {
    const payload: { key: string; value: string }[] = [];
    for (const row of mergedItems.value) {
      if (row.readonly) continue;
      const v = edits.value[row.key] ?? "";
      if (row.is_encrypted && v === "") continue;
      const orig =
        row.is_encrypted && row.value === "••••••••" ? "" : row.value === "••••••••" ? "" : row.value;
      if (v === orig) continue;
      payload.push({ key: row.key, value: v });
    }
    if (payload.length === 0) {
      infoBanner.value = t("admin.config.noChanges");
      return;
    }
    const res = await patchAdminConfigs(payload);
    try {
      sessionStorage.removeItem(DRAFT_STORAGE_KEY);
    } catch {
      /* empty */
    }
    await reloadValues();
    await nextTick();
    // 服务端对密文返回 ••••••••，initEdits 会清空输入框（表示留空不改）；保存后把本次提交值写回，避免用户误以为内容丢失
    for (const item of payload) {
      edits.value[item.key] = item.value;
    }
    if (res?.hint) infoBanner.value = res.hint;
  } catch (e) {
    valuesError.value = formatErr(e);
  } finally {
    saving.value = false;
  }
}

function onTokenChanged() {
  auth.loadFromStorage();
  reloadValues();
}

async function loadInfraPreview() {
  try {
    const data = await fetchInfrastructurePreview();
    infraPreview.value = {
      database_url: data.database_url ?? "",
      redis_url: data.redis_url ?? "",
      encryption_key: data.encryption_key ?? "",
    };
  } catch {
    infraPreview.value = {};
  }
}

function onBeforeUnload(ev: BeforeUnloadEvent) {
  if (!isDirty.value) return;
  ev.preventDefault();
  ev.returnValue = "";
}

onBeforeRouteLeave((_to, _from, next) => {
  if (!isDirty.value) {
    next();
    return;
  }
  if (window.confirm(t("admin.config.leaveUnsavedConfirm"))) {
    next();
  } else {
    next(false);
  }
});

onMounted(async () => {
  await loadSchema();
  await nextTick();
  initEdits(mergedItems.value);
  await Promise.all([loadInfraPreview(), reloadValues()]);
  window.addEventListener("aurashift-admin-token-changed", onTokenChanged);
  window.addEventListener("beforeunload", onBeforeUnload);
});

onUnmounted(() => {
  window.removeEventListener("aurashift-admin-token-changed", onTokenChanged);
  window.removeEventListener("beforeunload", onBeforeUnload);
  if (persistDraftTimer) clearTimeout(persistDraftTimer);
});
</script>
