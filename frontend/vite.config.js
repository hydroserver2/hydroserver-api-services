import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import dotenv from 'dotenv';

dotenv.config();

export default defineConfig({
  plugins: [vue()],
  define: {
    'import.meta.env.VUE_APP_GOOGLE_MAPS_API_KEY': JSON.stringify(process.env.VUE_APP_GOOGLE_MAPS_API_KEY),
  },
});
