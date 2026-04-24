<template>
  <div class="min-h-screen px-4 py-8 pb-16">
    <div class="mx-auto max-w-[860px]">
      <header class="mb-6 flex items-center justify-between gap-3">
        <button
          type="button"
          class="hover-frame inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-medium text-stone-700 shadow-sm"
          @click="goBack"
        >
          <span aria-hidden="true">←</span>
          Back
        </button>
        <a href="/" class="text-xs font-semibold uppercase tracking-[0.18em] text-stone-500">Aura / touxiangAI</a>
      </header>

      <main class="rounded-2xl border border-stone-200/70 bg-white p-6 shadow-sm sm:p-8">
        <h1 class="text-2xl font-bold tracking-tight text-stone-950">Refund Policy</h1>
        <p class="mt-2 text-sm text-stone-600">
          Effective date: <span class="font-medium">2026-04-24</span>
        </p>

        <p class="mt-4 text-sm leading-relaxed text-stone-700">
          Aura / touxiangAI provides digital services (AI avatar generation). This policy explains when refunds are
          available for credit packs and subscriptions.
        </p>

        <section class="mt-8 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">1. General Rule</h2>
          <p class="font-medium text-stone-900">
            Because generated images are delivered immediately as a digital service, purchases are generally
            non-refundable once generation has succeeded.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">2. Full Refund for Generation Failures</h2>
          <p>
            If the Service fails to generate Output after you submit a request (for example, a platform error or
            repeated processing failures) and we are unable to deliver the generated images, we will provide a full
            refund for the affected credits or charge.
          </p>
          <p>
            We may verify failure by checking task logs, error codes, and delivery status. Where possible, we may offer
            a retry or credit restoration as the fastest resolution.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">3. Credit Packs</h2>
          <ul class="list-disc space-y-1 pl-5">
            <li>Unused credits may be refundable only where required by law or where generation fails.</li>
            <li>Credits consumed for successful generation are not refundable.</li>
          </ul>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">4. Subscriptions</h2>
          <ul class="list-disc space-y-1 pl-5">
            <li>You can cancel a subscription at any time. Cancellation takes effect at the end of the billing period.</li>
            <li>We do not provide refunds for partial subscription periods except where required by law or for generation failures.</li>
          </ul>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">5. Chargebacks & Fraud</h2>
          <p>
            If you initiate a chargeback without contacting support first, we may suspend access to the Service pending
            resolution. Fraudulent chargebacks may result in account termination.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">6. How to Request a Refund</h2>
          <p>
            Email <span class="font-medium">support@aurashift.ai</span> with:
          </p>
          <ul class="list-disc space-y-1 pl-5">
            <li>Your account email (if applicable)</li>
            <li>Order/transaction ID (if available)</li>
            <li>The task ID(s) that failed</li>
            <li>A brief description of the issue</li>
          </ul>
          <p>
            We typically respond within 3–5 business days.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">7. Policy Updates</h2>
          <p>
            We may update this Refund Policy from time to time. Updates will be posted on this page with a new
            effective date.
          </p>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();
function goBack() {
  if (window.history.length > 1) router.back();
  else router.push({ name: "home" });
}
</script>

