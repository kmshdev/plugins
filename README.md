# kmshdev Codex plugins

Public Codex plugins maintained by [kmshdev](https://github.com/kmshdev).

## Install the marketplace

```sh
codex plugin marketplace add kmshdev/plugins --ref main
codex plugin add docdev@kmshdev
```

Restart Codex if the newly installed plugin does not appear immediately.

## Plugins

### docdev

`docdev` creates evidence-backed development, planning, architecture, and library documentation in MDX. Its optional Astro workflow validates the MDX contract and renders the content as a static documentation site.

The plugin provides two skills:

- `$docdev-author` investigates repository evidence, creates typed MDX documents from templates, and validates their frontmatter and structure.
- `$docdev-site` scaffolds a reusable Astro documentation site, imports validated MDX, and runs content, type, and production-build checks.

The plugin source is under [`plugins/docdev`](./plugins/docdev). The marketplace catalog is [`/.agents/plugins/marketplace.json`](./.agents/plugins/marketplace.json).

## Validate locally

From a checkout of this repository:

```sh
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/docdev
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/docdev/skills/docdev-author
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/docdev/skills/docdev-site
```

The validators are bundled with Codex. The skill validator requires PyYAML.

## License

MIT. See [`LICENSE`](./LICENSE).
