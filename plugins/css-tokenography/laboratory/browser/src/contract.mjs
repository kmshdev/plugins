export const PROTOCOL = "css-tokenography-browser-lab/v1";

export function readPath(value, dottedPath) {
  return dottedPath.split(".").reduce((current, part) => current?.[part], value);
}

export function verifyAssertions(observation, assertions) {
  const failures = [];
  for (const assertion of assertions) {
    const actual = readPath(observation, assertion.path);
    let pass = false;
    if ("equals" in assertion) pass = JSON.stringify(actual) === JSON.stringify(assertion.equals);
    if ("notEquals" in assertion) pass = actual !== assertion.notEquals;
    if ("includes" in assertion) pass = typeof actual === "string" && actual.includes(assertion.includes);
    if ("greaterThan" in assertion) pass = actual > assertion.greaterThan;
    if ("lessThan" in assertion) {
      const right = typeof assertion.lessThan === "string" ? readPath(observation, assertion.lessThan) : assertion.lessThan;
      pass = actual < right;
    }
    if (!pass) failures.push({ assertion, actual });
  }
  return failures;
}

function sectionStatus(results, field) {
  const statuses = results.map((result) => result[field] ?? result.status);
  if (statuses.some((status) => status === "fail")) return "fail";
  return statuses.some((status) => status === "unavailable") ? "unavailable" : "pass";
}

function computedRelease(deterministic, browser) {
  const failures = [];
  const unavailable = [];
  if (deterministic === "fail") failures.push("deterministic");
  else if (deterministic === "unavailable") unavailable.push("deterministic");
  if (browser === "fail") failures.push("browser");
  else if (browser === "unavailable") unavailable.push("browser");
  if (failures.length) return { status: "fail", reasons: failures };
  if (unavailable.length) return { status: "unavailable", reasons: unavailable };
  return { status: "pass", reasons: [] };
}

export function makeReport({ engines, results, generatedAt = new Date().toISOString() }) {
  const deterministicStatus = sectionStatus(results, "deterministic_status");
  const browserStatus = sectionStatus(results, "browser_status");
  const release = computedRelease(deterministicStatus, browserStatus);
  const fixtures = results.flatMap((result) => result.fixtures ?? []).map((fixture) => ({
    ...fixture,
    engine: fixture.engine ?? results.find((result) => (result.fixtures ?? []).includes(fixture))?.engine ?? null,
  }));
  return {
    protocol: PROTOCOL,
    generated_at: generatedAt,
    deterministic: { status: deterministicStatus, checks: results.map((result) => ({ engine: result.engine, status: result.deterministic_status ?? result.status, blocker: result.blocker ?? null })) },
    browser: { status: browserStatus, fixtures },
    agentic: { status: "skipped", required: false, evaluations: [] },
    release,
  };
}
