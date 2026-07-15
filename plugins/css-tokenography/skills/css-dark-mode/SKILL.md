---
name: css-dark-mode
description: Implement or audit light/dark color schemes, color-scheme, prefers-color-scheme, light-dark(), token overrides, persisted user choice, system synchronization, and contrast across themes. Use when theme switching behavior is primary; use css-variables for the underlying token graph.
---

# Dark mode in CSS

## Workflow

1. Build semantic color tokens before adding theme overrides.
2. Declare supported `color-scheme` values so form controls and browser UI can render consistently.
3. Use system preference as the default, then let an explicit user choice override it.
4. Persist only an explicit choice; provide a way to return to system behavior.
5. Apply the theme before first paint when possible to avoid a flash, without blocking rendering on unnecessary script.
6. Validate every state, illustration, chart, focus ring, scrollbar, and forced-colors behavior in both schemes.

Use `light-dark()` when the support boundary and token architecture make it simpler; otherwise use scoped custom-property overrides. Return token changes, preference precedence, persistence behavior, first-paint behavior, and contrast results. Topic source: https://design.dev/guides/dark-mode-css/.
