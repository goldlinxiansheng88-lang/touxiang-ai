import type { AxiosError, AxiosInstance } from "axios";

import { i18n } from "@/i18n";

/** 代理/网关返回 HTML 时 axios 常报 500 且无 JSON detail，便于排查「后端未启动或端口不对」 */
export function installAxiosHtmlResponseHint(instance: AxiosInstance): void {
  instance.interceptors.response.use(
    (r) => r,
    (err: AxiosError) => {
      const res = err.response;
      const data = res?.data;
      const ct = String(res?.headers?.["content-type"] ?? "");
      if (
        res &&
        typeof data === "string" &&
        (ct.includes("text/html") || /^\s*</.test(data))
      ) {
        err.message = i18n.global.t("axios.htmlError", { status: res.status });
      }
      return Promise.reject(err);
    },
  );
}
