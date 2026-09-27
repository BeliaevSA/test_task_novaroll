import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
 
// Прокси /api -> backend:8000 в dev-режиме, зеркалит поведение nginx.conf в проде
// (там location /api/ { proxy_pass http://backend:8000/; }).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
 