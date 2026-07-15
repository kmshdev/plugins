# Maintenance and refresh

1. Remap `https://design.dev/guides/` and `https://design.dev/tools/`; compare index links, sitemap-backed map results, and the previous inventory.
2. Scrape changed guide/tool pages and record the retrieval date. Keep raw output outside the plugin in an ignored Firecrawl or work-note directory.
3. Recheck material browser, accessibility, performance, and Windsurf claims against current official sources.
4. Update `guide-coverage.json`, `tool-coverage.json`, and `standards-divergences.md` without copying substantial source prose.
5. Run `python3 scripts/validate_coverage.py --plugin .`, all unit tests, every skill quick validator, and plugin-creator validation.
6. Use plugin-creator's `update_plugin_cachebuster.py` and reinstall from the personal marketplace when shipping an update.
