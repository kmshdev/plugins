---
name: ios-taste
description: Design or critique a user-facing SwiftUI screen when its visual hierarchy and character matter.
---

# iOS Taste

Shape the screen around the user’s immediate goal, context, and content. Decide what should be noticed first, then choose a layout, controls, typography, and motion that make the task clear. Keep the app’s existing brand and navigation language unless the user asks to change them.

Use familiar system patterns when they serve the task. Custom cards, charts, or full-bleed imagery should clarify content or interaction, not serve as a default substitute for `List`, `Form`, or `LabeledContent`. Use realistic preview data to judge hierarchy, and inspect the rendered result in relevant sizes and appearances when possible.

For a design comparison or polish pass, identify a small number of specific issues and revise the affected screen. Preserve accessibility, Dynamic Type, and semantic controls.

## Optional resources

- Read [Apple design observations](references/apple-design-dna.md) when a native design precedent would help. Treat its measurements and examples as observations, not universal tokens.
- Use [the palette generator](scripts/generate_palette.py) only when the task calls for a new palette. Keep existing brand colors for work within an established app.
