<template>
  <div class="min-h-screen px-4 py-8 pb-16">
    <h2 class="text-center text-lg font-semibold mb-1">{{ t("result.title") }}</h2>
    <p v-if="aspectLabel" class="mb-5 text-center text-[11px] font-medium text-stone-500">
      {{ t("result.imageSpecUsed", { spec: aspectLabel }) }}
    </p>
    <div class="max-w-[500px] mx-auto">
      <div
        class="relative rounded-2xl overflow-hidden shadow-md aspect-[3/4] bg-oat"
        @click="onReveal"
      >
        <img
          v-if="imgUrl"
          :src="imgUrl"
          alt=""
          class="w-full h-full object-cover transition-transform duration-600 ease-out"
          :class="revealed ? 'scale-100' : 'scale-[0.98]'"
        />
        <div
          v-if="showMist"
          class="absolute inset-0 bg-gradient-to-b from-white/85 via-white/40 to-transparent flex items-center justify-center transition-opacity duration-600 ease-out"
          :class="revealed ? 'opacity-0 pointer-events-none' : 'opacity-100'"
        >
          <span class="text-stone-600 text-sm font-medium">{{ t("result.tapReveal") }}</span>
        </div>
      </div>
      <p class="mt-6 text-center text-stone-600 text-sm leading-relaxed px-2">
        {{ previewText }}
      </p>
      <p v-if="fullText && unlocked" class="mt-2 text-center text-stone-500 text-sm">
        {{ fullText }}
      </p>

      <div v-if="!unlocked" class="mt-8 space-y-4">
        <p v-if="payLoading" class="text-center text-sm text-stone-500">{{ t("common.loading") }}</p>
        <p v-else-if="payMeta && !anyPayEnabled" class="text-center text-sm text-amber-900">
          {{ t("result.payNotConfigured") }}
        </p>
        <template v-else-if="payMeta && anyPayEnabled">
          <div v-if="enabledMethodIds.length > 1" class="text-sm">
            <p class="text-stone-600 mb-2">{{ t("result.choosePayMethod") }}</p>
            <div class="flex flex-wrap gap-3">
              <label
                v-for="id in enabledMethodIds"
                :key="id"
                class="inline-flex items-center gap-2 cursor-pointer text-stone-800"
              >
                <input v-model="selectedProvider" type="radio" class="accent-blush" :value="id" />
                <span>{{ providerLabel(id) }}</span>
              </label>
            </div>
          </div>
          <button
            type="button"
            class="hover-frame w-full py-3 rounded-full bg-blush text-white font-medium shadow disabled:opacity-50"
            :disabled="payBusy || !selectedProvider"
            @click="unlock"
          >
            {{ payBusy ? t("result.payBusy") : t("result.unlock", { usd: priceLabel }) }}
          </button>
          <div
            v-if="usdtPayload"
            class="rounded-2xl border border-stone-200 bg-white p-4 text-sm text-stone-700 space-y-3 shadow-sm"
          >
            <p class="font-semibold text-stone-900">{{ t("result.usdtTitle") }}</p>
            <div class="flex justify-between gap-2">
              <span class="text-stone-500">{{ t("result.usdtNetwork") }}</span>
              <span class="font-mono text-xs">{{ usdtPayload.network }}</span>
            </div>
            <div class="flex justify-between gap-2 items-start">
              <span class="text-stone-500 shrink-0">{{ t("result.usdtAmount") }}</span>
              <span class="font-mono text-xs text-right break-all">{{ usdtPayload.amount }}</span>
            </div>
            <div>
              <div class="flex justify-between items-center gap-2 mb-1">
                <span class="text-stone-500">{{ t("result.usdtAddress") }}</span>
                <button
                  type="button"
                  class="hover-frame rounded-md px-1 py-0.5 text-blush text-xs font-medium"
                  @click="copyText(usdtPayload.address)"
                >
                  {{ t("result.copy") }}
                </button>
              </div>
              <p class="font-mono text-xs break-all bg-stone-50 rounded-lg p-2">{{ usdtPayload.address }}</p>
            </div>
            <div>
              <span class="text-stone-500">{{ t("result.usdtOrderRef") }}</span>
              <p class="font-mono text-xs mt-1 break-all">{{ usdtPayload.order_id }}</p>
            </div>
            <p class="text-xs text-stone-500 leading-relaxed">{{ t("result.usdtNote") }}</p>
          </div>
        </template>
      </div>

      <div class="mt-6 flex flex-wrap gap-3 justify-center text-sm text-stone-600">
        <span>{{ t("result.save") }}</span>
        <span>{{ t("result.pinterest") }}</span>
      </div>
      <button
        type="button"
        class="hover-frame mt-4 w-full rounded-xl py-2.5 text-stone-500 text-sm"
        @click="$router.push({ name: 'home' })"
      >
        {{ t("result.tryAnother") }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

const { t } = useI18n();
import { createCheckout, getPaymentMethods, getTask, type PaymentMethodsResponse } from "@/api/client";

const props = defineProps<{ taskId: string }>();
const route = useRoute();

const isPaid = ref(false);
const blurred = ref<string | null>(null);
const highres = ref<string | null>(null);
const previewText = ref("");
const fullText = ref("");
const revealed = ref(false);
/** 展示用「生图规格」文案（与 flow.imageSpec.* 对齐） */
const aspectLabel = ref("");

const payLoading = ref(true);
const payMeta = ref<PaymentMethodsResponse | null>(null);
const selectedProvider = ref<string | null>(null);
const payBusy = ref(false);
const usdtPayload = ref<{
  order_id: string;
  address: string;
  network: string;
  amount: string;
} | null>(null);

const unlocked = computed(() => isPaid.value);

const showMist = computed(() => unlocked.value && highres.value && !revealed.value);

const imgUrl = computed(() => {
  if (!unlocked.value) return blurred.value;
  return highres.value || blurred.value;
});

const anyPayEnabled = computed(() => payMeta.value?.methods.some((m) => m.enabled) ?? false);

const enabledMethodIds = computed(() =>
  (payMeta.value?.methods ?? []).filter((m) => m.enabled).map((m) => m.id),
);

const priceLabel = computed(() => {
  const meta = payMeta.value;
  if (!meta) return "$—";
  const usd = meta.checkout_amount_usd || "—";
  const u = meta.checkout_amount_usdt || usd;
  if (selectedProvider.value === "usdt") return `${u} USDT`;
  return `$${usd}`;
});

let poll: ReturnType<typeof setInterval> | null = null;

async function refresh() {
  const task = await getTask(props.taskId);
  isPaid.value = Boolean(task.is_paid);
  blurred.value = (task.blurred_image_url as string) || null;
  highres.value = (task.highres_url as string) || null;
  previewText.value = String(task.preview_text || "");
  fullText.value = String(task.full_text || "");
  const ar = String(task.aspect_ratio || "auto");
  const i18nKey = `flow.imageSpec.${ar.replace(/:/g, "_")}`;
  const localized = t(i18nKey);
  aspectLabel.value = localized !== i18nKey ? localized : ar;
}

async function loadPayMeta() {
  payLoading.value = true;
  try {
    const m = await getPaymentMethods();
    payMeta.value = m;
    const ids = m.methods.filter((x) => x.enabled).map((x) => x.id);
    if (m.default_provider && ids.includes(m.default_provider)) {
      selectedProvider.value = m.default_provider;
    } else if (ids.length === 1) {
      selectedProvider.value = ids[0] ?? null;
    } else if (ids.length > 1) {
      selectedProvider.value = ids[0] ?? null;
    } else {
      selectedProvider.value = null;
    }
  } catch {
    payMeta.value = null;
    selectedProvider.value = null;
  } finally {
    payLoading.value = false;
  }
}

function providerLabel(id: string) {
  if (id === "stripe") return t("result.payWithStripe");
  if (id === "creem") return t("result.payWithCreem");
  if (id === "lemon_squeezy") return t("result.payWithLemon");
  if (id === "usdt") return t("result.payWithUsdt");
  return id;
}

async function copyText(s: string) {
  try {
    await navigator.clipboard.writeText(s);
  } catch {
    /* ignore */
  }
}

function onReveal() {
  if (showMist.value) revealed.value = true;
}

async function unlock() {
  if (!selectedProvider.value || payBusy.value) return;
  payBusy.value = true;
  try {
    const res = await createCheckout(props.taskId, selectedProvider.value);
    if (res.provider === "usdt") {
      usdtPayload.value = res.usdt;
      payBusy.value = false;
      return;
    }
    if (res.checkout_url) {
      window.location.href = res.checkout_url;
      return;
    }
  } catch {
    payBusy.value = false;
    return;
  }
  payBusy.value = false;
}

function startPoll() {
  if (poll) return;
  poll = setInterval(async () => {
    await refresh();
    if (isPaid.value && poll) {
      clearInterval(poll);
      poll = null;
    }
  }, 2500);
}

onMounted(async () => {
  await Promise.all([refresh(), loadPayMeta()]);
  if (route.query.session_id || !isPaid.value) {
    startPoll();
  }
});

onUnmounted(() => {
  if (poll) clearInterval(poll);
});

watch(isPaid, (v) => {
  if (v) revealed.value = false;
});
</script>
