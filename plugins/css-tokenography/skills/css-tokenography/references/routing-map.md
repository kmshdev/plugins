# CSS Tokenography routing map

Each specialist appears exactly once in this inventory:

- `$css-gradients` — gradients, color stops, interpolation, and gradient generation.
- `$css-transforms` — 2D/3D transforms, transform composition, matrices, and transform origins.
- `$css-transitions` — transition properties, duration, delay, and easing curves.
- `$css-grid` — grid tracks, named areas, subgrid, placement, and grid diagnostics.
- `$css-selectors` — selector syntax, specificity, `:has()`, `:is()`, `:where()`, and `:nth-child()`.
- `$css-flexbox` — one-dimensional layout, wrapping, alignment, ordering, and flex sizing.
- `$css-centering` — choosing and validating centering techniques.
- `$css-functions` — `clamp()`, `min()`, `max()`, `calc()`, and CSS numeric conversions.
- `$css-variables` — custom properties, semantic tokens, color tokens, and token architecture.
- `$css-animations` — keyframes, animation timing, motion accessibility, and animation choreography.
- `$css-cascade-layers` — cascade origins, layers, ordering, and precedence.
- `$css-scroll-driven-animations` — scroll/view timelines and scroll-linked effects.
- `$css-media-queries` — viewport and user-preference media queries.
- `$css-container-queries` — component-bound responsive queries, query containers, and units.
- `$css-dark-mode` — color-scheme negotiation, dark themes, and theme switching.
- `$web-typography` — type systems, font loading, fluid type, legibility, and international text.
- `$web-performance-optimization` — Core Web Vitals, rendering cost, payloads, delivery, and performance budgets.

## Overlap rules

- Layout: use `$css-grid` for two-dimensional tracks, `$css-flexbox` for one-dimensional flow, and `$css-centering` when the decision itself is the task.
- Responsive design: combine `$css-media-queries` for viewport/preferences, `$css-container-queries` for component adaptation, and the relevant layout specialist.
- Tokens and themes: combine `$css-variables` with `$css-dark-mode`; add `$css-gradients` only when gradient/color interpolation is material.
- Motion: use `$css-transitions` for state interpolation, `$css-animations` for keyframes, `$css-scroll-driven-animations` for timeline-linked motion, and `$css-transforms` when geometry changes.
- Selectors and cascade: use `$css-selectors` for matching/specificity and `$css-cascade-layers` for layer precedence.
- Typography: use `$web-typography`; add `$css-functions` for calculated scales and `$css-media-queries` or `$css-container-queries` for responsive type behavior.
- Performance: add `$web-performance-optimization` when CSS, fonts, images, animation, rendering, or third parties have measurable delivery/runtime consequences.

When a prompt lacks a useful topic signal, use the core UI triad:
`$css-grid`, `$css-variables`, and `$web-typography`.
