import { defineConfig, devices } from "@playwright/test";

export const deterministicContext = Object.freeze({
  viewport: { width: 1024, height: 768 },
  deviceScaleFactor: 1,
  locale: "en-US",
  timezoneId: "UTC",
  colorScheme: "light",
  reducedMotion: "reduce",
  forcedColors: "none",
});

const project = (name, browserName) => ({
  name,
  use: {
    ...devices["Desktop Chrome"],
    browserName,
    ...deterministicContext,
    headless: true,
  },
});

export default defineConfig({
  testDir: "./test/browser",
  outputDir: "./test-results",
  snapshotPathTemplate: "{testDir}/../../snapshots/{projectName}/{arg}{ext}",
  forbidOnly: Boolean(process.env.CI),
  fullyParallel: false,
  retries: 0,
  workers: 1,
  use: {
    ...deterministicContext,
    actionTimeout: 10_000,
    navigationTimeout: 10_000,
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    video: "off",
  },
  expect: {
    timeout: 5_000,
    toHaveScreenshot: {
      animations: "disabled",
      caret: "hide",
      scale: "css",
      maxDiffPixelRatio: 0,
    },
  },
  projects: [
    project("chromium", "chromium"),
    project("firefox", "firefox"),
    project("webkit", "webkit"),
  ],
});
