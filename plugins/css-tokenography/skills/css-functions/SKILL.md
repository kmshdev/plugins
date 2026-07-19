---
name: css-functions
description: Apply or validate CSS value functions including calc(), min(), max(), clamp(), round(), mod(), rem(), trigonometric functions, color functions, attr(), var(), and aspect-ratio math. Use when CSS computation or generated numeric values are central.
---

# CSS functions

## Workflow

1. Define units and bounds before composing a function.
2. Keep dimensional algebra valid; only add or compare compatible dimensions.
3. Prefer `min()`, `max()`, and `clamp()` when they express a real constraint, not as decoration.
4. Preserve a readable fallback for newer functions when target-browser evidence requires it.
5. Test computed values at minimum, interpolation, maximum, zoom, and changed root font size.

## Tools

- `clamp-generator`: input min/max pixels and min/max viewport pixels; output a fluid rem/vw expression.
- `aspect-ratio-calculator`: input width and height; output the numeric and reduced CSS ratio.
- `border-radius-playground` and `custom-cursor-generator`: serialize reviewed CSS values.
- ASCII generation remains procedural because the live glyph assets are not exposed; do not invent a supposedly faithful font.

Run `python3 scripts/design_tool.py --tool <name> --format json`. Return formulas, units, boundary values, fallbacks, and assumptions. Topic source: https://design.dev/guides/css-functions/.
