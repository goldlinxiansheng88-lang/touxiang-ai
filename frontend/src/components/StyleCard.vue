<template>
  <component
    :is="isGrid ? 'button' : 'div'"
    :type="isGrid ? 'button' : undefined"
    class="style-card text-left w-full"
    :class="
      isGrid
        ? 'hover-frame group cursor-pointer touch-manipulation rounded-2xl transition-transform active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-blush/60'
        : 'rounded-3xl'
    "
    @click="onRootClick"
  >
    <div
      ref="cardRef"
      class="style-card-hit relative aspect-[2/3] w-full overflow-visible rounded-2xl border border-stone-200/35 bg-white/20 transition-[box-shadow,border-color,transform] duration-300 ease-out"
      :class="
        isGrid
          ? 'pointer-events-auto shadow-[0_1px_2px_rgba(28,25,23,0.04),0_10px_40px_-12px_rgba(28,25,23,0.1)] ring-1 ring-white/30 group-hover:border-stone-200/55 group-hover:shadow-[0_1px_2px_rgba(28,25,23,0.05),0_20px_56px_-16px_rgba(28,25,23,0.16)] group-hover:ring-white/45'
          : 'pointer-events-none rounded-3xl border-stone-200/45 shadow-[0_8px_40px_-12px_rgba(28,25,23,0.18),0_20px_60px_-20px_rgba(28,25,23,0.14)] ring-2 ring-white/45'
      "
      @pointerenter="isGrid ? onPointerEnter : undefined"
      @pointermove="isGrid ? onPointerMove : undefined"
      @pointerleave="isGrid ? onPointerLeave : undefined"
    >
      <div class="absolute inset-0 overflow-hidden" :class="isHero ? 'rounded-3xl' : 'rounded-2xl'">
        <div
          class="pointer-events-none absolute inset-0"
          :style="{ background: gradient }"
          aria-hidden="true"
        />
        <img
          v-if="!imgFailed"
          :key="thumbUrl"
          :src="thumbUrl"
          class="pointer-events-none absolute inset-0 h-full w-full select-none object-cover object-center transition-transform duration-300 ease-out motion-reduce:transition-none"
          :class="isGrid ? 'group-hover:scale-[1.045] motion-reduce:group-hover:scale-100' : ''"
          :alt="displayName"
          draggable="false"
          loading="lazy"
          referrerpolicy="no-referrer"
          @error="imgFailed = true"
        />
        <div
          class="card-gradient pointer-events-none absolute inset-x-0 bottom-0 z-[1]"
          :class="isHero ? 'p-3 pt-12' : 'p-2.5 pt-10'"
        >
          <p
            class="text-white font-medium leading-tight"
            :class="isHero ? 'text-base sm:text-lg' : 'text-sm'"
          >
            {{ displayName }}
          </p>
          <p class="text-white/75 mt-0.5" :class="isHero ? 'text-sm' : 'text-xs'">{{ socialProof }}</p>
        </div>
      </div>
      <!-- 指针在卡片内才显示；移动时 33% 画幅选框随指针平移，静止后锁定为整图边缘 -->
      <div
        v-show="isGrid && pointerInside"
        class="tracking-frame pointer-events-none absolute z-[5] rounded-sm"
        :style="trackingFrameStyle"
        aria-hidden="true"
      >
        <div class="corner corner-tl" aria-hidden="true">
          <span class="corner-stroke corner-stroke--h" />
          <span class="corner-stroke corner-stroke--v" />
        </div>
        <div class="corner corner-tr" aria-hidden="true">
          <span class="corner-stroke corner-stroke--h" />
          <span class="corner-stroke corner-stroke--v" />
        </div>
        <div class="corner corner-bl" aria-hidden="true">
          <span class="corner-stroke corner-stroke--h" />
          <span class="corner-stroke corner-stroke--v" />
        </div>
        <div class="corner corner-br" aria-hidden="true">
          <span class="corner-stroke corner-stroke--h" />
          <span class="corner-stroke corner-stroke--v" />
        </div>
      </div>
      <div v-if="isGrid" v-show="pointerInside" class="action-btn pointer-events-none">{{ t("home.clickToUse") }}</div>
    </div>
  </component>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import type { StyleItem } from "@/types/aura";
import { styleGradient, styleThumbUrl } from "@/data/styleVisuals";
import { styleItemName, styleItemProof } from "@/utils/i18nDisplay";

const props = withDefaults(
  defineProps<{
    item: StyleItem;
    /** grid：可点击列表；hero：生图页大图展示，不可点 */
    variant?: "grid" | "hero";
  }>(),
  { variant: "grid" },
);

const emit = defineEmits<{ select: [] }>();

const { t, locale, getLocaleMessage } = useI18n();

const isGrid = computed(() => props.variant === "grid");
const isHero = computed(() => props.variant === "hero");

function onRootClick() {
  if (isGrid.value) emit("select");
}

const displayName = computed(() =>
  styleItemName(getLocaleMessage, locale.value, props.item.id, props.item.display_name),
);

const socialProof = computed(() =>
  styleItemProof(getLocaleMessage, locale.value, props.item.id, props.item.social_proof),
);

const imgFailed = ref(false);

const cardRef = ref<HTMLElement | null>(null);
/** 指针是否在卡片（图片区域）内；仅此时显示角标 */
const pointerInside = ref(false);
/** 指针静止后：选框贴合整图外缘 */
const frameLocked = ref(false);
/** 浮动选框（px，相对 style-card-hit） */
const frameLeft = ref(0);
const frameTop = ref(0);
const frameW = ref(0);
const frameH = ref(0);
/** L 两臂长度（px），随选框尺寸变化 */
const armPx = ref(20);

let lockTimer: ReturnType<typeof setTimeout> | null = null;
/** 指针静止后多久贴齐整图；越小越快，过小易在慢移时误触发 */
const LOCK_DELAY_MS = 38;

function clamp(n: number, lo: number, hi: number) {
  return Math.min(hi, Math.max(lo, n));
}

function clearLockTimer() {
  if (lockTimer != null) {
    clearTimeout(lockTimer);
    lockTimer = null;
  }
}

function setArmFromFrame(fw: number, fh: number) {
  const m = Math.min(fw, fh);
  armPx.value = Math.round(clamp(m * 0.065, 14, 36));
}

function scheduleLock() {
  clearLockTimer();
  lockTimer = setTimeout(() => {
    applyLockedFrame();
    lockTimer = null;
  }, LOCK_DELAY_MS);
}

function applyLockedFrame() {
  const el = cardRef.value;
  if (!el) return;
  const r = el.getBoundingClientRect();
  const w = r.width;
  const h = r.height;
  if (w <= 0 || h <= 0) return;
  frameLeft.value = 0;
  frameTop.value = 0;
  frameW.value = w;
  frameH.value = h;
  frameLocked.value = true;
  setArmFromFrame(w, h);
}

function updateTrackingFrame(e: PointerEvent) {
  const el = cardRef.value;
  if (!el) return;
  const r = el.getBoundingClientRect();
  const w = r.width;
  const h = r.height;
  if (w <= 0 || h <= 0) return;
  // 与图片同比例，33% 画幅随指针平移（略小于 1 才能贴边内移动）
  const scale = 0.33;
  const fw = w * scale;
  const fh = h * scale;
  const cx = e.clientX - r.left;
  const cy = e.clientY - r.top;
  frameLeft.value = clamp(cx - fw / 2, 0, w - fw);
  frameTop.value = clamp(cy - fh / 2, 0, h - fh);
  frameW.value = fw;
  frameH.value = fh;
  setArmFromFrame(fw, fh);
}

const trackingFrameStyle = computed(() => ({
  left: `${frameLeft.value}px`,
  top: `${frameTop.value}px`,
  width: `${frameW.value}px`,
  height: `${frameH.value}px`,
  "--arm": `${armPx.value}px`,
}));

function onPointerEnter(e: PointerEvent) {
  clearLockTimer();
  pointerInside.value = true;
  frameLocked.value = false;
  updateTrackingFrame(e);
  scheduleLock();
}

function onPointerMove(e: PointerEvent) {
  if (!pointerInside.value) return;
  if (frameLocked.value) {
    frameLocked.value = false;
  }
  clearLockTimer();
  updateTrackingFrame(e);
  scheduleLock();
}

function onPointerLeave() {
  clearLockTimer();
  pointerInside.value = false;
  frameLocked.value = false;
}

onUnmounted(() => {
  clearLockTimer();
});

const gradient = computed(() => styleGradient(props.item.id));
/** 接口下发的 thumbnail_url 优先（与后端一致），否则用内置 Unsplash 映射 */
const thumbUrl = computed(() => {
  const u = props.item.thumbnail_url?.trim();
  if (u && /^https?:\/\//i.test(u)) return u;
  return styleThumbUrl(props.item.id);
});

watch(thumbUrl, () => {
  imgFailed.value = false;
});
</script>

<style scoped>
/* 底部略加深，保证白字在实拍人像上可读 */
.card-gradient {
  background: linear-gradient(to top, rgba(0, 0, 0, 0.72), rgba(0, 0, 0, 0.2) 50%, transparent);
}

.tracking-frame {
  box-sizing: border-box;
}

/* 细线 L 形角标：相对 tracking-frame 四角 */
.corner {
  position: absolute;
  width: calc(var(--arm, 20px) + 4px);
  height: calc(var(--arm, 20px) + 4px);
  pointer-events: none;
}
.corner-stroke {
  position: absolute;
  border-radius: 9999px;
  /* 橙黄，略描边以便在亮/暗背景上都可见 */
  background: #fbbf24;
  box-shadow:
    0 0 0 1px rgba(180, 83, 9, 0.5),
    0 1px 5px rgba(0, 0, 0, 0.28);
}
.corner-stroke--h {
  height: 2px;
  width: var(--arm, 20px);
}
.corner-stroke--v {
  width: 2px;
  height: var(--arm, 20px);
}
.corner-tl {
  top: 0;
  left: 0;
}
.corner-tl .corner-stroke--h {
  top: 0;
  left: 0;
}
.corner-tl .corner-stroke--v {
  top: 0;
  left: 0;
}
.corner-tr {
  top: 0;
  right: 0;
}
.corner-tr .corner-stroke--h {
  top: 0;
  right: 0;
}
.corner-tr .corner-stroke--v {
  top: 0;
  right: 0;
}
.corner-bl {
  bottom: 0;
  left: 0;
}
.corner-bl .corner-stroke--h {
  bottom: 0;
  left: 0;
}
.corner-bl .corner-stroke--v {
  bottom: 0;
  left: 0;
}
.corner-br {
  bottom: 0;
  right: 0;
}
.corner-br .corner-stroke--h {
  bottom: 0;
  right: 0;
}
.corner-br .corner-stroke--v {
  bottom: 0;
  right: 0;
}
.action-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.65);
  letter-spacing: 0.02em;
}
</style>
