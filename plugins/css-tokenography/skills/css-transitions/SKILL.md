---
name: css-transitions
description: Implement or audit CSS property transitions, explicit transition-property lists, durations, delays, easing functions, discrete transitions, and interruptible state changes. Use for state-to-state motion; use css-animations for autonomous keyframe sequences.
---

# CSS transitions

## Workflow

1. Define the before and after states, including how the state is triggered and interrupted.
2. List only the properties that should transition; never use `transition: all` in production guidance.
3. Prefer transform and opacity when they express the same outcome, but choose correctness over cargo-cult compositing.
4. Select easing from the interaction: deceleration for entrances, acceleration for exits, symmetric timing for reversible state changes.
5. Keep short interaction feedback responsive and make transitions interruptible.
6. Provide a `prefers-reduced-motion` path that removes nonessential motion without hiding state changes.

## Easing tool

Run `python3 scripts/cubic_bezier_studio.py --format json` with `x1`, `y1`, `x2`, and `y2`. The CLI constrains finite x coordinates to `[0,1]` and permits finite y overshoot, matching CSS easing semantics. Use `hover-effect-generator` only for the target state, then add explicit transition properties and accessible non-hover activation.

## Review output

Return the state pair, property list, timing/easing rationale, interruption behavior, reduced-motion behavior, and any layout/paint cost. Primary references: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_transitions and https://design.dev/guides/css-transitions/.
