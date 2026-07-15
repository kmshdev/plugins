---
name: css-gradients
description: Design, implement, or audit CSS linear, radial, and conic gradients, color-stop interpolation, layered gradient patterns, and gradient-backed text. Use for gradient syntax or generated gradient CSS; do not use for general custom-property theming or dark-mode architecture.
---

# CSS gradients

## Workflow

1. Identify whether the visual model is linear, radial, conic, repeating, or layered.
2. Define color stops explicitly; add positions only when the natural distribution is wrong.
3. Choose a color space intentionally. Prefer perceptual spaces for interpolation when supported and verify gamut/fallback behavior.
4. Add a solid-color fallback when the gradient carries essential contrast.
5. Test contrast across the full rendered region, not only the endpoint colors.
6. Keep decorative gradients out of content semantics and preserve text readability in forced-colors mode.

## Generation tools

Run `python3 scripts/design_tool.py --tool gradient-mixer --format json` with JSON containing `type`, `direction` or `shape`, and `stops`. Use the same script with `css-background-generator` or `metallic-effect-generator` for reviewed CSS values. These commands model deterministic CSS output, not browser previews.

## Guardrails

- Avoid copied preset gradients when a small tokenized stop set expresses the intent.
- Avoid gradient text without a readable fallback `color`.
- Measure large animated gradients; do not assume compositing makes them cheap.
- Put reusable colors in custom properties, but keep the gradient composition local to its component role.

Return the chosen model, generated CSS, fallbacks, contrast risks, and browser-sensitive assumptions. Consult [coverage](../../references/coverage.md) and [standards corrections](../../references/standards-divergences.md). Topic source: https://design.dev/guides/css-gradients/.
