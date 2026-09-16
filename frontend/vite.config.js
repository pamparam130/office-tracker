import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 5173,
    // для локальной разработки без докера
    proxy: { '/api': 'http://localhost:8000' }
  }
})
