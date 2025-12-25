import axios from "axios";
import { ElMessage } from "element-plus";

import i18n from "../i18n";

const http = axios.create({
  baseURL: "/api/v1",
  timeout: 15000,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("scopes");
      if (window.location.pathname !== "/login") {
        ElMessage.error(i18n.global.t("common.sessionExpired"));
        window.location.href = `/login?redirect=${encodeURIComponent(
          window.location.pathname,
        )}`;
      }
    }
    return Promise.reject(error);
  },
);

export default http;
