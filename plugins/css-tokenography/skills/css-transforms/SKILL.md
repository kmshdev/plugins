---
name: css-transforms
description: Compose, implement, or review CSS 2D and 3D transforms, transform order, origins, perspective, coordinate systems, and transform-related visual effects. Use when translate, rotate, scale, skew, matrix, perspective, filter, clip-path, or transform composition is the primary task.
---

# CSS transforms

## Workflow

1. Establish the element's local coordinate system and the intended visual pivot.
2. Express the smallest ordered transform list; order is semantic because transform functions compose right-to-left as matrices.
3. Keep layout requirements separate: transforms change painting and hit geometry but do not reflow surrounding layout.
4. For 3D, distinguish the `perspective` property on an ancestor from the `perspective()` transform function, then set `transform-style` and backface behavior only when needed.
5. Verify focus indicators, pointer targets, overflow, stacking contexts, and reduced-motion behavior.
6. Measure rendering before adding layer-promotion hints.

When diagnosing overlap, use the CSS Grid skill's `z_index_visualizer.py` with computed facts. Transform, individual translate/rotate/scale, perspective, and filter effects can create stacking contexts, but opacity and isolation do not establish fixed-position containing blocks. Always keep those trigger registries separate.

## Deterministic model

Run `python3 scripts/design_tool.py --tool css-transform-playground --format json`. Input accepts ordered component fields such as `translate_x`, `rotate`, `scale`, `perspective`, and `origin`. Related semantic models cover backdrop filters, shadows, clip paths, filters, liquid-glass styling, and neumorphism; treat their visual result as browser-dependent.

## Guardrails

- Do not add `translateZ(0)` or `will-change` as a default optimization.
- Keep essential content usable when transforms or filters are unsupported.
- Avoid scaling interactive text to zero or moving focusable controls off-screen without updating interaction state.
- Use individual transform properties only when their fixed translate-rotate-scale order matches the design.

Report transform order, coordinate assumptions, accessibility effects, and measured performance evidence. Primary references: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_transforms and https://design.dev/guides/css-transforms/.
