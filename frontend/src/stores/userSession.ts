import { defineStore } from "pinia";
import { ref } from "vue";

import { fetchAuthMe, logoutAuth } from "@/api/client";

export const useUserSessionStore = defineStore("userSession", () => {
  const authenticated = ref(false);
  const email = ref("");
  const displayName = ref("");

  async function refresh() {
    try {
      const d = await fetchAuthMe();
      if (d.authenticated) {
        authenticated.value = true;
        email.value = d.email ?? "";
        displayName.value = d.display_name ?? "";
      } else {
        authenticated.value = false;
        email.value = "";
        displayName.value = "";
      }
    } catch {
      authenticated.value = false;
      email.value = "";
      displayName.value = "";
    }
  }

  async function logout() {
    try {
      await logoutAuth();
    } finally {
      await refresh();
    }
  }

  return { authenticated, email, displayName, refresh, logout };
});
