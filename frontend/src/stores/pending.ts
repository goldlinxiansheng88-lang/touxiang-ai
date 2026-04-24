import { defineStore } from "pinia";
import { ref } from "vue";

import type { AspectRatioValue } from "@/data/imageSpec";

export const usePendingStore = defineStore("pending", () => {
  const scene = ref("AVATAR");
  const style = ref<string | null>(null);
  const file = ref<File | null>(null);
  /** 生图规格（画幅），与后端 tasks.aspect_ratio 一致 */
  const aspectRatio = ref<AspectRatioValue | string>("auto");
  /** 生图分辨率（最长边），用于积分计费 */
  const resolution = ref<number>(1024);
  /** 背景移除（附加扣费） */
  const removeBackground = ref(false);

  function setPick(s: string, st: string | null, f: File | null) {
    scene.value = s;
    style.value = st;
    file.value = f;
  }

  function setAspectRatio(v: AspectRatioValue | string) {
    aspectRatio.value = v;
  }

  function setResolution(v: number) {
    resolution.value = v;
  }

  function setRemoveBackground(v: boolean) {
    removeBackground.value = v;
  }

  function clear() {
    file.value = null;
    style.value = null;
    aspectRatio.value = "auto";
    resolution.value = 1024;
    removeBackground.value = false;
  }

  return {
    scene,
    style,
    file,
    aspectRatio,
    resolution,
    removeBackground,
    setPick,
    setAspectRatio,
    setResolution,
    setRemoveBackground,
    clear,
  };
});
