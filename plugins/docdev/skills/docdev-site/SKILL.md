---
name: docdev-site
description: Scaffold, integrate, validate, or build a static Astro documentation website that consumes validated docdev MDX files. Use when Codex must render development, planning, architecture, or library documentation into webpages, add an MDX documentation surface to a repository, or prepare a local static build; do not use for authoring documents alone or for deployment without explicit publication authority.
---

# Docdev Site

Render portable docdev MDX without making Astro part of the authoring contract.

## Workflow

1. Read the target repository instructions, package manager, existing web stack,
   MDX location, build commands, and publication boundary.
2. If the repository already has a documentation renderer, integrate the MDX
   contract into that renderer instead of adding a second framework.
3. For a new standalone renderer, read
   [references/astro-integration.md](references/astro-integration.md), then scaffold:

   ```bash
   python3 scripts/scaffold_site.py <target-directory> --content-dir <mdx-directory>
   ```

4. Validate authored content with the sibling `docdev-author` validator before
   building. Resolve the sibling script from the plugin directory rather than
   assuming a global installation path.
5. Use the target repository's package manager. For the bundled starter, preserve
   `package-lock.json` and install reproducibly:

   ```bash
   npm ci
   npm run check
   npm run build
   ```

6. Preview the production build and inspect every generated route at minimum at
   `390x844` and `1440x900`. Require HTTP 200, no unintended horizontal overflow,
   one page H1, sequential headings, working internal links, keyboard-reachable
   skip navigation, and no browser console error. Inspect fenced code presentation
   when the input contains code; otherwise state that positive code-block styling
   was not exercised. A successful build is not visual proof.
7. Read [references/publishing.md](references/publishing.md) only when publication
   is requested. Require explicit authority before commits, pushes, or deployments.

## Rules

- Preserve the MDX files as the source of truth; never hand-edit generated HTML.
- Keep content schemas strict and route order deterministic.
- Fail duplicate slugs and invalid frontmatter during build.
- When modifying the starter or its validator, create two temporary documents with
  one slug and prove `npm run validate` fails before accepting the change.
- Use local, relative assets and a configurable base path for static hosting.
- Do not add Astro to a repository with a mature accepted docs framework merely
  because the bundled starter exists.
- Keep private evidence, absolute source paths, internal metadata, and credentials
  out of publishable output.
- Re-resolve current framework versions before updating the pinned starter.

## Resources

- `assets/astro-template/`: pinned, minimal static Astro starter.
- `scripts/scaffold_site.py`: deterministic, non-destructive template copier.
- `references/astro-integration.md`: verified framework composition and extension points.
- `references/publishing.md`: publication classification and verification contract.
