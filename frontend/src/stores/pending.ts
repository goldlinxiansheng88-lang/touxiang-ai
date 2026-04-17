import { defineStore } from "pinia";
import { ref } from "vue";

export const usePendingStore = defineStore("pending", () => {
  const scene = ref("AVATAR");
  const style = ref<string | null>(null);
  const file = ref<File | null>(null);

  function setPick(s: string, st: string | null, f: File | null) {
    scene.value = s;
    style.value = st;
    file.value = f;
  }

  function clear() {
    file.value = null;
    style.value = null;
  }

  return { scene, style, file, setPick, clear };
});
