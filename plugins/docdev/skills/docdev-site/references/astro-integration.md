# Astro integration

The bundled starter was grounded on the official Astro documentation retrieved on
2026-07-15 and npm package metadata:

- Astro content collections: https://docs.astro.build/en/guides/content-collections/
- Astro content module: https://docs.astro.build/en/reference/modules/astro-content/
- MDX integration: https://docs.astro.build/en/guides/integrations-guide/mdx/
- Pinned packages: `astro@7.0.9`, `@astrojs/mdx@7.0.3`,
  `@astrojs/check@0.9.9`, `@types/node@24.13.3`, and the latest compatible
  `typescript@6.0.3`.

Astro 7.0.9 requires Node `>=22.12.0`. TypeScript 7.0.2 was current at retrieval
time but is intentionally not used because `@astrojs/check@0.9.9` declares a peer
range of `^5.0.0 || ^6.0.0`; do not bypass that compatibility gate.

## Current composition

- Define build-time collections in `src/content.config.ts`.
- Load local `**/*.{md,mdx}` using `glob()` from `astro/loaders`.
- Validate frontmatter with `z` from `astro/zod`.
- Query with `getCollection()` and sort results explicitly; collection order is not
  deterministic across platforms.
- Generate static detail routes with `getStaticPaths()`.
- Render an entry with `render(entry)` and the returned `<Content />` component.
- Enable MDX through `@astrojs/mdx` in `astro.config.mjs`.
- Run `scripts/validate-content.mjs` before `astro check` and `astro build` because
  Astro's glob loader warns and overwrites duplicate IDs before route code can compare them.

`docdev.config.mjs` contains the MDX directory relative to the site root. The content
configuration resolves it from `process.cwd()` during Astro commands. Keep the build
working directory at the generated site root. Use `npm ci` with the pinned lockfile;
use `npm install` only while intentionally changing the starter dependency graph.

## Integration boundary

Adopt an existing repository's package manager, layouts, navigation, components,
tokens, and deployment adapter. Reuse the docdev schema, validators, deterministic
sorting, and duplicate-slug guard. Do not overwrite an established content model.
