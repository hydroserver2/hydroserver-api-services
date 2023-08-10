import { defineConfig, UserConfig } from 'vitest/config'
import { resolve } from 'path'

export default defineConfig({
  test: {
    globals: true,
    environmentMatchGlobs: [['src/components/**', 'jsdom']],
  },
  resolve: {
    extensions: ['.js', '.json', '.vue', '.less', '.scss', '.ts'],
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
}) as UserConfig
