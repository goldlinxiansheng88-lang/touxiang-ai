import { defineStore } from "pinia";
import { ref } from "vue";

const KEY = "aurashift_admin_token";

export const useAdminAuthStore = defineStore("adminAuth", () => {
  const token = ref("");

  function loadFromStorage() {
    token.value = localStorage.getItem(KEY)?.trim() ?? "";
  }

  function setToken(raw: string) {
    const v = raw.trim();
    token.value = v;
    if (v) localStorage.setItem(KEY, v);
    else localStorage.removeItem(KEY);
  }

  loadFromStorage();

  return { token, setToken, loadFromStorage };
});
