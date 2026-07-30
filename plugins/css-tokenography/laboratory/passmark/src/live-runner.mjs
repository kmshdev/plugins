import { readFile } from "node:fs/promises";

import { validateFlowManifest } from "./contract.mjs";
import { buildLivePassmarkConfig, preflightRedis } from "./live-config.mjs";

const flowManifestUrl = new URL("../flows.json", import.meta.url);

export async function loadFlows() {
  return validateFlowManifest(JSON.parse(await readFile(flowManifestUrl, "utf8")));
}

export async function preflightLiveEvaluation(env = process.env) {
  const config = buildLivePassmarkConfig(env);
  await preflightRedis(config.redis);
  return config;
}

/**
 * Invoke this only from a Playwright test after preflightLiveEvaluation succeeds.
 * Dynamic import keeps fake contract tests and ordinary plugin use provider-free.
 */
export async function runLiveFlow({ page, test, expect, flow, config }) {
  const { configure, runSteps } = await import("passmark");
  configure(config.passmark);
  await page.goto(new URL(flow.path, config.baseUrl).toString());
  await runSteps({
    page,
    test,
    expect,
    userFlow: flow.userFlow,
    steps: flow.steps,
    assertions: flow.assertions.map((assertion) => ({
      ...assertion,
      ...(config.options.video ? { video: true } : {}),
    })),
  });
  return {
    flowId: flow.id,
    status: config.options.cua || config.options.video ? "manual-review" : "passed",
    evidence: {
      kind: "passmark-live",
      manualReviewReason: config.options.cua || config.options.video
        ? "CUA and video evidence require manual review"
        : null,
    },
  };
}
