# Rule templates

Use `.devin/rules/*.md` for new workspace rules. Choose `always_on` only for instructions needed on every message; prefer `model_decision`, `glob`, or `manual` to control context cost.

## Glob

```markdown
---
trigger: glob
globs: src/**/*.css
---

Use the repository's token layers and verify forced-colors behavior.
```

## Model decision

```markdown
---
trigger: model_decision
description: Apply when changing shared CSS tokens or theme contracts.
---

Trace every token consumer and validate both color schemes before editing.
```

## Manual

```markdown
---
trigger: manual
---

Run the full CSS accessibility and performance review.
```

Validate a file with `python3 scripts/validate_rule.py --input path/to/rule.md --format json`.
