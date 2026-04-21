<template>
  <div class="min-h-screen px-3 pb-10">
    <header class="pt-6 pb-4">
      <h2 class="text-lg font-semibold text-center">{{ t("flow.styleSelectTitle") }}</h2>
    </header>
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-w-[1200px] mx-auto">
      <StyleCard v-for="st in styles" :key="st.id" :item="st" @select="goGenerate(st.id)" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { showFailToast } from "vant";
import { fetchConfig, type StyleItem } from "@/api/client";
import StyleCard from "@/components/StyleCard.vue";
import { usePendingStore } from "@/stores/pending";

const router = useRouter();
const { t } = useI18n();
const pending = usePendingStore();
const styles = ref<StyleItem[]>([]);

onMounted(async () => {
  if (!pending.file) {
    router.replace({ name: "home" });
    return;
  }
  const cfg = await fetchConfig();
  styles.value = cfg.styles.filter((s) => !s.id.startsWith("tp_"));
});

function goGenerate(styleId: string) {
  if (!pending.file) {
    showFailToast(t("flow.pickImageFirst"));
    router.replace({ name: "home" });
    return;
  }
  router.push({
    name: "style-generate",
    params: { styleId },
    query: { from: "choose-style" },
  });
}
</script>
