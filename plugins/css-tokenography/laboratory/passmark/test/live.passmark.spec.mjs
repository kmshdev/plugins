import { test, expect } from "@playwright/test";

import { loadFlows, preflightLiveEvaluation, runLiveFlow } from "../src/live-runner.mjs";

test.describe("optional internal Passmark laboratory", () => {
  let config;
  let flows;

  test.beforeAll(async () => {
    // This preflight opens no browser and never prints configuration values.
    config = await preflightLiveEvaluation();
    flows = await loadFlows();
  });

  for (const flowId of [
    "named-grid-creation",
    "disconnected-grid-rejection",
    "subgrid-placement",
    "responsive-flexbox",
    "transform-plus-transition",
    "dark-mode-variables",
    "selector-matching",
  ]) {
    test(flowId, async ({ page }) => {
      const flow = flows.find((candidate) => candidate.id === flowId);
      await runLiveFlow({ page, test, expect, flow, config });
    });
  }
});
