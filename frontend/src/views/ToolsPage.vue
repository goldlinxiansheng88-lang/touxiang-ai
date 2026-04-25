<template>
  <div class="min-h-screen px-3 pb-14">
    <header class="mx-auto max-w-[860px] pt-8 pb-4">
      <button
        type="button"
        class="hover-frame mb-4 inline-flex items-center gap-1 rounded-full border border-stone-200/80 bg-white/80 px-3 py-1.5 text-sm font-medium text-stone-700 shadow-sm"
        @click="router.push({ name: 'home' })"
      >
        ← {{ t("toolsPage.back") }}
      </button>
      <h1 class="text-2xl font-bold tracking-tight text-stone-950 sm:text-3xl">
        {{ t("toolsPage.title") }}
      </h1>
      <p class="mt-2 text-sm text-stone-600">
        {{ t("toolsPage.subtitle") }}
      </p>
    </header>

    <main class="mx-auto max-w-[860px] space-y-4">
      <!-- Practical tools -->
      <section class="rounded-2xl border border-stone-200/80 bg-white/80 p-5 shadow-sm backdrop-blur-sm">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-base font-semibold text-stone-900">
            {{ t("toolsPage.practical.title") }}
          </h2>
          <label
            class="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-medium text-stone-700 hover:bg-stone-50"
          >
            <input class="hidden" type="file" accept="image/*" @change="onPickFile" />
            <span class="text-stone-900">＋</span>
            <span>{{ t("toolsPage.practical.pick") }}</span>
          </label>
        </div>

        <p class="mt-2 text-xs leading-relaxed text-stone-500">
          {{ t("toolsPage.practical.hint") }}
        </p>

        <div v-if="!srcUrl" class="mt-5 rounded-xl border border-dashed border-stone-200 bg-stone-50 px-4 py-10 text-center text-sm text-stone-500">
          {{ t("toolsPage.practical.empty") }}
        </div>

        <div v-else class="mt-5 grid gap-4 lg:grid-cols-2 lg:items-start">
          <div class="rounded-2xl border border-stone-200 bg-white p-4">
            <div class="flex items-center justify-between gap-3">
              <div class="text-sm font-semibold text-stone-900">{{ t("toolsPage.practical.preview") }}</div>
              <button
                type="button"
                class="rounded-lg border border-stone-200 bg-white px-3 py-1.5 text-xs font-semibold text-stone-700 hover:bg-stone-50"
                @click="resetAll"
              >
                {{ t("toolsPage.practical.reset") }}
              </button>
            </div>
            <div class="mt-3 overflow-hidden rounded-xl border border-stone-100 bg-stone-50">
              <img :src="previewUrl" class="h-auto w-full object-contain" />
            </div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-xs text-stone-600">
              <div class="rounded-lg bg-stone-50 px-2 py-1.5">
                <span class="font-semibold text-stone-800">{{ t("toolsPage.practical.metaIn") }}</span>
                <span class="ml-1">{{ inputMeta }}</span>
              </div>
              <div class="rounded-lg bg-stone-50 px-2 py-1.5">
                <span class="font-semibold text-stone-800">{{ t("toolsPage.practical.metaOut") }}</span>
                <span class="ml-1">{{ outputMeta }}</span>
              </div>
            </div>
          </div>

          <div class="space-y-3">
            <div class="rounded-2xl border border-stone-200 bg-white p-4">
              <div class="text-sm font-semibold text-stone-900">{{ t("toolsPage.practical.resizeTitle") }}</div>
              <div class="mt-3 grid grid-cols-2 gap-3">
                <label class="space-y-1 text-xs font-semibold text-stone-600">
                  <div>{{ t("toolsPage.practical.width") }}</div>
                  <input
                    v-model.number="targetW"
                    type="number"
                    min="1"
                    class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-sm text-stone-900 outline-none focus:border-stone-400"
                    @input="onResizeInput('w')"
                  />
                </label>
                <label class="space-y-1 text-xs font-semibold text-stone-600">
                  <div>{{ t("toolsPage.practical.height") }}</div>
                  <input
                    v-model.number="targetH"
                    type="number"
                    min="1"
                    class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-sm text-stone-900 outline-none focus:border-stone-400"
                    @input="onResizeInput('h')"
                  />
                </label>
              </div>
              <label class="mt-3 inline-flex items-center gap-2 text-sm text-stone-700">
                <input v-model="keepAspect" type="checkbox" class="h-4 w-4 rounded border-stone-300" />
                <span>{{ t("toolsPage.practical.keepAspect") }}</span>
              </label>
            </div>

            <div class="rounded-2xl border border-stone-200 bg-white p-4">
              <div class="text-sm font-semibold text-stone-900">{{ t("toolsPage.practical.exportTitle") }}</div>
              <div class="mt-3 grid gap-3 sm:grid-cols-2">
                <label class="space-y-1 text-xs font-semibold text-stone-600">
                  <div>{{ t("toolsPage.practical.format") }}</div>
                  <select
                    v-model="format"
                    class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-sm text-stone-900 outline-none focus:border-stone-400"
                  >
                    <option value="image/jpeg">JPG</option>
                    <option value="image/png">PNG</option>
                    <option value="image/webp">WEBP</option>
                  </select>
                </label>
                <label class="space-y-1 text-xs font-semibold text-stone-600">
                  <div>{{ t("toolsPage.practical.quality") }}</div>
                  <input
                    v-model.number="quality"
                    type="range"
                    min="0.2"
                    max="1"
                    step="0.05"
                    class="w-full"
                    :disabled="format === 'image/png'"
                  />
                  <div class="text-xs font-medium text-stone-500">
                    {{ Math.round(quality * 100) }}%
                    <span v-if="format === 'image/png'"> · {{ t("toolsPage.practical.pngLossless") }}</span>
                  </div>
                </label>
              </div>

              <div class="mt-4 rounded-xl border border-stone-200 bg-stone-50 p-3">
                <div class="flex items-center justify-between gap-3">
                  <div class="text-sm font-semibold text-stone-800">{{ t("toolsPage.practical.watermarkTitle") }}</div>
                  <label class="inline-flex items-center gap-2 text-sm text-stone-700">
                    <input v-model="wmEnabled" type="checkbox" class="h-4 w-4 rounded border-stone-300" />
                    <span>{{ t("toolsPage.practical.enable") }}</span>
                  </label>
                </div>
                <div class="mt-3 grid gap-3 sm:grid-cols-2">
                  <label class="space-y-1 text-xs font-semibold text-stone-600">
                    <div>{{ t("toolsPage.practical.wmText") }}</div>
                    <input
                      v-model="wmText"
                      type="text"
                      :disabled="!wmEnabled"
                      class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-sm text-stone-900 outline-none focus:border-stone-400 disabled:bg-stone-100"
                    />
                  </label>
                  <label class="space-y-1 text-xs font-semibold text-stone-600">
                    <div>{{ t("toolsPage.practical.wmPosition") }}</div>
                    <select
                      v-model="wmPos"
                      :disabled="!wmEnabled"
                      class="w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-sm text-stone-900 outline-none focus:border-stone-400 disabled:bg-stone-100"
                    >
                      <option value="br">{{ t("toolsPage.practical.posBr") }}</option>
                      <option value="bl">{{ t("toolsPage.practical.posBl") }}</option>
                      <option value="tr">{{ t("toolsPage.practical.posTr") }}</option>
                      <option value="tl">{{ t("toolsPage.practical.posTl") }}</option>
                      <option value="center">{{ t("toolsPage.practical.posCenter") }}</option>
                    </select>
                  </label>
                </div>
              </div>

              <div class="mt-4 flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  class="rounded-xl bg-stone-900 px-4 py-2 text-sm font-semibold text-white hover:bg-stone-800"
                  @click="applyAndExport"
                >
                  {{ t("toolsPage.practical.export") }}
                </button>
                <a
                  v-if="outUrl"
                  class="rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-stone-900 hover:bg-stone-50"
                  :href="outUrl"
                  :download="downloadName"
                >
                  {{ t("toolsPage.practical.download") }}
                </a>
                <span v-if="errMsg" class="text-sm font-medium text-rose-700">{{ errMsg }}</span>
              </div>
              <p class="mt-2 text-xs text-stone-500">
                {{ t("toolsPage.practical.note") }}
              </p>
            </div>
          </div>
        </div>
      </section>

      <p class="rounded-xl border border-amber-200/80 bg-amber-50/90 px-3 py-2 text-xs leading-relaxed text-amber-950">
        {{ t("toolsPage.disclaimer") }}
      </p>

      <article
        v-for="key in cardKeys"
        :key="key"
        class="rounded-2xl border border-stone-200/80 bg-white/80 p-5 shadow-sm backdrop-blur-sm"
      >
        <div class="flex flex-wrap items-baseline justify-between gap-2">
          <h2 class="text-base font-semibold text-stone-900">
            {{ t(`toolsPage.cards.${key}.title`) }}
          </h2>
          <span class="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-stone-600">
            {{ t(`toolsPage.cards.${key}.tag`) }}
          </span>
        </div>
        <p class="mt-2 text-sm font-medium text-stone-700">
          {{ t(`toolsPage.cards.${key}.pain`) }}
        </p>
        <p class="mt-2 text-sm leading-relaxed text-stone-600">
          {{ t(`toolsPage.cards.${key}.stack`) }}
        </p>
        <p class="mt-2 text-sm leading-relaxed text-stone-600">
          {{ t(`toolsPage.cards.${key}.product`) }}
        </p>
      </article>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

const router = useRouter();
const { t } = useI18n();

const cardKeys = [
  "objectRemover",
  "restoreUpscale",
  "beauty",
  "bgRemove",
  "faceSwap",
] as const;

const srcUrl = ref<string | null>(null);
const previewUrl = ref<string | null>(null);
const outUrl = ref<string | null>(null);
const downloadName = ref<string>("export.jpg");
const errMsg = ref<string | null>(null);

const inputW = ref<number>(0);
const inputH = ref<number>(0);
const inputBytes = ref<number>(0);

const targetW = ref<number>(0);
const targetH = ref<number>(0);
const keepAspect = ref<boolean>(true);
const aspect = ref<number>(1);

const format = ref<"image/jpeg" | "image/png" | "image/webp">("image/jpeg");
const quality = ref<number>(0.85);

const wmEnabled = ref<boolean>(false);
const wmText = ref<string>("AuraShift");
const wmPos = ref<"br" | "bl" | "tr" | "tl" | "center">("br");

const inputMeta = computed(() => {
  if (!srcUrl.value) return "-";
  const kb = Math.max(1, Math.round(inputBytes.value / 1024));
  return `${inputW.value}×${inputH.value} · ${kb} KB`;
});

const outputMeta = computed(() => {
  if (!srcUrl.value) return "-";
  const fmt = format.value === "image/png" ? "PNG" : format.value === "image/webp" ? "WEBP" : "JPG";
  return `${targetW.value}×${targetH.value} · ${fmt} · ${Math.round(quality.value * 100)}%`;
});

function revokeUrl(u: string | null) {
  if (!u) return;
  try {
    URL.revokeObjectURL(u);
  } catch {
    // ignore
  }
}

function resetAll() {
  errMsg.value = null;
  revokeUrl(srcUrl.value);
  revokeUrl(previewUrl.value);
  revokeUrl(outUrl.value);
  srcUrl.value = null;
  previewUrl.value = null;
  outUrl.value = null;
  downloadName.value = "export.jpg";
  inputW.value = 0;
  inputH.value = 0;
  inputBytes.value = 0;
  targetW.value = 0;
  targetH.value = 0;
  keepAspect.value = true;
  aspect.value = 1;
}

async function loadImageMeta(url: string) {
  const img = new Image();
  img.decoding = "async";
  img.src = url;
  await img.decode();
  inputW.value = img.naturalWidth || img.width;
  inputH.value = img.naturalHeight || img.height;
  aspect.value = inputW.value / Math.max(1, inputH.value);
  targetW.value = inputW.value;
  targetH.value = inputH.value;
}

async function onPickFile(e: Event) {
  errMsg.value = null;
  revokeUrl(outUrl.value);
  outUrl.value = null;

  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  if (!file) return;

  resetAll();
  inputBytes.value = file.size;
  const u = URL.createObjectURL(file);
  srcUrl.value = u;
  previewUrl.value = u;

  const ext = file.type === "image/png" ? "png" : file.type === "image/webp" ? "webp" : "jpg";
  downloadName.value = `export.${ext}`;

  try {
    await loadImageMeta(u);
  } catch {
    errMsg.value = t("toolsPage.practical.errLoad");
  }
}

function onResizeInput(which: "w" | "h") {
  if (!keepAspect.value) return;
  if (!aspect.value || aspect.value <= 0) return;
  if (which === "w") {
    const w = Math.max(1, Math.floor(targetW.value || 1));
    targetW.value = w;
    targetH.value = Math.max(1, Math.round(w / aspect.value));
  } else {
    const h = Math.max(1, Math.floor(targetH.value || 1));
    targetH.value = h;
    targetW.value = Math.max(1, Math.round(h * aspect.value));
  }
}

function computeWmXY(canvasW: number, canvasH: number, pad: number) {
  if (wmPos.value === "center") return { x: canvasW / 2, y: canvasH / 2, align: "center" as const, baseline: "middle" as const };
  if (wmPos.value === "tl") return { x: pad, y: pad, align: "left" as const, baseline: "top" as const };
  if (wmPos.value === "tr") return { x: canvasW - pad, y: pad, align: "right" as const, baseline: "top" as const };
  if (wmPos.value === "bl") return { x: pad, y: canvasH - pad, align: "left" as const, baseline: "bottom" as const };
  return { x: canvasW - pad, y: canvasH - pad, align: "right" as const, baseline: "bottom" as const };
}

async function applyAndExport() {
  errMsg.value = null;
  revokeUrl(outUrl.value);
  outUrl.value = null;

  if (!srcUrl.value) return;
  const w = Math.max(1, Math.floor(targetW.value || 1));
  const h = Math.max(1, Math.floor(targetH.value || 1));
  targetW.value = w;
  targetH.value = h;

  try {
    const img = await createImageBitmap(await (await fetch(srcUrl.value)).blob());
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("noctx");

    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(img, 0, 0, w, h);

    if (wmEnabled.value && wmText.value.trim()) {
      const pad = Math.max(12, Math.round(Math.min(w, h) * 0.03));
      const fontSize = Math.max(14, Math.round(Math.min(w, h) * 0.045));
      ctx.font = `700 ${fontSize}px system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif`;
      const { x, y, align, baseline } = computeWmXY(w, h, pad);
      ctx.textAlign = align;
      ctx.textBaseline = baseline;
      ctx.lineWidth = Math.max(2, Math.round(fontSize * 0.12));
      ctx.strokeStyle = "rgba(0,0,0,0.35)";
      ctx.fillStyle = "rgba(255,255,255,0.85)";
      ctx.strokeText(wmText.value.trim(), x, y);
      ctx.fillText(wmText.value.trim(), x, y);
    }

    const q = format.value === "image/png" ? undefined : Math.min(1, Math.max(0.2, quality.value));
    const blob: Blob = await new Promise((resolve, reject) => {
      canvas.toBlob(
        (b) => (b ? resolve(b) : reject(new Error("toBlob"))),
        format.value,
        q,
      );
    });

    const ext = format.value === "image/png" ? "png" : format.value === "image/webp" ? "webp" : "jpg";
    downloadName.value = `export.${ext}`;
    outUrl.value = URL.createObjectURL(blob);
    previewUrl.value = outUrl.value;
  } catch {
    errMsg.value = t("toolsPage.practical.errExport");
  }
}

onBeforeUnmount(() => {
  revokeUrl(srcUrl.value);
  revokeUrl(previewUrl.value);
  revokeUrl(outUrl.value);
});
</script>
