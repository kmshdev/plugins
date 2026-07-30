const FLOW_PROTOCOL = "css-tokenography-passmark-flows/v1";

const FLOW_IDS = new Set([
  "named-grid-creation",
  "disconnected-grid-rejection",
  "subgrid-placement",
  "responsive-flexbox",
  "transform-plus-transition",
  "dark-mode-variables",
  "selector-matching",
]);

function contractError(message) {
  return new TypeError(`Invalid Passmark laboratory contract: ${message}`);
}

function requireNonEmptyString(value, path) {
  if (typeof value !== "string" || value.trim() === "") {
    throw contractError(`${path} must be a non-empty string`);
  }
}

function validateSteps(steps, path) {
  if (!Array.isArray(steps) || steps.length === 0) {
    throw contractError(`${path} must contain at least one step`);
  }

  for (const [index, step] of steps.entries()) {
    if (!step || typeof step !== "object") {
      throw contractError(`${path}[${index}] must be an object`);
    }
    requireNonEmptyString(step.description, `${path}[${index}].description`);
    if (step.ai?.mode === "cua") {
      throw contractError(`${path}[${index}] may not opt into CUA; CUA is a live-runner-only opt-in`);
    }
  }
}

function validateAssertions(assertions, path) {
  if (!Array.isArray(assertions) || assertions.length === 0) {
    throw contractError(`${path} must contain at least one assertion`);
  }

  for (const [index, assertion] of assertions.entries()) {
    if (!assertion || typeof assertion !== "object") {
      throw contractError(`${path}[${index}] must be an object`);
    }
    requireNonEmptyString(assertion.assertion, `${path}[${index}].assertion`);
    if (assertion.video === true) {
      throw contractError(`${path}[${index}] may not opt into video; video is a live-runner-only opt-in`);
    }
  }
}

export function validateFlowManifest(manifest) {
  if (!manifest || typeof manifest !== "object") {
    throw contractError("manifest must be an object");
  }
  if (manifest.protocol !== FLOW_PROTOCOL) {
    throw contractError(`protocol must equal ${FLOW_PROTOCOL}`);
  }
  if (!Array.isArray(manifest.flows) || manifest.flows.length !== FLOW_IDS.size) {
    throw contractError(`flows must contain exactly ${FLOW_IDS.size} definitions`);
  }

  const ids = new Set();
  for (const [index, flow] of manifest.flows.entries()) {
    const path = `flows[${index}]`;
    if (!flow || typeof flow !== "object") {
      throw contractError(`${path} must be an object`);
    }
    requireNonEmptyString(flow.id, `${path}.id`);
    if (!FLOW_IDS.has(flow.id)) {
      throw contractError(`${path}.id must be one of the approved replayable flow identifiers`);
    }
    if (ids.has(flow.id)) {
      throw contractError(`${path}.id must be unique`);
    }
    ids.add(flow.id);
    requireNonEmptyString(flow.fixture, `${path}.fixture`);
    requireNonEmptyString(flow.path, `${path}.path`);
    if (!flow.path.startsWith("/")) {
      throw contractError(`${path}.path must be a local absolute path`);
    }
    requireNonEmptyString(flow.userFlow, `${path}.userFlow`);
    validateSteps(flow.steps, `${path}.steps`);
    validateAssertions(flow.assertions, `${path}.assertions`);
  }

  return Object.freeze(manifest.flows.map((flow) => Object.freeze({ ...flow })));
}

export function evaluateRunnerResults(flows, results) {
  if (!Array.isArray(results) || results.length !== flows.length) {
    throw contractError("runner must return exactly one result per flow");
  }

  const flowIds = new Set(flows.map((flow) => flow.id));
  const resultIds = new Set();
  const normalized = results.map((result, index) => {
    if (!result || typeof result !== "object") {
      throw contractError(`runner result ${index} must be an object`);
    }
    if (!flowIds.has(result.flowId) || resultIds.has(result.flowId)) {
      throw contractError(`runner result ${index} has an unknown or duplicate flowId`);
    }
    resultIds.add(result.flowId);
    if (!["passed", "failed", "disagreement", "manual-review", "unavailable"].includes(result.status)) {
      throw contractError(`runner result ${index} has an unsupported status`);
    }
    return Object.freeze({
      flowId: result.flowId,
      status: result.status,
      evidence: result.evidence ?? null,
      manualReview: result.status === "disagreement" || result.status === "manual-review",
    });
  });

  const status = normalized.some((result) => result.status === "failed" || result.status === "disagreement")
    ? "failed"
    : normalized.some((result) => result.status === "manual-review")
      ? "manual-review"
    : normalized.some((result) => result.status === "unavailable")
      ? "unavailable"
      : "passed";

  return Object.freeze({
    protocol: "css-tokenography-passmark-report/v1",
    consensusPolicy: "fail-on-disagreement",
    status,
    results: normalized,
  });
}

export async function runFlows({ flows, runner }) {
  if (!runner || typeof runner.run !== "function") {
    throw contractError("runner must implement run(flow)");
  }
  const results = [];
  for (const flow of flows) {
    results.push(await runner.run(flow));
  }
  return evaluateRunnerResults(flows, results);
}

export { FLOW_PROTOCOL, FLOW_IDS };
