import { defineConfig } from "vitest/config";
import { resolve } from "path";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["tests/unit/**/*.spec.ts", "tests/integration/**/*.spec.ts"],
    exclude: ["tests/e2e/**"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      include: ["src/**/*.ts"],
      exclude: ["src/**/*.d.ts", "src/app/**/*.tsx", "src/app/**/*.ts"],
    },
    // Integration tests need local Supabase running
    // Run with: npm run test:integration (requires supabase start)
    setupFiles: [],
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
    },
  },
});
