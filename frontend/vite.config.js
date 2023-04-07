import { defineConfig } from 'vite';
import { resolve } from 'path'
import vue from '@vitejs/plugin-vue';
import dotenv from 'dotenv';

dotenv.config();

export default defineConfig({
  base: '/static/vite/',
  plugins: [vue()],
  resolve: {
    extensions: ['.js', '.json', '.vue', '.less', '.scss'],
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: resolve('./dist/vite'),
    manifest: true,
    rollupOptions: {
      input: {
        main: resolve('./src/main.js')
      },
      output: {
        chunkFileNames: undefined,
      }
    }
  },
  define: {
    'import.meta.env.VUE_APP_GOOGLE_MAPS_API_KEY': JSON.stringify(process.env.VUE_APP_GOOGLE_MAPS_API_KEY),
  },
});
