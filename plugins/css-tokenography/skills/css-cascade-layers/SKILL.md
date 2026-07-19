---
name: css-cascade-layers
description: Design, migrate, or debug CSS cascade layers, layer ordering, unlayered styles, important declarations, third-party CSS isolation, and specificity reduction. Use when precedence architecture or layer migration is the central task.
---

# CSS cascade layers

## Workflow

1. Trace origin/importance, encapsulation context, style attributes, layers, specificity, scoping proximity, and source order as separate cascade stages before changing selectors.
2. Declare the complete named layer order once near the entrypoint.
3. Put third-party/reset rules in low-priority layers and application overrides in explicit later layers.
4. For normal declarations, outer encapsulation contexts outrank inner contexts; for important declarations, inner contexts outrank outer contexts.
5. For normal declarations, later layers outrank earlier layers and unlayered styles outrank layered styles. For important declarations, earlier layers outrank later layers and layered styles outrank unlayered styles.
6. Keep style attributes outside selector specificity; do not invent a fourth specificity component.
7. Use `:where()` to keep low-level selectors intentionally weak.
8. Migrate one ownership boundary at a time and compare computed styles before and after.

Return the current cascade trace, proposed layer order, migrated files/selectors, important-declaration effects, and regression evidence. Primary references: https://www.w3.org/TR/css-cascade-6/ and https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascade/Using_cascade_layers; topic source: https://design.dev/guides/css-cascade-layers/.
