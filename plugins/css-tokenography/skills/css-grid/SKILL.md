---
name: css-grid
description: Build, generate, or debug two-dimensional CSS Grid layouts, explicit and implicit tracks, named areas, auto-placement, alignment, subgrid inheritance, and grid placement boundaries. Use for grid-specific layout tasks and the bundled grid-area or subgrid CLIs.
---

# CSS Grid

## Workflow

1. Describe rows and columns from content constraints before choosing track syntax.
2. Use explicit tracks and named areas for stable page regions; use auto-placement for repeated content.
3. Choose `auto-fit` versus `auto-fill` from empty-track behavior, not from memorized recipes.
4. Use subgrid when descendants must share ancestor tracks; verify the item span because inherited track count comes from that span.
5. Check intrinsic minimum sizes, overflow, source order, dense placement, focus order, and writing modes.
6. Confirm computed placement in a browser for user-facing layouts.

## Grid-area mapper

Run `python3 scripts/grid_area_mapper.py --input layout.json --format json`. Supply `rows`, `columns`, `cells`, and optional `gap`. Empty cells use `.`. The CLI rejects malformed matrices, reserved names, disconnected regions, and non-rectangular named areas, then emits `grid-template-areas` CSS.

## Subgrid visualizer

Run `python3 scripts/subgrid_visualizer.py --input subgrid.json --format json`. Supply parent track counts/gap and item line spans with `subgrid_columns`, `subgrid_rows`, and optional nested `children`. The CLI validates boundaries and exposes inherited tracks and gaps.

Use `design_tool.py --tool z-index-visualizer` only as a declaration model; diagnose stacking contexts separately. Primary references: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout and https://design.dev/guides/css-grid/.
