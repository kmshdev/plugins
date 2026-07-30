---
name: css-selectors
description: Author, simplify, or diagnose CSS selectors, specificity, combinators, attribute selectors, pseudo-classes, :is(), :where(), :not(), :has(), and An+B matching. Use when selector matching or cascade weight is the central problem.
---

# CSS selectors

## Workflow

1. Start from the smallest stable semantic hook available in the markup.
2. Prefer low-specificity component boundaries and use `:where()` when a group should add zero weight.
3. Calculate selector specificity as `(A,B,C)`: IDs; classes, attributes, and pseudo-classes; types and pseudo-elements. Keep inline styles in the separate cascade stage.
4. Treat `:is()`, `:not()`, and `:has()` as the maximum specificity of their selector-list arguments; treat `:where()` and its arguments as zero.
5. Add one pseudo-class plus the maximum selector-list argument for `:nth-child(... of S)` and `:nth-last-child(... of S)`.
6. Keep selector-list members separate. Do not combine their specificity tuples.
7. Keep relational selectors scoped; measure matching cost only when runtime evidence points to selector work.
8. Avoid DOM-shape selectors when content reordering or conditional rendering can change sibling positions.
9. Resolve conflicts through layers and clearer ownership before increasing specificity.

## Tools

- Run `python3 scripts/specificity_calculator.py --format json` with `{"selector":"..."}` for per-member Selectors Level 4 tuples, half-open source spans, and standards notes. Malformed or unbalanced syntax exits nonzero.
- Run `python3 scripts/nth_child_selector.py --format json` with `expression` and optional `element` to validate and normalize An+B syntax and generate a safe selector.

Run `selector-matching-runtime` through
[the optional browser laboratory](../../references/browser-laboratory.md) when
the review needs real `matches()`, `:has()`, or `:nth-child(... of S)`
behavior. Runtime matching supplements the deterministic specificity tuple; it
does not replace cascade analysis.

Return the matched intent, each selector-list member and its specificity tuple, ownership/layer context, and resilience risks. Primary reference: https://www.w3.org/TR/selectors-4/#specificity-rules and topic source: https://design.dev/guides/css-selectors/.
