# Existing CSS skill migration

The section-level preserve/rewrite/split/retire record is machine-readable in `source-migration.json`.

| Source skill | Disposition | Main destinations | Retired surface |
|---|---|---|---|
| css-animate | split | css-transitions, css-animations, css-scroll-driven-animations | View Transitions remains only a cross-reference because no requested guide owns it |
| css-debug | rewrite | css-selectors, css-grid, css-variables, web-performance-optimization | competing implementation catch-all; orchestration now belongs to css-tokenography |
| css-expert | retire-catch-all | css-tokenography router plus all 17 guide specialists | broad “any CSS task” implementation contract |
| css-layout | split | css-grid, css-flexbox, css-centering, css-container-queries | broad layout trigger |
| css-refactor | rewrite as workflows | cascade, selectors, variables, media queries, typography | compatibility shims and stale blanket migrations |
| css-responsive | split | css-media-queries, css-container-queries, web-typography, web performance | viewport-only assumptions |
| css-theme | split | css-variables, css-dark-mode, css-gradients | broad theme trigger |

Useful invariants from better-colors, better-typography, and better-ui were synthesized into the variables, typography, transition, and accessibility workflows. Their source files remain unchanged.
