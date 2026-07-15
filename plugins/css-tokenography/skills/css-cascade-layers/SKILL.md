---
name: css-cascade-layers
description: Design, migrate, or debug CSS cascade layers, layer ordering, unlayered styles, important declarations, third-party CSS isolation, and specificity reduction. Use when precedence architecture or layer migration is the central task.
---

# CSS cascade layers

## Workflow

1. Trace origin, importance, encapsulation, layer, specificity, scoping proximity, and source order before changing selectors.
2. Declare the complete named layer order once near the entrypoint.
3. Put third-party/reset rules in low-priority layers and application overrides in explicit later layers.
4. Remember that normal unlayered author styles outrank normal layered author styles, while important layer order reverses.
5. Use `:where()` to keep low-level selectors intentionally weak.
6. Migrate one ownership boundary at a time and compare computed styles before and after.

Return the current cascade trace, proposed layer order, migrated files/selectors, important-declaration effects, and regression evidence. Primary reference: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascade/Using_cascade_layers and topic source https://design.dev/guides/css-cascade-layers/.
