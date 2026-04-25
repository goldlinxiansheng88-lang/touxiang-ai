<template>
  <div class="mx-auto w-full max-w-[980px]">
    <header class="mb-5 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold tracking-tight text-stone-950">{{ t("admin.creditsTopup.title") }}</h1>
        <p class="mt-1 text-sm text-stone-600">{{ t("admin.creditsTopup.hint") }}</p>
      </div>
    </header>

    <div v-if="!authorized" class="mb-4 rounded-xl border border-amber-200/70 bg-amber-50 px-4 py-3 text-sm text-amber-950">
      <span v-html="t('admin.creditsTopup.authBanner')" />
    </div>

    <section class="rounded-2xl border border-stone-200/80 bg-white p-4 shadow-sm sm:p-5">
      <div class="grid gap-3 sm:grid-cols-2">
        <label class="block">
          <span class="mb-1 block text-xs font-semibold text-stone-700">{{ t("admin.creditsTopup.publicId") }}</span>
          <div class="flex gap-2">
            <input
              v-model.trim="publicId"
              class="w-full rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm text-stone-900 shadow-sm outline-none focus:border-stone-300"
              :placeholder="t('admin.creditsTopup.publicId')"
            />
            <button
              type="button"
              class="hover-frame inline-flex shrink-0 items-center justify-center rounded-xl bg-stone-900 px-4 py-2 text-sm font-semibold text-white shadow-sm disabled:opacity-40"
              :disabled="lookupBusy || !publicId"
              @click="onLookup"
            >
              {{ t("admin.creditsTopup.lookup") }}
            </button>
          </div>
        </label>
      </div>

      <div v-if="user" class="mt-4 rounded-xl border border-stone-200/70 bg-stone-50/50 p-3 text-sm text-stone-800">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="min-w-0">
            <p class="font-semibold text-stone-900">{{ user.username }}</p>
            <p class="mt-0.5 text-xs text-stone-600">
              UUID: <span class="font-mono">{{ user.id }}</span>
            </p>
            <p v-if="user.created_at" class="mt-0.5 text-xs text-stone-600">
              Created: <span class="font-mono">{{ user.created_at }}</span>
            </p>
          </div>
          <div class="rounded-xl border border-stone-200 bg-white px-3 py-2 text-center shadow-sm">
            <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-stone-500">Credits</p>
            <p class="mt-1 text-lg font-bold tabular-nums text-stone-900">{{ user.credits_balance }}</p>
          </div>
        </div>
      </div>

      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <label class="block">
          <span class="mb-1 block text-xs font-semibold text-stone-700">{{ t("admin.creditsTopup.confirmUsername") }}</span>
          <input
            v-model.trim="confirmUsername"
            class="w-full rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm text-stone-900 shadow-sm outline-none focus:border-stone-300"
            :placeholder="t('admin.creditsTopup.username')"
            :disabled="!user"
          />
        </label>
        <label class="block">
          <span class="mb-1 block text-xs font-semibold text-stone-700">{{ t("admin.creditsTopup.credits") }}</span>
          <input
            v-model.number="credits"
            type="number"
            min="1"
            step="1"
            class="w-full rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm text-stone-900 shadow-sm outline-none focus:border-stone-300"
            :disabled="!user"
          />
        </label>
      </div>

      <label class="mt-3 block">
        <span class="mb-1 block text-xs font-semibold text-stone-700">{{ t("admin.creditsTopup.note") }}</span>
        <textarea
          v-model.trim="note"
          rows="3"
          class="w-full resize-none rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm text-stone-900 shadow-sm outline-none focus:border-stone-300"
          :disabled="!user"
        />
      </label>

      <div class="mt-4 flex items-center justify-end gap-2">
        <button
          type="button"
          class="hover-frame inline-flex items-center justify-center rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-semibold text-stone-800 shadow-sm disabled:opacity-40"
          :disabled="submitBusy"
          @click="reset"
        >
          Reset
        </button>
        <button
          type="button"
          class="hover-frame inline-flex items-center justify-center rounded-xl bg-blush px-5 py-2 text-sm font-semibold text-white shadow-sm ring-1 ring-black/5 disabled:opacity-40"
          :disabled="submitBusy || !canSubmit"
          @click="onSubmit"
        >
          {{ submitBusy ? t("admin.creditsTopup.submitting") : t("admin.creditsTopup.submit") }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { showFailToast, showSuccessToast } from "vant";

import { adminTopupCredits, lookupAdminUserByPublicId, type AdminUserLookup } from "@/api/adminClient";

const { t } = useI18n();

const authorized = computed(() => Boolean(localStorage.getItem("aurashift_admin_token")?.trim()));

const publicId = ref("");
const lookupBusy = ref(false);
const user = ref<AdminUserLookup | null>(null);

const confirmUsername = ref("");
const credits = ref<number>(10);
const note = ref<string>("");
const submitBusy = ref(false);

const canSubmit = computed(() => {
  if (!user.value) return false;
  if (!publicId.value.trim()) return false;
  if (!confirmUsername.value.trim()) return false;
  if (!credits.value || credits.value <= 0) return false;
  return true;
});

async function onLookup() {
  const pid = publicId.value.trim();
  if (!pid) {
    showFailToast(t("admin.creditsTopup.lookupEmpty"));
    return;
  }
  lookupBusy.value = true;
  try {
    user.value = await lookupAdminUserByPublicId(pid);
    // prefill to reduce copy mistakes; still requires operator to retype to submit
    confirmUsername.value = "";
  } catch (e: any) {
    user.value = null;
    const msg = String(e?.response?.data?.detail || e?.message || "");
    if (msg.toLowerCase().includes("not found")) {
      showFailToast(t("admin.creditsTopup.lookupNotFound"));
    } else {
      showFailToast(msg || "Request failed");
    }
  } finally {
    lookupBusy.value = false;
  }
}

async function onSubmit() {
  if (!user.value) return;
  submitBusy.value = true;
  try {
    const res = await adminTopupCredits({
      public_id: publicId.value.trim(),
      confirm_username: confirmUsername.value.trim(),
      credits: Number(credits.value),
      note: note.value || undefined,
    });
    // refresh shown balance
    user.value = await lookupAdminUserByPublicId(publicId.value.trim());
    showSuccessToast(t("admin.creditsTopup.ok", { balance: res.balance_after }));
  } catch (e: any) {
    const msg = String(e?.response?.data?.detail || e?.message || "");
    if (msg.includes("不匹配") || msg.includes("核对")) {
      showFailToast(t("admin.creditsTopup.mismatch"));
    } else {
      showFailToast(msg || "Request failed");
    }
  } finally {
    submitBusy.value = false;
  }
}

function reset() {
  publicId.value = "";
  user.value = null;
  confirmUsername.value = "";
  credits.value = 10;
  note.value = "";
}
</script>

