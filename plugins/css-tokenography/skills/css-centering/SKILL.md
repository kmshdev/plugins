---
name: css-centering
description: Select, implement, or debug CSS centering for blocks, inline content, unknown-size content, overlays, dialogs, and absolute positioning. Use when horizontal or vertical centering is the specific outcome, not for general layout architecture.
---

# CSS centering

## Decision workflow

1. Identify the centering box, axis, available size, and whether the child has a known size.
2. Use Grid `place-items: center` for two-axis centering in a dedicated container.
3. Use Flexbox when centering participates in a one-dimensional distribution.
4. Use auto inline margins for a sized block in normal flow.
5. Use logical inset plus translate for an independently positioned overlay; account for transforms already owned by the element.
6. For dialogs, prefer the platform's dialog/popover positioning and preserve safe-area and small-viewport access.

## Checks

- Verify overflow does not make content unreachable.
- Use logical properties for writing modes and bidirectional layouts.
- Test zoom, dynamic content, virtual keyboards, and reduced motion.
- Do not use line-height hacks for multi-line or unknown content.

Return the chosen centering context, CSS, known-size assumptions, and failure cases. Topic source: https://design.dev/guides/css-centering/.
