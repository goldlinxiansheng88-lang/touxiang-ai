<template>
  <div class="min-h-screen pb-10 bg-[#F8F8F8]">
    <header class="relative pt-10 pb-6 px-4">
      <div class="absolute top-3 end-3 z-20 flex flex-row items-center gap-2">
        <LanguageSelector />
        <button
        type="button"
        class="inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-full border border-stone-300 bg-white px-3.5 py-2 text-sm font-semibold text-stone-800 shadow-md ring-1 ring-black/5 hover:bg-stone-50 active:scale-[0.98]"
        :aria-label="session.authenticated ? t('home.account') : t('home.login')"
        @click="showAuth = true"
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
        <h1 class="text-2xl font-semibold tracking-tight text-stone-800">{{ t("home.title") }}</h1>
        <p class="text-sm text-stone-500 mt-1">{{ t("home.tagline") }}</p>
      </div>
    </header>

    <UserAuthModal v-model:show="showAuth" @success="session.refresh()" />

    <div class="overflow-x-auto px-3 mb-4 no-scrollbar">
      <div class="flex gap-2 min-w-max py-1">
        <button
          v-for="s in scenes"
          :key="s.id"
          type="button"
          class="scene-pill"
          :class="{ active: activeScene === s.id }"
          @click="onScenePick(s.id)"
        >
          <span class="mr-1">{{ s.icon }}</span>
          {{ scenePillLabel(s) }}
        </button>
      </div>
    </div>

    <div
      class="px-3 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-w-[1200px] mx-auto"
    >
      <StyleCard v-for="st in styles" :key="st.id" :item="st" @select="onStylePick(st.id)" />
    </div>

    <input ref="fileScene" type="file" accept="image/*" class="hidden" @change="onFile($event, 'scene')" />
    <input ref="fileStyle" type="file" accept="image/*" class="hidden" @change="onFile($event, 'style')" />

    <AuraSubmitOverlay :show="submitting" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import Compressor from "compressorjs";
import { showFailToast } from "vant";
import AuraSubmitOverlay from "@/components/AuraSubmitOverlay.vue";
import LanguageSelector from "@/components/LanguageSelector.vue";
import UserAuthModal from "@/components/UserAuthModal.vue";
import { createTask, fetchConfig, getApiErrorMessage, type Scene, type StyleItem } from "@/api/client";
import StyleCard from "@/components/StyleCard.vue";
import { usePendingStore } from "@/stores/pending";
import { useUserSessionStore } from "@/stores/userSession";
import { sceneLabel } from "@/utils/i18nDisplay";

const router = useRouter();
const { t, locale, getLocaleMessage } = useI18n();
const pending = usePendingStore();
const session = useUserSessionStore();

function scenePillLabel(s: Scene) {
  return sceneLabel(getLocaleMessage, locale.value, s.id, s.label);
}

const showAuth = ref(false);

const scenes = ref<Scene[]>([]);
const styles = ref<StyleItem[]>([]);
const activeScene = ref("AVATAR");
const fileScene = ref<HTMLInputElement | null>(null);
const fileStyle = ref<HTMLInputElement | null>(null);
const sceneIntent = ref<string | null>(null);
const submitting = ref(false);

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
    showFailToast(t("errors.authCallback", { msg: decodeURIComponent(authErr) }));
    window.history.replaceState({}, "", window.location.pathname + window.location.hash);
  }
  await session.refresh();
  const cfg = await fetchConfig();
  scenes.value = cfg.scenes;
  styles.value = cfg.styles;
});

function onScenePick(id: string) {
  activeScene.value = id;
  sceneIntent.value = id;
  fileScene.value?.click();
}

function onStylePick(styleId: string) {
  pending.setPick(activeScene.value, styleId, null);
  fileStyle.value?.click();
}

function compress(file: File): Promise<File> {
  return new Promise((resolve, reject) => {
    new Compressor(file, {
      maxWidth: 1024,
      maxHeight: 1024,
      maxSizeMB: 5,
      success: (result) => {
        const blob = result as Blob;
        const name = file.name.replace(/\.[^.]+$/, "") + ".jpg";
        resolve(new File([blob], name, { type: blob.type || "image/jpeg" }));
      },
      error: reject,
    });
  });
}

async function onFile(ev: Event, kind: "scene" | "style") {
  const input = ev.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  if (!file) return;
  const f = await compress(file);
  if (kind === "scene") {
    pending.setPick(sceneIntent.value || activeScene.value, null, f);
    router.push({ name: "choose-style" });
  } else {
    if (!pending.style) return;
    pending.setPick(pending.scene, pending.style, f);
    submitting.value = true;
    try {
      const refCookie = document.cookie
        .split("; ")
        .find((r) => r.startsWith("aff_ref="))
        ?.split("=")[1];
      const res = await createTask(
        pending.file!,
        pending.scene,
        pending.style!,
        refCookie ? decodeURIComponent(refCookie) : null
      );
      pending.clear();
      await router.push({ name: "loading", params: { taskId: res.task_id } });
    } catch (e: unknown) {
      submitting.value = false;
      const msg = getApiErrorMessage(e);
      showFailToast(t("errors.createTask", { msg }));
    }
  }
}
</script>

<style scoped>
.scene-pill {
  @apply px-4 py-2 rounded-full text-sm bg-white/80 backdrop-blur border border-stone-200/60 text-stone-700;
}
.scene-pill.active {
  @apply border-blush ring-2 ring-blush/30;
  box-shadow: inset 0 -2px 0 0 #d4a5a5;
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>
