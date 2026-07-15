---
name: css-animations
description: Design, implement, or audit CSS @keyframes and animation-* behavior, including iteration, direction, fill, composition, play state, loaders, choreography, and reduced-motion fallbacks. Use for autonomous or multi-stage keyframe sequences; use css-transitions for state interpolation.
---

# CSS animations

## Workflow

1. State the animation's user-facing purpose and completion state.
2. Define the minimal keyframes; omit redundant 0%/100% values already supplied by the underlying style when safe.
3. Set name, duration, easing, iteration, direction, fill, and play state explicitly.
4. Prefer transform and opacity when they preserve semantics, but measure expensive paint effects rather than banning them categorically.
5. Pause or remove nonessential continuous motion and supply a `prefers-reduced-motion` path.
6. Verify focus, announcements, cancellation, page-load behavior, and background-tab behavior.

The `css-loaders` model in `scripts/design_tool.py` serializes an animation shorthand only; author original keyframes and ensure loading state is also exposed semantically. Return purpose, keyframes, timing, cancellation, reduced-motion behavior, and performance observations. Primary references: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_animations and https://design.dev/guides/css-animations/.
