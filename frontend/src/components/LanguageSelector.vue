<template>
  <div ref="root" class="relative">
    <button
      type="button"
      class="inline-flex max-w-[9rem] items-center gap-1 rounded-full border border-stone-300 bg-white px-2.5 py-2 text-xs font-semibold text-stone-800 shadow-sm ring-1 ring-black/5 hover:bg-stone-50 sm:max-w-[11rem] sm:px-3 sm:text-sm"
      :aria-expanded="open"
      aria-haspopup="listbox"
      :aria-label="$t('lang.selector')"
      @click.stop="open = !open"
    >
      <svg
        class="h-4 w-4 shrink-0 text-stone-600"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="10" />
        <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
      </svg>
      <span class="truncate">{{ currentLabel }}</span>
      <span class="text-stone-400" aria-hidden="true">▾</span>
    </button>

    <Transition name="lang-pop">
      <div
        v-if="open"
        class="absolute right-0 top-full z-[110] mt-1 w-[min(100vw-2rem,18rem)] rounded-xl border border-stone-200 bg-white py-1 shadow-lg ring-1 ring-black/5"
        role="listbox"
        @click.stop
      >
        <div class="border-b border-stone-100 px-2 pb-1.5 pt-1">
          <input
            v-model="query"
            type="search"
            autocomplete="off"
            class="w-full rounded-lg border border-stone-200 px-2 py-1.5 text-xs text-stone-900 placeholder:text-stone-400 focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
            :placeholder="$t('lang.search')"
            @keydown.escape.prevent="open = false"
          />
        </div>
        <div class="max-h-60 overflow-y-auto py-0.5">
          <button
            v-for="opt in filteredOptions"
            :key="opt.code"
            type="button"
            role="option"
            class="flex w-full items-center px-3 py-2 text-left text-sm hover:bg-stone-50"
            :class="opt.code === locale ? 'bg-stone-100 font-medium text-stone-900' : 'text-stone-700'"
            @click="select(opt.code)"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import { i18n } from "@/i18n";
import { LANGUAGE_OPTIONS, LOCALE_USER_KEY, SUPPORTED_LOCALE_SET } from "@/locales/languages";
import { applyVantLocale } from "@/utils/localeAdmin";

const { locale } = useI18n();

const open = ref(false);
const query = ref("");
const root = ref<HTMLElement | null>(null);

const currentLabel = computed(() => {
  const code = locale.value as string;
  return LANGUAGE_OPTIONS.find((o) => o.code === code)?.label ?? code;
});

const filteredOptions = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return LANGUAGE_OPTIONS;
  return LANGUAGE_OPTIONS.filter((o) => o.label.toLowerCase().includes(q) || o.code.toLowerCase().includes(q));
});

function applyLocale(code: string) {
  if (!SUPPORTED_LOCALE_SET.has(code)) return;
  locale.value = code;
  i18n.global.locale.value = code;
  document.documentElement.setAttribute("dir", code === "ar" ? "rtl" : "ltr");
  document.documentElement.setAttribute("lang", code.split("-")[0] || "en");
  applyVantLocale(code);
}

function select(code: string) {
  localStorage.setItem(LOCALE_USER_KEY, code);
  applyLocale(code);
  open.value = false;
  query.value = "";
}

function onDocClick(ev: MouseEvent) {
  if (!open.value) return;
  const el = root.value;
  if (el && !el.contains(ev.target as Node)) open.value = false;
}

watch(open, (v) => {
  if (!v) query.value = "";
});

onMounted(() => {
  document.addEventListener("click", onDocClick);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocClick);
});
</script>

<style scoped>
.lang-pop-enter-active,
.lang-pop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.lang-pop-enter-from,
.lang-pop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
