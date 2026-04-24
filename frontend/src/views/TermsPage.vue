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
        <h1 class="text-2xl font-bold tracking-tight text-stone-950">Terms of Service</h1>
        <p class="mt-2 text-sm text-stone-600">
          Effective date: <span class="font-medium">2026-04-24</span>
        </p>
        <p class="mt-4 text-sm leading-relaxed text-stone-700">
          These Terms of Service ("Terms") govern your access to and use of Aura / touxiangAI (the "Service"), an AI
          avatar generation product that lets you upload a photo and generate stylized avatar images.
          By accessing or using the Service, you agree to these Terms.
        </p>

        <section class="mt-8 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">1. Eligibility</h2>
          <p>
            You must be at least 13 years old to use the Service. If you are under the age of majority in your
            jurisdiction, you may use the Service only with the consent of a parent or legal guardian.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">2. Accounts</h2>
          <p>
            You may use the Service as a guest or via an account. You are responsible for maintaining the security of
            your account and for all activities that occur under your account.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">3. User Content (Your Photos)</h2>
          <p>
            You retain ownership of the photos you upload ("User Content"). You represent and warrant that you have all
            rights necessary to upload and use the User Content with the Service, including consent from any person
            appearing in the photo.
          </p>
          <p>
            You grant us a limited, worldwide, non-exclusive license to host, store, reproduce, and process your User
            Content solely to provide and improve the Service (including generating images, troubleshooting, and fraud
            prevention). This license ends when you delete your User Content or account, except where retention is
            required by law or for legitimate business purposes described in our Privacy Policy.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">4. Generated Output</h2>
          <p>
            The Service produces AI-generated images based on your inputs ("Output"). Output may be similar to content
            generated for other users. You are responsible for how you use Output and for ensuring it complies with
            applicable laws and third-party rights.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">5. Prohibited Use</h2>
          <ul class="list-disc space-y-1 pl-5">
            <li>Uploading content you do not have rights to use, or that violates privacy rights.</li>
            <li>Using the Service to generate illegal content, harassment, or non-consensual imagery.</li>
            <li>Attempting to reverse engineer, scrape, or disrupt the Service.</li>
            <li>Bypassing usage limits, abusing credits, or engaging in fraud/chargeback abuse.</li>
          </ul>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">6. Pricing, Credits, and Subscriptions</h2>
          <p>
            The Service may be offered through credit packs and/or subscription plans. Credits are consumed when
            generating Output. Plan details, pricing, and renewal terms are shown at checkout.
          </p>
          <p>
            Unless otherwise stated, subscriptions renew automatically until cancelled. You can cancel at any time and
            your cancellation will take effect at the end of the current billing period.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">7. Refunds</h2>
          <p>
            Refunds are governed by our Refund Policy at <a class="underline" href="/refund">/refund</a>.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">8. Intellectual Property</h2>
          <p>
            The Service, including its software, design, and branding, is owned by Aura / touxiangAI or its licensors
            and is protected by applicable intellectual property laws. You may not use our trademarks without prior
            written permission.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">9. Disclaimer</h2>
          <p>
            The Service is provided "as is" and "as available" without warranties of any kind. We do not warrant that
            the Service will be uninterrupted, error-free, or that Output will meet your expectations.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">10. Limitation of Liability</h2>
          <p>
            To the maximum extent permitted by law, Aura / touxiangAI will not be liable for any indirect, incidental,
            special, consequential, or punitive damages, or any loss of profits or data, arising from your use of the
            Service. Our total liability for any claim will not exceed the amount you paid to use the Service in the
            3 months preceding the event giving rise to the claim.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">11. Termination</h2>
          <p>
            We may suspend or terminate your access to the Service if you violate these Terms or if necessary to
            protect the Service, users, or third parties. You may stop using the Service at any time.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">12. Changes</h2>
          <p>
            We may update these Terms from time to time. If changes are material, we will provide reasonable notice by
            posting the updated Terms on this page. Continued use of the Service after changes become effective means
            you accept the updated Terms.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">13. Contact</h2>
          <p>
            Questions about these Terms? Contact us at <span class="font-medium">support@aurashift.ai</span>.
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

