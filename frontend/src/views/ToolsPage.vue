<template>
  <div class="min-h-screen px-3 pb-14">
    <header class="mx-auto max-w-[860px] pt-8 pb-4">
      <button
        type="button"
        class="hover-frame mb-4 inline-flex items-center gap-1 rounded-full border border-stone-200/80 bg-white/80 px-3 py-1.5 text-sm font-medium text-stone-700 shadow-sm"
        @click="router.push({ name: 'home' })"
      >
        ← {{ t("toolsPage.back") }}
      </button>
      <h1 class="text-2xl font-bold tracking-tight text-stone-950 sm:text-3xl">
        {{ t("toolsPage.title") }}
      </h1>
      <p class="mt-2 text-sm text-stone-600">
        {{ t("toolsPage.subtitle") }}
      </p>
      <p class="mt-4 rounded-xl border border-amber-200/80 bg-amber-50/90 px-3 py-2 text-xs leading-relaxed text-amber-950">
        {{ t("toolsPage.disclaimer") }}
      </p>
    </header>

    <main class="mx-auto max-w-[860px] space-y-4">
      <article
        v-for="key in cardKeys"
        :key="key"
        class="rounded-2xl border border-stone-200/80 bg-white/80 p-5 shadow-sm backdrop-blur-sm"
      >
        <div class="flex flex-wrap items-baseline justify-between gap-2">
          <h2 class="text-base font-semibold text-stone-900">
            {{ t(`toolsPage.cards.${key}.title`) }}
          </h2>
          <span class="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-stone-600">
            {{ t(`toolsPage.cards.${key}.tag`) }}
          </span>
        </div>
        <p class="mt-2 text-sm font-medium text-stone-700">
          {{ t(`toolsPage.cards.${key}.pain`) }}
        </p>
        <p class="mt-2 text-sm leading-relaxed text-stone-600">
          {{ t(`toolsPage.cards.${key}.stack`) }}
        </p>
        <p class="mt-2 text-sm leading-relaxed text-stone-600">
          {{ t(`toolsPage.cards.${key}.product`) }}
        </p>
      </article>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

const router = useRouter();
const { t } = useI18n();

const cardKeys = [
  "objectRemover",
  "restoreUpscale",
  "beauty",
  "bgRemove",
  "faceSwap",
] as const;
</script>
