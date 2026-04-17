<template>
  <button
    type="button"
    class="style-card cursor-pointer touch-manipulation text-left w-full rounded-xl transition-transform active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-blush/60"
    @click="emit('select')"
  >
    <div
      class="aspect-[2/3] rounded-xl overflow-hidden relative shadow-sm border border-stone-200/40"
    >
      <div
        class="pointer-events-none absolute inset-0"
        :style="{ background: gradient }"
        aria-hidden="true"
      />
      <img
        v-if="!imgFailed"
        :key="thumbUrl"
        :src="thumbUrl"
        class="pointer-events-none absolute inset-0 h-full w-full select-none object-cover object-center"
        :alt="displayName"
        draggable="false"
        loading="lazy"
        referrerpolicy="no-referrer"
        @error="imgFailed = true"
      />
      <div class="card-gradient pointer-events-none absolute inset-x-0 bottom-0 z-[1] p-2.5 pt-10">
        <p class="text-white text-sm font-medium leading-tight">{{ displayName }}</p>
        <p class="text-white/75 text-xs mt-0.5">{{ socialProof }}</p>
      </div>
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import type { StyleItem } from "@/types/aura";
import { styleGradient, styleThumbUrl } from "@/data/styleVisuals";
import { styleItemName, styleItemProof } from "@/utils/i18nDisplay";

const props = defineProps<{ item: StyleItem }>();

const emit = defineEmits<{ select: [] }>();

const { locale, getLocaleMessage } = useI18n();

const displayName = computed(() =>
  styleItemName(getLocaleMessage, locale.value, props.item.id, props.item.display_name),
);

const socialProof = computed(() =>
  styleItemProof(getLocaleMessage, locale.value, props.item.id, props.item.social_proof),
);

const imgFailed = ref(false);

const gradient = computed(() => styleGradient(props.item.id));
/** 接口下发的 thumbnail_url 优先（与后端一致），否则用内置 Unsplash 映射 */
const thumbUrl = computed(() => {
  const u = props.item.thumbnail_url?.trim();
  if (u && /^https?:\/\//i.test(u)) return u;
  return styleThumbUrl(props.item.id);
});

watch(thumbUrl, () => {
  imgFailed.value = false;
});
</script>

<style scoped>
/* 底部略加深，保证白字在实拍人像上可读 */
.card-gradient {
  background: linear-gradient(to top, rgba(0, 0, 0, 0.72), rgba(0, 0, 0, 0.2) 50%, transparent);
}
</style>
