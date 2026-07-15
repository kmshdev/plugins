---
name: css-scroll-driven-animations
description: Implement or review CSS scroll-driven animations with scroll timelines, view timelines, animation-range, named timeline scoping, progressive enhancement, and reduced-motion behavior. Use when animation progress is linked to scroll or element visibility.
---

# CSS scroll-driven animations

## Workflow

1. Choose a scroll progress timeline for a scroll container or a view progress timeline for subject visibility.
2. Identify the scroller, axis, subject, and attachment range explicitly.
3. Keep the keyframes meaningful without time-based assumptions.
4. Use `animation-range` to constrain view progress when the full cover range is not desired.
5. Guard newer behavior with `@supports` and provide a static or time-based fallback only when it preserves intent.
6. Disable nonessential motion under `prefers-reduced-motion` and test nested scrollers, RTL/writing modes, and resize.

Do not add a JavaScript scroll listener when CSS timelines satisfy the contract. Return timeline type/source, range, keyframes, fallback, and browser evidence. Primary reference: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll-driven_animations and topic source https://design.dev/guides/scroll-timeline/.
