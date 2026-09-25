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

`nautilus-trader` provides six independently usable skills for NautilusTrader
0.64.0 Rust: actors, strategies, data integration, backtesting, live nodes and
persistent run delivery with CI/CD scaffolds, PostgreSQL, Redis and cloud catalogs.
It includes configuration-driven FX/equity examples, construction-only Databento
plus Interactive Brokers wiring, advanced order/composition guidance, replay,
Rust test/simulation/benchmark recipes and original icons.

Released installs use `main` for the five existing 0.64 workflows. To test the
new run-delivery skill before its merge, replace `--ref main` below with
`--ref codex/nautilus-rust-workflows`:

```sh
codex plugin marketplace add kmshdev/plugins --ref main
codex plugin add nautilus-trader@kmshdev --json
```

Check that the returned version begins with `0.64.0+codex.`. The response's
`installedPath` contains the plugin guide and examples. After merge, use `main`
rather than retaining the temporary candidate ref. The selected ref applies to
the `kmshdev` marketplace; this command does not install or update unrelated plugins.

See [the plugin guide](plugins/nautilus-trader/README.md) for installation,
repository-only activation and runnable examples, and
[the build log](plugins/nautilus-trader/BUILD-LOG.md) for verified scope.

### iOS and Swift workflow suite

- [`adversial-ios-review-and-refactor`](./plugins/adversial-ios-review-and-refactor) packages formal rendered iOS, SwiftUI, and Swift gates. `$ios-review-and-refactor` coordinates scoped fixes after their verdicts. The identifier retains its requested spelling; the display name is **iOS Review and Refactor**.
- [`ios-interface-craft`](./plugins/ios-interface-craft) routes screen design, visual critique, platform conventions, navigation, motion, and design-system work. It keeps `ios-taste` advisory and separate from the formal gates.
- [`swift-app-foundations`](./plugins/swift-app-foundations) covers SwiftData, measured performance, and modular MVVM-C architecture when that architecture belongs to the app.
- [`code-quality-workbench`](./plugins/code-quality-workbench) selects a general maintainability, architecture, simplification, refactoring, or DDD pass on request. It does not run at every session end.
- [`ios-feature-delivery`](./plugins/ios-feature-delivery) provides `$ios-feature-workflow` and a [copyable trigger prompt](./plugins/ios-feature-delivery/skills/ios-feature-workflow/references/trigger-prompt.md) for implementing, running, verifying, and reviewing one app feature. It uses Build iOS Apps when installed and falls back to the project's native build tools.

The packaged specialist skills are self-contained snapshots of the individually downloadable skills in `dot-skills`. Each package records its source skill paths and hashes in `references/source-inventory.json`.

### engineering-research-and-planning

[`engineering-research-and-planning`](./plugins/engineering-research-and-planning) provides an explicit router for nine focused methods: app and feature plans, technical RFCs, living ExecPlans, external code pattern research, codebase and Swift domain analysis, and deterministic metric design and validation. It selects the method that matches the requested deliverable without making planning a prerequisite for routine coding work.

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
