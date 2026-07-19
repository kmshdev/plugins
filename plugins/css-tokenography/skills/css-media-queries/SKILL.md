---
name: css-media-queries
description: Design or audit CSS media queries for viewport/layout breakpoints, interaction capabilities, color scheme, contrast, motion, data, print, and other environment features. Use for page or environment adaptation; use css-container-queries for component-size adaptation.
---

# CSS media queries

## Workflow

1. Start with a functional base style, then add a query only at an observed constraint boundary.
2. Prefer range syntax when it makes bounds unambiguous and verify overlapping intervals.
3. Query capabilities such as hover/pointer rather than inferring them from screen size.
4. Respect motion, contrast, color-scheme, forced-colors, and data preferences without hiding required content.
5. Use print rules for printable information architecture, not a screenshot of the screen layout.
6. Test zoom, orientation, split view, dynamic viewport units, and real target devices.

Browser feature detection is intentionally procedural: use `@supports`, `CSS.supports()`, and target-browser tests rather than a static user-agent table. Return each query's observed trigger, fallback, overlap analysis, and accessibility effect. Primary reference: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_media_queries and topic source https://design.dev/guides/media-queries/.
