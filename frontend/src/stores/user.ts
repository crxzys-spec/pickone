import { defineStore } from "pinia";

function loadScopes(): string[] {
  const raw = localStorage.getItem("scopes");
  if (!raw) {
    return [];
  }
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export const useUserStore = defineStore("user", {
  state: () => ({
    token: localStorage.getItem("access_token") ?? "",
    scopes: loadScopes(),
  }),
  actions: {
    setAuth(token: string, scopes: string[]) {
      this.token = token;
      this.scopes = scopes;
      localStorage.setItem("access_token", token);
      localStorage.setItem("scopes", JSON.stringify(scopes));
    },
    clear() {
      this.token = "";
      this.scopes = [];
      localStorage.removeItem("access_token");
      localStorage.removeItem("scopes");
    },
  },
});
