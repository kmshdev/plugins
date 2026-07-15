---
name: windsurf-rules
description: Author, migrate, or review Windsurf and Devin Desktop Cascade rules, including current rule locations, trigger frontmatter, glob activation, manual invocation, discovery, precedence, character limits, and AGENTS.md interaction. Use only for Windsurf/Devin rule configuration, not general CSS instructions.
---

# Windsurf rules

## Current contract

- Prefer workspace rules in `.devin/rules/*.md`; `.windsurf/rules/*.md` is a backward-compatible fallback and `.windsurfrules` is legacy.
- Store the global always-on file at `~/.codeium/windsurf/memories/global_rules.md`.
- Workspace rules use `trigger: always_on`, `model_decision`, `glob`, or `manual`.
- A glob rule also declares `globs`; a model-decision rule needs a concrete description; manual rules are activated with `@rule-name`.
- Root `AGENTS.md` is always on. Subdirectory `AGENTS.md` files are auto-scoped to their directory.
- Prefer `.devin` when duplicate `.devin` and `.windsurf` rules exist. Keep workspace files under the current 12,000-character limit and global rules under 6,000 characters.

## Authoring workflow

1. Choose global, workspace, directory-scoped AGENTS.md, or enterprise scope from actual ownership.
2. Choose the narrowest trigger that reliably activates the instruction.
3. Put discovery language in `description`; put executable, testable instructions in the body.
4. Keep paths/globs relative and verify them against the real repository tree.
5. Separate universal engineering rules from product/tool-specific instructions.
6. Test positive and negative activation cases and check for conflicting parent/global rules.

## Templates

Glob rule:

```markdown
---
trigger: glob
globs: **/*.test.ts
---

Use the repository test runner and assert observable behavior.
```

Model-decision rule:

```markdown
---
trigger: model_decision
description: Apply when changing database migrations or schema contracts.
---

Inspect backward compatibility and rollback behavior before editing.
```

## Review output

Report file/scope, trigger validity, glob reach, discovery/precedence, duplicate instructions, character limit, positive activation case, negative activation case, and exact corrections. Official source: https://docs.windsurf.com/windsurf/cascade/memories. Topic source: https://design.dev/guides/windsurf-rules/.
