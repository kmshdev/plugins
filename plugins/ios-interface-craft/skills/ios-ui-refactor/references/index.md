# Existing SwiftUI screens reference index

Read only the categories relevant to the task. Choose rules that fit the task and supported SDK. Some examples assume a modular clinic app; their architecture constraints apply only to projects that adopted that design.

## Rule Categories by Priority

| Priority | Category | Principle | Impact | Prefix | Rules |
|----------|----------|-----------|--------|--------|-------|
| 1 | Less, But Better | Rams #10 + Segall "Think Minimal" | CRITICAL | `less-` | 7 |
| 2 | Self-Evident Design | Rams #4 + Segall "Think Human" | CRITICAL | `evident-` | 6 |
| 3 | Honest Interfaces | Rams #6 + Segall "Think Brutal" | CRITICAL | `honest-` | 6 |
| 4 | Invisible Design | Rams #5 + Edson "Product Is Marketing" | HIGH | `invisible-` | 6 |
| 5 | Systems, Not Pieces | Edson "Systems Thinking" + Rams #8 | HIGH | `system-` | 6 |
| 6 | Thorough to the Last Detail | Rams #8 + Rams #2 | HIGH | `thorough-` | 7 |
| 7 | Enduring Over Trendy | Rams #7 + Edson "Design With Conviction" | MEDIUM-HIGH | `enduring-` | 5 |
| 8 | Refined Through Iteration | Edson "Design Out Loud" + Rams #1/#3 | MEDIUM | `refined-` | 8 |

## Quick Reference

### 1. Less, But Better (CRITICAL)

Rams #10: "Good design is as little design as possible." Segall: Apple succeeded by saying no to a thousand things.

- [`less-single-focal`](less-single-focal.md) - One primary focal point per screen
- [`less-type-restraint`](less-type-restraint.md) - Limit to 3-4 distinct type treatments per screen
- [`less-one-typeface`](less-one-typeface.md) - One typeface per app, differentiate with weight and size
- [`less-color-restraint`](less-color-restraint.md) - Reserve saturated colors for small interactive elements
- [`less-one-color-purpose`](less-one-color-purpose.md) - Each semantic color serves exactly one purpose
- [`less-purposeful-motion`](less-purposeful-motion.md) - Every animation must communicate state change or provide feedback
- [`less-fewer-controls`](less-fewer-controls.md) - Remove controls that do not serve the core task

### 2. Self-Evident Design (CRITICAL)

Rams #4: "Good design makes a product understandable." Segall: interfaces must speak in terms people understand.

- [`evident-visual-weight`](evident-visual-weight.md) - Combine size, weight, and contrast for hierarchy
- [`evident-whitespace-grouping`](evident-whitespace-grouping.md) - Use whitespace to separate conceptual groups
- [`evident-progressive-disclosure`](evident-progressive-disclosure.md) - Use progressive disclosure for dense information
- [`evident-reading-order`](evident-reading-order.md) - Align visual weight with logical reading order
- [`evident-navigation-intent`](evident-navigation-intent.md) - Sheets for tasks and creation, push for drill-down hierarchy
- [`evident-label-clarity`](evident-label-clarity.md) - Use clear labels over ambiguous icons

### 3. Honest Interfaces (CRITICAL)

Rams #6: "Good design is honest." Segall: clarity without sugar-coating.

- [`honest-semantic-colors`](honest-semantic-colors.md) - Use semantic colors, never hard-coded black or white
- [`honest-contrast`](honest-contrast.md) - Ensure WCAG AA contrast ratios
- [`honest-dark-mode`](honest-dark-mode.md) - Define light and dark variants for every custom color
- [`honest-foreground-style`](honest-foreground-style.md) - Use foregroundStyle over foregroundColor
- [`honest-depth-cues`](honest-depth-cues.md) - Use materials for layering, not drop shadows for depth
- [`honest-loading-states`](honest-loading-states.md) - Show real progress, not indefinite spinners

### 4. Invisible Design (HIGH)

Rams #5: "Good design is unobtrusive." Edson: the product itself is the marketing.

- [`invisible-spring-physics`](invisible-spring-physics.md) - Default to spring animations for all UI transitions
- [`invisible-spring-presets`](invisible-spring-presets.md) - Use .smooth for routine, .snappy for interactive, .bouncy for delight
- [`invisible-no-easing`](invisible-no-easing.md) - Prefer springs over linear and easeInOut for UI elements
- [`invisible-system-materials`](invisible-system-materials.md) - Use system materials, not custom semi-transparent backgrounds
- [`invisible-symbol-effects`](invisible-symbol-effects.md) - Use built-in symbolEffect, not manual symbol animation
- [`invisible-content-transitions`](invisible-content-transitions.md) - Use contentTransition for changing text and numbers

### 5. Systems, Not Pieces (HIGH)

Edson: "Design is systems thinking." Rams #8: nothing must be arbitrary or left to chance.

- [`system-spacing-grid`](system-spacing-grid.md) - Use a 4pt base unit for all spacing
- [`system-consistent-padding`](system-consistent-padding.md) - Use consistent padding across all screens
- [`system-corner-radii`](system-corner-radii.md) - Standardize corner radii per component type
- [`system-alignment`](system-alignment.md) - Consistent alignment per content type within a screen
- [`system-color-naming`](system-color-naming.md) - Name custom colors by role, not hue
- [`system-brand-integration`](system-brand-integration.md) - Map brand palette onto iOS semantic color roles

### 6. Thorough to the Last Detail (HIGH)

Rams #8: "Care and accuracy in the design process show respect for the user." Rams #2: if the user cannot reliably use it, the product has failed.

- [`thorough-reduce-motion`](thorough-reduce-motion.md) - Always provide reduce motion fallback
- [`thorough-touch-targets`](thorough-touch-targets.md) - All interactive elements at least 44x44 points
- [`thorough-safe-areas`](thorough-safe-areas.md) - Always respect safe areas
- [`thorough-readable-weights`](thorough-readable-weights.md) - Avoid light font weights for body text
- [`thorough-vibrancy-levels`](thorough-vibrancy-levels.md) - Match vibrancy level to content importance
- [`thorough-material-thickness`](thorough-material-thickness.md) - Choose material thickness by contrast needs
- [`thorough-background-interaction`](thorough-background-interaction.md) - Enable background interaction for peek-style sheets

### 7. Enduring Over Trendy (MEDIUM-HIGH)

Rams #7: "Good design is long-lasting." Edson: commit to a voice that persists across product generations.

- [`enduring-system-text-styles`](enduring-system-text-styles.md) - Use Apple text styles, never fixed font sizes
- [`enduring-weight-not-caps`](enduring-weight-not-caps.md) - Use weight for emphasis, not ALL CAPS
- [`enduring-swipe-back`](enduring-swipe-back.md) - Never break the system back-swipe gesture
- [`enduring-zoom-navigation`](enduring-zoom-navigation.md) - Use zoom transitions for collection-to-detail navigation
- [`enduring-card-modularity`](enduring-card-modularity.md) - Use self-contained cards for dashboard layouts

### 8. Refined Through Iteration (MEDIUM)

Edson: "Design out loud" — prototype relentlessly until every interaction feels inevitable. Rams #1: innovation serves genuine purpose.

- [`refined-scroll-transitions`](refined-scroll-transitions.md) - Use scrollTransition for scroll-position visual effects
- [`refined-phase-animator`](refined-phase-animator.md) - Use PhaseAnimator for multi-step animation sequences
- [`refined-mesh-gradients`](refined-mesh-gradients.md) - Use MeshGradient for premium dynamic backgrounds
- [`refined-text-renderer`](refined-text-renderer.md) - Use TextRenderer for hero text animations only
- [`refined-inspector`](refined-inspector.md) - Use inspector for trailing-edge detail panels
- [`refined-multi-detent`](refined-multi-detent.md) - Provide multiple sheet detents with drag indicator
- [`refined-matched-geometry`](refined-matched-geometry.md) - Use matchedGeometryEffect for contextual origin transitions
- [`refined-no-hard-cuts`](refined-no-hard-cuts.md) - Always animate between states, even minimally
