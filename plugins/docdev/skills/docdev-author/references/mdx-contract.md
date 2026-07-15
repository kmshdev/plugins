# MDX authoring contract

Use this contract for every document created by `docdev-author`.

## Required frontmatter

```yaml
---
title: "Human-readable title"
summary: "One concrete sentence describing the document outcome."
type: "development"
status: "draft"
slug: "human-readable-title"
created: "2026-07-15"
updated: "2026-07-15"
audience: ["developers"]
owners: []
tags: []
evidence: []
---
```

Allowed `type` values are `development`, `plan`, `architecture`, and `library`.
Allowed `status` values are `draft`, `review`, `approved`, and `deprecated`.

Keep arrays JSON-compatible on one line so the bundled standard-library validator
can parse them without a YAML dependency. Use repository-relative locators or public
URLs in `evidence`; never include credentials, private excerpts, or absolute paths in
content intended for publication.

## Body structure

- Let the renderer create the page `<h1>` from `title`; begin body sections at `##`.
- Keep heading depth sequential. Do not jump from `##` to `####`.
- Use fenced code blocks for commands and source examples.
- Put evidence beside the claim it supports. Label inference and proposals explicitly.
- Prefer durable links and symbols over line numbers when source churn is expected.
- Remove scaffolding language. `{{...}}`, TODO, TBD, and lorem ipsum fail validation.

## Safety boundary

Do not place `<script>`, inline event handlers, or `javascript:` URLs in MDX. Do not
assume a component exists because another documentation site provides it. Verify a
target component contract before importing it.

Authoring validation establishes format consistency, not factual correctness. Verify
commands, links, examples, and runtime claims independently.
