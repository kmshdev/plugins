---
name: css-container-queries
description: Build or debug CSS size, style, and scroll-state container queries, containment setup, named containers, container query units, and component-local responsive behavior. Use when a component should adapt to its containing context rather than the viewport.
---

# CSS container queries

## Workflow

1. Identify the component boundary and the ancestor whose available inline/block size is meaningful.
2. Set `container-type` on the owning ancestor; add `container-name` only when disambiguation is needed.
3. Write the component's functional base state first, then query at content-driven breakpoints.
4. Use `cqi`/`cqb` units only when the queried container supplies a stable scale.
5. Avoid querying and styling the same containment boundary in a way that creates circular sizing.
6. Test nested containers, writing modes, containment side effects, unsupported browsers, and zoom.

Return the container owner, query features, base behavior, breakpoint evidence, and fallback. Primary reference: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries and topic source https://design.dev/guides/css-container-queries/.
