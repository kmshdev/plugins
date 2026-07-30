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

## Deterministic transform model

Run `python3 scripts/css_transform_playground.py --input transform.json --format json`. Set `transform.kind` to `none` or `list`; a list contains ordered objects such as `{"name":"rotateY","args":["25deg"]}`. Ancestor `perspective` and `perspective_origin` are separate from a `perspective()` function, and `transform_origin` is reported without pretending that element geometry is known.

The CLI validates translate, scale, rotate, skew, `matrix()`, `matrix3d()`, and `perspective()` arity and units, preserves caller order, and computes a dependency-free 4x4 matrix. `none` is semantically different from an identity-valued list because only the latter creates stacking and containing blocks. Matrix output does not include origin or ancestor-perspective layout effects, which require box geometry and browser collection.

## Filters and backdrop filters

Run `python3 scripts/css_filter_effects.py` or `python3 scripts/backdrop_filter_playground.py` with `property`, `kind`, and an ordered `functions` array. The typed grammar covers blur, amount functions, hue rotation, bounded drop shadows, and network-free `url(#id)` references; external URLs are rejected. Backdrop input may also declare surface background, alpha, border, and radius facts.

Non-`none` filter lists report their stacking and absolute/fixed containing-block effects. Backdrop visibility is inferred only from declared alpha facts, uses sRGB filter interpolation metadata, and retains the Filter Effects Level 2 draft/no-consensus caveat. The model serializes declarations; it does not render pixels or resolve a browser backdrop root.

## Guardrails

- Do not add `translateZ(0)` or `will-change` as a default optimization.
- Never describe a transform as guaranteed GPU acceleration or compositor promotion; those are browser-dependent runtime decisions.
- Keep essential content usable when transforms or filters are unsupported.
- Avoid scaling interactive text to zero or moving focusable controls off-screen without updating interaction state.
- Use individual transform properties only when their fixed translate-rotate-scale order matches the design.

Use [the optional browser laboratory](../../references/browser-laboratory.md)
for `transform-runtime`, `filter-runtime`, and `backdrop-filter-runtime` when
the task depends on computed matrices, containing blocks, stacking behavior,
runtime support, or pixels. Preserve per-engine disagreement; do not infer
compositor promotion from a passing visual comparison.

Report transform order, coordinate assumptions, accessibility effects, and measured performance evidence. Primary references: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_transforms and https://design.dev/guides/css-transforms/.
