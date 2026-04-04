import { defineConfig } from 'vite'

export default defineConfig({
  root: 'app/web',      // Onde o Vite busca o index.html e o main.js
  envDir: '../../',     // Sobe dois níveis (de app/web para IA Agent) para ler o .env
  server: {
    port: 5173,         // Porta padrão para evitar conflitos
    strictPort: true,
  }
})