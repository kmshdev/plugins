# SwiftUI architecture reference index

Read only the categories relevant to the task. These rules describe a modular MVVM-C implementation. Apply them only within a project that has chosen that architecture, and verify API availability before using a rule.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix | Rules |
|----------|----------|--------|--------|-------|
| 1 | View Identity & Diffing | CRITICAL | `diff-` | 6 |
| 2 | State Architecture | CRITICAL | `state-` | 7 |
| 3 | View Composition | HIGH | `view-` | 6 |
| 4 | Navigation & Coordination | HIGH | `nav-` | 5 |
| 5 | Layer Architecture | HIGH | `layer-` | 6 |
| 6 | Dependency Injection | MEDIUM-HIGH | `di-` | 4 |
| 7 | List & Collection Performance | MEDIUM | `list-` | 4 |
| 8 | Async & Data Flow | MEDIUM | `data-` | 5 |

## Quick Reference

### 1. View Identity & Diffing (CRITICAL)

- [`diff-equatable-views`](diff-equatable-views.md) - Apply @Equatable macro to every SwiftUI view
- [`diff-closure-skip`](diff-closure-skip.md) - Use @SkipEquatable for closure/handler properties
- [`diff-reference-types`](diff-reference-types.md) - Never store reference types without Equatable conformance
- [`diff-identity-stability`](diff-identity-stability.md) - Use stable O(1) identifiers in ForEach
- [`diff-avoid-anyview`](diff-avoid-anyview.md) - Never use AnyView — use @ViewBuilder or generics
- [`diff-printchanges-debug`](diff-printchanges-debug.md) - Use _printChanges() to diagnose unnecessary re-renders

### 2. State Architecture (CRITICAL)

- [`state-observable-class`](state-observable-class.md) - Use @Observable classes for all ViewModels
- [`state-ownership`](state-ownership.md) - @State for owned data, plain property for injected data
- [`state-single-source`](state-single-source.md) - One source of truth per piece of state
- [`state-scoped-observation`](state-scoped-observation.md) - Leverage @Observable property-level tracking
- [`state-binding-minimal`](state-binding-minimal.md) - Pass @Binding only for two-way data flow
- [`state-environment-global`](state-environment-global.md) - Use @Environment for app-wide shared dependencies
- [`state-no-published`](state-no-published.md) - Never use @Published or ObservableObject

### 3. View Composition (HIGH)

- [`view-body-complexity`](view-body-complexity.md) - Maximum 10 nodes in view body
- [`view-extract-subviews`](view-extract-subviews.md) - Extract computed properties/helpers into separate View structs
- [`view-no-logic-in-body`](view-no-logic-in-body.md) - Zero business logic in body
- [`view-minimal-dependencies`](view-minimal-dependencies.md) - Pass only needed properties, not entire models
- [`view-viewbuilder-composition`](view-viewbuilder-composition.md) - Use @ViewBuilder for conditional composition
- [`view-no-init-sideeffects`](view-no-init-sideeffects.md) - Never perform work in View init

### 4. Navigation & Coordination (HIGH)

- [`nav-coordinator-pattern`](nav-coordinator-pattern.md) - Every feature has a coordinator owning NavigationStack
- [`nav-routes-enum`](nav-routes-enum.md) - Define all routes as a Hashable enum
- [`nav-deeplink-support`](nav-deeplink-support.md) - Coordinators must support URL-based deep linking
- [`nav-modal-sheets`](nav-modal-sheets.md) - Present modals via coordinator, not inline
- [`nav-no-navigationlink`](nav-no-navigationlink.md) - Never use NavigationLink(destination:) — use navigationDestination(for:)

### 5. Layer Architecture (HIGH)

- [`layer-dependency-rule`](layer-dependency-rule.md) - Domain layer has zero framework imports
- [`layer-usecase-protocol`](layer-usecase-protocol.md) - Do not add a use-case layer; keep orchestration in ViewModel + repository protocols
- [`layer-repository-protocol`](layer-repository-protocol.md) - Repository protocols in Domain, implementations in Data
- [`layer-model-value-types`](layer-model-value-types.md) - Domain models are structs, never classes
- [`layer-no-view-repository`](layer-no-view-repository.md) - Views never access repositories directly; ViewModel calls repository protocols
- [`layer-viewmodel-boundary`](layer-viewmodel-boundary.md) - ViewModels expose display-ready state only

### 6. Dependency Injection (MEDIUM-HIGH)

- [`di-environment-injection`](di-environment-injection.md) - Inject container-managed protocol dependencies via @Environment
- [`di-protocol-abstraction`](di-protocol-abstraction.md) - All injected dependencies are protocol types
- [`di-container-composition`](di-container-composition.md) - Compose `DependencyContainer` in App target and expose VM factories
- [`di-mock-testing`](di-mock-testing.md) - Every protocol dependency has a mock for testing

### 7. List & Collection Performance (MEDIUM)

- [`list-constant-viewcount`](list-constant-viewcount.md) - ForEach must produce constant view count per element
- [`list-filter-in-model`](list-filter-in-model.md) - Filter/sort in ViewModel, never inside ForEach
- [`list-lazy-stacks`](list-lazy-stacks.md) - Use LazyVStack/LazyHStack for unbounded content
- [`list-id-keypath`](list-id-keypath.md) - Provide explicit id keyPath — never rely on implicit identity

### 8. Async & Data Flow (MEDIUM)

- [`data-task-modifier`](data-task-modifier.md) - Use `.task(id:)` as the primary feature data-loading trigger
- [`data-async-init`](data-async-init.md) - Never perform async work in init
- [`data-error-loadable`](data-error-loadable.md) - Model loading states as enum, not booleans
- [`data-combine-avoid`](data-combine-avoid.md) - Prefer async/await over Combine for new code
- [`data-cancellation`](data-cancellation.md) - Use .task automatic cancellation — never manage Tasks manually
