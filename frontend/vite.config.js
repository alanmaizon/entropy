import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/ingest': 'http://localhost:8000',
      '/hypothesis': 'http://localhost:8000',
      '/knowledge': 'http://localhost:8000',
      '/graph': 'http://localhost:8000',
    },
  },
})
