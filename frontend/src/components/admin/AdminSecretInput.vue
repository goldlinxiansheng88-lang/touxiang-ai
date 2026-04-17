<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

import { fieldAccentClass } from "@/utils/configFieldUi";

const { t } = useI18n();

const model = defineModel<string>({ default: "" });

const props = withDefaults(
  defineProps<{
    disabled?: boolean;
    placeholder?: string;
    /** 追加到默认 input 上的类（如分项表单的 splitFieldClass） */
    extraInputClass?: string;
    autocomplete?: string;
    /** 分项/通用：右侧竖条 + 与整页「必填/选填」一致 */
    mark?: "required" | "optional";
  }>(),
  { autocomplete: "new-password" },
);

const visible = ref(false);

const inputClass =
  "w-full rounded-xl border border-stone-200 bg-white py-2.5 pl-3 pr-10 font-mono text-sm text-stone-900 shadow-sm transition focus:border-stone-400 focus:outline-none focus:ring-2 focus:ring-stone-900/10 disabled:cursor-not-allowed disabled:bg-stone-100 disabled:text-stone-500";

const accentClass = computed(() => {
  if (props.mark === "required") return fieldAccentClass(true);
  if (props.mark === "optional") return fieldAccentClass(false);
  return "";
});

const btnClass =
  "absolute right-2 top-1/2 z-10 -translate-y-1/2 rounded-md p-1.5 text-stone-500 transition hover:bg-stone-100 hover:text-stone-800 focus:outline-none focus:ring-2 focus:ring-stone-400/40 disabled:pointer-events-none disabled:opacity-40";
</script>

<template>
  <div class="relative">
    <input
      v-model="model"
      :type="visible ? 'text' : 'password'"
      :disabled="props.disabled"
      :placeholder="props.placeholder"
      :autocomplete="props.autocomplete"
      :aria-required="props.mark === 'required'"
      :class="[inputClass, accentClass, props.extraInputClass]"
    />
    <button
      type="button"
      :class="btnClass"
      :disabled="props.disabled"
      :aria-pressed="visible"
      :aria-label="visible ? t('admin.secretInput.hide') : t('admin.secretInput.show')"
      @click="visible = !visible"
    >
      <svg
        v-if="visible"
        class="h-5 w-5"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
        />
      </svg>
      <svg
        v-else
        class="h-5 w-5"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
        />
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
        />
      </svg>
    </button>
  </div>
</template>
