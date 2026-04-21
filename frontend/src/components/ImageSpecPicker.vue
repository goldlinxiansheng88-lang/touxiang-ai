<template>
  <div
    class="image-spec-picker w-full rounded-xl border border-stone-200/70 bg-[var(--aura-field)] p-2 shadow-sm"
  >
    <p class="mb-1.5 text-center text-[10px] font-medium tracking-wide text-stone-500">
      {{ t("flow.imageSpecTitle") }}
    </p>
    <div class="grid grid-cols-4 gap-1.5 sm:gap-2">
      <button
        v-for="opt in IMAGE_SPEC_OPTIONS"
        :key="opt.value"
        type="button"
        class="image-spec-btn flex flex-col items-center gap-0.5 rounded-lg border px-0.5 py-1 transition-all duration-150"
        :class="
          modelValue === opt.value
            ? 'border-blush/65 bg-blush/[0.12] text-stone-800 shadow-[0_0_0_1px_rgba(212,165,165,0.35)]'
            : 'border-stone-200/95 bg-white/60 text-stone-600 hover:border-stone-300 hover:bg-white hover:text-stone-800'
        "
        @click="emit('update:modelValue', opt.value)"
      >
        <span class="flex h-6 w-7 shrink-0 items-center justify-center">
          <svg
            v-if="opt.frame"
            class="text-current opacity-90"
            viewBox="0 0 40 36"
            width="28"
            height="25"
            aria-hidden="true"
          >
            <rect
              :x="frameGeom(opt.frame).x"
              :y="frameGeom(opt.frame).y"
              :width="frameGeom(opt.frame).rw"
              :height="frameGeom(opt.frame).rh"
              rx="1.5"
              fill="none"
              stroke="currentColor"
              stroke-width="1.75"
            />
          </svg>
          <svg
            v-else
            class="text-current opacity-90"
            viewBox="0 0 40 36"
            width="28"
            height="25"
            aria-hidden="true"
          >
            <rect x="5" y="8" width="30" height="20" rx="2" fill="none" stroke="currentColor" stroke-width="1.6" />
            <path d="M12 24l6-6 5 5 7-9" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
            <circle cx="26" cy="13" r="2" fill="currentColor" opacity="0.85" />
          </svg>
        </span>
        <span class="text-[10px] font-semibold leading-none">{{ labelFor(opt.value) }}</span>
      </button>
    </div>
    <p class="mt-1.5 text-center text-[9px] leading-snug text-stone-500/90">{{ t("flow.imageSpecHint") }}</p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { IMAGE_SPEC_OPTIONS, type AspectRatioValue } from "@/data/imageSpec";

defineProps<{
  modelValue: AspectRatioValue | string;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", v: AspectRatioValue): void;
}>();

const { t } = useI18n();

function labelFor(v: AspectRatioValue): string {
  const key = `flow.imageSpec.${v.replace(":", "_")}`;
  return t(key);
}

function frameGeom(frame: { w: number; h: number }) {
  const max = 30;
  const r = frame.w / frame.h;
  let rw: number;
  let rh: number;
  if (r >= 1) {
    rw = max;
    rh = max / r;
  } else {
    rh = max;
    rw = max * r;
  }
  return { rw, rh, x: (40 - rw) / 2, y: (36 - rh) / 2 };
}
</script>

<style scoped>
.image-spec-btn:focus-visible {
  outline: 2px solid rgb(212 165 165 / 0.55);
  outline-offset: 1px;
}
</style>
