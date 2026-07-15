---
name: docdev-author
description: Create, revise, or audit evidence-backed engineering documentation in MDX, including development guides, implementation or migration plans, architecture and ADR-style documents, and library/API documentation. Use when Codex must turn repository evidence, runtime behavior, designs, commands, or API surfaces into durable `.mdx` documentation; do not use for rendering or publishing a documentation website.
---

# Docdev Author

Create repository-specific MDX that distinguishes facts, observations, decisions,
proposals, and open questions. Keep authoring portable; invoke `$docdev-site` only
when the user also requests a rendered website.

## Workflow

1. Read the active instruction hierarchy, documentation index, source, tests,
   commands, and runtime evidence before drafting.
2. Classify the document:
   - `development`: setup, workflow, debugging, testing, or operations guidance.
   - `plan`: scoped implementation, migration, or execution plan.
   - `architecture`: boundaries, decisions, data flow, failure behavior, or ADRs.
   - `library`: package, API, CLI, SDK, or integration documentation.
3. Read [references/mdx-contract.md](references/mdx-contract.md) and exactly one
   matching type reference:
   - [development-docs.md](references/development-docs.md)
   - [planning-docs.md](references/planning-docs.md)
   - [architecture-docs.md](references/architecture-docs.md)
   - [library-docs.md](references/library-docs.md)
4. Create a file from the matching template:

   ```bash
   python3 scripts/create_doc.py <type> <output.mdx> --title "<title>" --summary "<summary>"
   ```

5. Replace generic scaffold prose with evidence-backed project content. Preserve
   the required headings so consumers and validators have a stable contract.
6. Validate before handoff:

   ```bash
   python3 scripts/validate_mdx.py <file-or-directory> [more paths]
   ```

7. Report the source evidence used, file path, validation command, and remaining
   uncertainty. Do not claim publication or runtime fidelity without its own probe.

## Rules

- Treat running behavior and executable tests as stronger evidence than prose.
- Cite repository-relative locators, commands, versions, or official URLs near
  material claims. Never invent implemented behavior.
- Use one page title from frontmatter; body headings start at `##` and remain sequential.
- Keep raw HTML and executable scripts out of authored MDX. Prefer Markdown and
  fenced code; use target-provided MDX components only when their contract is verified.
- Keep plans scoped, ordered, restartable, and mapped to acceptance evidence.
- Keep architecture documents explicit about current, target, and proposed state.
- Keep library examples executable and version-bound where behavior can drift.
- Do not deploy, publish, or modify generated website output unless explicitly asked.

## Resources

- `assets/templates/`: canonical MDX scaffolds copied by `create_doc.py`.
- `scripts/create_doc.py`: deterministic document creation without overwrite.
- `scripts/validate_mdx.py`: frontmatter, structure, placeholder, and safety checks.
- `references/`: the shared MDX contract and type-specific authoring guidance.
