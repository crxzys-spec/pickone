import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) {
            return;
          }
          if (id.includes("element-plus")) {
            return "element-plus";
          }
          if (id.includes("vue") || id.includes("vue-router") || id.includes("pinia")) {
            return "vue-vendor";
          }
          return "vendor";
        },
      },
    },
  },
});
