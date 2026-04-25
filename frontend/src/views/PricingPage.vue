<template>
  <div class="min-h-screen px-3 pb-14">
    <header class="mx-auto max-w-[720px] pt-8 pb-4">
      <button
        type="button"
        class="hover-frame mb-4 inline-flex items-center gap-1 rounded-full border border-stone-200/80 bg-white/80 px-3 py-1.5 text-sm font-medium text-stone-700 shadow-sm"
        @click="router.push({ name: 'home' })"
      >
        ← {{ t("pricingPage.back") }}
      </button>
      <h1 class="text-2xl font-bold tracking-tight text-stone-950 sm:text-3xl">
        {{ t("pricingPage.title") }}
      </h1>
      <p class="mt-3 text-sm leading-relaxed text-stone-600">
        {{ t("pricingPage.intro") }}
      </p>
    </header>

    <main class="mx-auto max-w-[720px] space-y-6">
      <section class="rounded-2xl border border-stone-200/80 bg-white/85 p-5 shadow-sm">
        <h2 class="text-base font-semibold text-stone-900">
          {{ t("pricingPage.creditsTitle") }}
        </h2>
        <ul class="mt-3 space-y-2 text-sm text-stone-700">
          <li class="flex justify-between gap-3 border-b border-stone-100 pb-2">
            <span>{{ t("pricingPage.tier512") }}</span>
            <span class="shrink-0 font-medium tabular-nums">{{ t("pricingPage.tier512Credits") }}</span>
          </li>
          <li class="flex justify-between gap-3 border-b border-stone-100 pb-2">
            <span>{{ t("pricingPage.tier1024") }}</span>
            <span class="shrink-0 font-medium tabular-nums">{{ t("pricingPage.tier1024Credits") }}</span>
          </li>
          <li class="flex justify-between gap-3 border-b border-stone-100 pb-2">
            <span>{{ t("pricingPage.tier2048") }}</span>
            <span class="shrink-0 font-medium tabular-nums">{{ t("pricingPage.tier2048Credits") }}</span>
          </li>
          <li class="flex justify-between gap-3 pt-1">
            <span>{{ t("pricingPage.tier4096") }}</span>
            <span class="shrink-0 font-medium tabular-nums">{{ t("pricingPage.tier4096Credits") }}</span>
          </li>
        </ul>
        <p class="mt-4 text-xs leading-relaxed text-stone-500">
          {{ t("pricingPage.addonBg") }}
        </p>
        <p class="mt-2 text-xs leading-relaxed text-stone-500">
          {{ t("pricingPage.regenerate") }}
        </p>
      </section>

      <section class="rounded-2xl border border-stone-200/60 bg-stone-50/80 p-5 text-sm leading-relaxed text-stone-600">
        {{ t("pricingPage.checkoutNote") }}
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

const router = useRouter();
const { t } = useI18n();
</script>
