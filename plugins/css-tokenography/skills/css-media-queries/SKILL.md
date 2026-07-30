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

For collected runtime facts, run
`python3 scripts/feature_detection.py --input observations.json --format json`.
The analyzer accepts named engines and boolean feature observations, reports
all/partial/none support, and never consults a user-agent table. Collect the
facts with `feature-detection-runtime` in
[the optional browser laboratory](../../references/browser-laboratory.md).

Return each query's observed trigger, fallback, overlap analysis, and
accessibility effect. Primary reference:
https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_media_queries and topic
source https://design.dev/guides/media-queries/.
