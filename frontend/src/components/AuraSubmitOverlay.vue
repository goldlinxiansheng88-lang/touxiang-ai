<template>
  <Teleport to="body">
    <Transition name="aura-overlay">
      <div
        v-if="show"
        class="aura-shell fixed inset-0 z-[9998] flex flex-col items-center justify-center overflow-hidden px-6 isolate"
        :class="theme.shell"
        role="alert"
        aria-live="polite"
        aria-busy="true"
      >
        <!-- 大块柔光 blob：慢漂移，增加景深 -->
        <div class="aura-blobs absolute inset-[-25%] pointer-events-none" aria-hidden="true" />
        <!-- 氛围底：柔雾 + 缓慢流动的极光色带（随主题变化） -->
        <div class="aura-mist absolute inset-0" aria-hidden="true" />
        <div class="aura-aurora absolute inset-[-20%] opacity-90" aria-hidden="true" />

        <!-- 柔光粒子（纯 CSS） -->
        <div class="aura-dust absolute inset-0 opacity-40" aria-hidden="true" />

        <!-- 轻暗角：压住中心视觉 -->
        <div class="aura-vignette pointer-events-none absolute inset-0" aria-hidden="true" />

        <!-- 慢速色罩：情绪冷暖在空气中流动 -->
        <div class="aura-chroma-breathe pointer-events-none absolute inset-0 z-[1]" aria-hidden="true" />
        <!-- 游移聚光：像在剧场里追着主角的一束光 -->
        <div class="aura-spotlight pointer-events-none absolute z-[1]" aria-hidden="true" />
        <!-- 漂浮微粒：视线在空气中有一点落点 -->
        <div class="aura-motes pointer-events-none absolute inset-0 z-[2]" aria-hidden="true">
          <span class="aura-mote aura-mote-1" />
          <span class="aura-mote aura-mote-2" />
          <span class="aura-mote aura-mote-3" />
          <span class="aura-mote aura-mote-4" />
          <span class="aura-mote aura-mote-5" />
        </div>

        <!-- 柔焦散景（大光斑，略慢于 blob） -->
        <div class="aura-bokeh pointer-events-none absolute inset-0 z-[1]" aria-hidden="true">
          <span class="aura-bokeh-dot aura-bokeh-a" />
          <span class="aura-bokeh-dot aura-bokeh-b" />
          <span class="aura-bokeh-dot aura-bokeh-c" />
        </div>

        <!-- 胶片颗粒：打破过度「数码光滑」 -->
        <div class="aura-grain pointer-events-none absolute inset-0 z-[3]" aria-hidden="true">
          <svg class="aura-grain-svg h-full w-full" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
            <filter id="aura-grain-filter" x="-10%" y="-10%" width="120%" height="120%">
              <feTurbulence type="fractalNoise" baseFrequency="0.78" numOctaves="4" stitchTiles="stitch" />
              <feColorMatrix type="saturate" values="0" />
            </filter>
            <rect width="100%" height="100%" filter="url(#aura-grain-filter)" />
          </svg>
        </div>

        <!-- 中心：悬浮 + 呼吸光球 + 双环 + 星芒错落动效 -->
        <div class="aura-stage aura-stage-motion relative z-10 flex flex-col items-center">
          <div class="aura-orb-wrap relative mb-5 md:mb-6">
            <div class="aura-ripple absolute inset-[-8px] rounded-full" aria-hidden="true" />
            <div class="aura-ripple aura-ripple--echo absolute inset-[-8px] rounded-full" aria-hidden="true" />
            <div class="aura-orb-glow aura-orb-glow-main absolute inset-0 scale-150 rounded-full blur-3xl" />
            <div class="aura-orb-glow aura-orb-glow-halo absolute inset-0 rounded-full blur-[52px]" />
            <div class="aura-ring-sheen absolute inset-[-10px] rounded-full" />
            <div
              class="aura-orb relative flex h-28 w-28 items-center justify-center overflow-hidden rounded-full md:h-32 md:w-32"
            >
              <div class="aura-orb-sheen pointer-events-none absolute inset-0 rounded-full" aria-hidden="true" />
              <span class="sparkle-row relative z-[3] flex items-baseline justify-center gap-1.5 md:gap-2.5" aria-hidden="true">
                <span
                  v-for="(ch, si) in sparkleChars"
                  :key="si"
                  class="sparkle-char sparkle-inner text-xl md:text-2xl"
                  :style="{ animationDelay: `${si * 0.38}s` }"
                >{{ ch }}</span>
              </span>
            </div>
            <div class="aura-ring-outer absolute inset-[-6px] rounded-full" />
          </div>

          <!-- 情绪地平线：轻锚点，让等待有「落点」 -->
          <div class="aura-horizon mb-7 flex justify-center md:mb-8" aria-hidden="true">
            <div class="aura-horizon-line" />
          </div>

          <div class="aura-title-shell flex min-h-[4.25rem] w-full max-w-md items-center justify-center px-1 md:min-h-[4.75rem]">
            <Transition name="aura-phrase" mode="out-in">
              <p
                :key="phrase"
                class="aura-title text-balance text-center text-lg font-medium tracking-[0.02em] text-stone-800/[0.92] antialiased md:text-[1.42rem] md:leading-snug"
                style="font-family: inherit"
              >
                {{ phrase }}
              </p>
            </Transition>
          </div>
          <p
            class="aura-brand aura-brand-motion mt-2 text-[0.65rem] font-medium uppercase tracking-[0.42em] text-stone-400/90 md:text-xs md:tracking-[0.48em]"
          >
            AuraShift
          </p>
          <p
            class="aura-sub aura-sub-motion mt-6 max-w-[19rem] text-center text-[0.8125rem] leading-relaxed text-stone-500/75 md:mt-7 md:text-sm"
          >
            {{ t("overlay.subtitle") }}
          </p>
        </div>

        <!-- 底沿微光：无具体进度，仅暗示「仍在流动」 -->
        <div class="aura-mood-anchor pointer-events-none absolute bottom-0 left-0 right-0 z-[4] flex flex-col items-center pb-7 pt-3" aria-hidden="true">
          <div class="aura-mood-line">
            <div class="aura-mood-line-shimmer" />
          </div>
        </div>

        <!-- 氛围音开关：默认轻垫音 + 换句提示音；记忆偏好 -->
        <button
          type="button"
          class="aura-sound-toggle hover-frame"
          :aria-pressed="!ambientMuted"
          :aria-label="ambientMuted ? t('overlay.unmuteAmbient') : t('overlay.muteAmbient')"
          @click="toggleAmbient"
        >
          <svg v-if="!ambientMuted" class="aura-sound-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11 5L6 9H3v6h3l5 4V5z" />
            <path stroke-linecap="round" d="M15.5 8.5c1.5 1.5 1.5 5.5 0 7M18 6c2.5 2.5 2.5 11.5 0 14" />
          </svg>
          <svg v-else class="aura-sound-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11 5L6 9H3v6h3l5 4V5z" />
            <path stroke-linecap="round" d="M21 9l-6 6M15 9l6 6" />
          </svg>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import {
  disposeAuraAudio,
  isAmbientMuted,
  playPhraseChime,
  setAmbientMuted,
  startAuraAmbient,
  stopAuraAmbient,
} from "@/utils/auraAmbientSound";

const { t, tm } = useI18n();

const props = defineProps<{ show: boolean }>();

function prefersReducedMotion(): boolean {
  return typeof matchMedia !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches;
}

const ambientMuted = ref(isAmbientMuted());
const soundEngaged = ref(false);

/** 多套极简高级氛围：柔渐变 + 同色呼吸球；每次打开遮罩随机其一 */
const THEME_PRESETS = [
  {
    shell: "theme-rose",
    sparkles: "✦ ✦ ✦",
  },
  {
    shell: "theme-lavender",
    sparkles: "✧ ✧ ✧",
  },
  {
    shell: "theme-sage",
    sparkles: "◇ ◇ ◇",
  },
  {
    shell: "theme-peach",
    sparkles: "✦ · ✦",
  },
  {
    shell: "theme-moon",
    sparkles: "✶ ✶ ✶",
  },
  {
    shell: "theme-sand",
    sparkles: "⁂ ⁂ ⁂",
  },
  {
    shell: "theme-dusk",
    sparkles: "✴ ✴ ✴",
  },
] as const;

const theme = ref<(typeof THEME_PRESETS)[number]>(THEME_PRESETS[0]);

/** 星符拆成多枚，便于错落闪烁 */
const sparkleChars = computed(() => {
  const raw = theme.value.sparkles
    .split(/\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
  return raw.length ? raw : ["✦"];
});

const phrases = computed(() => {
  const raw = tm("submitPhrases");
  return Array.isArray(raw) && raw.length ? (raw as string[]) : ["…"];
});

const phrase = ref("");
let timer: ReturnType<typeof setInterval> | null = null;
let idx = 0;

function tick() {
  const list = phrases.value;
  idx = (idx + 1) % list.length;
  phrase.value = list[idx] ?? "";
}

async function syncAmbientOnOpen() {
  if (!props.show || ambientMuted.value) {
    soundEngaged.value = false;
    return;
  }
  if (prefersReducedMotion()) {
    soundEngaged.value = false;
    return;
  }
  try {
    await startAuraAmbient();
    soundEngaged.value = true;
  } catch {
    soundEngaged.value = false;
  }
}

watch(
  () => props.show,
  async (v) => {
    document.body.style.overflow = v ? "hidden" : "";
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    if (v) {
      const pick = THEME_PRESETS[Math.floor(Math.random() * THEME_PRESETS.length)];
      if (pick) theme.value = pick;
      idx = 0;
      phrase.value = phrases.value[0] ?? "";
      timer = setInterval(tick, 3600);
      await syncAmbientOnOpen();
    } else {
      soundEngaged.value = false;
      await stopAuraAmbient();
    }
  },
  { immediate: true }
);

watch(phrases, (list) => {
  if (list.length && props.show) phrase.value = list[idx % list.length] ?? "";
});

watch(phrase, (_newVal, oldVal) => {
  if (!props.show) return;
  if (oldVal === undefined || oldVal === "") return;
  if (ambientMuted.value || !soundEngaged.value) return;
  playPhraseChime();
});

async function toggleAmbient() {
  ambientMuted.value = !ambientMuted.value;
  setAmbientMuted(ambientMuted.value);
  if (ambientMuted.value) {
    soundEngaged.value = false;
    await stopAuraAmbient();
    return;
  }
  if (!props.show) return;
  try {
    await startAuraAmbient();
    soundEngaged.value = true;
  } catch {
    soundEngaged.value = false;
  }
}

onMounted(() => {
  if (props.show) document.body.style.overflow = "hidden";
});

onBeforeUnmount(() => {
  document.body.style.overflow = "";
  if (timer) clearInterval(timer);
  soundEngaged.value = false;
  void disposeAuraAudio();
});
</script>

<style scoped>
/* 整屏微光：叠在主题底色之上缓慢游移 */
.aura-shell::before {
  content: "";
  position: absolute;
  inset: -5%;
  z-index: 0;
  pointer-events: none;
  background: radial-gradient(ellipse 125% 95% at 48% 42%, rgba(255, 255, 255, 0.09), transparent 55%);
  mix-blend-mode: soft-light;
  animation: shell-sheen-drift 40s ease-in-out infinite;
}

@keyframes shell-sheen-drift {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
    opacity: 0.85;
  }
  38% {
    transform: translate(2.2%, -1.8%) scale(1.04);
    opacity: 1;
  }
  72% {
    transform: translate(-1.2%, 2%) scale(0.97);
    opacity: 0.78;
  }
}

/* —— 主题 1：玫瑰雾（默认气质，与现有一致） —— */
.theme-rose {
  background: radial-gradient(ellipse 120% 80% at 50% 20%, #fdf8f5 0%, #f5f0eb 45%, #ebe3dc 100%);
}
.theme-rose .aura-mist {
  background: radial-gradient(circle at 30% 40%, rgba(220, 38, 38, 0.18), transparent 55%),
    radial-gradient(circle at 70% 60%, rgba(156, 163, 175, 0.12), transparent 50%);
}
.theme-rose .aura-aurora {
  background: linear-gradient(
    125deg,
    rgba(220, 38, 38, 0.35) 0%,
    rgba(245, 240, 235, 0.2) 25%,
    rgba(180, 200, 220, 0.25) 50%,
    rgba(220, 38, 38, 0.2) 75%,
    rgba(245, 240, 235, 0.3) 100%
  );
}
.theme-rose .aura-orb-glow-main {
  background: radial-gradient(circle, rgba(220, 38, 38, 0.55) 0%, transparent 70%);
}
.theme-rose .aura-orb {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.5) 0%, rgba(220, 38, 38, 0.4) 40%, rgba(185, 90, 90, 0.45) 100%);
  box-shadow: 0 8px 40px rgba(220, 38, 38, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.6);
}
.theme-rose .aura-ring-outer {
  border-color: rgba(255, 255, 255, 0.45);
  box-shadow: 0 0 0 1px rgba(220, 38, 38, 0.15);
}
.theme-rose .sparkle-inner {
  color: rgba(255, 255, 255, 0.92);
}

/* —— 主题 2：薰衣草雾 —— */
.theme-lavender {
  background: radial-gradient(ellipse 120% 85% at 50% 15%, #faf8ff 0%, #f0edf8 50%, #e8e2f4 100%);
}
.theme-lavender .aura-mist {
  background: radial-gradient(circle at 25% 35%, rgba(167, 139, 250, 0.14), transparent 52%),
    radial-gradient(circle at 75% 65%, rgba(196, 181, 253, 0.12), transparent 48%);
}
.theme-lavender .aura-aurora {
  background: linear-gradient(
    130deg,
    rgba(167, 139, 250, 0.28) 0%,
    rgba(237, 233, 254, 0.35) 35%,
    rgba(199, 210, 254, 0.3) 65%,
    rgba(167, 139, 250, 0.22) 100%
  );
}
.theme-lavender .aura-orb-glow-main {
  background: radial-gradient(circle, rgba(167, 139, 250, 0.5) 0%, transparent 70%);
}
.theme-lavender .aura-orb {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.55) 0%, rgba(196, 181, 253, 0.42) 45%, rgba(167, 139, 250, 0.38) 100%);
  box-shadow: 0 8px 40px rgba(139, 92, 246, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.65);
}
.theme-lavender .aura-ring-outer {
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 0 1px rgba(167, 139, 250, 0.18);
}
.theme-lavender .sparkle-inner {
  color: rgba(255, 255, 255, 0.95);
}

/* —— 主题 3：鼠尾草雾 —— */
.theme-sage {
  background: radial-gradient(ellipse 115% 82% at 48% 18%, #f6faf7 0%, #ecf5ef 48%, #e0ebe4 100%);
}
.theme-sage .aura-mist {
  background: radial-gradient(circle at 35% 38%, rgba(134, 180, 160, 0.16), transparent 54%),
    radial-gradient(circle at 68% 62%, rgba(167, 200, 185, 0.12), transparent 50%);
}
.theme-sage .aura-aurora {
  background: linear-gradient(
    122deg,
    rgba(134, 180, 160, 0.26) 0%,
    rgba(236, 253, 245, 0.3) 40%,
    rgba(180, 210, 195, 0.22) 75%,
    rgba(134, 180, 160, 0.18) 100%
  );
}
.theme-sage .aura-orb-glow-main {
  background: radial-gradient(circle, rgba(110, 170, 150, 0.45) 0%, transparent 70%);
}
.theme-sage .aura-orb {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.52) 0%, rgba(180, 215, 200, 0.4) 42%, rgba(130, 175, 155, 0.42) 100%);
  box-shadow: 0 8px 38px rgba(100, 150, 130, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.58);
}
.theme-sage .aura-ring-outer {
  border-color: rgba(255, 255, 255, 0.48);
  box-shadow: 0 0 0 1px rgba(120, 170, 150, 0.14);
}
.theme-sage .sparkle-inner {
  color: rgba(255, 255, 255, 0.9);
}

/* —— 主题 4：蜜桃雾 —— */
.theme-peach {
  background: radial-gradient(ellipse 118% 80% at 50% 22%, #fff9f6 0%, #fef3ed 46%, #f8e8de 100%);
}
.theme-peach .aura-mist {
  background: radial-gradient(circle at 28% 42%, rgba(251, 182, 150, 0.2), transparent 53%),
    radial-gradient(circle at 72% 58%, rgba(253, 186, 170, 0.14), transparent 49%);
}
.theme-peach .aura-aurora {
  background: linear-gradient(
    128deg,
    rgba(251, 182, 150, 0.32) 0%,
    rgba(255, 245, 238, 0.28) 30%,
    rgba(255, 218, 200, 0.26) 60%,
    rgba(251, 182, 150, 0.2) 100%
  );
}
.theme-peach .aura-orb-glow-main {
  background: radial-gradient(circle, rgba(251, 146, 120, 0.48) 0%, transparent 70%);
}
.theme-peach .aura-orb {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.52) 0%, rgba(255, 200, 180, 0.42) 40%, rgba(248, 150, 130, 0.38) 100%);
  box-shadow: 0 8px 42px rgba(251, 146, 120, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.62);
}
.theme-peach .aura-ring-outer {
  border-color: rgba(255, 255, 255, 0.46);
  box-shadow: 0 0 0 1px rgba(251, 146, 120, 0.16);
}
.theme-peach .sparkle-inner {
  color: rgba(255, 255, 255, 0.94);
}

/* —— 主题 5：月辉雾 —— */
.theme-moon {
  background: radial-gradient(ellipse 120% 78% at 50% 12%, #f8fafc 0%, #eef2f8 50%, #e2e8f0 100%);
}
.theme-moon .aura-mist {
  background: radial-gradient(circle at 32% 36%, rgba(148, 163, 184, 0.14), transparent 52%),
    radial-gradient(circle at 70% 64%, rgba(186, 200, 220, 0.14), transparent 50%);
}
.theme-moon .aura-aurora {
  background: linear-gradient(
    125deg,
    rgba(148, 163, 184, 0.22) 0%,
    rgba(226, 232, 240, 0.35) 38%,
    rgba(199, 210, 254, 0.2) 72%,
    rgba(148, 163, 184, 0.18) 100%
  );
}
.theme-moon .aura-orb-glow-main {
  background: radial-gradient(circle, rgba(148, 163, 184, 0.42) 0%, transparent 70%);
}
.theme-moon .aura-orb {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.58) 0%, rgba(203, 213, 225, 0.4) 42%, rgba(148, 163, 184, 0.4) 100%);
  box-shadow: 0 8px 40px rgba(100, 116, 139, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.7);
}
.theme-moon .aura-ring-outer {
  border-color: rgba(255, 255, 255, 0.55);
  box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.12);
}
.theme-moon .sparkle-inner {
  color: rgba(255, 255, 255, 0.96);
}

/* —— 主题 6：香槟沙雾 —— */
.theme-sand {
  background: radial-gradient(ellipse 116% 82% at 50% 20%, #fdfcfa 0%, #f7f2e8 48%, #ede4d8 100%);
}
.theme-sand .aura-mist {
  background: radial-gradient(circle at 30% 40%, rgba(214, 200, 175, 0.18), transparent 54%),
    radial-gradient(circle at 68% 60%, rgba(200, 185, 165, 0.12), transparent 48%);
}
.theme-sand .aura-aurora {
  background: linear-gradient(
    127deg,
    rgba(214, 200, 175, 0.26) 0%,
    rgba(250, 245, 235, 0.3) 35%,
    rgba(220, 205, 185, 0.22) 70%,
    rgba(214, 200, 175, 0.18) 100%
  );
}
.theme-sand .aura-orb-glow-main {
  background: radial-gradient(circle, rgba(190, 170, 145, 0.42) 0%, transparent 70%);
}
.theme-sand .aura-orb {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.5) 0%, rgba(235, 225, 210, 0.45) 40%, rgba(200, 180, 160, 0.42) 100%);
  box-shadow: 0 8px 38px rgba(160, 140, 120, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.55);
}
.theme-sand .aura-ring-outer {
  border-color: rgba(255, 255, 255, 0.44);
  box-shadow: 0 0 0 1px rgba(190, 170, 145, 0.14);
}
.theme-sand .sparkle-inner {
  color: rgba(255, 255, 255, 0.9);
}

/* —— 主题 7：暮霭紫灰 —— */
.theme-dusk {
  background: radial-gradient(ellipse 118% 80% at 50% 18%, #f5f3f9 0%, #ebe6f2 46%, #ddd5e8 100%);
}
.theme-dusk .aura-mist {
  background: radial-gradient(circle at 27% 38%, rgba(139, 120, 180, 0.14), transparent 53%),
    radial-gradient(circle at 73% 62%, rgba(160, 150, 190, 0.12), transparent 49%);
}
.theme-dusk .aura-aurora {
  background: linear-gradient(
    126deg,
    rgba(139, 120, 180, 0.24) 0%,
    rgba(230, 225, 245, 0.28) 42%,
    rgba(180, 170, 210, 0.2) 78%,
    rgba(139, 120, 180, 0.16) 100%
  );
}
.theme-dusk .aura-orb-glow-main {
  background: radial-gradient(circle, rgba(120, 100, 160, 0.4) 0%, transparent 70%);
}
.theme-dusk .aura-orb {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.48) 0%, rgba(200, 185, 225, 0.38) 44%, rgba(130, 110, 170, 0.4) 100%);
  box-shadow: 0 8px 40px rgba(100, 80, 140, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.55);
}
.theme-dusk .aura-ring-outer {
  border-color: rgba(255, 255, 255, 0.42);
  box-shadow: 0 0 0 1px rgba(120, 100, 160, 0.14);
}
.theme-dusk .sparkle-inner {
  color: rgba(255, 255, 255, 0.92);
}

/* —— 全局氛围层（不随主题换色，只做景深与质感） —— */
.aura-blobs {
  z-index: 0;
  background: radial-gradient(ellipse 58% 52% at 16% 70%, rgba(255, 255, 255, 0.48), transparent 58%),
    radial-gradient(ellipse 50% 46% at 84% 26%, rgba(255, 255, 255, 0.34), transparent 54%),
    radial-gradient(ellipse 44% 40% at 50% 50%, rgba(255, 255, 255, 0.12), transparent 52%);
  opacity: 0.88;
  animation: blobs-drift 26s ease-in-out infinite alternate;
}

.aura-vignette {
  z-index: 2;
  background: radial-gradient(ellipse 92% 88% at 50% 44%, transparent 34%, rgba(15, 23, 42, 0.078) 100%);
  mix-blend-mode: multiply;
  animation: vignette-drift 34s ease-in-out infinite;
}

@keyframes vignette-drift {
  0%,
  100% {
    transform: scale(1) translate(0, 0);
  }
  50% {
    transform: scale(1.05) translate(0.8%, -0.4%);
  }
}

/* 情绪色罩：冷暖在空气中极慢交替，调动细微情绪 */
.aura-chroma-breathe {
  opacity: 0.55;
  mix-blend-mode: soft-light;
  background: linear-gradient(
    118deg,
    rgba(255, 200, 210, 0.11) 0%,
    rgba(200, 210, 255, 0.12) 35%,
    rgba(255, 235, 210, 0.09) 65%,
    rgba(220, 200, 245, 0.1) 100%
  );
  background-size: 240% 240%;
  animation: chroma-air-shift 52s ease-in-out infinite;
}

@keyframes chroma-air-shift {
  0%,
  100% {
    background-position: 0% 40%;
    opacity: 0.42;
  }
  50% {
    background-position: 100% 60%;
    opacity: 0.62;
  }
}

/* 剧场聚光：缓慢游移，视线有「被引导」感 */
.aura-spotlight {
  left: 50%;
  top: 24%;
  width: min(92vw, 680px);
  height: min(58vh, 520px);
  transform: translate(-50%, -32%);
  background: radial-gradient(ellipse 52% 48% at 50% 48%, rgba(255, 255, 255, 0.14), transparent 68%);
  mix-blend-mode: soft-light;
  animation: spotlight-wander 56s ease-in-out infinite;
}

@keyframes spotlight-wander {
  0%,
  100% {
    transform: translate(-50%, -32%) translate(0, 0) scale(1);
    opacity: 0.75;
  }
  28% {
    transform: translate(-50%, -32%) translate(5%, 4%) scale(1.06);
    opacity: 0.95;
  }
  55% {
    transform: translate(-50%, -32%) translate(-4%, 6%) scale(0.96);
    opacity: 0.7;
  }
  78% {
    transform: translate(-50%, -32%) translate(3%, -3%) scale(1.03);
    opacity: 0.88;
  }
}

/* 漂浮微粒 */
.aura-mote {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.15) 60%, transparent 70%);
  box-shadow: 0 0 14px rgba(255, 255, 255, 0.35);
  opacity: 0.55;
  animation: mote-drift 16s ease-in-out infinite;
}
.aura-mote-1 {
  left: 10%;
  top: 20%;
  width: 3px;
  height: 3px;
  animation-delay: 0s;
}
.aura-mote-2 {
  right: 14%;
  top: 28%;
  width: 4px;
  height: 4px;
  animation-delay: -3.5s;
}
.aura-mote-3 {
  left: 22%;
  bottom: 30%;
  width: 2px;
  height: 2px;
  animation-delay: -7s;
}
.aura-mote-4 {
  right: 20%;
  bottom: 24%;
  width: 3px;
  height: 3px;
  animation-delay: -5s;
}
.aura-mote-5 {
  left: 48%;
  top: 12%;
  width: 2px;
  height: 2px;
  opacity: 0.4;
  animation-delay: -9s;
}

@keyframes mote-drift {
  0%,
  100% {
    transform: translate(0, 0);
    opacity: 0.35;
  }
  50% {
    transform: translate(10px, -14px);
    opacity: 0.75;
  }
}

/* 情绪地平线 */
.aura-horizon-line {
  height: 1px;
  width: min(42vw, 200px);
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.08) 15%,
    rgba(255, 255, 255, 0.35) 50%,
    rgba(255, 255, 255, 0.08) 85%,
    transparent
  );
  opacity: 0.65;
  animation: horizon-glow 6s ease-in-out infinite;
}

@keyframes horizon-glow {
  0%,
  100% {
    opacity: 0.45;
    transform: scaleX(0.92);
  }
  50% {
    opacity: 0.85;
    transform: scaleX(1);
  }
}

/* 底沿微光条 */
.aura-mood-line {
  position: relative;
  height: 2px;
  width: min(48vw, 220px);
  overflow: hidden;
  border-radius: 9999px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.12), transparent);
  opacity: 0.55;
}

.aura-mood-line-shimmer {
  position: absolute;
  inset: 0;
  width: 40%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.55),
    rgba(255, 255, 255, 0.2),
    transparent
  );
  animation: mood-shimmer-slide 3.8s cubic-bezier(0.45, 0.05, 0.25, 1) infinite;
}

@keyframes mood-shimmer-slide {
  0% {
    transform: translateX(-120%);
    opacity: 0;
  }
  15% {
    opacity: 1;
  }
  85% {
    opacity: 1;
  }
  100% {
    transform: translateX(320%);
    opacity: 0;
  }
}

/* 主题雾层：全屏轻移，与 blob 错频 */
.aura-mist {
  animation: mist-layer-drift 28s ease-in-out infinite;
}

@keyframes mist-layer-drift {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  40% {
    transform: translate(1.8%, -1.1%) scale(1.03);
  }
  75% {
    transform: translate(-1.2%, 1.4%) scale(0.985);
  }
}

/* 柔焦散景：大光斑慢移，像镜头焦外 */
.aura-bokeh {
  overflow: hidden;
}
.aura-bokeh-dot {
  position: absolute;
  border-radius: 50%;
  filter: blur(42px);
  mix-blend-mode: soft-light;
  pointer-events: none;
}
.aura-bokeh-a {
  width: min(46vw, 240px);
  height: min(46vw, 240px);
  left: 5%;
  top: 14%;
  background: rgba(255, 255, 255, 0.58);
  opacity: 0.44;
  animation: bokeh-drift-a 22s ease-in-out infinite;
}
.aura-bokeh-b {
  width: min(38vw, 200px);
  height: min(38vw, 200px);
  right: 2%;
  bottom: 22%;
  background: rgba(255, 255, 255, 0.48);
  opacity: 0.36;
  animation: bokeh-drift-b 26s ease-in-out infinite;
}
.aura-bokeh-c {
  width: min(34vw, 180px);
  height: min(34vw, 180px);
  left: 38%;
  bottom: 8%;
  background: rgba(255, 255, 255, 0.42);
  opacity: 0.3;
  animation: bokeh-drift-c 19s ease-in-out infinite;
}
@keyframes bokeh-drift-a {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(6%, 4%) scale(1.08);
  }
}
@keyframes bokeh-drift-b {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-5%, -3%) scale(1.06);
  }
}
@keyframes bokeh-drift-c {
  0%,
  100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-4%, 5%) scale(1.04);
  }
}

.aura-grain-svg {
  display: block;
}
.aura-grain {
  mix-blend-mode: overlay;
  animation: grain-live 4.2s ease-in-out infinite;
}

@keyframes grain-live {
  0%,
  100% {
    opacity: 0.16;
  }
  50% {
    opacity: 0.26;
  }
}

.aura-ripple {
  border: 1px solid rgba(255, 255, 255, 0.22);
  animation: aura-ripple-expand 4.2s cubic-bezier(0.22, 1, 0.36, 1) infinite;
}

.aura-ripple--echo {
  animation-delay: -2.15s;
}
@keyframes aura-ripple-expand {
  0% {
    transform: scale(0.9);
    opacity: 0.4;
  }
  88% {
    opacity: 0.03;
  }
  100% {
    transform: scale(1.48);
    opacity: 0;
  }
}

.aura-title {
  text-shadow:
    0 1px 0 rgba(255, 255, 255, 0.48),
    0 12px 36px rgba(15, 23, 42, 0.06);
  font-feature-settings: "kern" 1, "liga" 1;
}

.aura-brand {
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.28);
}

.aura-brand-motion {
  animation: brand-line-pulse 8s ease-in-out infinite;
}

@keyframes brand-line-pulse {
  0%,
  100% {
    opacity: 0.72;
  }
  50% {
    opacity: 0.94;
  }
}

.aura-sub-motion {
  animation: sub-line-breathe 9.5s ease-in-out infinite;
  animation-delay: -2s;
}

@keyframes sub-line-breathe {
  0%,
  100% {
    opacity: 0.62;
    transform: translateY(0);
  }
  50% {
    opacity: 0.82;
    transform: translateY(-1px);
  }
}

.aura-aurora {
  background-size: 220% 220%;
  animation: aurora-flow 12s ease-in-out infinite;
}

@keyframes aurora-flow {
  0%,
  100% {
    background-position: 0% 45%;
    transform: rotate(-1.2deg) scale(1);
  }
  50% {
    background-position: 100% 55%;
    transform: rotate(3.5deg) scale(1.07);
  }
}

.aura-dust {
  background-image: radial-gradient(1px 1px at 20% 30%, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 60% 70%, rgba(255, 255, 255, 0.35), transparent),
    radial-gradient(1px 1px at 80% 20%, rgba(255, 255, 255, 0.4), transparent),
    radial-gradient(1px 1px at 40% 85%, rgba(255, 255, 255, 0.3), transparent);
  background-size: 100% 100%;
  animation:
    dust-twinkle 5s ease-in-out infinite,
    dust-field-drift 18s ease-in-out infinite;
}

@keyframes dust-field-drift {
  0%,
  100% {
    transform: translate(0, 0) rotate(0deg);
  }
  50% {
    transform: translate(1.8%, -2.2%) rotate(0.9deg);
  }
}

@keyframes dust-twinkle {
  0%,
  100% {
    opacity: 0.35;
  }
  50% {
    opacity: 0.55;
  }
}

@keyframes blobs-drift {
  0% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(2.4%, -1.6%) scale(1.05);
  }
  66% {
    transform: translate(-1.8%, 2%) scale(0.975);
  }
  100% {
    transform: translate(0.8%, 1%) scale(1.03);
  }
}

/* 主内容柱：整体轻呼吸，与光球同频错相 */
.aura-stage-motion {
  animation: stage-column-float 11s ease-in-out infinite;
}

@keyframes stage-column-float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.aura-orb-wrap {
  animation: orb-float 5.8s cubic-bezier(0.45, 0.05, 0.3, 1) infinite;
  filter: drop-shadow(0 22px 36px rgba(15, 23, 42, 0.1));
}

@keyframes orb-float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.aura-orb-glow-main {
  animation: orb-glow-pulse 3.2s ease-in-out infinite;
}

.aura-orb-glow-halo {
  background: radial-gradient(circle, rgba(255, 255, 255, 0.38) 0%, transparent 74%);
  animation: orb-glow-halo-soft 5s ease-in-out infinite;
}

@keyframes orb-glow-pulse {
  0%,
  100% {
    opacity: 0.7;
    transform: scale(1.4);
  }
  50% {
    opacity: 1;
    transform: scale(1.55);
  }
}

@keyframes orb-glow-halo-soft {
  0%,
  100% {
    opacity: 0.38;
    transform: scale(1.78);
  }
  50% {
    opacity: 0.72;
    transform: scale(1.92);
  }
}

.aura-ring-sheen {
  border: 1px solid rgba(255, 255, 255, 0.26);
  opacity: 0.52;
  animation: ring-sheen-breathe 4.2s ease-in-out infinite;
}

@keyframes ring-sheen-breathe {
  0%,
  100% {
    opacity: 0.38;
    transform: scale(1);
  }
  50% {
    opacity: 0.62;
    transform: scale(1.015);
  }
}

.aura-orb-sheen {
  z-index: 0;
  background: linear-gradient(
    115deg,
    transparent 0%,
    transparent 30%,
    rgba(255, 255, 255, 0.16) 44%,
    rgba(255, 255, 255, 0.45) 50%,
    rgba(255, 255, 255, 0.18) 56%,
    transparent 70%,
    transparent 100%
  );
  background-size: 240% 240%;
  animation: orb-specular-shift 6.2s ease-in-out infinite;
  opacity: 0.78;
  mix-blend-mode: soft-light;
}

@keyframes orb-specular-shift {
  0%,
  100% {
    background-position: 85% 35%;
  }
  50% {
    background-position: 15% 65%;
  }
}

.sparkle-char {
  display: inline-block;
  animation: sparkle-twinkle 2.7s ease-in-out infinite;
  text-shadow:
    0 0 16px rgba(255, 255, 255, 0.45),
    0 0 2px rgba(255, 255, 255, 0.55);
}

@keyframes sparkle-twinkle {
  0%,
  100% {
    opacity: 0.55;
    transform: translateY(0) scale(0.93) rotate(-6deg);
  }
  50% {
    opacity: 1;
    transform: translateY(-2px) scale(1.07) rotate(5deg);
  }
}

.aura-orb {
  backdrop-filter: blur(10px) saturate(1.08);
  -webkit-backdrop-filter: blur(10px) saturate(1.08);
  animation: orb-breathe 3.1s cubic-bezier(0.45, 0.05, 0.3, 1) infinite;
}

.aura-orb::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 50%;
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.46),
    inset 0 -12px 28px rgba(255, 255, 255, 0.11);
  pointer-events: none;
  z-index: 2;
}

@keyframes orb-breathe {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.045);
  }
}

.aura-ring-outer {
  border: 1px solid transparent;
  animation: ring-spin 12s linear infinite;
}

@keyframes ring-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.aura-phrase-enter-active,
.aura-phrase-leave-active {
  transition:
    opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.58s cubic-bezier(0.18, 1, 0.32, 1),
    filter 0.45s ease;
}

.aura-phrase-enter-from {
  opacity: 0;
  transform: translateY(16px);
  filter: blur(9px);
}

.aura-phrase-leave-to {
  opacity: 0;
  transform: translateY(-12px);
  filter: blur(5px);
}

@media (prefers-reduced-motion: reduce) {
  .aura-shell::before,
  .aura-blobs,
  .aura-bokeh-dot,
  .aura-chroma-breathe,
  .aura-spotlight,
  .aura-mote,
  .aura-horizon-line,
  .aura-mood-line-shimmer,
  .aura-mist,
  .aura-vignette,
  .aura-aurora,
  .aura-dust,
  .aura-stage-motion,
  .aura-brand-motion,
  .aura-sub-motion,
  .aura-orb-wrap,
  .aura-orb-glow-main,
  .aura-orb-glow-halo,
  .aura-ring-sheen,
  .aura-ripple,
  .aura-orb,
  .aura-orb-sheen,
  .aura-ring-outer,
  .sparkle-char {
    animation: none !important;
  }
  .aura-phrase-enter-active,
  .aura-phrase-leave-active {
    transition-duration: 0.12s !important;
  }
  .aura-phrase-enter-from,
  .aura-phrase-leave-to {
    filter: none !important;
    transform: none !important;
  }
  .aura-orb-glow-halo {
    opacity: 0.55;
  }
  .aura-grain {
    opacity: 0.12;
  }
  .aura-chroma-breathe {
    opacity: 0.35;
  }
  .aura-spotlight {
    opacity: 0.65;
  }
}

.aura-overlay-enter-active,
.aura-overlay-leave-active {
  transition: opacity 0.52s cubic-bezier(0.22, 1, 0.36, 1);
}
.aura-overlay-enter-active .aura-stage,
.aura-overlay-leave-active .aura-stage {
  transition:
    opacity 0.58s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.75s cubic-bezier(0.16, 1, 0.3, 1),
    filter 0.55s ease;
}
.aura-overlay-enter-from,
.aura-overlay-leave-to {
  opacity: 0;
}
.aura-overlay-enter-from .aura-stage {
  opacity: 0;
  transform: translateY(20px) scale(0.89);
  filter: blur(8px);
}
.aura-overlay-leave-to .aura-stage {
  opacity: 0;
  transform: translateY(-12px) scale(0.96);
  filter: blur(4px);
}

/* 氛围音：玻璃质感按钮，不抢主视觉 */
.aura-sound-toggle {
  position: absolute;
  bottom: 1.15rem;
  right: 1.15rem;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.85rem;
  height: 2.85rem;
  border-radius: 9999px;
  color: rgba(68, 64, 60, 0.55);
  background: rgba(255, 255, 255, 0.38);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.65) inset,
    0 8px 28px rgba(15, 23, 42, 0.09);
  transition:
    transform 0.22s cubic-bezier(0.22, 1, 0.36, 1),
    background 0.2s ease,
    color 0.2s ease;
}
.aura-sound-toggle:hover {
  transform: scale(1.07);
  color: rgba(68, 64, 60, 0.78);
  background: rgba(255, 255, 255, 0.52);
}
.aura-sound-toggle:active {
  transform: scale(0.98);
}
.aura-sound-icon {
  width: 1.38rem;
  height: 1.38rem;
}
</style>
