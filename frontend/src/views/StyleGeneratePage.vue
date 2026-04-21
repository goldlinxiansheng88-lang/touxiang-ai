<template>
  <div class="min-h-screen px-3 pb-12 pt-6">
    <div v-if="!ready" class="py-16 text-center text-sm text-stone-500">
      {{ t("common.loading") }}
    </div>
    <template v-else>
      <div class="mx-auto mb-5 max-w-[min(26.52rem,calc(100vw-1.5rem))]">
        <button
          type="button"
          class="hover-frame mb-4 inline-flex items-center gap-1 rounded-full border border-stone-200/80 bg-white/80 px-3 py-1.5 text-sm font-medium text-stone-700 shadow-sm"
          @click="goBack"
        >
          ← {{ backLabel }}
        </button>
      </div>

      <div v-if="!styleItem" class="text-center text-sm text-stone-500">
        {{ t("flow.packUnknown") }}
      </div>
      <div
        v-else
        class="mx-auto w-full max-w-[min(26.52rem,calc(100vw-1.5rem))] space-y-4"
      >
        <StyleCard :item="styleItem" variant="hero" />
        <AuraGenerateForm
          :scene-id="sceneIdResolved"
          :style-id="styleId"
          :style-choices="[]"
          :initial-file="initialFile"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import AuraGenerateForm from "@/components/AuraGenerateForm.vue";
import { fetchConfig, type StyleItem } from "@/api/client";
import StyleCard from "@/components/StyleCard.vue";
import { usePendingStore } from "@/stores/pending";
import { useUserSessionStore } from "@/stores/userSession";

const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const pending = usePendingStore();
const session = useUserSessionStore();

const styles = ref<StyleItem[]>([]);
const ready = ref(false);

const styleId = computed(() => String(route.params.styleId || ""));

const from = computed(() => String(route.query.from || "home"));
const packIdQ = computed(() => String(route.query.packId || ""));

const styleItem = computed(() => styles.value.find((s) => s.id === styleId.value) ?? null);

const sceneIdResolved = computed(() => {
  const q = route.query.scene;
  if (typeof q === "string" && q.trim()) return q.trim();
  return pending.scene || "AVATAR";
});

const initialFile = computed(() => (from.value === "choose-style" ? pending.file : null));

const backLabel = computed(() => {
  if (from.value === "pack") return t("flow.styleGenBackPack");
  if (from.value === "choose-style") return t("flow.styleGenBackChoose");
  return t("flow.styleGenBackHome");
});

onMounted(async () => {
  await session.refresh();
  const cfg = await fetchConfig();
  styles.value = cfg.styles;
  ready.value = true;

  if (!styles.value.some((s) => s.id === styleId.value)) {
    router.replace({ name: "home" });
    return;
  }
  if (from.value === "choose-style" && !pending.file) {
    router.replace({ name: "home" });
  }
});

function goBack() {
  if (from.value === "pack" && packIdQ.value) {
    router.push({ name: "pack-explore", params: { packId: packIdQ.value } });
    return;
  }
  if (from.value === "choose-style") {
    router.push({ name: "choose-style" });
    return;
  }
  router.push({ name: "home" });
}
</script>
