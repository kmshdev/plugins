# SwiftUI navigation reference index

Read only the categories relevant to the task. These rules describe a modular MVVM-C implementation. Apply them only within a project that has chosen that architecture, and verify API availability before using a rule.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Navigation Architecture | CRITICAL | `arch-` |
| 2 | Navigation Anti-Patterns | CRITICAL | `anti-` |

| 3 | Transition & Animation | HIGH | `anim-` |
| 4 | Modal Presentation | HIGH | `modal-` |
| 5 | Flow Orchestration | HIGH | `flow-` |
| 6 | Navigation Performance | MEDIUM-HIGH | `perf-` |
| 7 | Navigation Accessibility | MEDIUM | `ally-` |
| 8 | State & Restoration | MEDIUM | `state-` |

## Quick Reference

### 1. Navigation Architecture (CRITICAL)

- [`arch-navigation-stack`](arch-navigation-stack.md) - Use NavigationStack over deprecated NavigationView
- [`arch-value-based-links`](arch-value-based-links.md) - Use value-based NavigationLink over destination closures
- [`arch-destination-registration`](arch-destination-registration.md) - Register navigationDestination at stack root
- [`arch-destination-item`](arch-destination-item.md) - Use navigationDestination(item:) for optional-based navigation (iOS 26 / Swift 6.2)
- [`arch-route-enum`](arch-route-enum.md) - Define routes as Hashable enums
- [`arch-split-view`](arch-split-view.md) - Use NavigationSplitView for multi-column layouts
- [`arch-coordinator`](arch-coordinator.md) - Extract navigation logic into Observable coordinator
- [`arch-observable-environment`](arch-observable-environment.md) - Use @Environment with @Observable and @Bindable for shared state
- [`arch-deep-linking`](arch-deep-linking.md) - Handle deep links by appending to NavigationPath
- [`arch-navigation-path`](arch-navigation-path.md) - Use NavigationPath for heterogeneous type-erased navigation
- [`arch-equatable-views`](arch-equatable-views.md) - Apply @Equatable macro to every navigation view
- [`arch-observable-only`](arch-observable-only.md) - Use @Observable only — never ObservableObject or @Published
- [`arch-no-anyview`](arch-no-anyview.md) - Never use AnyView in navigation — use @ViewBuilder or generics
- [`arch-coordinator-modals`](arch-coordinator-modals.md) - Present all modals via coordinator — never inline @State

### 2. Navigation Anti-Patterns (CRITICAL)

- [`anti-mixed-link-styles`](anti-mixed-link-styles.md) - Avoid mixing NavigationLink(destination:) with NavigationLink(value:)
- [`anti-scattered-destinations`](anti-scattered-destinations.md) - Avoid scattering navigationDestination across views
- [`anti-shared-stack`](anti-shared-stack.md) - Avoid sharing NavigationStack across tabs
- [`anti-hidden-back-button`](anti-hidden-back-button.md) - Avoid hiding back button without preserving swipe gesture
- [`anti-navigation-in-init`](anti-navigation-in-init.md) - Avoid heavy work in view initializers
- [`anti-hamburger-menu`](anti-hamburger-menu.md) - Avoid hamburger menu navigation
- [`anti-programmatic-tab-switch`](anti-programmatic-tab-switch.md) - Avoid programmatic tab selection changes

### 3. Transition & Animation (HIGH)

- [`anim-zoom-transition`](anim-zoom-transition.md) - Use zoom navigation transition for hero animations (iOS 18+)
- [`anim-matched-geometry-same-view`](anim-matched-geometry-same-view.md) - Use matchedGeometryEffect only within same view hierarchy
- [`anim-spring-config`](anim-spring-config.md) - Use modern spring animation syntax (iOS 26 / Swift 6.2)
- [`anim-gesture-driven`](anim-gesture-driven.md) - Use interactive spring animations for gesture-driven transitions
- [`anim-transition-source-styling`](anim-transition-source-styling.md) - Style transition sources with shape and background
- [`anim-reduce-motion-transitions`](anim-reduce-motion-transitions.md) - Respect reduce motion for all navigation animations
- [`anim-scroll-driven`](anim-scroll-driven.md) - Use onScrollGeometryChange for scroll-driven transitions (iOS 18+)

### 4. Modal Presentation (HIGH)

- [`modal-sheet-vs-push`](modal-sheet-vs-push.md) - Use push for drill-down, sheet for supplementary content
- [`modal-detents`](modal-detents.md) - Use presentation detents for contextual sheet sizing
- [`modal-fullscreen-cover`](modal-fullscreen-cover.md) - Use fullScreenCover only for immersive standalone experiences
- [`modal-sheet-placement`](modal-sheet-placement.md) - Place .sheet on container view, not on NavigationLink
- [`modal-interactive-dismiss`](modal-interactive-dismiss.md) - Guard unsaved changes with interactiveDismissDisabled
- [`modal-nested-navigation`](modal-nested-navigation.md) - Use separate NavigationStack inside modals

### 5. Flow Orchestration (HIGH)

- [`flow-tab-independence`](flow-tab-independence.md) - Give each tab its own NavigationStack
- [`flow-multi-step`](flow-multi-step.md) - Use NavigationStack with route array for multi-step flows
- [`flow-sidebar-navigation`](flow-sidebar-navigation.md) - Use NavigationSplitView with selection binding for sidebar
- [`flow-tab-sidebar-adaptive`](flow-tab-sidebar-adaptive.md) - Use sidebarAdaptable TabView for iPad tab-to-sidebar (iOS 18+)
- [`flow-pop-to-root`](flow-pop-to-root.md) - Implement pop-to-root by clearing NavigationPath
- [`flow-screen-independence`](flow-screen-independence.md) - Keep screens independent of parent navigation context

### 6. Navigation Performance (MEDIUM-HIGH)

- [`perf-lazy-destinations`](perf-lazy-destinations.md) - Use value-based NavigationLink for lazy destination construction
- [`perf-task-modifier`](perf-task-modifier.md) - Use .task for async data loading on navigation
- [`perf-state-object-ownership`](perf-state-object-ownership.md) - Own @Observable state with @State, pass as plain property
- [`perf-avoid-body-side-effects`](perf-avoid-body-side-effects.md) - Avoid side effects in view body


### 7. Navigation Accessibility (MEDIUM)

- [`ally-rotor-headers`](ally-rotor-headers.md) - Mark navigation section headers for VoiceOver rotor
- [`ally-focus-after-navigation`](ally-focus-after-navigation.md) - Manage focus after programmatic navigation events
- [`ally-group-navigation-elements`](ally-group-navigation-elements.md) - Group related navigation elements to reduce swipe count
- [`ally-hide-decorative-navigation`](ally-hide-decorative-navigation.md) - Hide decorative navigation elements from VoiceOver
- [`ally-keyboard-focus`](ally-keyboard-focus.md) - Use @FocusState for keyboard navigation in forms

### 8. State & Restoration (MEDIUM)

- [`state-codable-routes`](state-codable-routes.md) - Make route enums Codable for navigation persistence
- [`state-scene-storage`](state-scene-storage.md) - Use SceneStorage for per-scene navigation persistence
- [`state-tab-persistence`](state-tab-persistence.md) - Persist selected tab with SceneStorage
- [`state-deep-link-urls`](state-deep-link-urls.md) - Parse deep link URLs into route enums
- [`state-avoid-app-level-path`](state-avoid-app-level-path.md) - Avoid defining NavigationPath at App level
