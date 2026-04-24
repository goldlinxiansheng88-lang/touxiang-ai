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
        <h1 class="text-2xl font-bold tracking-tight text-stone-950">Privacy Policy</h1>
        <p class="mt-2 text-sm text-stone-600">
          Effective date: <span class="font-medium">2026-04-24</span>
        </p>
        <p class="mt-4 text-sm leading-relaxed text-stone-700">
          This Privacy Policy explains how Aura / touxiangAI ("we", "us") collects, uses, and shares information when
          you use our AI avatar generation service (the "Service"). This policy is intended to comply with the GDPR
          (EU/UK) and the California Consumer Privacy Act (CCPA/CPRA).
        </p>

        <section class="mt-8 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">1. Who We Are</h2>
          <p>
            Aura / touxiangAI is the provider of the Service. For privacy questions, contact
            <span class="font-medium">support@aurashift.ai</span>.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">2. Information We Collect</h2>
          <ul class="list-disc space-y-1 pl-5">
            <li>
              <span class="font-medium">Content you provide</span>: photos you upload, style selections, and generated
              images ("User Content").
            </li>
            <li>
              <span class="font-medium">Account data</span>: email address and display name if you create an account or
              sign in via OAuth.
            </li>
            <li>
              <span class="font-medium">Usage & device data</span>: device identifiers (e.g., cookie-based ID), IP
              address, browser type, pages/actions, and diagnostic logs.
            </li>
            <li>
              <span class="font-medium">Payment data</span>: we may receive payment status and transaction identifiers
              from payment providers. We do not store full payment card details on our servers.
            </li>
          </ul>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">3. How We Use Information</h2>
          <ul class="list-disc space-y-1 pl-5">
            <li>Provide the Service: upload processing, AI generation, and delivering Output.</li>
            <li>Operate accounts: authentication, security, and fraud prevention.</li>
            <li>Improve the Service: analytics, debugging, and performance optimization.</li>
            <li>Billing: manage credits/subscriptions and handle refunds.</li>
            <li>Compliance: comply with laws and enforce our Terms.</li>
          </ul>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">4. Legal Bases (GDPR)</h2>
          <p>
            Where the GDPR applies, we process personal data under these legal bases: (a) performance of a contract
            (to provide the Service), (b) legitimate interests (security, fraud prevention, improving the Service),
            (c) consent (where required, such as certain cookies), and (d) compliance with legal obligations.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">5. How We Share Information</h2>
          <p>We share information only as needed to run the Service:</p>
          <ul class="list-disc space-y-1 pl-5">
            <li>
              <span class="font-medium">Service providers</span>: hosting, storage, analytics, customer support, and
              email/OAuth providers.
            </li>
            <li>
              <span class="font-medium">AI inference providers</span>: to generate images based on your inputs (your
              uploaded image URL and prompts may be sent to the provider).
            </li>
            <li>
              <span class="font-medium">Payment processors</span>: to process payments and manage subscriptions.
            </li>
            <li>
              <span class="font-medium">Legal</span>: if required by law, or to protect rights, safety, and security.
            </li>
          </ul>
          <p>
            We do not sell personal information. We do not share personal information for cross-context behavioral
            advertising in exchange for money.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">6. Cookies & Similar Technologies</h2>
          <p>
            We use cookies or similar technologies for authentication, security, and to remember preferences (such as
            language). You can control cookies through your browser settings.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">7. Data Retention</h2>
          <p>
            We retain personal data only as long as necessary for the purposes described in this policy, including to
            provide the Service, comply with legal obligations, resolve disputes, and enforce agreements. You may delete
            your account or request deletion as described below.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">8. International Transfers</h2>
          <p>
            Your data may be processed in countries other than your own. Where required, we use appropriate safeguards
            for international transfers (such as standard contractual clauses).
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">9. Security</h2>
          <p>
            We implement reasonable technical and organizational measures to protect personal data. However, no method
            of transmission or storage is 100% secure.
          </p>
        </section>

        <section class="mt-6 space-y-4 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">10. Your Rights (GDPR)</h2>
          <p>
            Where the GDPR applies, you may have rights to access, correct, delete, restrict or object to processing,
            and data portability. You may also withdraw consent at any time where processing is based on consent.
          </p>
          <p>
            You can contact us to exercise these rights. You also have the right to lodge a complaint with your local
            supervisory authority.
          </p>
        </section>

        <section class="mt-6 space-y-4 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">11. Your Rights (CCPA/CPRA)</h2>
          <p>
            California residents may have the right to know what personal information we collect, use, and disclose;
            request deletion; correct inaccurate information; and not be discriminated against for exercising these
            rights.
          </p>
          <p>
            We do not sell your personal information. If we ever engage in "sharing" as defined by CPRA for targeted
            advertising, we will provide a mechanism to opt out.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">12. Children</h2>
          <p>
            The Service is not directed to children under 13, and we do not knowingly collect personal information from
            children under 13. If you believe a child has provided personal information, please contact us.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">13. Changes to This Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. We will post the updated version on this page with a
            new effective date.
          </p>
        </section>

        <section class="mt-6 space-y-3 text-sm leading-relaxed text-stone-700">
          <h2 class="text-base font-semibold text-stone-900">14. Contact</h2>
          <p>
            Email: <span class="font-medium">support@aurashift.ai</span>
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

