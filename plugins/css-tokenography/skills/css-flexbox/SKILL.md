---
name: css-flexbox
description: Build or debug one-dimensional CSS Flexbox layouts, wrapping, main/cross-axis alignment, flexible sizing, gaps, ordering, and common navigation or distribution patterns. Use when a row or column flow is primary; use css-grid for two-dimensional track alignment.
---

# CSS Flexbox

## Workflow

1. Choose the main axis from content flow, then decide whether items may wrap.
2. Separate distribution on the main axis from alignment on the cross axis.
3. Set `flex-basis`, growth, and shrink behavior explicitly when intrinsic sizes are insufficient.
4. Check the automatic minimum size; use `min-inline-size: 0` only where content may shrink or truncate.
5. Preserve meaningful DOM order; visual `order` must not create a keyboard or reading-order mismatch.
6. Test long labels, localization, zoom, wrapping, overflow, and empty states.

## Flexbox Playground

Run `python3 skills/css-flexbox/scripts/flexbox_playground.py --input <fixture> --format json` from the plugin root. The JSON object accepts:

- `direction`: `row`, `row-reverse`, `column`, or `column-reverse`; defaults to `row`.
- `wrap`: `nowrap`, `wrap`, or `wrap-reverse`; defaults to `nowrap`.
- `justify_content`: `normal`, `start`, `end`, `center`, `space-between`, `space-around`, or `space-evenly`; defaults to `normal`.
- `align_items`: `normal`, `stretch`, `start`, `end`, `center`, or `baseline`; defaults to `normal`.
- `gap`: `normal` or a primitive nonnegative length/percentage; defaults to `normal`.
- `items`: an optional source-ordered array of unique IDs and optional integer `order` values.

The report returns canonical container declarations, logical main/cross axes, source order, order-modified source order, and accessibility and fidelity limits. Reversed directions do not rewrite source order. The model does not predict wrapping, free-space distribution, or item sizes without container and item dimensions, and logical axes still depend on the document's writing mode and direction for physical orientation.

Topic source: https://design.dev/guides/flexbox/.
