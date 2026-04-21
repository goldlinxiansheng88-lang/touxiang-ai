import { defineStore } from "pinia";
import { ref } from "vue";

import type { AspectRatioValue } from "@/data/imageSpec";

export const usePendingStore = defineStore("pending", () => {
  const scene = ref("AVATAR");
  const style = ref<string | null>(null);
  const file = ref<File | null>(null);
  /** 生图规格（画幅），与后端 tasks.aspect_ratio 一致 */
  const aspectRatio = ref<AspectRatioValue | string>("auto");

  function setPick(s: string, st: string | null, f: File | null) {
    scene.value = s;
    style.value = st;
    file.value = f;
  }

  function setAspectRatio(v: AspectRatioValue | string) {
    aspectRatio.value = v;
  }

  function clear() {
    file.value = null;
    style.value = null;
    aspectRatio.value = "auto";
  }

  return { scene, style, file, aspectRatio, setPick, setAspectRatio, clear };
});
