import { defineConfig, devices } from "@playwright/test";

/**
 * T006 — Playwright configuration
 * baseURL: http://localhost:3000 (Next.js dev server)
 * A15: adversarial tests in tests/e2e/adversarial.spec.ts are mandatory CI gate
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env["CI"],
  retries: process.env["CI"] ? 2 : 0,
  workers: process.env["CI"] ? 1 : undefined,
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["line"],
  ],
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  // Start Next.js dev server before tests run
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env["CI"],
    timeout: 120_000,
  },
});
