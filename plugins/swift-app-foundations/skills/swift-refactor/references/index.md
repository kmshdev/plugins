# Swift refactoring reference index

Read only the categories relevant to the task. These rules describe a modular MVVM-C implementation. Apply them only within a project that has chosen that architecture, and verify API availability before using a rule.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix | Rules |
|----------|----------|--------|--------|-------|
| 1 | View Identity & Diffing | CRITICAL | `diff-` | 4 |
| 2 | API Modernization | CRITICAL | `api-` | 7 |
| 3 | State Architecture | CRITICAL | `state-` | 6 |
| 4 | View Composition | HIGH | `view-` | 7 |
| 5 | Navigation & Coordination | HIGH | `nav-` | 5 |
| 6 | Layer Architecture | HIGH | `layer-` | 5 |
| 7 | Architecture Patterns | HIGH | `arch-` | 5 |
| 8 | Dependency Injection | MEDIUM-HIGH | `di-` | 2 |
| 9 | Type Safety & Protocols | MEDIUM-HIGH | `type-` | 4 |
| 10 | List & Collection Performance | MEDIUM | `list-` | 4 |
| 11 | Async & Data Flow | MEDIUM | `data-` | 3 |
| 12 | Swift Language Fundamentals | MEDIUM | `swift-` | 8 |

## Quick Reference

### 1. View Identity & Diffing (CRITICAL)

- [`diff-equatable-views`](diff-equatable-views.md) - Add @Equatable macro to every SwiftUI view
- [`diff-closure-skip`](diff-closure-skip.md) - Use @EquatableIgnored for closure properties
- [`diff-identity-stability`](diff-identity-stability.md) - Use stable O(1) identifiers in ForEach
- [`diff-printchanges-debug`](diff-printchanges-debug.md) - Use _printChanges() to diagnose re-renders

### 2. API Modernization (CRITICAL)

- [`api-observable-macro`](api-observable-macro.md) - Migrate ObservableObject to @Observable macro
- [`api-navigationstack-migration`](api-navigationstack-migration.md) - Replace NavigationView with NavigationStack
- [`api-onchange-signature`](api-onchange-signature.md) - Migrate to new onChange signature
- [`api-environment-object-removal`](api-environment-object-removal.md) - Replace @EnvironmentObject with @Environment
- [`api-alert-confirmation-dialog`](api-alert-confirmation-dialog.md) - Migrate Alert to confirmationDialog API
- [`api-list-foreach-identifiable`](api-list-foreach-identifiable.md) - Replace id: \.self with Identifiable conformance
- [`api-toolbar-migration`](api-toolbar-migration.md) - Replace navigationBarItems with toolbar modifier

### 3. State Architecture (CRITICAL)

- [`state-scope-minimization`](state-scope-minimization.md) - Minimize state scope to nearest consumer
- [`state-derived-over-stored`](state-derived-over-stored.md) - Use computed properties over redundant @State
- [`state-binding-extraction`](state-binding-extraction.md) - Extract @Binding to isolate child re-renders
- [`state-remove-observation`](state-remove-observation.md) - Migrate @ObservedObject to @Observable tracking
- [`state-onappear-to-task`](state-onappear-to-task.md) - Replace onAppear closures with .task modifier
- [`state-stateobject-placement`](state-stateobject-placement.md) - Migrate @StateObject to @State with @Observable

### 4. View Composition (HIGH)

- [`view-extract-subviews`](view-extract-subviews.md) - Extract subviews for diffing checkpoints
- [`view-eliminate-anyview`](view-eliminate-anyview.md) - Replace AnyView with @ViewBuilder or generics
- [`view-computed-to-struct`](view-computed-to-struct.md) - Convert computed view properties to struct views
- [`view-modifier-extraction`](view-modifier-extraction.md) - Extract repeated modifiers into custom ViewModifiers
- [`view-conditional-content`](view-conditional-content.md) - Use Group or conditional modifiers over conditional views
- [`view-preference-keys`](view-preference-keys.md) - Replace callback closures with PreferenceKey
- [`view-body-complexity`](view-body-complexity.md) - Reduce view body to maximum 10 nodes

### 5. Navigation & Coordination (HIGH)

- [`nav-centralize-destinations`](nav-centralize-destinations.md) - Refactor navigation to coordinator pattern
- [`nav-value-based-links`](nav-value-based-links.md) - Replace NavigationLink with coordinator routes
- [`nav-path-state-management`](nav-path-state-management.md) - Use NavigationPath for programmatic navigation
- [`nav-split-view-adoption`](nav-split-view-adoption.md) - Use NavigationSplitView for multi-column layouts
- [`nav-sheet-item-pattern`](nav-sheet-item-pattern.md) - Replace boolean sheet triggers with item binding

### 6. Layer Architecture (HIGH)

- [`layer-dependency-rule`](layer-dependency-rule.md) - Extract domain layer with zero framework imports
- [`layer-usecase-protocol`](layer-usecase-protocol.md) - Remove use-case/interactor layer; keep orchestration in ViewModel + repository protocols
- [`layer-repository-protocol`](layer-repository-protocol.md) - Repository protocols in Domain, implementations in Data
- [`layer-no-view-repository`](layer-no-view-repository.md) - Remove direct repository access from views
- [`layer-viewmodel-boundary`](layer-viewmodel-boundary.md) - Refactor ViewModels to expose display-ready state only

### 7. Architecture Patterns (HIGH)

- [`arch-viewmodel-elimination`](arch-viewmodel-elimination.md) - Restructure inline state into @Observable ViewModel
- [`arch-protocol-dependencies`](arch-protocol-dependencies.md) - Extract protocol dependencies through ViewModel layer
- [`arch-environment-key-injection`](arch-environment-key-injection.md) - Use Environment keys for service injection
- [`arch-feature-module-extraction`](arch-feature-module-extraction.md) - Extract features into independent modules
- [`arch-model-view-separation`](arch-model-view-separation.md) - Extract business logic into Domain models and repository-backed ViewModels

### 8. Dependency Injection (MEDIUM-HIGH)

- [`di-container-composition`](di-container-composition.md) - Compose dependency container at app root
- [`di-mock-testing`](di-mock-testing.md) - Add mock implementation for every protocol dependency

### 9. Type Safety & Protocols (MEDIUM-HIGH)

- [`type-tagged-identifiers`](type-tagged-identifiers.md) - Replace String IDs with tagged types
- [`type-result-over-optionals`](type-result-over-optionals.md) - Use Result type over optional with error flag
- [`type-phantom-types`](type-phantom-types.md) - Use phantom types for compile-time state machines
- [`type-force-unwrap-elimination`](type-force-unwrap-elimination.md) - Eliminate force unwraps with safe alternatives

### 10. List & Collection Performance (MEDIUM)

- [`list-constant-viewcount`](list-constant-viewcount.md) - Ensure ForEach produces constant view count per element
- [`list-filter-in-model`](list-filter-in-model.md) - Move filter/sort logic from ForEach into ViewModel
- [`list-lazy-stacks`](list-lazy-stacks.md) - Replace VStack/HStack with Lazy variants for unbounded content
- [`list-id-keypath`](list-id-keypath.md) - Provide explicit id keyPath — never rely on implicit identity

### 11. Async & Data Flow (MEDIUM)

- [`data-task-modifier`](data-task-modifier.md) - Replace onAppear async work with .task modifier
- [`data-error-loadable`](data-error-loadable.md) - Model loading states as enum instead of boolean flags
- [`data-cancellation`](data-cancellation.md) - Use .task automatic cancellation — never manage Tasks manually

### 12. Swift Language Fundamentals (MEDIUM)

- [`swift-let-vs-var`](swift-let-vs-var.md) - Use let for constants, var for variables
- [`swift-structs-vs-classes`](swift-structs-vs-classes.md) - Prefer structs over classes
- [`swift-camel-case-naming`](swift-camel-case-naming.md) - Use camelCase naming convention
- [`swift-string-interpolation`](swift-string-interpolation.md) - Use string interpolation for dynamic text
- [`swift-functions-clear-names`](swift-functions-clear-names.md) - Name functions and parameters for clarity
- [`swift-for-in-loops`](swift-for-in-loops.md) - Use for-in loops for collections
- [`swift-optionals`](swift-optionals.md) - Handle optionals safely with unwrapping
- [`swift-closures`](swift-closures.md) - Use closures for inline functions
