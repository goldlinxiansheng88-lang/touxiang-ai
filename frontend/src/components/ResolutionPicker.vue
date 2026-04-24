<template>
  <div class="w-full rounded-xl border border-stone-200/70 bg-[var(--aura-field)] p-2 shadow-sm">
    <p class="mb-1.5 text-center text-[10px] font-medium tracking-wide text-stone-500">
      Resolution
    </p>
    <div class="grid grid-cols-2 gap-1.5 sm:grid-cols-4 sm:gap-2">
      <button
        v-for="opt in options"
        :key="opt.res"
        type="button"
        class="hover-frame flex flex-col items-center gap-0.5 rounded-lg border px-1 py-2 text-center transition-all duration-150"
        :class="
          modelValue === opt.res
            ? 'border-blush/65 bg-blush/[0.12] text-stone-800 shadow-[0_0_0_1px_rgba(220,38,38,0.35)]'
            : 'border-stone-200/95 bg-white/60 text-stone-600 hover:border-stone-300 hover:bg-white hover:text-stone-800'
        "
        @click="emit('update:modelValue', opt.res)"
      >
        <span class="text-[11px] font-semibold leading-none">{{ opt.label }}</span>
        <span class="text-[10px] text-stone-500">{{ opt.credits }} credits</span>
      </button>
    </div>
    <p class="mt-1.5 text-center text-[9px] leading-snug text-stone-500/90">
      Billing is based on selected resolution tier (long edge). Higher tiers cost more credits.
    </p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ modelValue: number }>();
const emit = defineEmits<{ (e: "update:modelValue", v: number): void }>();

const options = [
  { res: 512, label: "512", credits: 2 },
  { res: 1024, label: "1024", credits: 4 },
  { res: 2048, label: "2048", credits: 9 },
  { res: 4096, label: "4096", credits: 20 },
] as const;
</script>

