<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { getPaymentMethods } from '@/api/client'

const { t } = useI18n()

type Billing = 'monthly' | 'yearly'
const billing = ref<Billing>('yearly')

const subscriptionHref = ref<string | null>(null)
const creditsPackHref = ref<string | null>(null)

onMounted(async () => {
  try {
    const m = await getPaymentMethods()
    subscriptionHref.value = m.subscription_checkout_url?.trim() || null
    creditsPackHref.value = m.credits_pack_checkout_url?.trim() || null
  } catch {
    subscriptionHref.value = null
    creditsPackHref.value = null
  }
})

const signupCredits = computed(() => {
  const raw = (import.meta as any).env?.VITE_SIGNUP_CREDITS_BONUS
  const n = Number(raw)
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : 5
})

const starterIncludedKeys = [
  'pricingPage.starter.inc1',
  'pricingPage.starter.inc2',
  'pricingPage.starter.inc3',
] as const
const starterStrikeKeys = ['pricingPage.starter.strike1', 'pricingPage.starter.strike2'] as const

const proFeatureKeys = [
  'pricingPage.pro.f1',
  'pricingPage.pro.f2',
  'pricingPage.pro.f3',
  'pricingPage.pro.f4',
  'pricingPage.pro.f5',
  'pricingPage.pro.f6',
] as const

const maxFeatureKeys = [
  'pricingPage.max.f1',
  'pricingPage.max.f2',
  'pricingPage.max.f3',
  'pricingPage.max.f4',
] as const

const creditRows = computed(() => [
  {
    label: t('pricingPage.tier512'),
    credits: t('pricingPage.tier512Credits'),
    tag: t('pricingPage.tier512Tag'),
  },
  {
    label: t('pricingPage.tier1024'),
    credits: t('pricingPage.tier1024Credits'),
    tag: t('pricingPage.tier1024Tag'),
  },
  {
    label: t('pricingPage.tier2048'),
    credits: t('pricingPage.tier2048Credits'),
    tag: t('pricingPage.tier2048Tag'),
  },
  {
    label: t('pricingPage.tier4096'),
    credits: t('pricingPage.tier4096Credits'),
    tag: t('pricingPage.tier4096Tag'),
  },
])
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50 text-slate-900">
    <div class="mx-auto max-w-[1080px] px-4 py-10 sm:py-14">
      <RouterLink
        to="/"
        class="inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition hover:text-slate-900"
      >
        <span aria-hidden="true">←</span>
        {{ t('pricingPage.back') }}
      </RouterLink>

      <!-- Hero -->
      <header class="mt-8 text-center sm:mt-10">
        <h1 class="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
          {{ t('pricingPage.heroTitle') }}
        </h1>
        <p class="mx-auto mt-3 max-w-2xl text-base text-slate-600 sm:text-lg">
          {{ t('pricingPage.heroSubtitle') }}
        </p>

        <!-- Billing toggle -->
        <div class="mt-8 flex flex-wrap items-center justify-center gap-3">
          <span class="text-sm font-medium text-slate-500">{{ t('pricingPage.billingLabel') }}</span>
          <div
            class="inline-flex rounded-full border border-slate-200 bg-white p-1 shadow-sm"
            role="group"
            :aria-label="t('pricingPage.billingLabel')"
          >
            <button
              type="button"
              class="relative rounded-full px-4 py-2 text-sm font-semibold transition"
              :class="
                billing === 'monthly'
                  ? 'bg-slate-900 text-white shadow'
                  : 'text-slate-600 hover:text-slate-900'
              "
              @click="billing = 'monthly'"
            >
              {{ t('pricingPage.billingMonthly') }}
            </button>
            <button
              type="button"
              class="relative rounded-full px-4 py-2 text-sm font-semibold transition"
              :class="
                billing === 'yearly'
                  ? 'bg-slate-900 text-white shadow'
                  : 'text-slate-600 hover:text-slate-900'
              "
              @click="billing = 'yearly'"
            >
              {{ t('pricingPage.billingYearly') }}
              <span
                class="ml-1.5 inline-flex items-center rounded-full bg-emerald-500 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white"
              >
                {{ t('pricingPage.yearlySaveBadge') }}
              </span>
            </button>
          </div>
        </div>
      </header>

      <!-- Plans -->
      <section class="mt-12 grid gap-6 lg:grid-cols-3 lg:items-stretch">
        <!-- Starter -->
        <article
          class="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div class="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {{ t('pricingPage.planStarter.name') }}
          </div>
          <div class="mt-2 text-3xl font-bold text-slate-900">{{ t('pricingPage.planStarter.price') }}</div>
          <p class="mt-1 text-sm text-slate-500">{{ t('pricingPage.planStarter.subPrice') }}</p>
          <p class="mt-4 rounded-xl bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700">
            {{ t('pricingPage.planStarter.highlight', { credits: signupCredits }) }}
          </p>
          <ul class="mt-5 flex-1 space-y-2 text-sm text-slate-700">
            <li v-for="k in starterIncludedKeys" :key="k" class="flex gap-2">
              <span class="mt-0.5 text-emerald-600" aria-hidden="true">✓</span>
              <span>{{ t(k) }}</span>
            </li>
            <li v-for="k in starterStrikeKeys" :key="k" class="flex gap-2 text-slate-400 line-through">
              <span class="mt-0.5" aria-hidden="true">—</span>
              <span>{{ t(k) }}</span>
            </li>
          </ul>
          <RouterLink
            to="/"
            class="mt-6 inline-flex w-full items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
          >
            {{ t('pricingPage.planStarter.cta') }}
          </RouterLink>
        </article>

        <!-- Pro -->
        <article
          class="relative flex flex-col rounded-2xl border-2 border-blue-500 bg-white p-6 shadow-md ring-4 ring-blue-500/10"
        >
          <span
            class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-blue-600 px-3 py-1 text-xs font-bold uppercase tracking-wide text-white"
          >
            {{ t('pricingPage.planPro.popular') }}
          </span>
          <div class="mt-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
            {{ t('pricingPage.planPro.name') }}
          </div>
          <div class="mt-2 text-3xl font-bold text-slate-900">
            <template v-if="billing === 'yearly'">{{ t('pricingPage.planPro.priceYearly') }}</template>
            <template v-else>{{ t('pricingPage.planPro.priceMonthly') }}</template>
          </div>
          <p v-if="billing === 'yearly'" class="mt-1 text-sm text-emerald-700">
            {{ t('pricingPage.planPro.billedYearly') }}
          </p>
          <p v-else class="mt-1 text-sm text-slate-500">{{ t('pricingPage.planPro.billedMonthly') }}</p>
          <p class="mt-4 rounded-xl bg-blue-50 px-3 py-2 text-sm font-medium text-blue-900">
            {{ t('pricingPage.planPro.highlight') }}
          </p>
          <ul class="mt-5 flex-1 space-y-2 text-sm text-slate-700">
            <li v-for="k in proFeatureKeys" :key="k" class="flex gap-2">
              <span class="mt-0.5 text-emerald-600" aria-hidden="true">✓</span>
              <span>{{ t(k) }}</span>
            </li>
          </ul>
          <a
            v-if="subscriptionHref"
            class="mt-6 inline-flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
            :href="subscriptionHref"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ t('pricingPage.planPro.cta') }}
          </a>
          <button
            v-else
            type="button"
            disabled
            class="mt-6 inline-flex w-full cursor-not-allowed items-center justify-center rounded-xl bg-slate-200 px-4 py-3 text-sm font-semibold text-slate-500"
          >
            {{ t('pricingPage.planPro.cta') }}
          </button>
        </article>

        <!-- Max -->
        <article
          class="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div class="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {{ t('pricingPage.planMax.name') }}
          </div>
          <div class="mt-2 text-3xl font-bold text-slate-900">
            <template v-if="billing === 'yearly'">{{ t('pricingPage.planMax.priceYearly') }}</template>
            <template v-else>{{ t('pricingPage.planMax.priceMonthly') }}</template>
          </div>
          <p v-if="billing === 'yearly'" class="mt-1 text-sm text-emerald-700">
            {{ t('pricingPage.planMax.billedYearly') }}
          </p>
          <p v-else class="mt-1 text-sm text-slate-500">{{ t('pricingPage.planMax.billedMonthly') }}</p>
          <p class="mt-4 rounded-xl bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700">
            {{ t('pricingPage.planMax.highlight') }}
          </p>
          <ul class="mt-5 flex-1 space-y-2 text-sm text-slate-700">
            <li v-for="k in maxFeatureKeys" :key="k" class="flex gap-2">
              <span class="mt-0.5 text-emerald-600" aria-hidden="true">✓</span>
              <span>{{ t(k) }}</span>
            </li>
          </ul>
          <a
            v-if="subscriptionHref"
            class="mt-6 inline-flex w-full items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
            :href="subscriptionHref"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ t('pricingPage.planMax.cta') }}
          </a>
          <button
            v-else
            type="button"
            disabled
            class="mt-6 inline-flex w-full cursor-not-allowed items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-400"
          >
            {{ t('pricingPage.planMax.cta') }}
          </button>
        </article>
      </section>

      <!-- Aura explainer -->
      <section
        class="mt-12 rounded-2xl border border-amber-100 bg-amber-50/80 px-5 py-6 sm:px-8 sm:py-8"
      >
        <h2 class="text-lg font-semibold text-amber-950">{{ t('pricingPage.auraTitle') }}</h2>
        <p class="mt-2 text-sm leading-relaxed text-amber-900/90 sm:text-base">
          {{ t('pricingPage.auraBody') }}
        </p>
        <p class="mt-4 border-l-4 border-amber-300 pl-4 text-sm italic text-amber-900/80 sm:text-base">
          {{ t('pricingPage.auraSample') }}
        </p>
      </section>

      <!-- Top-ups -->
      <section class="mt-14">
        <h2 class="text-center text-xl font-semibold text-slate-900 sm:text-2xl">
          {{ t('pricingPage.topupsTitle') }}
        </h2>
        <p class="mx-auto mt-2 max-w-xl text-center text-sm text-slate-600">
          {{ t('pricingPage.topupsLead') }}
        </p>
        <div class="mt-8 grid gap-4 sm:grid-cols-3">
          <div
            v-for="(pack, idx) in [
              { credits: '100', priceKey: 'pack100Price', labelKey: 'pack100' },
              { credits: '300', priceKey: 'pack300Price', labelKey: 'pack300' },
              { credits: '1000', priceKey: 'pack1000Price', labelKey: 'pack1000' },
            ]"
            :key="idx"
            class="rounded-2xl border border-slate-200 bg-white p-5 text-center shadow-sm"
          >
            <div class="text-2xl font-bold text-slate-900">{{ t(`pricingPage.${pack.labelKey}`) }}</div>
            <div class="mt-2 text-lg font-semibold text-blue-600">{{ t(`pricingPage.${pack.priceKey}`) }}</div>
          </div>
        </div>
        <div class="mt-6 flex justify-center">
          <a
            v-if="creditsPackHref"
            class="inline-flex items-center justify-center rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            :href="creditsPackHref"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ t('pricingPage.linkCreditsPack') }}
          </a>
          <button
            v-else
            type="button"
            disabled
            class="inline-flex cursor-not-allowed items-center justify-center rounded-xl bg-slate-200 px-6 py-3 text-sm font-semibold text-slate-500"
          >
            {{ t('pricingPage.linkCreditsPack') }}
          </button>
        </div>
      </section>

      <!-- Credits breakdown -->
      <section class="mt-14 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <h2 class="text-lg font-semibold text-slate-900 sm:text-xl">{{ t('pricingPage.creditsTitle') }}</h2>
        <p class="mt-2 text-sm text-slate-600">{{ t('pricingPage.creditsLead') }}</p>
        <div class="mt-6 overflow-x-auto">
          <table class="w-full min-w-[520px] border-collapse text-left text-sm">
            <thead>
              <tr class="border-b border-slate-200 text-xs font-semibold uppercase tracking-wide text-slate-500">
                <th class="py-3 pr-4">{{ t('pricingPage.tableColOutput') }}</th>
                <th class="py-3 pr-4">{{ t('pricingPage.tableColCredits') }}</th>
                <th class="py-3">{{ t('pricingPage.tableColNote') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, i) in creditRows"
                :key="i"
                class="border-b border-slate-100 last:border-0"
              >
                <td class="py-3 pr-4 font-medium text-slate-900">{{ row.label }}</td>
                <td class="py-3 pr-4 text-slate-700">{{ row.credits }}</td>
                <td class="py-3 text-slate-500">{{ row.tag }}</td>
              </tr>
              <tr class="border-t border-slate-200">
                <td class="py-3 pr-4 font-medium text-slate-900">{{ t('pricingPage.addonTitle') }}</td>
                <td class="py-3 pr-4 text-slate-700">{{ t('pricingPage.addonCreditsShort') }}</td>
                <td class="py-3 text-slate-500">{{ t('pricingPage.addonNoteShort') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="mt-4 text-xs text-slate-500">{{ t('pricingPage.regenShort') }}</p>
        <p class="mt-2 text-xs text-slate-500">{{ t('pricingPage.signupShort', { credits: signupCredits }) }}</p>
      </section>

      <!-- Guarantees -->
      <section class="mt-14 grid gap-8 border-t border-slate-200 pt-10 sm:grid-cols-3">
        <div>
          <h3 class="text-sm font-semibold text-slate-900">{{ t('pricingPage.guarantee1Title') }}</h3>
          <p class="mt-2 text-sm text-slate-600">{{ t('pricingPage.guarantee1Body') }}</p>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-slate-900">{{ t('pricingPage.guarantee2Title') }}</h3>
          <p class="mt-2 text-sm text-slate-600">{{ t('pricingPage.guarantee2Body') }}</p>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-slate-900">{{ t('pricingPage.guarantee3Title') }}</h3>
          <p class="mt-2 text-sm text-slate-600">{{ t('pricingPage.guarantee3Body') }}</p>
        </div>
      </section>

      <!-- Checkout note + optional second subscribe -->
      <footer class="mt-12 space-y-4 border-t border-slate-200 pt-8 text-center text-xs text-slate-500">
        <p>{{ t('pricingPage.checkoutNote') }}</p>
        <p v-if="!subscriptionHref && !creditsPackHref">{{ t('pricingPage.linksEmpty') }}</p>
        <div v-else class="flex flex-wrap justify-center gap-3">
          <a
            v-if="subscriptionHref"
            class="text-sm font-medium text-blue-600 hover:text-blue-800"
            :href="subscriptionHref"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ t('pricingPage.linkSubscribe') }} →
          </a>
        </div>
      </footer>
    </div>
  </div>
</template>
