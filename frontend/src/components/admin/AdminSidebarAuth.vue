<template>
  <div
    id="admin-auth-anchor"
    class="mx-2 mb-2.5 mt-auto shrink-0 rounded-xl border border-white/10 bg-zinc-950/50 px-2.5 py-3.5 shadow-inner sm:mx-2.5"
  >
    <p class="text-[10px] font-semibold uppercase tracking-wider text-zinc-500">{{ t("admin.sidebar.accessControl") }}</p>
    <p class="mt-1 text-[11px] leading-relaxed text-zinc-500">
      {{ t("admin.sidebar.passwordLineBefore") }}
      <code class="rounded bg-zinc-800/90 px-1 py-0.5 font-mono text-[10px] text-zinc-300">ADMIN_PASSWORD</code>
      {{ t("admin.sidebar.passwordLineAfter") }}
    </p>
    <input
      v-model="input"
      type="password"
      autocomplete="off"
      :placeholder="t('admin.sidebar.passwordPlaceholder')"
      class="mb-2 mt-2.5 w-full rounded-lg border border-zinc-600/80 bg-zinc-900/80 px-2.5 py-2 text-sm text-zinc-100 shadow-inner placeholder:text-zinc-600 focus:border-blush/60 focus:outline-none focus:ring-1 focus:ring-blush/30"
      @keydown.enter="save"
    />
    <button
      type="button"
      class="w-full rounded-lg bg-zinc-100 py-2 text-sm font-semibold text-zinc-900 shadow-sm transition hover:bg-white active:scale-[0.99]"
      @click="save"
    >
      {{ t("admin.sidebar.saveAuth") }}
    </button>
    <p v-if="auth.token" class="mt-2 text-[11px] font-medium text-emerald-400/90">{{ t("admin.sidebar.authorized") }}</p>
    <p v-else class="mt-2 text-[11px] text-zinc-500">{{ t("admin.sidebar.unauthorized") }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import { useAdminAuthStore } from "@/stores/adminAuth";

const { t } = useI18n();
const auth = useAdminAuthStore();
const input = ref(auth.token);

watch(
  () => auth.token,
  (tok) => {
    input.value = tok;
  },
);

function save() {
  auth.setToken(input.value);
  window.dispatchEvent(new CustomEvent("aurashift-admin-token-changed"));
}
</script>
