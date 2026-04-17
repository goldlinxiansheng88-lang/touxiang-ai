import { createApp } from "vue";
import { createPinia } from "pinia";
import Vant from "vant";
import "vant/lib/index.css";
import "./styles/main.css";
import App from "./App.vue";
import { i18n } from "./i18n";
import { ADMIN_FORCED_LOCALE, LOCALE_USER_KEY, SUPPORTED_LOCALE_SET } from "./locales/languages";
import router from "./router";
import { applyDomLocale, applyVantLocale } from "./utils/localeAdmin";

const savedLocale = localStorage.getItem(LOCALE_USER_KEY)?.trim();

function pathnameWithoutBase(): string {
  if (typeof window === "undefined") return "/";
  const path = window.location.pathname || "/";
  const base = (import.meta.env.BASE_URL || "/").replace(/\/$/, "");
  if (base && base !== "/" && path.startsWith(base)) {
    const rest = path.slice(base.length);
    return rest.startsWith("/") ? rest : `/${rest}`;
  }
  return path;
}

/** 直链管理页时优先 zh-CN；支持 Vite base 子路径部署 */
const openAdmin =
  typeof window !== "undefined" &&
  (pathnameWithoutBase() === "/admin" || pathnameWithoutBase().startsWith("/admin/"));
if (openAdmin) {
  i18n.global.locale.value = ADMIN_FORCED_LOCALE;
  applyDomLocale(ADMIN_FORCED_LOCALE);
  applyVantLocale(ADMIN_FORCED_LOCALE);
} else if (savedLocale && SUPPORTED_LOCALE_SET.has(savedLocale)) {
  i18n.global.locale.value = savedLocale;
  applyDomLocale(savedLocale);
  applyVantLocale(savedLocale);
}

const app = createApp(App);
app.use(createPinia());
app.use(i18n);
app.use(router);
app.use(Vant);
app.mount("#app");
