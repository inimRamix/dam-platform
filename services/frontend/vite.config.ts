import path from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const proxyTarget =
  process.env.VITE_API_PROXY_TARGET || "http://api:8000";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/api": {
        target: proxyTarget,
        changeOrigin: true,
      },
    },
  },
});
