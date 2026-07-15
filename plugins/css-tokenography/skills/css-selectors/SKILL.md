---
name: css-selectors
description: Author, simplify, or diagnose CSS selectors, specificity, combinators, attribute selectors, pseudo-classes, :is(), :where(), :not(), :has(), and An+B matching. Use when selector matching or cascade weight is the central problem.
---

# CSS selectors

## Workflow

1. Start from the smallest stable semantic hook available in the markup.
2. Prefer low-specificity component boundaries and use `:where()` when a group should add zero weight.
3. Treat `:is()`, `:not()`, and `:has()` specificity as the maximum specificity of their selector-list arguments.
4. Keep relational selectors scoped; measure matching cost only when runtime evidence points to selector work.
5. Avoid DOM-shape selectors when content reordering or conditional rendering can change sibling positions.
6. Resolve conflicts through layers and clearer ownership before increasing specificity.

## Tools

- Run `python3 scripts/design_tool.py --tool specificity-calculator --format json` with `{"selector":"..."}` for a compact selector audit.
- Run `python3 scripts/design_tool.py --tool nth-child-selector --format json` with `expression` and optional `element` to validate An+B syntax.

Return the matched intent, selector, specificity tuple, ownership/layer context, and resilience risks. Topic source: https://design.dev/guides/css-selectors/.
