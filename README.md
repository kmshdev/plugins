# kmshdev Codex plugins

Public Codex plugins maintained by [kmshdev](https://github.com/kmshdev).

## Install the marketplace

```sh
codex plugin marketplace add kmshdev/plugins --ref main
codex plugin add docdev@kmshdev
codex plugin add css-tokenography@kmshdev
```

Restart Codex if the newly installed plugin does not appear immediately.

## Plugins

### docdev

`docdev` creates evidence-backed development, planning, architecture, and library documentation in MDX. Its optional Astro workflow validates the MDX contract and renders the content as a static documentation site.

The plugin provides two skills:

- `$docdev-author` investigates repository evidence, creates typed MDX documents from templates, and validates their frontmatter and structure.
- `$docdev-site` scaffolds a reusable Astro documentation site, imports validated MDX, and runs content, type, and production-build checks.

The plugin source is under [`plugins/docdev`](./plugins/docdev). The marketplace catalog is [`/.agents/plugins/marketplace.json`](./.agents/plugins/marketplace.json).

### css-tokenography

`css-tokenography` provides one implicitly invokable orchestration router plus 17 explicitly invokable CSS, typography, and web-performance specialists for Codex. The suite is backed by standards research, source coverage records, and dependency-free developer-tool CLIs.

Broad CSS requests route through `$css-tokenography`; explicit `$css-grid`, `$web-typography`, and other specialist invocations remain available. Every specialist disables implicit invocation so broad prompts have one deterministic entry point.

Its deterministic tooling includes grid-area mapping, subgrid modeling, performance-budget analysis, WCAG contrast checks, OKLCH conversion, CSS specificity, fluid `clamp()` generation, transform composition, and cubic Bézier validation. Browser-, raster-, or codec-dependent tools have explicit procedural workflows instead of hidden omissions.

The plugin source is under [`plugins/css-tokenography`](./plugins/css-tokenography). Its guide, tool, and source-skill inventories are under [`plugins/css-tokenography/references`](./plugins/css-tokenography/references). The current semantic audit and next-phase implementation plan are [`standards-audit-2026-07-19.md`](./plugins/css-tokenography/references/standards-audit-2026-07-19.md) and [`standards-hardening-execplan.md`](./plugins/css-tokenography/references/standards-hardening-execplan.md).

### nautilus-trader

`nautilus-trader` provides five independently usable skills for NautilusTrader
0.64.0 Rust: actors, strategies, data integration, backtesting and live nodes.
It includes configuration-driven FX/equity examples, construction-only Databento
plus Interactive Brokers wiring, advanced order/composition guidance, replay,
Rust test/simulation/benchmark recipes and original icons.

The 0.64 beta is published on `codex/nautilus-rust-workflows`; `main` currently
contains the older 0.63 release. Install the beta explicitly:

```sh
codex plugin marketplace add kmshdev/plugins --ref codex/nautilus-rust-workflows
codex plugin add nautilus-trader@kmshdev --json
```

Check that the returned version begins with `0.64.0+codex.`. The response's
`installedPath` contains the plugin guide and examples. This selects the beta
ref for the `kmshdev` marketplace; it does not install or update unrelated plugins.

See [the plugin guide](plugins/nautilus-trader/README.md) for installation,
repository-only activation and runnable examples, and
[the build log](plugins/nautilus-trader/BUILD-LOG.md) for verified scope.

## Validate locally

From a checkout of this repository:

```sh
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/docdev
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/docdev/skills/docdev-author
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/docdev/skills/docdev-site
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/css-tokenography
python3 plugins/css-tokenography/scripts/validate_coverage.py --plugin plugins/css-tokenography
python3 plugins/css-tokenography/skills/css-tokenography/scripts/validate_router.py --plugin plugins/css-tokenography
python3 -m unittest discover -s plugins/css-tokenography/tests -v
```

The validators are bundled with Codex. The skill validator requires PyYAML.

## License

MIT. See [`LICENSE`](./LICENSE).
