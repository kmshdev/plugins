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

Run `python3 scripts/design_tool.py --tool flexbox-playground --format json` with direction, wrap, justify, align, and gap controls to serialize the container core. Return container rules, item sizing rules, overflow behavior, and accessibility checks. Topic source: https://design.dev/guides/flexbox/.
