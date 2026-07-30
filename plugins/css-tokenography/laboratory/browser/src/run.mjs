import { access, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium, devices, firefox, webkit } from "@playwright/test";
import { collect } from "./collectors.mjs";
import { makeReport, verifyAssertions } from "./contract.mjs";
import { ENGINES, FIXTURES } from "./fixtures.mjs";
import { startFixtureServer } from "./fixture-server.mjs";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const BROWSERS = { chromium, firefox, webkit };
const CONTEXT = Object.freeze({
  ...devices["Desktop Chrome"],
  viewport: { width: 1024, height: 768 },
  deviceScaleFactor: 1,
  locale: "en-US",
  timezoneId: "UTC",
  colorScheme: "light",
  reducedMotion: "reduce",
  forcedColors: "none",
});

export function parseArguments(argv) {
  const options = { engines: ENGINES, format: "json", updateSnapshots: false };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--engines") options.engines = argv[++index]?.split(",").filter(Boolean) ?? [];
    else if (argument === "--format") options.format = argv[++index] ?? "";
    else if (argument === "--update-snapshots") options.updateSnapshots = true;
    else if (argument === "--help") options.help = true;
    else throw new Error(`unknown argument: ${argument}`);
  }
  if (!options.engines.length || options.engines.some((engine) => !ENGINES.includes(engine))) throw new Error("--engines must contain chromium, firefox, and/or webkit");
  if (!["json", "text"].includes(options.format)) throw new Error("--format must be json or text");
  if (
    options.updateSnapshots
    && process.env.CI
    && process.env.CSS_TOKENOGRAPHY_BASELINE_GENERATION !== "1"
  ) {
    throw new Error(
      "--update-snapshots is not permitted in required CI; use the dedicated baseline-generation workflow",
    );
  }
  return options;
}

function screenshotPath(engine, fixture) {
  return resolve(ROOT, "snapshots", engine, `${fixture.id}.png`);
}

async function compareScreenshot(page, engine, fixture, updateSnapshots) {
  const path = screenshotPath(engine, fixture);
  const reportPath = `snapshots/${engine}/${fixture.id}.png`;
  let previous = null;
  let image = null;
  for (let attempt = 0; attempt < 5; attempt += 1) {
    image = await page.screenshot({ animations: "disabled", caret: "hide", scale: "css" });
    if (previous?.equals(image)) break;
    previous = image;
    await page.waitForTimeout(50);
  }
  if (updateSnapshots) {
    await mkdir(dirname(path), { recursive: true });
    await writeFile(path, image);
    return { status: "updated", path: reportPath };
  }
  try {
    const baseline = await readFile(path);
    return { status: baseline.equals(image) ? "pass" : "fail", path: reportPath };
  } catch (error) {
    if (error?.code === "ENOENT") return { status: "missing", path: reportPath };
    throw error;
  }
}

async function isInstalled(browser) {
  try {
    await access(browser.executablePath());
    return true;
  } catch {
    return false;
  }
}

export async function runLaboratory(options) {
  const unavailable = [];
  for (const engine of options.engines) if (!(await isInstalled(BROWSERS[engine]))) unavailable.push(engine);
  if (unavailable.length) {
    const unavailableSet = new Set(unavailable);
    return makeReport({ engines: options.engines, results: options.engines.map((engine) => ({
      engine,
      status: "unavailable",
      deterministic_status: "unavailable",
      browser_status: "unavailable",
      blocker: unavailableSet.has(engine)
        ? `Playwright ${engine} executable is not installed; run the explicit documented playwright install command.`
        : `Not run because the requested multi-engine set is incomplete: ${unavailable.join(", ")}.`,
      fixtures: FIXTURES.map((fixture) => ({ id: fixture.id, engine, browser_version: null, owner: fixture.owner, claim_ids: fixture.claimIds, status: "unavailable", observation_status: "unavailable" })),
    })) });
  }
  const server = await startFixtureServer();
  try {
    const results = [];
    for (const engine of options.engines) {
      const browser = await BROWSERS[engine].launch({ headless: true });
      const version = browser.version();
      const fixtures = [];
      try {
        for (const fixture of FIXTURES) {
          const context = await browser.newContext(CONTEXT);
          const page = await context.newPage();
          await page.route("**/*", (route) => route.request().url().startsWith(server.origin) ? route.continue() : route.abort());
          try {
            await page.goto(server.urlFor(fixture.path), { waitUntil: "load" });
            const observation = await collect(page, fixture.collectors);
            const assertionFailures = verifyAssertions(observation, fixture.assertions);
            const screenshot = fixture.visualBaseline ? await compareScreenshot(page, engine, fixture, options.updateSnapshots) : { status: "not-required" };
            const deterministicStatus = assertionFailures.length ? "fail" : "pass";
            const browserStatus = screenshot.status === "fail" || screenshot.status === "missing" ? "fail" : "pass";
            const status = deterministicStatus === "pass" && browserStatus === "pass" ? "pass" : "fail";
            fixtures.push({ id: fixture.id, engine, browser_version: version, owner: fixture.owner, claim_ids: fixture.claimIds, status, deterministic_status: deterministicStatus, browser_status: browserStatus, observation_status: "observed", observation, assertion_failures: assertionFailures, screenshot });
          } catch (error) {
            fixtures.push({ id: fixture.id, engine, browser_version: version, owner: fixture.owner, claim_ids: fixture.claimIds, status: "fail", deterministic_status: "fail", browser_status: "fail", observation_status: "error", blocker: error instanceof Error ? error.message : String(error) });
          } finally {
            await context.close();
          }
        }
      } finally {
        await browser.close();
      }
      results.push({ engine, browser_version: version, status: fixtures.every((fixture) => fixture.status === "pass") ? "pass" : "fail", deterministic_status: fixtures.every((fixture) => fixture.deterministic_status === "pass") ? "pass" : "fail", browser_status: fixtures.every((fixture) => fixture.browser_status === "pass") ? "pass" : "fail", fixtures });
    }
    return makeReport({ engines: options.engines, results });
  } finally {
    await server.close();
  }
}

function printHelp() {
  process.stdout.write("Usage: node src/run.mjs [--engines chromium,firefox,webkit] [--format json|text] [--update-snapshots]\n");
}

async function main() {
  let options;
  try { options = parseArguments(process.argv.slice(2)); } catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 2; return; }
  if (options.help) { printHelp(); return; }
  const report = await runLaboratory(options);
  if (options.format === "json") process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
  else process.stdout.write(`Browser laboratory: ${report.release.status} (${options.engines.join(", ")})\n`);
  process.exitCode = report.release.status === "pass" ? 0 : report.release.status === "unavailable" ? 2 : 1;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) main().catch((error) => { process.stderr.write(`${error.stack ?? error}\n`); process.exitCode = 1; });
