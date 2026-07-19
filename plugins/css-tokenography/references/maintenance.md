# Maintenance and refresh

Current standards checkpoint: `standards-audit-2026-07-19.md`.

Next implementation phase: `standards-hardening-execplan.md`.

## Automation adapter boundaries

`automation-adapters.json` is metadata, not an installation or execution manifest. The default plugin remains dependency-free and network-free; optional commands are never invoked while validating the registry.

Run `python3 scripts/validate_adapters.py --plugin . --format json` after changing adapter metadata. Passmark remains `blocked-pending-license-review`, and BrowseryTools remains `observation-only` under the records in `licenses/`.

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
5. Run `python3 scripts/validate_coverage.py --plugin .`, all unit tests, every skill quick validator, and plugin-creator validation.
6. Use plugin-creator's `update_plugin_cachebuster.py` and reinstall from the personal marketplace when shipping an update.
