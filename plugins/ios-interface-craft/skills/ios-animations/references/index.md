# SwiftUI motion reference index

Read only the categories relevant to the task. Rules are examples and checks for the stated context; verify API availability and project conventions before applying them.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix | Rules |
|----------|----------|--------|--------|-------|
| 1 | Spring Physics | CRITICAL | `spring-` | 8 |
| 2 | Timing & Feel | CRITICAL | `feel-` | 6 |
| 3 | Gesture Continuity | HIGH | `gesture-` | 7 |
| 4 | Spatial Transitions | HIGH | `spatial-` | 6 |
| 5 | Micro-interactions | HIGH | `micro-` | 6 |
| 6 | Orchestration | HIGH | `orch-` | 5 |
| 7 | Craft & Polish | HIGH | `craft-` | 5 |
| 8 | Content Motion | MEDIUM-HIGH | `content-` | 5 |

## Quick Reference

### 1. Spring Physics (CRITICAL)

- [`spring-motion-tokens`](spring-motion-tokens.md) — Define motion tokens as a caseless enum for all spring presets
- [`spring-smooth-default`](spring-smooth-default.md) — Default to .smooth spring for all UI transitions
- [`spring-snappy-responsive`](spring-snappy-responsive.md) — Use .snappy spring for responsive interactions
- [`spring-bouncy-celebration`](spring-bouncy-celebration.md) — Use .bouncy spring for playful and celebratory moments
- [`spring-custom-parameters`](spring-custom-parameters.md) — Tune custom springs with response and dampingFraction
- [`spring-velocity-preservation`](spring-velocity-preservation.md) — Springs preserve velocity on interruption
- [`spring-never-linear`](spring-never-linear.md) — Never use linear or easeInOut for interactive UI
- [`spring-completion-chaining`](spring-completion-chaining.md) — Use withAnimation completion for chained sequences

### 2. Timing & Feel (CRITICAL)

- [`feel-250ms-max`](feel-250ms-max.md) — Keep UI animations under 250ms
- [`feel-faster-better`](feel-faster-better.md) — Faster animations almost always feel better
- [`feel-asymmetric-enter-exit`](feel-asymmetric-enter-exit.md) — Use asymmetric timing for enter and exit
- [`feel-distance-proportional`](feel-distance-proportional.md) — Match duration to distance traveled
- [`feel-haptic-sync`](feel-haptic-sync.md) — Sync haptic feedback to visual animation keyframes
- [`feel-stagger-timing`](feel-stagger-timing.md) — Stagger reveals at 30-50ms intervals

### 3. Gesture Continuity (HIGH)

- [`gesture-rubber-band`](gesture-rubber-band.md) — Rubber band at drag boundaries
- [`gesture-momentum-dismiss`](gesture-momentum-dismiss.md) — Dismiss on velocity OR distance threshold
- [`gesture-snap-points`](gesture-snap-points.md) — Use velocity-aware snap points
- [`gesture-interruptible`](gesture-interruptible.md) — Make all gesture animations interruptible
- [`gesture-scroll-drag-conflict`](gesture-scroll-drag-conflict.md) — Resolve scroll and drag gesture conflicts
- [`gesture-state-transient`](gesture-state-transient.md) — Use GestureState for transient drag state
- [`gesture-projected-landing`](gesture-projected-landing.md) — Project gesture velocity for natural landing position

### 4. Spatial Transitions (HIGH)

- [`spatial-matched-geometry`](spatial-matched-geometry.md) — Use matchedGeometryEffect for expand/collapse morphs
- [`spatial-zoom-navigation`](spatial-zoom-navigation.md) — Use zoom navigation transition for collection detail (iOS 18)
- [`spatial-transition-origin`](spatial-transition-origin.md) — Anchor transitions to their trigger location
- [`spatial-hero-shared-element`](spatial-hero-shared-element.md) — Share multiple element IDs for rich hero animations
- [`spatial-sheet-morph`](spatial-sheet-morph.md) — Use matchedGeometryEffect for sheet presentations
- [`spatial-tab-continuity`](spatial-tab-continuity.md) — Maintain spatial direction in tab transitions

### 5. Micro-interactions (HIGH)

- [`micro-button-press-scale`](micro-button-press-scale.md) — Scale buttons to 0.97 on press for tactile feedback
- [`micro-haptic-pairing`](micro-haptic-pairing.md) — Pair every visual state change with haptic feedback
- [`micro-symbol-effect`](micro-symbol-effect.md) — Use symbolEffect for SF Symbol animations
- [`micro-toggle-bounce`](micro-toggle-bounce.md) — Add bounce to toggle state changes
- [`micro-long-press-fill`](micro-long-press-fill.md) — Animate progressive fill for long press actions
- [`micro-loading-phase`](micro-loading-phase.md) — Use repeating spring for organic loading states

### 6. Orchestration (HIGH)

- [`orch-phase-animator`](orch-phase-animator.md) — Use PhaseAnimator for multi-step sequences
- [`orch-keyframe-animator`](orch-keyframe-animator.md) — Use KeyframeAnimator for timeline-precise motion
- [`orch-stagger-children`](orch-stagger-children.md) — Stagger child elements for orchestrated reveals
- [`orch-coordinated-entrance`](orch-coordinated-entrance.md) — Coordinate multi-element entrances with shared trigger
- [`orch-timeline-view`](orch-timeline-view.md) — Use TimelineView for continuous repeating animations

### 7. Craft & Polish (HIGH)

- [`craft-reduce-motion`](craft-reduce-motion.md) — Respect accessibilityReduceMotion with crossfade fallback
- [`craft-blur-bridge`](craft-blur-bridge.md) — Use blur to bridge imperfect transition states
- [`craft-drawing-group`](craft-drawing-group.md) — Use drawingGroup() for Metal-backed complex animations
- [`craft-geometry-group`](craft-geometry-group.md) — Use geometryGroup() to isolate layout animation propagation
- [`craft-transaction-debug`](craft-transaction-debug.md) — Use Transaction to debug and override animation behavior

### 8. Content Motion (MEDIUM-HIGH)

- [`content-numeric-text`](content-numeric-text.md) — Use contentTransition(.numericText) for number changes
- [`content-scroll-transition`](content-scroll-transition.md) — Use scrollTransition for scroll-position effects
- [`content-visual-effect`](content-visual-effect.md) — Use visualEffect for position-aware animations
- [`content-symbol-replace`](content-symbol-replace.md) — Animate symbol replacement with contentTransition
- [`content-text-renderer`](content-text-renderer.md) — Use Text Renderer for character-level animation (iOS 18)
