import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: { environment: 'jsdom', setupFiles: './src/test-setup.ts' },
  coverage: {
    provider: 'v8',
    thresholds: { lines: 80, functions: 80, branches: 75, statements: 80 },
  },
})
