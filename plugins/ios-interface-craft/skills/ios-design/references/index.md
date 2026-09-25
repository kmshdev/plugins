# New SwiftUI screens reference index

Read only the categories relevant to the task. Choose rules that fit the task and supported SDK. Some examples assume a modular clinic app; their architecture constraints apply only to projects that adopted that design.

## Rule Categories by Priority

| Priority | Category | Principle | Impact | Prefix | Rules |
|----------|----------|-----------|--------|--------|-------|
| 1 | Empathy in Every Pixel | Kocienda "Empathy" · Edson "Design Is About People" | CRITICAL | `empathy-` | 8 |
| 2 | The Visual System | Edson "Systems Thinking" · Kocienda "Convergence" | CRITICAL | `system-` | 8 |
| 3 | Craft: State as Foundation | Kocienda "Craft" | CRITICAL | `craft-` | 7 |
| 4 | Creative Composition | Kocienda "Creative Selection" | HIGH | `compose-` | 6 |
| 5 | Taste: The Right Choice | Kocienda "Taste" · Edson "Design with Conviction" | HIGH | `taste-` | 8 |
| 6 | Navigation as Conversation | Edson "Design Is a Conversation" · Kocienda "The Demo" | HIGH | `converse-` | 9 |
| 7 | Design Out Loud: Layout | Edson "Design Out Loud" · Kocienda "Intersection" | HIGH | `layout-` | 8 |
| 8 | The Product Speaks | Edson "Product Is the Marketing" · Kocienda "Demo Culture" | MEDIUM | `product-` | 8 |

## Quick Reference

### 1. Empathy in Every Pixel (CRITICAL)

Kocienda: "Empathy — trying to see the world from other people's perspectives." Edson: design begins with the person holding the device.

- [`empathy-semantic-colors`](empathy-semantic-colors.md) - Use semantic colors, never hard-coded values
- [`empathy-dark-mode`](empathy-dark-mode.md) - Support Dark Mode from day one
- [`empathy-foreground-style`](empathy-foreground-style.md) - Use foregroundStyle over foregroundColor
- [`empathy-safe-areas`](empathy-safe-areas.md) - Always respect safe areas for content
- [`empathy-voiceover-labels`](empathy-voiceover-labels.md) - Add VoiceOver labels to every interactive element
- [`empathy-touch-targets`](empathy-touch-targets.md) - Ensure 44x44 point minimum touch targets
- [`empathy-reduce-motion`](empathy-reduce-motion.md) - Always provide reduce motion fallback
- [`empathy-readable-width`](empathy-readable-width.md) - Constrain text to readable width on iPad

### 2. The Visual System (CRITICAL)

Edson: "Zoom out to see relationships between objects." Kocienda: convergence — many decisions narrowing toward one coherent whole.

- [`system-typography`](system-typography.md) - Use system typography styles, never fixed sizes
- [`system-visual-hierarchy`](system-visual-hierarchy.md) - Establish clear visual hierarchy through size, weight, and color
- [`system-spacing-grid`](system-spacing-grid.md) - Use a 4pt base unit for all spacing
- [`system-material-backgrounds`](system-material-backgrounds.md) - Use material backgrounds for depth and layering
- [`system-sf-symbols`](system-sf-symbols.md) - Use SF Symbols for consistent iconography
- [`system-gradients`](system-gradients.md) - Apply gradients for visual depth, not decoration
- [`system-standard-margins`](system-standard-margins.md) - Use system standard margins consistently
- [`system-stack-config`](system-stack-config.md) - Configure stack alignment and spacing explicitly

### 3. Craft: State as Foundation (CRITICAL)

Kocienda: "Craft — applying skill to achieve a high-quality result."

- [`craft-state-local`](craft-state-local.md) - Use @State for view-local value types
- [`craft-state-binding`](craft-state-binding.md) - Use @Binding for child view mutations
- [`craft-state-environment`](craft-state-environment.md) - Use @Environment for shared app-wide data
- [`craft-state-observable`](craft-state-observable.md) - Use @Observable for model classes
- [`craft-avoid-body-state`](craft-avoid-body-state.md) - Never create state inside the view body
- [`craft-minimize-scope`](craft-minimize-scope.md) - Minimize state scope to reduce re-renders
- [`craft-state-bindable`](craft-state-bindable.md) - Use @Bindable for @Observable bindings

### 4. Creative Composition (HIGH)

Kocienda: "Creative selection — great software is built through composition and recombination."

- [`compose-body-some-view`](compose-body-some-view.md) - Return some View from body, never concrete types
- [`compose-custom-properties`](compose-custom-properties.md) - Use properties to make views configurable
- [`compose-modifier-order`](compose-modifier-order.md) - Apply view modifiers in the correct order
- [`compose-viewbuilder`](compose-viewbuilder.md) - Use @ViewBuilder for flexible slot-based composition
- [`compose-prefer-value-types`](compose-prefer-value-types.md) - Prefer value types for view data
- [`compose-prefer-composition`](compose-prefer-composition.md) - Prefer composition over inheritance for view reuse

### 5. Taste: The Right Choice (HIGH)

Kocienda: "Taste — refined judgment, the ability to choose the one right solution." Edson: commit to one approach and perfect it.

- [`taste-list-vs-lazyvstack`](taste-list-vs-lazyvstack.md) - Choose List for system features, LazyVStack for custom layouts
- [`taste-sheet-vs-fullscreen`](taste-sheet-vs-fullscreen.md) - Choose sheet for tasks, fullScreenCover for immersion
- [`taste-picker`](taste-picker.md) - Choose the right picker style for the data type
- [`taste-grid-vs-lazygrid`](taste-grid-vs-lazygrid.md) - Choose Grid for aligned data, LazyVGrid for scrollable collections
- [`taste-button`](taste-button.md) - Use button styles that match the action's importance
- [`taste-textfield`](taste-textfield.md) - Configure text input with the right keyboard and content type
- [`taste-alerts`](taste-alerts.md) - Use alerts only for critical, blocking information
- [`taste-action-sheets`](taste-action-sheets.md) - Use confirmation dialogs for contextual multi-choice actions

### 6. Navigation as Conversation (HIGH)

Edson: "Design is a conversation between the product and the person." Kocienda: demos as conversations about whether the interface speaks clearly.

- [`converse-navigationstack`](converse-navigationstack.md) - Use NavigationStack for programmatic, type-safe navigation
- [`converse-tabview`](converse-tabview.md) - Organize app sections with TabView for parallel navigation
- [`converse-sheet-item`](converse-sheet-item.md) - Use item binding for data-driven sheet presentation
- [`converse-dismiss`](converse-dismiss.md) - Use environment dismiss for modal closure
- [`converse-toolbar`](converse-toolbar.md) - Place toolbar items in the correct semantic positions
- [`converse-tab-bar`](converse-tab-bar.md) - Use tab bar for top-level section navigation
- [`converse-nav-bar`](converse-nav-bar.md) - Configure navigation bar to communicate context
- [`converse-hierarchy`](converse-hierarchy.md) - Design clear navigation hierarchy before writing code
- [`converse-search`](converse-search.md) - Integrate search with the searchable modifier

### 7. Design Out Loud: Layout (HIGH)

Edson: "Design Out Loud — prototype relentlessly until layout feels inevitable." Kocienda: the intersection of technology and liberal arts.

- [`layout-stacks`](layout-stacks.md) - Use stacks instead of manual positioning
- [`layout-spacer`](layout-spacer.md) - Use Spacer for flexible space distribution
- [`layout-frame-sizing`](layout-frame-sizing.md) - Use frame() for explicit size constraints
- [`layout-zstack`](layout-zstack.md) - Use ZStack for purposeful layered composition
- [`layout-grid`](layout-grid.md) - Use Grid for aligned non-scrolling tabular content
- [`layout-lazy-grids`](layout-lazy-grids.md) - Use LazyVGrid for scrollable multi-column layouts
- [`layout-adaptive`](layout-adaptive.md) - Use adaptive layouts for different size classes
- [`layout-scroll-indicators`](layout-scroll-indicators.md) - Show scroll indicators for long scrollable content

### 8. The Product Speaks (MEDIUM)

Edson: "The product itself is the marketing." Kocienda: every animation and loading state built to survive Steve Jobs' scrutiny.

- [`product-transitions`](product-transitions.md) - Use semantic transitions for appearing views
- [`product-loading-states`](product-loading-states.md) - Show honest loading states, not indefinite spinners
- [`product-with-animation`](product-with-animation.md) - Use withAnimation for explicit state-driven animation
- [`product-matched-geometry`](product-matched-geometry.md) - Use matchedGeometryEffect for contextual origin transitions
- [`product-list-cells`](product-list-cells.md) - Design list cells with standard layouts
- [`product-content-unavailable`](product-content-unavailable.md) - Use ContentUnavailableView for empty and error states
- [`product-segmented`](product-segmented.md) - Use segmented controls for visible, mutually exclusive options
- [`product-menus`](product-menus.md) - Use menus for secondary actions without cluttering the interface
