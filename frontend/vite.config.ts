import type { ServerResponse } from "node:http";

import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiTarget = env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";

  /** 代理连不上后端时默认返回 HTML，axios 会误判；改为 JSON detail 便于前端展示。 */
  const onProxyError = (err: unknown, res: ServerResponse | undefined) => {
    if (!res || res.headersSent) return;
    const msg = err instanceof Error ? err.message : String(err);
    res.writeHead(502, { "Content-Type": "application/json; charset=utf-8" });
    res.end(
      JSON.stringify({
        detail:
          `[Vite 代理] 无法连接后端 ${apiTarget}（${msg}）。` +
            "请先在终端启动 API，例如进入 backend 目录执行：uvicorn app.main:app --reload --host 127.0.0.1 --port 8000。" +
            "若 API 运行在其他地址，请在 frontend 目录创建 .env.development 并设置 VITE_API_PROXY_TARGET=你的地址。",
      }),
    );
  };

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: true,
          // 长连接（SSE 日志流）避免代理过早断开
          timeout: 0,
          proxyTimeout: 0,
          configure(proxy) {
            proxy.on("error", (err, _req, res) => {
              onProxyError(err, res as ServerResponse);
            });
          },
        },
        "/static": {
          target: apiTarget,
          changeOrigin: true,
          configure(proxy) {
            proxy.on("error", (err, _req, res) => {
              onProxyError(err, res as ServerResponse);
            });
          },
        },
      },
    },
  };
});
