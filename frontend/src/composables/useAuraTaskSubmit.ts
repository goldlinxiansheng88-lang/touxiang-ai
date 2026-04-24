import Compressor from "compressorjs";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { showFailToast } from "vant";
import { createTask, getApiErrorMessage } from "@/api/client";
import { usePendingStore } from "@/stores/pending";

export function useAuraTaskSubmit() {
  const router = useRouter();
  const { t, locale } = useI18n();
  const pending = usePendingStore();
  const submitting = ref(false);

  function compress(file: File): Promise<File> {
    return new Promise((resolve, reject) => {
      new Compressor(file, {
        maxWidth: 1024,
        maxHeight: 1024,
        maxSizeMB: 5,
        success: (result) => {
          const blob = result as Blob;
          const name = file.name.replace(/\.[^.]+$/, "") + ".jpg";
          resolve(new File([blob], name, { type: blob.type || "image/jpeg" }));
        },
        error: reject,
      });
    });
  }

  async function submit(params: { file: File; scene: string; style: string }) {
    submitting.value = true;
    try {
      const f = await compress(params.file);
      const refCookie = document.cookie
        .split("; ")
        .find((r) => r.startsWith("aff_ref="))
        ?.split("=")[1];
      const res = await createTask(
        f,
        params.scene,
        params.style,
        refCookie ? decodeURIComponent(refCookie) : null,
        pending.aspectRatio,
        String(locale.value || "en"),
      );
      pending.clear();
      await router.push({ name: "loading", params: { taskId: res.task_id } });
    } catch (e: unknown) {
      submitting.value = false;
      showFailToast(t("errors.createTask", { msg: getApiErrorMessage(e) }));
    }
  }

  return { submitting, submit };
}
