import { defineConfig } from 'vite'
import { resolve } from 'path'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'

export default defineConfig({
  base: process.env.NODE_ENV === 'development' ? '' : '/static/vite/',
  plugins: [
    vue(),
    vuetify({ styles: { configFile: 'src/assets/css/variables.scss' } }),
  ],
  server: {
    host: '127.0.0.1',
    port: 5173
  },
  resolve: {
    extensions: ['.js', '.json', '.vue', '.less', '.scss', '.ts'],
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: resolve('./dist/vite'),
    manifest: true,
    rollupOptions: {
      input: {
        main: resolve('./src/main.ts'),
      },
      output: {
        chunkFileNames: undefined,
      },
    },
  },
})
