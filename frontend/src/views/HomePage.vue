<template>
  <div class="min-h-screen pb-10">
    <header class="relative pt-10 pb-6 px-4">
      <div class="absolute top-3 end-3 z-[60] flex flex-row items-center gap-2 pointer-events-auto">
        <LanguageSelector />
        <button
        type="button"
        class="hover-frame inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-full border border-stone-300 bg-white px-3.5 py-2 text-sm font-semibold text-stone-800 shadow-md ring-1 ring-black/5 hover:bg-stone-50 active:scale-[0.98]"
        :aria-label="session.authenticated ? t('home.account') : t('home.login')"
        @click="session.authenticated ? router.push({ name: 'profile' }) : (showAuth = true)"
      >
        <svg
          class="h-[22px] w-[22px] shrink-0 text-stone-700"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
        <span v-if="!session.authenticated" class="max-w-[4.5rem] truncate">{{ t("home.login") }}</span>
        <span v-else class="max-w-[4.5rem] truncate">{{
          (session.displayName || session.email || t("auth.signedIn")).slice(0, 1).toUpperCase()
        }}</span>
      </button>
      </div>
      <div class="text-center">
        <h1
          class="text-[1.65rem] font-semibold tracking-tight text-stone-900 sm:text-3xl [text-shadow:0_1px_0_rgba(255,255,255,0.55)]"
        >
          {{ t("home.title") }}
        </h1>
        <p class="mt-2 text-[13px] font-medium uppercase tracking-[0.22em] text-stone-500/85 sm:text-sm">
          {{ t("home.tagline") }}
        </p>
      </div>
    </header>

    <UserAuthModal v-model:show="showAuth" @success="session.refresh()" />

    <!-- 与下方风格网格同宽，避免宽屏下分类条铺满全屏而网格居中，看起来像「左侧分类 + 网格上方空白」 -->
    <div class="w-full max-w-[1200px] mx-auto px-3">
      <div class="overflow-x-auto mb-4 no-scrollbar">
        <div class="flex gap-2 min-w-max py-1 justify-start sm:justify-center">
          <button
            v-for="s in scenes"
            :key="s.id"
            type="button"
            class="scene-pill hover-frame"
            :class="{ active: activeScene === s.id }"
            @click="onScenePick(s.id)"
          >
            <span class="mr-1">{{ s.icon }}</span>
            {{ scenePillLabel(s) }}
          </button>
        </div>
      </div>

      <section
        v-if="explorePacksVisible.length"
        class="explore-packs mb-6 w-full border-t border-stone-200/50 px-2 py-7 sm:px-4 sm:py-8"
        aria-labelledby="explore-packs-title"
      >
        <h2
          id="explore-packs-title"
          class="explore-packs-title text-center font-semibold tracking-tight text-stone-800 [text-shadow:0_1px_0_rgba(255,255,255,0.55)]"
        >
          {{ t("home.explorePacks.title") }}
        </h2>
        <div class="explore-packs-cloud mx-auto mt-7 flex max-w-[920px] flex-wrap justify-center gap-x-2 gap-y-3 sm:gap-x-3">
          <button
            v-for="(p, idx) in explorePacksVisible"
            :key="p.id"
            type="button"
            class="explore-chip hover-frame touch-manipulation"
            :class="`explore-chip--s${idx % 5}`"
            @click="goExplorePack(p.id)"
          >
            <span class="explore-chip-emoji" aria-hidden="true">{{ p.emoji }}</span>
            <span class="explore-chip-label">{{ t(p.labelKey) }}</span>
          </button>
        </div>
      </section>

      <div id="aura-style-grid" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 scroll-mt-6">
        <StyleCard v-for="st in stylesForHomeGrid" :key="st.id" :item="st" @select="onStylePick(st.id)" />
      </div>
    </div>

    <AuraGenerateSheet
      v-model="panelOpen"
      :title="panelSheetTitle"
      :scene-id="panelSceneId"
      :style-id="null"
      :style-choices="stylesForHomeGrid"
      :initial-file="null"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { showFailToast } from "vant";
import AuraGenerateSheet from "@/components/AuraGenerateSheet.vue";
import LanguageSelector from "@/components/LanguageSelector.vue";
import UserAuthModal from "@/components/UserAuthModal.vue";
import { fetchConfig, type Scene, type StyleItem } from "@/api/client";
import StyleCard from "@/components/StyleCard.vue";
import { useUserSessionStore } from "@/stores/userSession";
import { filterExplorePacks } from "@/data/explorePacks";
import { sceneLabel } from "@/utils/i18nDisplay";

const router = useRouter();
const { t, locale, getLocaleMessage } = useI18n();
const session = useUserSessionStore();

function scenePillLabel(s: Scene) {
  return sceneLabel(getLocaleMessage, locale.value, s.id, s.label);
}

const showAuth = ref(false);

const scenes = ref<Scene[]>([]);
const styles = ref<StyleItem[]>([]);
/** 首页主网格不展示主题包专用风格（避免 200+ 张挤占首屏） */
const stylesForHomeGrid = computed(() => styles.value.filter((s) => !s.id.startsWith("tp_")));
const explorePacksVisible = computed(() => filterExplorePacks(scenes.value));
const activeScene = ref("AVATAR");

const panelOpen = ref(false);
const panelSceneId = ref("AVATAR");

const panelSheetTitle = computed(() => {
  const sc = scenes.value.find((s) => s.id === panelSceneId.value);
  const sn = sc ? sceneLabel(getLocaleMessage, locale.value, sc.id, sc.label) : "";
  return t("flow.generatePanelTitleScene", { scene: sn });
});

onMounted(async () => {
  const q = new URLSearchParams(window.location.search);
  const ref = q.get("ref");
  if (ref) document.cookie = `aff_ref=${encodeURIComponent(ref)};path=/;max-age=${30 * 24 * 3600}`;
  if (q.get("login") === "ok") {
    await session.refresh();
    window.history.replaceState({}, "", window.location.pathname + window.location.hash);
  }
  const authErr = q.get("auth_error");
  if (authErr) {
    // get() 已是解码后的 UTF-8；再 decodeURIComponent 会在文案含「%」等字符时抛 URIError，打断后续初始化
    showFailToast(t("errors.authCallback", { msg: authErr }));
    window.history.replaceState({}, "", window.location.pathname + window.location.hash);
  }
  await session.refresh();
  const cfg = await fetchConfig();
  scenes.value = cfg.scenes;
  styles.value = cfg.styles;
});

function onScenePick(id: string) {
  activeScene.value = id;
  panelSceneId.value = id;
  panelOpen.value = true;
}

function goExplorePack(packId: string) {
  router.push({ name: "pack-explore", params: { packId } });
}

function onStylePick(styleId: string) {
  router.push({
    name: "style-generate",
    params: { styleId },
    query: { scene: activeScene.value, from: "home" },
  });
}
</script>

<style scoped>
.scene-pill {
  @apply px-4 py-2 rounded-full text-sm font-medium text-stone-700;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(231, 229, 228, 0.85);
  box-shadow:
    inset 0 1px 0 0 rgba(255, 255, 255, 0.9),
    0 1px 2px rgba(28, 25, 23, 0.04),
    0 8px 24px -10px rgba(28, 25, 23, 0.08);
}
.scene-pill:hover:not(.active) {
  border-color: rgba(214, 211, 209, 0.95);
  box-shadow:
    inset 0 1px 0 0 rgba(255, 255, 255, 0.95),
    0 1px 2px rgba(28, 25, 23, 0.05),
    0 12px 32px -12px rgba(28, 25, 23, 0.1);
}
.scene-pill.active {
  @apply border-blush text-stone-800;
  background: rgba(255, 255, 255, 0.88);
  box-shadow:
    inset 0 1px 0 0 rgba(255, 255, 255, 0.95),
    inset 0 -2px 0 0 rgba(220, 38, 38, 0.55),
    0 0 0 1px rgba(220, 38, 38, 0.25),
    0 10px 28px -12px rgba(220, 38, 38, 0.2);
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.explore-packs {
  background: transparent;
}
.explore-packs-title {
  font-size: 1.35rem;
  line-height: 1.25;
}
@media (min-width: 640px) {
  .explore-packs-title {
    font-size: 1.6rem;
  }
}
.explore-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 9999px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  color: #44403c;
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(231, 229, 228, 0.95);
  box-shadow:
    inset 0 1px 0 0 rgba(255, 255, 255, 0.95),
    0 1px 2px rgba(28, 25, 23, 0.05),
    0 6px 20px -8px rgba(28, 25, 23, 0.08);
  transition:
    background-color 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    transform 0.18s ease;
}
.explore-chip:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(214, 211, 209, 0.98);
  box-shadow:
    inset 0 1px 0 0 rgba(255, 255, 255, 1),
    0 1px 2px rgba(28, 25, 23, 0.06),
    0 10px 28px -10px rgba(28, 25, 23, 0.1);
}
.explore-chip:active {
  transform: scale(0.98);
}
.explore-chip-emoji {
  font-size: 1.05rem;
  line-height: 1;
}
.explore-chip-label {
  line-height: 1.2;
}
.explore-chip--s0 {
  transform: translateY(0);
}
.explore-chip--s1 {
  transform: translateY(4px);
}
.explore-chip--s2 {
  transform: translateY(1px);
}
.explore-chip--s3 {
  transform: translateY(5px);
}
.explore-chip--s4 {
  transform: translateY(2px);
}
.explore-chip--s0:hover,
.explore-chip--s1:hover,
.explore-chip--s2:hover,
.explore-chip--s3:hover,
.explore-chip--s4:hover {
  transform: translateY(0) scale(1.01);
}
.explore-chip--s0:active,
.explore-chip--s1:active,
.explore-chip--s2:active,
.explore-chip--s3:active,
.explore-chip--s4:active {
  transform: scale(0.98);
}
</style>
