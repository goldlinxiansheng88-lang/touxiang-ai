<template>
  <div class="min-h-screen px-3 pb-16">
    <header class="mx-auto max-w-[760px] pt-8 pb-2">
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

    <main class="mx-auto max-w-[760px] space-y-5">
      <section class="rounded-2xl border border-stone-200/80 bg-white/90 p-5 shadow-sm">
        <h2 class="text-base font-semibold text-stone-900">
          {{ t("pricingPage.creditsTitle") }}
        </h2>
        <p class="mt-2 text-xs leading-relaxed text-stone-500 sm:text-sm">
          {{ t("pricingPage.creditsLead") }}
        </p>
        <ul class="mt-4 divide-y divide-stone-100 rounded-xl border border-stone-100 bg-stone-50/40 text-sm text-stone-800">
          <li class="flex items-center justify-between gap-3 px-3 py-2.5">
            <span>{{ t("pricingPage.tier512") }}</span>
            <span class="shrink-0 font-semibold tabular-nums text-stone-900">{{ t("pricingPage.tier512Credits") }}</span>
          </li>
          <li class="flex items-center justify-between gap-3 px-3 py-2.5">
            <span>{{ t("pricingPage.tier1024") }}</span>
            <span class="shrink-0 font-semibold tabular-nums text-stone-900">{{ t("pricingPage.tier1024Credits") }}</span>
          </li>
          <li class="flex items-center justify-between gap-3 px-3 py-2.5">
            <span>{{ t("pricingPage.tier2048") }}</span>
            <span class="shrink-0 font-semibold tabular-nums text-stone-900">{{ t("pricingPage.tier2048Credits") }}</span>
          </li>
          <li class="flex items-center justify-between gap-3 px-3 py-2.5">
            <span>{{ t("pricingPage.tier4096") }}</span>
            <span class="shrink-0 font-semibold tabular-nums text-stone-900">{{ t("pricingPage.tier4096Credits") }}</span>
          </li>
        </ul>
      </section>

      <section class="rounded-2xl border border-stone-200/75 bg-white/85 p-5 shadow-sm">
        <h2 class="text-base font-semibold text-stone-900">
          {{ t("pricingPage.addonTitle") }}
        </h2>
        <p class="mt-2 text-sm leading-relaxed text-stone-600">
          {{ t("pricingPage.addonBg") }}
        </p>
      </section>

      <section class="rounded-2xl border border-stone-200/75 bg-white/85 p-5 shadow-sm">
        <h2 class="text-base font-semibold text-stone-900">
          {{ t("pricingPage.regenTitle") }}
        </h2>
        <p class="mt-2 text-sm leading-relaxed text-stone-600">
          {{ t("pricingPage.regenerate") }}
        </p>
      </section>

      <section class="rounded-2xl border border-emerald-200/60 bg-emerald-50/50 p-5 shadow-sm">
        <h2 class="text-base font-semibold text-emerald-950">
          {{ t("pricingPage.signupTitle") }}
        </h2>
        <p class="mt-2 text-sm leading-relaxed text-emerald-900/90">
          {{ t("pricingPage.signupBody", { credits: signupBonusCredits }) }}
        </p>
      </section>

      <section class="rounded-2xl border border-stone-200/75 bg-white/85 p-5 shadow-sm">
        <h2 class="text-base font-semibold text-stone-900">
          {{ t("pricingPage.subscriptionTitle") }}
        </h2>
        <p class="mt-2 text-sm leading-relaxed text-stone-600">
          {{ t("pricingPage.subscriptionBody") }}
        </p>
      </section>

      <section class="rounded-2xl border border-stone-200/60 bg-stone-50/90 p-5 text-sm leading-relaxed text-stone-700">
        <h2 class="text-base font-semibold text-stone-900">
          {{ t("pricingPage.ledgerTitle") }}
        </h2>
        <p class="mt-2">
          {{ t("pricingPage.ledgerBody") }}
        </p>
        <p class="mt-3 text-xs text-stone-500">
          {{ t("pricingPage.checkoutNote") }}
        </p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

const router = useRouter();
const { t } = useI18n();

/** 与 backend/app/services/credits.py grant_signup_bonus_once 中 bonus 常量保持一致 */
const signupBonusCredits = 5;
</script>
