import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true,          // aceita conexões de fora do container
    port: 80,            // o gateway encaminha "/" para a porta 80 deste container
    strictPort: true,
    allowedHosts: true,
    watch: { usePolling: true }, // necessário para detectar edições em volumes Docker (Windows/macOS)
  },
});