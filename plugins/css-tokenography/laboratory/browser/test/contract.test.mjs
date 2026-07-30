import assert from "node:assert/strict";
import test from "node:test";
import config, { deterministicContext } from "../playwright.config.mjs";
import { makeReport, PROTOCOL, verifyAssertions } from "../src/contract.mjs";
import { ENGINES, FIXTURES } from "../src/fixtures.mjs";
import { parseArguments } from "../src/run.mjs";
import { safeFixturePath } from "../src/fixture-server.mjs";

test("pins the ten deterministic fixture families", () => {
  assert.deepEqual(FIXTURES.map((fixture) => fixture.id), ["gradient-runtime", "transform-runtime", "filter-runtime", "backdrop-filter-runtime", "grid-runtime", "subgrid-runtime", "flexbox-runtime", "stacking-hit-test-runtime", "selector-matching-runtime", "feature-detection-runtime"]);
  assert.ok(FIXTURES.every((fixture) => fixture.requiredEngines.join(",") === ENGINES.join(",") && fixture.visualBaseline));
});

test("configures exactly Chromium, Firefox, and WebKit with deterministic context", () => {
  assert.deepEqual(config.projects.map((project) => project.name), ENGINES);
  assert.deepEqual(deterministicContext, { viewport: { width: 1024, height: 768 }, deviceScaleFactor: 1, locale: "en-US", timezoneId: "UTC", colorScheme: "light", reducedMotion: "reduce", forcedColors: "none" });
  assert.equal(config.use.video, "off");
});

test("parses only the Python wrapper's stable command options", () => {
  assert.deepEqual(parseArguments(["--engines", "webkit,chromium", "--format", "json", "--update-snapshots"]), { engines: ["webkit", "chromium"], format: "json", updateSnapshots: true });
  assert.throws(() => parseArguments(["--engines", "chrome"]), /engines/);
  assert.throws(() => parseArguments(["--download-browsers"]), /unknown/);
});

test("does not permit a baseline update from CI", () => {
  const before = process.env.CI;
  const beforeGeneration = process.env.CSS_TOKENOGRAPHY_BASELINE_GENERATION;
  process.env.CI = "1";
  try {
    assert.throws(() => parseArguments(["--update-snapshots"]), /not permitted/);
    process.env.CSS_TOKENOGRAPHY_BASELINE_GENERATION = "1";
    assert.equal(parseArguments(["--update-snapshots"]).updateSnapshots, true);
  } finally {
    if (before === undefined) delete process.env.CI;
    else process.env.CI = before;
    if (beforeGeneration === undefined) {
      delete process.env.CSS_TOKENOGRAPHY_BASELINE_GENERATION;
    } else {
      process.env.CSS_TOKENOGRAPHY_BASELINE_GENERATION = beforeGeneration;
    }
  }
});

test("assertion evaluation and release status preserve lower-layer failure", () => {
  const failures = verifyAssertions({ computed: { display: "block" } }, [{ path: "computed.display", equals: "grid" }]);
  assert.equal(failures.length, 1);
  const report = makeReport({ engines: ["chromium"], generatedAt: "2026-07-30T00:00:00.000Z", results: [{ engine: "chromium", status: "fail", fixtures: [] }] });
  assert.equal(report.protocol, PROTOCOL);
  assert.equal(report.release.status, "fail");
  assert.deepEqual(report.release.reasons, ["deterministic", "browser"]);
  assert.equal(report.agentic.status, "skipped");
});

test("a failed engine wins over an unavailable engine", () => {
  const report = makeReport({ engines: ["chromium", "firefox"], results: [
    { engine: "chromium", status: "unavailable", fixtures: [] },
    { engine: "firefox", status: "fail", fixtures: [] },
  ] });
  assert.equal(report.release.status, "fail");
  assert.deepEqual(report.release.reasons, ["deterministic", "browser"]);
});

test("fixture server rejects traversal outside the local fixture root", () => {
  assert.ok(safeFixturePath("gradients.html")?.endsWith("gradients.html"));
  assert.equal(safeFixturePath("../../package.json"), null);
});
