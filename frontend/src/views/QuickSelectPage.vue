<template>
  <div class="min-h-screen px-4 py-8 max-w-[min(21rem,calc(100vw-2rem))] mx-auto">
    <h2 class="text-base font-semibold mb-4 text-center">{{ t("quick.title") }}</h2>
    <div class="space-y-3 text-sm">
      <label class="block text-xs text-stone-600">{{ t("quick.scene") }}</label>
      <select v-model="scene" class="w-full rounded-lg border border-stone-200/90 px-2 py-2 text-xs bg-[var(--aura-field)]">
        <option v-for="s in scenes" :key="s.id" :value="s.id">
          {{ s.icon }} {{ quickSceneLabel(s) }}
        </option>
      </select>
      <label class="block text-xs text-stone-600 mt-2">{{ t("quick.style") }}</label>
      <select v-model="style" class="w-full rounded-lg border border-stone-200/90 px-2 py-2 text-xs bg-[var(--aura-field)]">
        <option v-for="st in styles" :key="st.id" :value="st.id">{{ quickStyleName(st) }}</option>
      </select>
      <div class="mt-3">
        <AuraGenerateForm
          :scene-id="scene"
          :style-id="style"
          :style-choices="[]"
          :initial-file="pending.file"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import AuraGenerateForm from "@/components/AuraGenerateForm.vue";
import { fetchConfig, type Scene, type StyleItem } from "@/api/client";
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

onMounted(async () => {
  if (!pending.file) {
    router.replace({ name: "home" });
    return;
  }
  const cfg = await fetchConfig();
  scenes.value = cfg.scenes;
  styles.value = cfg.styles.filter((s) => !s.id.startsWith("tp_"));
  scene.value = pending.scene || "AVATAR";
});
</script>
