# Coverage inventory

Retrieved on 2026-07-16 with Firecrawl.

- The current design.dev guides index exposes 39 detail URLs; 17 are in this plugin's required scope.
- The current tools index exposes 33 detail URLs. A sitemap-backed map also returned 33; a direct no-sitemap crawl returned 32. The supplied screenshot's category badges total 34 and are treated as stale visual evidence.
- `guide-coverage.json` owns the one-guide-to-one-skill mapping.
- `tool-coverage.json` records all 33 tools, including inputs, outputs, ownership, deterministic boundaries, artifacts, fixture-driven validation commands, status, and structured coverage gaps.
- `source-migration.json` records the preserve, rewrite, split, or retirement destination for each substantive source-skill section.

`implemented-full` means an owner-bound clean-room CLI has fixture-driven executable evidence for the observed tool's complete non-visual contract. `implemented-core` means the same evidence boundary covers named deterministic semantics while leaving presentation out. `procedural` makes no implementation-coverage claim; its structured gap names missing behavior, the future owner CLI and tests, and observable restoration outcomes.

## Evidence-envelope pilot

The canonical `color_contrast_checker.py` and `css_transform_playground.py` CLIs
accept an opt-in `--evidence` flag. Without that flag, their JSON and readable
outputs and exit behavior remain unchanged. With it, each CLI emits the same
deterministic report under `EvidenceEnvelope.core`; it does not run an optional
oracle. Therefore the empty observation set is classified as `unavailable`,
not as agreement, passing, or conformance evidence.
