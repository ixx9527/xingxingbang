import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts: ['xingxingbang.ixx9527.xin'],
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true
      },
      '/health': {
        target: 'http://backend:8000',
        changeOrigin: true
      }
    }
  }
})