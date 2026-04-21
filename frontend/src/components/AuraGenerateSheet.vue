<template>
  <Teleport to="body">
    <div
      v-show="modelValue"
      class="fixed inset-0 z-[200] flex items-end justify-center sm:items-center sm:p-4"
      role="dialog"
      aria-modal="true"
      :aria-label="title"
    >
      <button
        type="button"
        class="aura-scrim absolute inset-0"
        :aria-label="t('common.close')"
        @click="close"
      />
      <div
        class="aura-panel relative z-[1] w-full max-h-[90vh] max-w-[min(21rem,calc(100vw-1.5rem))] overflow-y-auto rounded-t-2xl p-3 pb-6 text-sm sm:rounded-2xl sm:pb-5"
        @click.stop
      >
        <div class="mb-2 flex items-start justify-between gap-2">
          <h2 class="pr-5 text-sm font-semibold leading-snug text-stone-900">
            {{ title }}
          </h2>
          <button
            type="button"
            class="hover-frame -mr-1 -mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-base text-stone-500 hover:bg-stone-200/60 hover:text-stone-800"
            :aria-label="t('common.close')"
            @click="close"
          >
            ×
          </button>
        </div>
        <AuraGenerateForm
          :key="formKey"
          :scene-id="sceneId"
          :style-id="styleId"
          :style-choices="styleChoices"
          :initial-file="initialFile"
        />
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import AuraGenerateForm from "@/components/AuraGenerateForm.vue";
import type { StyleItem } from "@/api/client";

const props = defineProps<{
  modelValue: boolean;
  title: string;
  sceneId: string;
  styleId: string | null;
  styleChoices: StyleItem[];
  initialFile: File | null;
}>();

const emit = defineEmits<{
  "update:modelValue": [boolean];
}>();

const { t } = useI18n();

/** 每次打开时重挂载表单，清空本地选图状态 */
const formKey = ref(0);
watch(
  () => props.modelValue,
  (v) => {
    if (v) formKey.value += 1;
  },
);

function close() {
  emit("update:modelValue", false);
}
</script>
