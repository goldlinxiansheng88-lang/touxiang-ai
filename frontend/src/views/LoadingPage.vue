<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-6 bg-[#F8F8F8]">
    <p class="text-stone-400 mb-4">✦ ✦ ✦</p>
    <p class="text-lg font-medium text-stone-700 text-center mb-6">{{ headline }}</p>
    <div
      v-if="thumb"
      class="w-40 h-40 rounded-2xl overflow-hidden shadow-md border border-stone-200/80 mb-6"
    >
      <img :src="thumb" class="w-full h-full object-cover" alt="" />
    </div>
    <p class="text-sm text-stone-500 text-center max-w-xs mb-8">{{ rotating }}</p>
    <div class="h-1 w-48 rounded-full bg-stone-200 overflow-hidden">
      <div class="h-full w-1/3 bg-blush animate-pulse rounded-full" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { getTask } from "@/api/client";

const props = defineProps<{ taskId: string }>();
const router = useRouter();
const { t, tm } = useI18n();

const hints = computed(() => {
  const raw = tm("loading.hints");
  return Array.isArray(raw) && raw.length ? (raw as string[]) : [t("loading.defaultRotating")];
});

const headline = ref("");
const rotating = ref("");
const thumb = ref<string | null>(null);

watch(
  () => hints.value,
  (h) => {
    if (h.length) {
      headline.value = t("loading.defaultHeadline");
      rotating.value = h[0] ?? "";
    }
  },
  { immediate: true },
);

let idx = 0;
let timer: ReturnType<typeof setInterval> | null = null;
let poll: ReturnType<typeof setInterval> | null = null;

onMounted(() => {
  headline.value = t("loading.defaultHeadline");
  rotating.value = hints.value[0] ?? t("loading.defaultRotating");

  timer = setInterval(() => {
    const h = hints.value;
    idx = (idx + 1) % h.length;
    rotating.value = h[idx] ?? "";
  }, 3000);

  poll = setInterval(async () => {
    try {
      const task = await getTask(props.taskId);
      const s = task.status as string;
      if (s === "COMPLETED") {
        router.replace({ name: "result", params: { taskId: props.taskId } });
      }
      if (s === "FAILED") {
        headline.value = t("loading.failed");
        rotating.value = String(task.error_message || t("loading.tryAgain"));
      }
    } catch {
      /* ignore */
    }
  }, 2000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
  if (poll) clearInterval(poll);
});
</script>
