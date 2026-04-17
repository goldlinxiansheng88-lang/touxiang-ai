<template>
  <div class="min-h-screen bg-[#F8F8F8] px-4 py-8 max-w-md mx-auto">
    <h2 class="text-lg font-semibold mb-6 text-center">{{ t("quick.title") }}</h2>
    <div class="space-y-4">
      <label class="block text-sm text-stone-600">{{ t("quick.scene") }}</label>
      <select v-model="scene" class="w-full rounded-lg border border-stone-200 p-3 bg-white">
        <option v-for="s in scenes" :key="s.id" :value="s.id">
          {{ s.icon }} {{ quickSceneLabel(s) }}
        </option>
      </select>
      <label class="block text-sm text-stone-600 mt-4">{{ t("quick.style") }}</label>
      <select v-model="style" class="w-full rounded-lg border border-stone-200 p-3 bg-white">
        <option v-for="st in styles" :key="st.id" :value="st.id">{{ quickStyleName(st) }}</option>
      </select>
      <button
        type="button"
        class="w-full mt-6 py-3 rounded-full bg-blush text-white font-medium"
        @click="go"
      >
        {{ t("quick.generate") }}
      </button>
    </div>

    <AuraSubmitOverlay :show="submitting" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { showFailToast } from "vant";
import AuraSubmitOverlay from "@/components/AuraSubmitOverlay.vue";
import { createTask, fetchConfig, getApiErrorMessage, type Scene, type StyleItem } from "@/api/client";
import { usePendingStore } from "@/stores/pending";
import { sceneLabel, styleItemName } from "@/utils/i18nDisplay";

const router = useRouter();
const { t, locale, getLocaleMessage } = useI18n();
const pending = usePendingStore();

function quickSceneLabel(s: Scene) {
  return sceneLabel(getLocaleMessage, locale.value, s.id, s.label);
}
function quickStyleName(st: StyleItem) {
  return styleItemName(getLocaleMessage, locale.value, st.id, st.display_name);
}
const scenes = ref<Scene[]>([]);
const styles = ref<StyleItem[]>([]);
const scene = ref("AVATAR");
const style = ref("GHIBLI");
const submitting = ref(false);

onMounted(async () => {
  if (!pending.file) {
    router.replace({ name: "home" });
    return;
  }
  const cfg = await fetchConfig();
  scenes.value = cfg.scenes;
  styles.value = cfg.styles;
  scene.value = pending.scene || "AVATAR";
});

async function go() {
  if (!pending.file) return;
  pending.setPick(scene.value, style.value, pending.file);
  submitting.value = true;
  try {
    const refCookie = document.cookie
      .split("; ")
      .find((r) => r.startsWith("aff_ref="))
      ?.split("=")[1];
    const res = await createTask(
      pending.file,
      scene.value,
      style.value,
      refCookie ? decodeURIComponent(refCookie) : null
    );
    pending.clear();
    await router.replace({ name: "loading", params: { taskId: res.task_id } });
  } catch (e: unknown) {
    submitting.value = false;
    const msg = getApiErrorMessage(e);
    showFailToast(t("errors.createTask", { msg }));
  }
}
</script>
