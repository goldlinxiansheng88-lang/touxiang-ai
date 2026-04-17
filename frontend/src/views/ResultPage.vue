<template>
  <div class="min-h-screen bg-[#F8F8F8] px-4 py-8 pb-16">
    <h2 class="text-center text-lg font-semibold mb-6">{{ t("result.title") }}</h2>
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

      <button
        v-if="!unlocked"
        type="button"
        class="mt-8 w-full py-3 rounded-full bg-blush text-white font-medium shadow"
        @click="unlock"
      >
        {{ t("result.unlock") }}
      </button>

      <div class="mt-6 flex flex-wrap gap-3 justify-center text-sm text-stone-600">
        <span>{{ t("result.save") }}</span>
        <span>{{ t("result.pinterest") }}</span>
      </div>
      <button
        type="button"
        class="mt-4 w-full py-2 text-stone-500 text-sm"
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
import { createCheckout, getTask } from "@/api/client";

const props = defineProps<{ taskId: string }>();
const route = useRoute();

const status = ref("");
const isPaid = ref(false);
const blurred = ref<string | null>(null);
const highres = ref<string | null>(null);
const previewText = ref("");
const fullText = ref("");
const revealed = ref(false);

const unlocked = computed(() => isPaid.value);

const showMist = computed(() => unlocked.value && highres.value && !revealed.value);

const imgUrl = computed(() => {
  if (!unlocked.value) return blurred.value;
  return highres.value || blurred.value;
});

let poll: ReturnType<typeof setInterval> | null = null;

async function refresh() {
  const t = await getTask(props.taskId);
  status.value = String(t.status);
  isPaid.value = Boolean(t.is_paid);
  blurred.value = (t.blurred_image_url as string) || null;
  highres.value = (t.highres_url as string) || null;
  previewText.value = String(t.preview_text || "");
  fullText.value = String(t.full_text || "");
}

function onReveal() {
  if (showMist.value) revealed.value = true;
}

async function unlock() {
  const { checkout_url } = await createCheckout(props.taskId);
  window.location.href = checkout_url;
}

onMounted(async () => {
  await refresh();
  if (route.query.session_id) {
    poll = setInterval(async () => {
      await refresh();
      if (isPaid.value && poll) {
        clearInterval(poll);
        poll = null;
      }
    }, 2000);
  }
});

onUnmounted(() => {
  if (poll) clearInterval(poll);
});

watch(isPaid, (v) => {
  if (v) revealed.value = false;
});
</script>
