# Quick reference

### 1. Dependency Direction (CRITICAL)

- [`dep-inward-only`](./dep-inward-only.md) - Source dependencies point inward only
- [`dep-interface-ownership`](./dep-interface-ownership.md) - Interfaces belong to clients not implementers
- [`dep-no-framework-imports`](./dep-no-framework-imports.md) - Avoid framework imports in inner layers
- [`dep-data-crossing-boundaries`](./dep-data-crossing-boundaries.md) - Use simple data structures across boundaries
- [`dep-acyclic-dependencies`](./dep-acyclic-dependencies.md) - Eliminate cyclic dependencies between components
- [`dep-stable-abstractions`](./dep-stable-abstractions.md) - Depend on stable abstractions not volatile concretions

### 2. Entity Design (CRITICAL)

- [`entity-pure-business-rules`](./entity-pure-business-rules.md) - Entities contain only enterprise business rules
- [`entity-no-persistence-awareness`](./entity-no-persistence-awareness.md) - Entities must not know how they are persisted
- [`entity-encapsulate-invariants`](./entity-encapsulate-invariants.md) - Encapsulate business invariants within entities
- [`entity-value-objects`](./entity-value-objects.md) - Use value objects for domain concepts
- [`entity-rich-not-anemic`](./entity-rich-not-anemic.md) - Build rich domain models not anemic data structures

### 3. Use Case Isolation (HIGH)

- [`usecase-single-responsibility`](./usecase-single-responsibility.md) - Each use case has one reason to change
- [`usecase-input-output-ports`](./usecase-input-output-ports.md) - Define input and output ports for use cases
- [`usecase-orchestrates-not-implements`](./usecase-orchestrates-not-implements.md) - Use cases orchestrate entities not implement business rules
- [`usecase-no-presentation-logic`](./usecase-no-presentation-logic.md) - Use cases must not contain presentation logic
- [`usecase-explicit-dependencies`](./usecase-explicit-dependencies.md) - Declare all dependencies explicitly in constructor
- [`usecase-transaction-boundary`](./usecase-transaction-boundary.md) - Use case defines the transaction boundary

### 4. Component Cohesion (HIGH)

- [`comp-screaming-architecture`](./comp-screaming-architecture.md) - Structure should scream the domain not the framework
- [`comp-common-closure`](./comp-common-closure.md) - Group classes that change together
- [`comp-common-reuse`](./comp-common-reuse.md) - Avoid forcing clients to depend on unused code
- [`comp-reuse-release-equivalence`](./comp-reuse-release-equivalence.md) - Release components as cohesive units
- [`comp-stable-dependencies`](./comp-stable-dependencies.md) - Depend in the direction of stability

### 5. Boundary Definition (MEDIUM-HIGH)

- [`bound-humble-object`](./bound-humble-object.md) - Use humble objects at architectural boundaries
- [`bound-partial-boundaries`](./bound-partial-boundaries.md) - Use partial boundaries when full separation is premature
- [`bound-boundary-cost-awareness`](./bound-boundary-cost-awareness.md) - Weigh boundary cost against ignorance cost
- [`bound-main-component`](./bound-main-component.md) - Treat main as a plugin to the application
- [`bound-defer-decisions`](./bound-defer-decisions.md) - Defer framework and database decisions
- [`bound-service-internal-architecture`](./bound-service-internal-architecture.md) - Services must have internal clean architecture

### 6. Interface Adapters (MEDIUM)

- [`adapt-controller-thin`](./adapt-controller-thin.md) - Keep controllers thin
- [`adapt-presenter-formats`](./adapt-presenter-formats.md) - Presenters format data for the view
- [`adapt-gateway-abstraction`](./adapt-gateway-abstraction.md) - Gateways hide external system details
- [`adapt-mapper-translation`](./adapt-mapper-translation.md) - Use mappers to translate between layers
- [`adapt-anti-corruption-layer`](./adapt-anti-corruption-layer.md) - Build anti-corruption layers for external systems

### 7. Framework Isolation (MEDIUM)

- [`frame-domain-purity`](./frame-domain-purity.md) - Domain layer has zero framework dependencies
- [`frame-orm-in-infrastructure`](./frame-orm-in-infrastructure.md) - Keep ORM usage in infrastructure layer
- [`frame-web-in-infrastructure`](./frame-web-in-infrastructure.md) - Web framework concerns stay in interface layer
- [`frame-di-container-edge`](./frame-di-container-edge.md) - Dependency injection containers live at the edge
- [`frame-logging-abstraction`](./frame-logging-abstraction.md) - Abstract logging behind domain interfaces

### 8. Testing Architecture (LOW-MEDIUM)

- [`test-tests-are-architecture`](./test-tests-are-architecture.md) - Tests are part of the system architecture
- [`test-testable-design`](./test-testable-design.md) - Design for testability from the start
- [`test-layer-isolation`](./test-layer-isolation.md) - Test each layer in isolation
- [`test-boundary-verification`](./test-boundary-verification.md) - Verify architectural boundaries with tests
