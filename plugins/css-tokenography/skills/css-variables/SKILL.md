---
name: css-variables
description: Design, implement, or audit CSS custom properties and design tokens, including primitive/semantic/component layers, inheritance, fallbacks, @property registration, OKLCH color tokens, and contrast validation. Use for token architecture and custom-property resolution; use css-dark-mode for theme switching behavior.
---

# CSS variables and tokens

## Workflow

1. Inventory existing values and consumers before introducing token layers.
2. Separate primitives from semantic roles and component overrides; name by purpose rather than appearance at semantic layers.
3. Place tokens at the narrowest scope that matches ownership and intended inheritance.
4. Use `var()` fallbacks for missing definitions, not for invalid-at-computed-value surprises.
5. Register typed animatable properties with `@property` only when initial value, inheritance, and syntax are deliberate.
6. Validate light/dark and state contrast at actual rendered combinations.

## Color tools

Run `python3 scripts/color_contrast_checker.py --format json` with a JSON object containing `foreground` and `background` six-digit sRGB hex colors. The output separates the exact WCAG 2.2 relative-luminance ratio used for threshold comparisons from the two-decimal `display_ratio`, and reports AA/AAA text plus 3:1 non-text threshold results. This color-pair report does not establish page, component, or product conformance.

APCA is not implemented. It is beta and polarity-sensitive, and this skill does not present it as a WCAG 3 conformance method. Use the [official APCA project documentation](https://git.apcacontrast.com/documentation/) and the current [WCAG 3 Working Draft](https://www.w3.org/TR/wcag-3.0/) when evaluating that separate, evolving method.

Run `python3 scripts/design_tool.py --tool oklch-color-converter --format json` with `{"hex":"#rrggbb"}` for dependency-free sRGB-to-OKLCH conversion and structured channels.

Return the token graph, scope/inheritance rules, fallback behavior, contrast results, and migration risks. Topic source: https://design.dev/guides/css-variables/.
