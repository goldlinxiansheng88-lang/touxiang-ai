<template>
  <div class="aura-generate-form space-y-2.5 text-sm">
    <ImageSpecPicker
      :model-value="pending.aspectRatio"
      @update:model-value="(v: string) => pending.setAspectRatio(v)"
    />

    <div v-if="showStyleSelect" class="space-y-1">
      <label class="block text-[11px] font-medium text-stone-600">{{ t("flow.generatePickStyleLabel") }}</label>
      <select
        v-model="innerStyleId"
        class="w-full rounded-lg border border-stone-200/90 bg-[var(--aura-field)] px-2 py-2 text-xs text-stone-900 shadow-sm"
      >
        <option v-for="st in styleChoices" :key="st.id" :value="st.id">{{ styleOptionLabel(st) }}</option>
      </select>
    </div>

    <div v-if="previewUrl" class="flex justify-center">
      <img
        :src="previewUrl"
        alt=""
        class="max-h-36 rounded-lg border border-stone-200 object-contain"
      />
    </div>
    <button
      type="button"
      class="hover-frame w-full rounded-xl border border-stone-200/80 bg-[var(--aura-muted)] py-2.5 text-center text-xs font-semibold text-stone-800 shadow-sm transition active:scale-[0.99]"
      @click="fileInput?.click()"
    >
      {{ localFile ? t("flow.packChangePhoto") : t("flow.packUploadPhoto") }}
    </button>
    <button
      type="button"
      class="hover-frame w-full rounded-xl bg-blush py-2.5 text-center text-sm font-semibold text-white shadow-md ring-1 ring-black/5 transition active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-45"
      :disabled="!localFile || !resolvedStyleId"
      @click="onSubmit"
    >
      {{ t("flow.packAuraTransform") }}
    </button>
    <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFilePicked" />

    <AuraSubmitOverlay :show="submitting" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { showFailToast } from "vant";
import AuraSubmitOverlay from "@/components/AuraSubmitOverlay.vue";
import ImageSpecPicker from "@/components/ImageSpecPicker.vue";
import type { StyleItem } from "@/api/client";
import { usePendingStore } from "@/stores/pending";
import { useAuraTaskSubmit } from "@/composables/useAuraTaskSubmit";
import { styleItemName } from "@/utils/i18nDisplay";

const props = defineProps<{
  sceneId: string;
  /** 已选风格时锁定，不再显示下拉 */
  styleId: string | null;
  /** styleId 为 null 时用于下拉（须非空） */
  styleChoices: StyleItem[];
  initialFile: File | null;
}>();

const { t, locale, getLocaleMessage } = useI18n();
const pending = usePendingStore();
const { submitting, submit } = useAuraTaskSubmit();

const fileInput = ref<HTMLInputElement | null>(null);
const localFile = ref<File | null>(null);
const previewUrl = ref("");
const innerStyleId = ref("");

const showStyleSelect = computed(() => props.styleId === null);

const resolvedStyleId = computed(() => {
  if (props.styleId != null && props.styleId !== "") return props.styleId;
  return innerStyleId.value || null;
});

watch(
  () => props.initialFile,
  (f) => {
    localFile.value = f ?? null;
  },
  { immediate: true },
);

watch(localFile, (f) => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = f ? URL.createObjectURL(f) : "";
});

watch(
  () => props.styleChoices,
  (list) => {
    if (!list.length) return;
    if (!innerStyleId.value || !list.some((s) => s.id === innerStyleId.value)) {
      innerStyleId.value = list[0]!.id;
    }
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
});

function styleOptionLabel(st: StyleItem) {
  return styleItemName(getLocaleMessage, locale.value, st.id, st.display_name);
}

function onFilePicked(ev: Event) {
  const input = ev.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  localFile.value = file ?? null;
}

async function onSubmit() {
  const style = resolvedStyleId.value;
  if (!localFile.value || !style) {
    showFailToast(t("flow.packPickPhotoFirst"));
    return;
  }
  pending.setPick(props.sceneId, style, localFile.value);
  await submit({ file: localFile.value, scene: props.sceneId, style });
}

defineExpose({ focusUpload: () => fileInput.value?.click() });
</script>
