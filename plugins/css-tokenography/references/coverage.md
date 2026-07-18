# Coverage inventory

Retrieved on 2026-07-16 with Firecrawl.

- The current design.dev guides index exposes 39 detail URLs; 17 are in this plugin's required scope.
- The current tools index exposes 33 detail URLs. A sitemap-backed map also returned 33; a direct no-sitemap crawl returned 32. The supplied screenshot's category badges total 34 and are treated as stale visual evidence.
- `guide-coverage.json` owns the one-guide-to-one-skill mapping.
- `tool-coverage.json` records all 33 tools, including inputs, outputs, ownership, deterministic boundaries, artifacts, fixtures, status, and exclusions.
- `source-migration.json` records the preserve, rewrite, split, or retirement destination for each substantive source-skill section.

`implemented-full` means the clean-room CLI models the observed tool's complete non-visual contract. `implemented-core` means the CLI models deterministic CSS or calculation semantics while leaving browser presentation out. `procedural` means browser, raster, codec, or unavailable asset behavior prevents a faithful dependency-free implementation; each such entry names the blocker and owning workflow.
