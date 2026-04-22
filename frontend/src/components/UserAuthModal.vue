<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 z-[100] flex items-end justify-center sm:items-center bg-black/40 p-4"
      role="dialog"
      aria-modal="true"
      @click.self="close"
    >
      <div
        class="w-full max-w-md rounded-2xl bg-white p-5 shadow-xl max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-stone-900">
            {{ session.authenticated ? t("auth.titleAccount") : t("auth.titleLogin") }}
          </h2>
          <button
            type="button"
            class="hover-frame rounded-lg px-2 py-0.5 text-stone-400 hover:text-stone-700 text-xl leading-none"
            @click="close"
          >
            ×
          </button>
        </div>

        <div v-if="session.authenticated" class="space-y-4">
          <div class="flex items-center gap-3 rounded-xl bg-stone-50 px-4 py-3">
            <div
              class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blush/20 text-lg font-semibold text-stone-800"
            >
              {{ (session.displayName || session.email || "?").slice(0, 1).toUpperCase() }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-stone-900">{{ session.displayName || t("auth.signedIn") }}</p>
              <p v-if="session.email" class="truncate text-xs text-stone-500">{{ session.email }}</p>
            </div>
          </div>
          <button
            type="button"
            class="hover-frame w-full rounded-xl border border-stone-200 py-2.5 text-sm font-medium text-stone-800 hover:bg-stone-50"
            :disabled="busy"
            @click="onLogout"
          >
            {{ busy ? t("auth.loggingOut") : t("auth.logout") }}
          </button>
        </div>

        <template v-else>
        <div class="flex gap-2 mb-4">
          <button
            type="button"
            class="hover-frame flex-1 rounded-xl py-2 text-sm font-medium transition"
            :class="mode === 'login' ? 'bg-stone-900 text-white' : 'bg-stone-100 text-stone-600'"
            @click="mode = 'login'"
          >
            {{ t("auth.loginTab") }}
          </button>
          <button
            type="button"
            class="hover-frame flex-1 rounded-xl py-2 text-sm font-medium transition"
            :class="mode === 'register' ? 'bg-stone-900 text-white' : 'bg-stone-100 text-stone-600'"
            @click="mode = 'register'"
          >
            {{ t("auth.registerTab") }}
          </button>
        </div>

        <form class="space-y-3" @submit.prevent="onEmailSubmit">
          <div>
            <label class="block text-xs font-medium text-stone-500 mb-1">{{ t("auth.email") }}</label>
            <input
              v-model="email"
              type="email"
              autocomplete="email"
              required
              class="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm text-stone-900 focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
              :placeholder="t('auth.emailPlaceholder')"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-stone-500 mb-1">{{ t("auth.password") }}</label>
            <input
              v-model="password"
              type="password"
              autocomplete="current-password"
              required
              minlength="8"
              class="w-full rounded-xl border border-stone-200 px-3 py-2.5 text-sm text-stone-900 focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
              :placeholder="t('auth.passwordPlaceholder')"
            />
          </div>
          <p v-if="err" class="text-xs text-red-600">{{ err }}</p>
          <button
            type="submit"
            class="hover-frame w-full rounded-xl bg-blush py-3 text-sm font-medium text-white shadow-md hover:opacity-95 disabled:opacity-50"
            :disabled="busy"
          >
            {{ busy ? t("auth.submitting") : mode === "login" ? t("auth.emailLogin") : t("auth.registerAndLogin") }}
          </button>
        </form>

        <div class="relative my-5">
          <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-stone-200" /></div>
          <div class="relative flex justify-center text-xs text-stone-400"><span class="bg-white px-2">{{ t("auth.or") }}</span></div>
        </div>

        <div class="space-y-2">
          <button
            type="button"
            class="hover-frame w-full flex items-center justify-center gap-2 rounded-xl border border-stone-200 py-2.5 text-sm font-medium text-stone-800 hover:bg-stone-50"
            @click="goOAuth('/api/auth/oauth/google/start')"
          >
            {{ t("auth.google") }}
          </button>
          <button
            type="button"
            class="hover-frame w-full flex items-center justify-center gap-2 rounded-xl border border-stone-200 py-2.5 text-sm font-medium text-stone-800 hover:bg-stone-50"
            @click="goOAuth('/api/auth/oauth/microsoft/start')"
          >
            {{ t("auth.microsoft") }}
          </button>
        </div>

        <p class="mt-4 text-[11px] leading-relaxed text-stone-400">
          {{ t("auth.oauthHint") }}
          <code class="rounded bg-stone-100 px-1">{{ callbackHint }}</code>
        </p>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import { apiUrl, loginEmail, registerEmail } from "@/api/client";
import { useUserSessionStore } from "@/stores/userSession";

const { t } = useI18n();
const session = useUserSessionStore();

const props = defineProps<{ show: boolean }>();
const emit = defineEmits<{ (e: "update:show", v: boolean): void; (e: "success"): void }>();

const show = computed({
  get: () => props.show,
  set: (v: boolean) => emit("update:show", v),
});

const mode = ref<"login" | "register">("login");
const email = ref("");
const password = ref("");
const busy = ref(false);
const err = ref("");

const callbackHint = "PUBLIC_BASE_URL + /api/auth/oauth/.../callback";

watch(
  () => props.show,
  async (v) => {
    if (v) {
      err.value = "";
      await session.refresh();
    }
  },
);

function close() {
  show.value = false;
}

async function onLogout() {
  busy.value = true;
  try {
    await session.logout();
    emit("success");
    close();
  } finally {
    busy.value = false;
  }
}

function goOAuth(path: string) {
  window.location.href = apiUrl(path);
}

async function onEmailSubmit() {
  err.value = "";
  busy.value = true;
  try {
    if (mode.value === "register") {
      await registerEmail(email.value.trim(), password.value);
    } else {
      await loginEmail(email.value.trim(), password.value);
    }
    await session.refresh();
    emit("success");
    close();
  } catch (e: unknown) {
    const ax = e as { response?: { data?: { detail?: unknown } } };
    const d = ax.response?.data?.detail;
    err.value = typeof d === "string" ? d : t("auth.loginFailed");
  } finally {
    busy.value = false;
  }
}
</script>
