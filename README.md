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

`css-tokenography` provides one implicitly invokable orchestration router plus 17 explicitly invokable CSS, typography, and web-performance specialists for Codex. The suite is backed by standards research, source coverage records, dependency-free developer-tool CLIs, and an optional browser laboratory.

Broad CSS requests route through `$css-tokenography`; explicit `$css-grid`, `$web-typography`, and other specialist invocations remain available. Every specialist disables implicit invocation so broad prompts have one deterministic entry point.

Its deterministic tooling includes grid-area mapping, subgrid modeling, performance-budget analysis, WCAG contrast checks, OKLCH conversion, CSS specificity, fluid `clamp()` generation, transform composition, and cubic Bézier validation. The optional laboratory adds Chromium, Firefox, and WebKit runtime probes for ten browser-dependent fixture families. Passmark is an internal-use, opt-in workflow evaluator above the deterministic layer; Stagehand remains an experimental flow-discovery boundary.

The plugin source is under [`plugins/css-tokenography`](./plugins/css-tokenography). Its guide, tool, source-skill, and browser-fixture inventories are under [`plugins/css-tokenography/references`](./plugins/css-tokenography/references). The semantic audit and browser-laboratory plan are [`standards-audit-2026-07-19.md`](./plugins/css-tokenography/references/standards-audit-2026-07-19.md) and [`browser-laboratory-execplan.md`](./plugins/css-tokenography/references/browser-laboratory-execplan.md).

## Validate locally

From a checkout of this repository:

```sh
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/docdev
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/docdev/skills/docdev-author
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/docdev/skills/docdev-site
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/css-tokenography
python3 plugins/css-tokenography/scripts/validate_coverage.py --plugin plugins/css-tokenography
python3 plugins/css-tokenography/scripts/validate_adapters.py --plugin plugins/css-tokenography --format json
python3 plugins/css-tokenography/skills/css-tokenography/scripts/validate_router.py --plugin plugins/css-tokenography
python3 -m unittest discover -s plugins/css-tokenography/tests -v
```

The validators are bundled with Codex. The skill validator requires PyYAML.
The optional browser laboratory is installed and run separately:

```sh
npm --prefix plugins/css-tokenography/laboratory/browser ci
npx --prefix plugins/css-tokenography/laboratory/browser playwright install chromium firefox webkit
python3 plugins/css-tokenography/scripts/run_browser_lab.py --engines chromium,firefox,webkit --format json
```

No plugin command implicitly installs Node packages, browsers, Redis, or model
provider dependencies.

## License

MIT. See [`LICENSE`](./LICENSE).
