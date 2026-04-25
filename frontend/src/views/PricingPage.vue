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
      <section
        class="rounded-2xl border border-blush/35 bg-gradient-to-b from-white to-rose-50/40 p-5 shadow-sm ring-1 ring-rose-100/60"
      >
        <h2 class="text-base font-semibold text-stone-900">
          {{ t("pricingPage.linksTitle") }}
        </h2>
        <p class="mt-2 text-xs leading-relaxed text-stone-600 sm:text-sm">
          {{ t("pricingPage.linksLead") }}
        </p>
        <div
          class="mt-4 flex flex-wrap items-center justify-center gap-3 sm:justify-start"
        >
          <a
            v-if="subscriptionHref"
            class="hover-frame inline-flex min-h-[44px] items-center justify-center rounded-full bg-blush px-5 py-2.5 text-sm font-semibold text-white shadow-md ring-1 ring-black/10"
            :href="subscriptionHref"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ t("pricingPage.linkSubscribe") }}
          </a>
          <button
            v-else
            type="button"
            class="inline-flex min-h-[44px] items-center justify-center rounded-full bg-blush/60 px-5 py-2.5 text-sm font-semibold text-white/90 shadow-sm ring-1 ring-black/5 opacity-60"
            disabled
          >
            {{ t("pricingPage.linkSubscribe") }}
          </button>

          <a
            v-if="creditsPackHref"
            class="hover-frame inline-flex min-h-[44px] items-center justify-center rounded-full border border-stone-300 bg-white px-5 py-2.5 text-sm font-semibold text-stone-800 shadow-sm"
            :href="creditsPackHref"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ t("pricingPage.linkCreditsPack") }}
          </a>
          <button
            v-else
            type="button"
            class="inline-flex min-h-[44px] items-center justify-center rounded-full border border-stone-300 bg-white px-5 py-2.5 text-sm font-semibold text-stone-800 shadow-sm opacity-60"
            disabled
          >
            {{ t("pricingPage.linkCreditsPack") }}
          </button>
        </div>
        <p
          v-if="linksLoaded && !subscriptionHref && !creditsPackHref"
          class="mt-4 rounded-lg border border-dashed border-stone-200 bg-white/70 px-3 py-2.5 text-sm text-stone-500"
        >
          {{ t("pricingPage.linksEmpty") }}
        </p>
      </section>

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
          {{ t("pricingPage.plansTitle") }}
        </h2>
        <p class="mt-2 text-sm leading-relaxed text-stone-600">
          {{ t("pricingPage.plansLead") }}
        </p>

        <div class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <div class="rounded-2xl border border-stone-200/70 bg-white p-4 shadow-sm">
            <div class="flex items-baseline justify-between gap-2">
              <h3 class="text-sm font-semibold text-stone-900">{{ t("pricingPage.planFree.name") }}</h3>
              <p class="text-sm font-bold text-stone-900">{{ t("pricingPage.planFree.price") }}</p>
            </div>
            <p class="mt-2 text-xs leading-relaxed text-stone-600">{{ t("pricingPage.planFree.desc") }}</p>
          </div>

          <div class="rounded-2xl border border-blush/40 bg-rose-50/40 p-4 shadow-sm ring-1 ring-rose-100/70">
            <div class="flex items-baseline justify-between gap-2">
              <h3 class="text-sm font-semibold text-stone-900">{{ t("pricingPage.planPro.name") }}</h3>
              <p class="text-sm font-bold text-stone-900">{{ t("pricingPage.planPro.price") }}</p>
            </div>
            <p class="mt-2 text-xs leading-relaxed text-stone-600">{{ t("pricingPage.planPro.desc") }}</p>
            <p class="mt-2 text-xs font-semibold text-stone-800">{{ t("pricingPage.planPro.credits") }}</p>
          </div>

          <div class="rounded-2xl border border-stone-200/70 bg-white p-4 shadow-sm">
            <div class="flex items-baseline justify-between gap-2">
              <h3 class="text-sm font-semibold text-stone-900">{{ t("pricingPage.planMax.name") }}</h3>
              <p class="text-sm font-bold text-stone-900">{{ t("pricingPage.planMax.price") }}</p>
            </div>
            <p class="mt-2 text-xs leading-relaxed text-stone-600">{{ t("pricingPage.planMax.desc") }}</p>
            <p class="mt-2 text-xs font-semibold text-stone-800">{{ t("pricingPage.planMax.credits") }}</p>
          </div>
        </div>
      </section>

      <section class="rounded-2xl border border-stone-200/75 bg-white/85 p-5 shadow-sm">
        <h2 class="text-base font-semibold text-stone-900">
          {{ t("pricingPage.packsTitle") }}
        </h2>
        <p class="mt-2 text-sm leading-relaxed text-stone-600">
          {{ t("pricingPage.packsLead") }}
        </p>
        <ul class="mt-4 divide-y divide-stone-100 rounded-xl border border-stone-100 bg-stone-50/40 text-sm text-stone-800">
          <li class="flex items-center justify-between gap-3 px-3 py-2.5">
            <span>{{ t("pricingPage.pack100") }}</span>
            <span class="shrink-0 font-semibold tabular-nums text-stone-900">{{ t("pricingPage.pack100Price") }}</span>
          </li>
          <li class="flex items-center justify-between gap-3 px-3 py-2.5">
            <span>{{ t("pricingPage.pack300") }}</span>
            <span class="shrink-0 font-semibold tabular-nums text-stone-900">{{ t("pricingPage.pack300Price") }}</span>
          </li>
          <li class="flex items-center justify-between gap-3 px-3 py-2.5">
            <span>{{ t("pricingPage.pack1000") }}</span>
            <span class="shrink-0 font-semibold tabular-nums text-stone-900">{{ t("pricingPage.pack1000Price") }}</span>
          </li>
        </ul>
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
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { getPaymentMethods } from "@/api/client";

const router = useRouter();
const { t } = useI18n();

/** 与 backend/app/services/credits.py grant_signup_bonus_once 中 bonus 常量保持一致 */
const signupBonusCredits = 5;

const linksLoaded = ref(false);
const subscriptionHref = ref<string | null>(null);
const creditsPackHref = ref<string | null>(null);

onMounted(async () => {
  try {
    const m = await getPaymentMethods();
    const pl = m.pricing_links;
    subscriptionHref.value = pl?.subscription ?? null;
    creditsPackHref.value = pl?.credits_pack ?? null;
  } catch {
    subscriptionHref.value = null;
    creditsPackHref.value = null;
  } finally {
    linksLoaded.value = true;
  }
});
</script>
