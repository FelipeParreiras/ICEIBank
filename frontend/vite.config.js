import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api/agencia-0": {
        target: "http://127.0.0.1:4045",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/agencia-0/, ""),
      },
      "/api/agencia-1": {
        target: "http://127.0.0.1:4046",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/agencia-1/, ""),
      },
      "/api/agencia-2": {
        target: "http://127.0.0.1:4047",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/agencia-2/, ""),
      },
    },
  },
});
