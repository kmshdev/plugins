# Maintenance and refresh

Current standards checkpoint: `standards-audit-2026-07-19.md`.

Current implementation plan: `browser-laboratory-execplan.md`.

## Automation adapter boundaries

`automation-adapters.json` is metadata, not an installation or execution manifest. The default plugin remains dependency-free and network-free; optional commands are never invoked while validating the registry.

Run `python3 scripts/validate_adapters.py --plugin . --format json` after changing adapter metadata. Playwright is the optional deterministic browser runner. Passmark is approved only for internal-use evaluation under the FSL record in `licenses/passmark.md`; Stagehand is experimental discovery only.

## Browser laboratory maintenance

`browser-fixtures.json` is the canonical ten-fixture inventory. Every
browser-dependent implemented claim must point to a fixture through
`tool-coverage.json`. The browser runner records each engine separately and
cannot silently normalize a disagreement into a pass.

The dependency-free wrapper never installs packages or browser binaries:

```bash
python3 scripts/run_browser_lab.py --engines chromium,firefox,webkit --format json
```

Install optional workspaces and browsers only through explicit maintainer
commands. Required comparison jobs must not pass `--update-snapshots`.
Screenshot baselines are valid only for the operating system, browser build,
fonts, and headless configuration that created them.

Passmark contract tests use a fake runner. Live evaluation requires explicit
opt-in, configured model providers, Redis, and the local browser fixture
server. A Passmark pass never overrides a deterministic or browser failure.
Stagehand output is candidate-only and cannot edit coverage, baselines, or
release decisions.

## Evidence-envelope pilot maintenance

The canonical contrast and transform CLIs import `css_tokenography_core` from a
path resolved relative to their own files, so calling them from outside the
plugin must continue to work. `--evidence` is serialization-only: it wraps the
existing report, never invokes an optional adapter, and emits JSON even when the
CLI's normal readable format is the default. A core-only envelope has no oracle
observations and must retain the `unavailable` classification.

After changing either pilot, run:

```bash
python3 -m unittest -v plugins.css-tokenography.tests.test_evidence_compatibility
```

The compatibility suite pins raw stdout bytes for the legacy JSON, CSS, and
human-readable modes, as well as failure exit codes and diagnostics.

## Refresh procedure

1. Remap `https://design.dev/guides/` and `https://design.dev/tools/`; compare index links, sitemap-backed map results, and the previous inventory.
2. Scrape changed guide/tool pages and record the retrieval date. Keep raw output outside the plugin in an ignored Firecrawl or work-note directory.
3. Recheck material browser, accessibility, and performance claims against current official sources.
4. Update `guide-coverage.json`, `tool-coverage.json`, and `standards-divergences.md` without copying substantial source prose.
5. Run `python3 scripts/validate_coverage.py --plugin .`, `python3 scripts/validate_adapters.py --plugin . --format json`, `python3 skills/css-tokenography/scripts/validate_router.py --plugin .`, all unit tests, all optional Node contract tests, all 18 skill quick validators, and plugin-creator validation.
6. Use plugin-creator's `update_plugin_cachebuster.py` and reinstall from the personal marketplace when shipping an update.

## Router evaluation

The plugin has 18 total skills: `$css-tokenography` is the only implicitly
invokable router, and the 17 design.dev guide specialists are explicit-only.
After changing routing descriptions, policies, or overlap rules:

```bash
python3 skills/css-tokenography/scripts/validate_router.py --plugin . --format json
python3 skills/css-tokenography/scripts/evaluate_routes.py --format human
```

The second command is a side-effect-free dry run. Use `--apply` only when
temporary marketplace replacement is authorized; the evaluator snapshots and
restores the configured `kmshdev` marketplace and candidate-plugin state.
