<template>
  <div class="min-h-screen px-3 pb-12">
    <header class="mx-auto max-w-[1200px] pt-8 pb-6">
      <button
        type="button"
        class="hover-frame mb-4 inline-flex items-center gap-1 rounded-full border border-stone-200/80 bg-white/80 px-3 py-1.5 text-sm font-medium text-stone-700 shadow-sm"
        @click="router.push({ name: 'home' })"
      >
        ← {{ t("packsPage.back") }}
      </button>
      <h1 class="text-center text-xl font-semibold tracking-tight text-stone-900 sm:text-2xl">
        {{ t("packsPage.title") }}
      </h1>
      <p class="mx-auto mt-3 max-w-2xl text-center text-sm leading-relaxed text-stone-600">
        {{ t("packsPage.intro") }}
      </p>
    </header>

    <div v-if="!ready" class="text-center text-sm text-stone-500">
      {{ t("common.loading") }}
    </div>
    <div v-else-if="!blocks.length" class="text-center text-sm text-stone-500">
      {{ t("packsPage.empty") }}
    </div>

    <div v-else class="mx-auto max-w-[1200px] space-y-10">
      <section v-for="block in blocks" :key="block.sceneId" class="scroll-mt-8">
        <h2
          class="border-b border-stone-200/70 pb-2 text-center text-xs font-semibold uppercase tracking-[0.22em] text-stone-500 sm:text-sm"
        >
          {{ block.sceneLabel }}
        </h2>
        <div class="mt-4 flex flex-wrap justify-center gap-2 sm:gap-3">
          <button
            v-for="(p, idx) in block.packs"
            :key="p.id"
            type="button"
            class="explore-chip hover-frame touch-manipulation"
            :class="`explore-chip--s${idx % 5}`"
            @click="goPack(p.id)"
          >
            <span class="explore-chip-emoji" aria-hidden="true">{{ p.emoji }}</span>
            <span class="explore-chip-label">{{ t(p.labelKey) }}</span>
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { fetchConfig, type Scene } from "@/api/client";
import { filterExplorePacks, packsGroupedByScene } from "@/data/explorePacks";
import { sceneLabel } from "@/utils/i18nDisplay";

const router = useRouter();
const { t, locale, getLocaleMessage } = useI18n();
const scenes = ref<Scene[]>([]);
const ready = ref(false);

const blocks = computed(() => {
  const packs = filterExplorePacks(scenes.value);
  const order = scenes.value.map((s) => s.id);
  return packsGroupedByScene(packs, order).map((b) => {
    const sc = scenes.value.find((s) => s.id === b.sceneId);
    return {
      sceneId: b.sceneId,
      packs: b.packs,
      sceneLabel: sc ? sceneLabel(getLocaleMessage, locale.value, sc.id, sc.label) : b.sceneId,
    };
  });
});

onMounted(async () => {
  try {
    const cfg = await fetchConfig();
    scenes.value = cfg.scenes;
  } finally {
    ready.value = true;
  }
});

function goPack(packId: string) {
  router.push({ name: "pack-explore", params: { packId } });
}
</script>

<style scoped>
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
