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

Run `python3 scripts/gradient_mixer.py --format json` with JSON containing `kind`, a kind-specific `geometry` object, and ordered `{color, position}` stops. The canonical generator validates linear, radial, and conic core syntax as data and preserves stop source order; its report names unsupported advanced grammar and does not claim browser rendering, gamut mapping, or contrast. Continue to use `design_tool.py` only for the still-procedural `css-background-generator` and `metallic-effect-generator` serializers.

For computed-image and source-order evidence across Chromium, Firefox, and
WebKit, run the `gradient-runtime` fixture through
[the optional browser laboratory](../../references/browser-laboratory.md).
Treat screenshots as secondary to the collected computed value.

## Guardrails

- Avoid copied preset gradients when a small tokenized stop set expresses the intent.
- Avoid gradient text without a readable fallback `color`.
- Measure large animated gradients; do not assume compositing makes them cheap.
- Put reusable colors in custom properties, but keep the gradient composition local to its component role.

Return the chosen model, generated CSS, fallbacks, contrast risks, and browser-sensitive assumptions. Consult [coverage](../../references/coverage.md) and [standards corrections](../../references/standards-divergences.md). Topic source: https://design.dev/guides/css-gradients/.
