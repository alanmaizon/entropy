import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const demo = process.env.VITE_DEMO === 'true'

export default defineConfig({
  base: demo ? '/entropy/' : '/',
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
