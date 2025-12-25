import { createI18n } from "vue-i18n";

import en from "./locales/en";
import zh from "./locales/zh";

export type Locale = "en" | "zh";

const saved = localStorage.getItem("locale");
const locale = saved === "en" || saved === "zh" ? saved : "zh";

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale,
  fallbackLocale: "en",
  messages: {
    en,
    zh,
  },
});

export function setLocale(value: Locale) {
  i18n.global.locale.value = value;
  localStorage.setItem("locale", value);
}

export default i18n;
