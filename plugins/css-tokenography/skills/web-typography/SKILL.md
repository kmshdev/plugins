---
name: web-typography
description: Design, implement, or audit web typography systems, font delivery, fallback metrics, variable fonts, semantic type tokens, fluid scales, hierarchy, measure, line-height, tracking, wrapping, truncation, numerals, international text, accessibility, and typography performance.
---

# Web typography

## Workflow

1. Inventory actual text roles, languages, scripts, weights, styles, variable axes, and numeric use cases.
2. Choose the smallest font family/weight/style set that serves those roles. Prefer WOFF2 and subset only with verified language coverage.
3. Define fallback stacks by metrics and script coverage. Use size/metric override descriptors when needed to reduce layout shift; never assume two sans-serif fonts share metrics.
4. Request only real font faces. Do not synthesize missing bold or italic styles when brand or legibility depends on them.
5. Define primitive sizes and semantic role tokens. Keep heading levels semantic and style them by role without breaking document hierarchy.
6. Use fluid type only between explicit readable bounds. Validate the slope at minimum, middle, maximum, zoom, and changed root size.
7. Tune line height by role, keep body measure roughly 45-75 characters where practical, and use tracking sparingly. Tight display tracking does not transfer to small body text.
8. Choose wrapping deliberately with `text-wrap`, `overflow-wrap`, hyphenation, and language metadata. Truncate only when the full value remains available through accessible interaction or surrounding context.
9. Use tabular numerals for changing columns, prices, timers, and tables. Keep copy natural; do not insert visual spacing characters that screen readers must interpret.
10. Test responsive layouts, CJK/Arabic/Indic scripts, RTL and mixed-direction content, long words, user font overrides, and 200% zoom. Use logical properties.
11. Keep mobile form text at a practical 16px floor unless real device evidence supports a different choice. Validate contrast with the actual font weight and anti-aliasing context.
12. Choose `font-display` per role and lifecycle. Preload only a current-page font discovered too late, with exact URL, format, and CORS mode; confirm the preload improves the waterfall.

## Tools

Run `python3 scripts/design_tool.py --tool px-to-rem-converter --format json` for explicit root-based conversion. Use `text-shadow-generator` only to serialize a reviewed shadow; shadows never substitute for contrast.

## Review output

Return findings by severity with selector/token evidence, rendered consequence, exact recommendation, and verification method. Include font requests/bytes, synthesized-face risks, token/hierarchy problems, measure/wrapping failures, internationalization risks, contrast dependencies, CLS risk, and preload/subsetting decisions.

Preserve the useful invariants from the local better-typography, better-colors, and better-ui sources without copying them mechanically. Primary references: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_fonts, https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display, and https://design.dev/guides/typography-web-design/.
