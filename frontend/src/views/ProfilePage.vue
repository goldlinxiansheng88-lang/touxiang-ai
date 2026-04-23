<template>
  <div class="min-h-screen px-4 py-8 pb-16">
    <div class="mx-auto max-w-[760px]">
      <header class="mb-6 flex items-center justify-between gap-3">
        <div class="min-w-0">
          <h1 class="text-xl font-bold tracking-tight text-stone-950">{{ t("profile.title") }}</h1>
          <p class="mt-1 text-xs text-stone-500">{{ t("profile.hint") }}</p>
        </div>
        <button
          v-if="session.authenticated"
          type="button"
          class="hover-frame rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-stone-700 shadow-sm"
          :disabled="busy"
          @click="onLogout"
        >
          {{ busy ? t("auth.loggingOut") : t("auth.logout") }}
        </button>
      </header>

      <div v-if="loading" class="py-12 text-center text-sm text-stone-500">{{ t("common.loading") }}</div>

      <div
        v-else-if="!profile?.user"
        class="rounded-2xl border border-stone-200/70 bg-white p-5 text-sm text-stone-700 shadow-sm"
      >
        <p class="font-medium text-stone-900">{{ t("profile.needLoginTitle") }}</p>
        <p class="mt-1 text-stone-600">{{ t("profile.needLoginHint") }}</p>
        <div class="mt-4">
          <button
            type="button"
            class="hover-frame rounded-xl bg-stone-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm"
            @click="showAuth = true"
          >
            {{ t("home.login") }}
          </button>
        </div>
      </div>

      <div v-else class="space-y-6">
        <section class="rounded-2xl border border-stone-200/70 bg-white p-5 shadow-sm">
          <div class="flex items-start gap-4">
            <div
              class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blush/20 text-lg font-semibold text-stone-800"
            >
              {{ initial }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-semibold text-stone-900">{{ displayName }}</p>
              <p v-if="profile.user.email" class="truncate text-xs text-stone-500">{{ profile.user.email }}</p>
              <div class="mt-3 flex flex-wrap gap-2 text-xs">
                <span
                  class="inline-flex items-center rounded-full border px-2 py-0.5"
                  :class="profile.user.is_vip ? 'border-amber-200 bg-amber-50 text-amber-900' : 'border-stone-200 bg-stone-50 text-stone-600'"
                >
                  {{ profile.user.is_vip ? t("profile.vipYes") : t("profile.vipNo") }}
                </span>
                <span class="inline-flex items-center rounded-full border border-stone-200 bg-stone-50 px-2 py-0.5 text-stone-600">
                  ID: <span class="ml-1 font-mono">{{ profile.user.id.slice(0, 8) }}</span>
                </span>
              </div>
            </div>
          </div>
        </section>

        <section class="rounded-2xl border border-stone-200/70 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <h2 class="text-sm font-semibold text-stone-900">{{ t("profile.myTasks") }}</h2>
            <button
              type="button"
              class="hover-frame rounded-lg border border-stone-200 bg-white px-3 py-1.5 text-xs font-medium text-stone-700"
              :disabled="tasksLoading"
              @click="reloadTasks"
            >
              {{ t("common.refresh") }}
            </button>
          </div>
          <div v-if="tasksLoading" class="py-8 text-center text-sm text-stone-500">{{ t("common.loading") }}</div>
          <div v-else-if="tasks.length === 0" class="py-8 text-center text-sm text-stone-500">{{ t("common.noData") }}</div>
          <ul v-else class="mt-3 divide-y divide-stone-100">
            <li v-for="it in tasks" :key="it.id" class="flex items-center justify-between gap-3 py-3">
              <div class="min-w-0">
                <p class="truncate text-sm text-stone-900">
                  <span class="font-mono text-xs text-stone-600">{{ it.id.slice(0, 8) }}</span>
                  <span class="mx-2 text-stone-300">·</span>
                  <span class="text-stone-700">{{ it.scene }}</span>
                  <span class="mx-2 text-stone-300">·</span>
                  <span class="text-stone-700">{{ it.style }}</span>
                </p>
                <p class="mt-0.5 text-xs text-stone-500">{{ it.created_at ?? "—" }}</p>
              </div>
              <button
                type="button"
                class="hover-frame shrink-0 rounded-lg border border-stone-200 bg-white px-3 py-1.5 text-xs font-medium text-stone-700"
                @click="goTask(it.id)"
              >
                {{ t("profile.view") }}
              </button>
            </li>
          </ul>
        </section>
      </div>
    </div>

    <UserAuthModal v-model:show="showAuth" @success="onAuthSuccess" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

import UserAuthModal from "@/components/UserAuthModal.vue";
import { fetchMyProfile, fetchMyTasks, type MyProfileResponse, type MyTaskRow } from "@/api/client";
import { useUserSessionStore } from "@/stores/userSession";

const { t } = useI18n();
const router = useRouter();
const session = useUserSessionStore();

const loading = ref(true);
const profile = ref<MyProfileResponse | null>(null);
const showAuth = ref(false);
const busy = ref(false);

const tasksLoading = ref(false);
const tasks = ref<MyTaskRow[]>([]);

const displayName = computed(() => {
  const u = (profile.value as any)?.user as MyProfileResponse["user"] | undefined;
  if (!u) return "";
  return (u.display_name || u.email || u.device_id || t("auth.signedIn")).toString();
});

const initial = computed(() => (displayName.value || "?").slice(0, 1).toUpperCase());

async function reloadProfile() {
  loading.value = true;
  try {
    profile.value = await fetchMyProfile();
  } finally {
    loading.value = false;
  }
}

async function reloadTasks() {
  tasksLoading.value = true;
  try {
    const d = await fetchMyTasks({ page: 1, page_size: 20 });
    tasks.value = d.items;
  } finally {
    tasksLoading.value = false;
  }
}

function goTask(id: string) {
  router.push({ name: "result", params: { taskId: id } });
}

async function onLogout() {
  busy.value = true;
  try {
    await session.logout();
    await reloadProfile();
    tasks.value = [];
  } finally {
    busy.value = false;
  }
}

async function onAuthSuccess() {
  await session.refresh();
  await reloadProfile();
  await reloadTasks();
}

onMounted(async () => {
  await session.refresh();
  await reloadProfile();
  await reloadTasks();
});
</script>

