import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

import { evaluateRunnerResults, runFlows, validateFlowManifest } from "../src/contract.mjs";

const manifestUrl = new URL("../flows.json", import.meta.url);

async function flows() {
  return validateFlowManifest(JSON.parse(await readFile(manifestUrl, "utf8")));
}

test("seven approved flows are replayable through a provider-neutral fake runner", async () => {
  const definitions = await flows();
  const seen = [];
  const report = await runFlows({
    flows: definitions,
    runner: {
      async run(flow) {
        seen.push(flow.id);
        return { flowId: flow.id, status: "passed", evidence: { fake: true } };
      },
    },
  });

  assert.equal(definitions.length, 7);
  assert.deepEqual(seen, definitions.map((flow) => flow.id));
  assert.equal(report.consensusPolicy, "fail-on-disagreement");
  assert.equal(report.status, "passed");
});

test("every live flow resolves to a local browser-laboratory fixture", async () => {
  const definitions = await flows();
  for (const flow of definitions) {
    const fixtureUrl = new URL(
      `../../browser${flow.path.replace(/^\/fixtures/, "/fixtures")}`,
      import.meta.url,
    );
    await access(fixtureUrl);
  }
});

test("a Passmark disagreement fails closed and requests manual review", async () => {
  const definitions = await flows();
  const report = evaluateRunnerResults(definitions, definitions.map((flow, index) => ({
    flowId: flow.id,
    status: index === 2 ? "disagreement" : "passed",
  })));

  assert.equal(report.status, "failed");
  assert.equal(report.results[2].manualReview, true);
});

test("CUA or video evidence remains manual-review-only", async () => {
  const definitions = await flows();
  const report = evaluateRunnerResults(definitions, definitions.map((flow, index) => ({
    flowId: flow.id,
    status: index === 0 ? "manual-review" : "passed",
  })));

  assert.equal(report.status, "manual-review");
  assert.equal(report.results[0].manualReview, true);
});

test("the contract rejects CUA and video inside replayable definitions", async () => {
  const valid = JSON.parse(await readFile(manifestUrl, "utf8"));
  valid.flows[0].steps[0].ai = { mode: "cua" };
  assert.throws(() => validateFlowManifest(valid), /live-runner-only opt-in/);

  delete valid.flows[0].steps[0].ai;
  valid.flows[0].assertions[0].video = true;
  assert.throws(() => validateFlowManifest(valid), /live-runner-only opt-in/);
});
