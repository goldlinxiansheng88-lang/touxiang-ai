<template>
  <div class="min-h-screen px-3 pb-10">
    <header class="mx-auto max-w-[1200px] pt-6 pb-4">
      <button
        type="button"
        class="hover-frame mb-4 inline-flex items-center gap-1 rounded-full border border-stone-200/80 bg-white/80 px-3 py-1.5 text-sm font-medium text-stone-700 shadow-sm"
        @click="router.push({ name: 'home' })"
      >
        ← {{ t("flow.packExploreBack") }}
      </button>
      <h1 class="text-center text-lg font-semibold text-stone-900 sm:text-xl">
        {{ pageTitle }}
      </h1>
      <p class="mx-auto mt-2 max-w-lg text-center text-xs text-stone-500 sm:text-sm">
        {{ t("flow.packExploreHint") }}
      </p>
    </header>

    <div v-if="!packIdValid" class="text-center text-sm text-stone-500">
      {{ t("flow.packUnknown") }}
    </div>
    <div v-else class="mx-auto grid max-w-[1200px] grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
      <StyleCard v-for="st in packStyles" :key="st.id" :item="st" @select="goGenerate(st.id)" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { fetchConfig, type StyleItem } from "@/api/client";
import StyleCard from "@/components/StyleCard.vue";
import { stylePrefixForExplorePack } from "@/data/packCodes";
import { useUserSessionStore } from "@/stores/userSession";

const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const session = useUserSessionStore();

const packId = computed(() => String(route.params.packId || ""));
const packIdValid = computed(() => Boolean(stylePrefixForExplorePack(packId.value)));

const allStyles = ref<StyleItem[]>([]);

const packStyles = computed(() => {
  const p = stylePrefixForExplorePack(packId.value);
  if (!p) return [];
  return allStyles.value.filter((s) => s.id.startsWith(`tp_${p}_`));
});

const pageTitle = computed(() => {
  if (!packIdValid.value) return t("flow.packUnknown");
  const labelKey = `home.explorePacks.${packId.value}`;
  const packLabel = t(labelKey);
  return t("flow.packExploreTitle", { pack: packLabel });
});

onMounted(async () => {
  await session.refresh();
  const cfg = await fetchConfig();
  allStyles.value = cfg.styles;
});

function goGenerate(styleId: string) {
  router.push({
    name: "style-generate",
    params: { styleId },
    query: { from: "pack", packId: packId.value },
  });
}
</script>
