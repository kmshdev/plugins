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

## Z-index visualizer

Run `python3 scripts/z_index_visualizer.py --input elements.json --format json`. Supply a DOM-like tree as explicit element IDs, parent IDs, unique document-order integers, computed-style subsets, and explicit layout, top-layer, and retained-animation facts. The model reports context triggers, nested atomic contexts, local negative/auto-zero/positive/top-layer paint phases, and separate absolute/fixed containing blocks.

The CLI accepts only pre-collected facts. It does not parse HTML or stylesheets and cannot replace browser collection or visual verification. Primary references: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout and https://design.dev/guides/css-grid/.

For rendered placement, inherited subgrid tracks, or hit-testing evidence, run
`grid-runtime`, `subgrid-runtime`, or `stacking-hit-test-runtime` through
[the optional browser laboratory](../../references/browser-laboratory.md).
Compare collected boxes and hit-test order before inspecting screenshots.
