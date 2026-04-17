<template>
  <div class="min-h-screen bg-[#F8F8F8] px-3 pb-10">
    <header class="pt-6 pb-4">
      <h2 class="text-lg font-semibold text-center">{{ t("flow.styleSelectTitle") }}</h2>
    </header>
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-w-[1200px] mx-auto">
      <StyleCard v-for="st in styles" :key="st.id" :item="st" @select="pick(st.id)" />
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
import { createTask, fetchConfig, getApiErrorMessage, type StyleItem } from "@/api/client";
import StyleCard from "@/components/StyleCard.vue";
import { usePendingStore } from "@/stores/pending";

const router = useRouter();
const { t } = useI18n();
const pending = usePendingStore();
const styles = ref<StyleItem[]>([]);
const submitting = ref(false);

onMounted(async () => {
  if (!pending.file) {
    router.replace({ name: "home" });
    return;
  }
  const cfg = await fetchConfig();
  styles.value = cfg.styles;
});

async function pick(styleId: string) {
  if (!pending.file) {
    showFailToast(t("flow.pickImageFirst"));
    router.replace({ name: "home" });
    return;
  }
  submitting.value = true;
  try {
    pending.setPick(pending.scene, styleId, pending.file);
    const refCookie = document.cookie
      .split("; ")
      .find((r) => r.startsWith("aff_ref="))
      ?.split("=")[1];
    const res = await createTask(
      pending.file,
      pending.scene,
      styleId,
      refCookie ? decodeURIComponent(refCookie) : null
    );
    pending.clear();
    await router.replace({ name: "loading", params: { taskId: res.task_id } });
  } catch (e: unknown) {
    submitting.value = false;
    const msg = getApiErrorMessage(e);
    showFailToast(t("flow.createFailedApi", { msg }));
  }
}
</script>
