# Implement the Phase 3 browser and agentic regression laboratory

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This plan follows `/Users/kmsh/.codex/agent/PLANS.md`. It is intentionally self-contained so a contributor can resume the work from this file and the repository alone.

## Purpose / Big Picture

CSS Tokenography currently validates CSS tool inputs and produces deterministic JSON, but several claims still depend on how real browser engines compute styles, place boxes, paint stacking contexts, and expose runtime feature support. After this change, a maintainer can run one command to collect structured evidence from Chromium, Firefox, and WebKit without allowing the runner to download browsers implicitly. The same laboratory will provide optional Passmark user-flow evaluations above the deterministic browser layer, with model disagreement failing closed and never overwriting deterministic failures.

The visible proof is a versioned JSON report. It names each fixture, engine, browser version, computed observations, screenshot result, and blocker. A three-engine run succeeds only when every required deterministic fixture passes. Agentic results are reported separately and can make a release stricter, but cannot turn a lower-layer failure into a pass.

## Progress

- [x] (2026-07-30 14:47Z) Confirmed `origin/main` at `7ac370cf6b8cb5d3ae1ec07870329abe0f0290e0` and created isolated branch `agent/css-tokenography-phase3`.
- [x] (2026-07-30 14:47Z) Ran the existing Python suite and coverage, adapter, and router validators successfully before edits.
- [x] (2026-07-30 14:47Z) Verified current dependency metadata: `@playwright/test` 1.62.0, Passmark 1.0.16, and Stagehand 3.7.1.
- [x] (2026-07-30 14:47Z) Added versioned laboratory report and ten-fixture manifest contracts.
- [x] (2026-07-30 14:47Z) Added the Playwright multi-engine laboratory and deterministic fixtures.
- [x] (2026-07-30 14:47Z) Generated and compared 30 Linux visual baselines with the pinned Playwright 1.62.0 container.
- [x] (2026-07-30 14:47Z) Added the optional Passmark contract and experimental Stagehand discovery boundary.
- [x] (2026-07-30 14:47Z) Connected browser evidence to coverage validation and specialist guidance.
- [x] (2026-07-30 14:47Z) Added path-scoped deterministic CI and manual baseline and agentic workflows.
- [x] (2026-07-30 14:47Z) Ran 247 Python tests, 15 Node contract tests, 30 Linux browser comparisons, all inventory validators, all 18 skill validators, and canonical plugin validation successfully.
- [x] (2026-07-30 14:47Z) Updated the plugin cachebuster from `0.1.0+codex.20260727162259` to `0.1.0+codex.20260730144132`.
- [ ] Commit coherent snapshots and push the branch.

## Surprises & Discoveries

- Observation: The existing Passmark registry entry treats Passmark as a `passmark --version` executable, but Passmark 1.0.16 publishes a library export and no `bin` entry.
  Evidence: the npm package manifest exposes `main`, `types`, and `exports`, but no command-line binary.

- Observation: Passmark’s package manifest uses `FSL-1.1-Apache-2.0`, while its repository badge and `LICENSE.md` identify `FSL-1.1-ALv2`.
  Evidence: the upstream license grants an Apache-2.0 future license two years after each version becomes available; npm records 1.0.16 as published on 2026-06-08.

- Observation: Playwright screenshot output varies by operating system, browser, fonts, and headless mode.
  Evidence: Playwright’s snapshot documentation requires baselines to be generated and compared in the same environment.

- Observation: Functions declared in the Node module are not serialized into
  `page.evaluate`.
  Evidence: the first live three-engine run failed 24 fixtures with
  `ReferenceError: rect is not defined`; moving the helper into the browser
  closure made all 30 computed probes pass.

- Observation: `npm run` can write lifecycle banners to stdout on npm 11 even
  when the child command emits JSON only.
  Evidence: the pinned Playwright container made the aggregate report
  unparsable until the browser workspace set `loglevel=silent`.

- Observation: Passmark 1.0.16 and Stagehand 3.7.1 currently bring audited
  transitive findings despite being optional.
  Evidence: `npm audit --json` reported 31 moderate and 7 high findings for
  Passmark, and 16 low, 1 moderate, and 1 high finding for Stagehand. The
  browser workspace reported none.

## Decision Log

- Decision: Keep the existing dependency-free Python CLIs as the public semantic core and place Node dependencies under `plugins/css-tokenography/laboratory/`.
  Rationale: installing the plugin must not install Node, browsers, AI providers, or Redis.
  Date/Author: 2026-07-30 / Codex.

- Decision: Use `@playwright/test` rather than a plugin MCP server.
  Rationale: the approved phase requires repeatable multi-project tests, structured fixtures, and screenshot baselines. MCP remains useful only for exploratory sessions.
  Date/Author: 2026-07-30 / Codex.

- Decision: Approve Passmark 1.0.16 only as an optional internal-use development dependency and record the FSL restrictions.
  Rationale: the user explicitly selected internal use. Passmark remains outside default plugin execution and distribution claims.
  Date/Author: 2026-07-30 / Codex.

- Decision: Configure Passmark with `fail-on-disagreement`; CUA and video remain opt-in manual evidence.
  Rationale: multi-model ambiguity must be visible. CUA bypasses portable caching, and video assertions use a single Gemini path and may fall back to snapshot behavior.
  Date/Author: 2026-07-30 / Codex.

- Decision: Keep Stagehand in a separate experimental workspace and out of required CI.
  Rationale: its discovery, caching, and self-healing capabilities overlap Passmark. It may propose candidate flows but cannot define CSS semantics or release status.
  Date/Author: 2026-07-30 / Codex.

## Outcomes & Retrospective

Phase 3 now has ten manifest-backed fixture families, three Playwright projects,
30 reviewed Linux baselines, 247 Python tests, 15 Node contract tests, and 30
passing browser comparisons. Browser Feature Detection moved from procedural to
implemented-core, producing an inventory of 8 implemented-full, 11
implemented-core, and 14 procedural tools.

The browser wrapper reports all 30 engine/fixture observations with monotonic
release precedence. A live run found and corrected the collector serialization
defect before release. The pinned Linux container then passed both the public
aggregate runner and the Playwright screenshot suite.

Passmark has seven provider-neutral flow contracts, explicit Redis and
credential preflight, fail-on-disagreement, and manual-only CUA/video evidence.
Its fake contract tests pass. A live model evaluation was not run because this
implementation session intentionally had no approved provider credentials or
Redis service; the manual workflow is the only remote execution boundary.
Stagehand remains candidate-only and cannot modify release evidence.

## Context and Orientation

The plugin lives at `plugins/css-tokenography`. Its 18 skills are under `skills/`: one implicitly invokable router and 17 explicit specialists. `references/tool-coverage.json` contains the 33 design.dev tool dispositions. `scripts/css_tokenography_core/` contains shared deterministic evidence types, while `scripts/run_oracles.py` invokes optional parser adapters. Existing Python tests live under `tests/`.

In this plan, a “fixture” is a small synthetic local HTML page with declared expected computed behavior. A “collector” is JavaScript executed by Playwright that serializes computed styles, rectangles, layout placement, hit testing, selector matches, or accessibility state. A “baseline” is a reviewed screenshot tied to a Playwright project and operating system. An “agentic evaluation” is a natural-language Passmark flow that runs only after deterministic browser checks.

The laboratory must preserve three authority layers. The Python core describes the plugin’s deterministic model. Browser observations show what an engine did at runtime. Passmark evaluates workflow fidelity. These layers are recorded separately because one cannot substitute for another.

## Plan of Work

First, add a versioned fixture manifest at `references/browser-fixtures.json` and a Python laboratory model under `scripts/css_tokenography_core/`. The model validates fixture ownership, engine lists, claim identifiers, standards links, observation status, and the final release decision. It must make precedence explicit: deterministic or browser failure wins; agentic success cannot override it.

Next, add `laboratory/browser/` as a private locked Node project pinned to
`@playwright/test` 1.62.0. Keep Passmark 1.0.16 in the separate
`laboratory/passmark/` workspace so the deterministic browser laboratory does
not install an agentic dependency. Configure Chromium, Firefox, and WebKit with
the same viewport, device scale, locale, timezone, color scheme, and
reduced-motion setting. Serve only local synthetic fixtures. Block unexpected
external requests during deterministic runs.

Implement ten fixture families: gradients, transforms, filters, backdrop filters, grid, subgrid, Flexbox, stacking and hit testing, selector matching, and feature detection. Each test must collect JSON before comparing screenshots. The report must retain per-engine results rather than normalizing disagreement away.

Add `scripts/run_browser_lab.py` as the dependency-free entry point. It must support `--help`, engine selection, JSON or readable output, and an explicit snapshot-update flag. It must preflight Node packages and browser binaries and return an unavailable report rather than calling any install command.

Add Passmark flow definitions for named grid creation, disconnected-grid rejection, subgrid placement, responsive Flexbox, transform plus transition, dark-mode variables, and selector matching. Unit and contract tests use a fake runner. The live runner requires explicit environment variables and Redis, disables telemetry by default, and uses `fail-on-disagreement`. CUA and video flags are rejected unless explicitly opted in; their results remain manual-review evidence.

Add `laboratory/stagehand/` as a separately installed experimental project pinned to Stagehand 3.7.1. Its only durable output is a candidate deterministic-flow JSON document. It cannot update coverage, baselines, or release status.

Finally, extend coverage validation so implemented browser-dependent claims must name a valid browser fixture. Promote Browser Feature Detection to `implemented-core` only after the three-engine fixture exists. Update the affected specialist guidance, maintenance documentation, root README, license records, and adapter registry. Add a path-scoped GitHub Actions workflow for deterministic Python and Playwright validation, plus manual workflows for baseline artifact generation and live Passmark evaluation.

## Concrete Steps

Work from:

    /Users/kmsh/.codex/work-notes/css-tokenography/github-publish/kmshdev-plugins/.worktrees/css-tokenography-phase3

Run the Python baseline and validators:

    python3 -m unittest discover -s plugins/css-tokenography/tests -v
    python3 plugins/css-tokenography/scripts/validate_coverage.py --plugin plugins/css-tokenography
    python3 plugins/css-tokenography/scripts/validate_adapters.py --plugin plugins/css-tokenography --format json
    python3 plugins/css-tokenography/skills/css-tokenography/scripts/validate_router.py --plugin plugins/css-tokenography --format json

Install the optional browser laboratory only when dependency installation is intended:

    npm --prefix plugins/css-tokenography/laboratory/browser ci

Install browsers explicitly; no test or plugin command may run this automatically:

    npx --prefix plugins/css-tokenography/laboratory/browser playwright install chromium firefox webkit

Run deterministic browser checks:

    python3 plugins/css-tokenography/scripts/run_browser_lab.py --engines chromium,firefox,webkit --format json

Run fake Passmark contract tests without credentials:

    npm --prefix plugins/css-tokenography/laboratory/passmark run test:passmark:contract

Run a live Passmark evaluation only with the documented model credentials and Redis already available:

    npm --prefix plugins/css-tokenography/laboratory/passmark run test:passmark:live

The live command must fail before opening a browser when required credentials or Redis are absent.

## Validation and Acceptance

The Python test suite must pass without Node installed. The browser wrapper’s `--help` must work without Node packages. When packages or browser binaries are missing, JSON output must say `unavailable`, identify the missing component, and return exit code 2 without downloading anything.

With browsers installed, all ten fixtures must run in Chromium, Firefox, and WebKit. Every result must name the fixture, engine, browser version, owner, claim IDs, and observation status. A browser disagreement must remain visible per engine and block any universal claim.

Every fixture must have a screenshot baseline for each required Linux engine, for 30 baselines total. Snapshot updates must require an explicit command and must be rejected in the required comparison job.

The aggregate result must prove precedence. A fake deterministic failure followed by a passing Passmark result must still fail. A Passmark disagreement must report disagreement and fail its own gate. A missing optional Passmark runtime must not be reported as success.

`references/tool-coverage.json` must remain 33 rows. The guide inventory must
remain 17 rows and the skill inventory 18 directories. No removed agent-product
skill may return.

Canonical plugin validation, all 18 quick skill validations, `git diff --check`, and the full Python and Node suites must pass before the cachebuster is updated and the branch is pushed.

## Idempotence and Recovery

The new worktree is isolated from existing user branches. Re-running fixture collection overwrites only ignored run artifacts. Required tests never rewrite baselines. The explicit snapshot-update command is the only baseline mutation path.

If package installation fails, remove only ignored `node_modules` and retry `npm ci`; do not alter the lockfile to obtain a pass. If a browser is unavailable, retain the structured unavailable result and run the explicit Playwright install command only when installation remains authorized.

If live Passmark credentials are absent, complete deterministic and fake-adapter validation and record the live run as blocked. Never print environment values. If a model disagrees, retain both verdicts and require review rather than consulting an arbiter.

## Artifacts and Notes

Research artifacts remain outside the repository under `/Users/kmsh/.codex/work-notes/css-tokenography/phase-3/.firecrawl`. Generated reports, traces, videos, and screenshot diffs remain ignored. Only reviewed fixture sources, manifests, and baseline images are tracked.

## Interfaces and Dependencies

`scripts/run_browser_lab.py` is the stable public laboratory command. It accepts `--engines`, `--format`, and `--update-snapshots`, and returns exit code 0 for pass, 1 for deterministic or visual failure, and 2 for unavailable dependencies.

`references/browser-fixtures.json` is a JSON array. Every row contains a unique fixture `id`, a specialist `owner`, one or more `tool_urls`, one or more `claim_ids`, a local fixture path, collectors, required engines, a visual-baseline flag, and standards URLs.

The browser runner emits protocol `css-tokenography-browser-lab/v1`. The aggregate report contains `deterministic`, `browser`, `agentic`, and `release` sections. `release.status` is computed from lower-layer precedence and is never supplied directly by an adapter.

The required Node dependency is exactly `@playwright/test` 1.62.0. The optional internal-use dependency is exactly Passmark 1.0.16. Stagehand 3.7.1 lives in its own experimental project. Redis 7 is a manual live-evaluation service, not a plugin runtime dependency.
