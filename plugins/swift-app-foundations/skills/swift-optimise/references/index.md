# Swift performance reference index

Read only the categories relevant to the task. Choose rules that fit the task and supported SDK. Some examples assume a modular clinic app; their architecture constraints apply only to projects that adopted that design.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Concurrency & Async | CRITICAL | `conc-` |
| 2 | Render & Scroll Performance | HIGH | `perf-` |
| 3 | Animation Performance | MEDIUM | `anim-` |

## Quick Reference

### 1. Concurrency & Async (CRITICAL)

- [`conc-combine-to-async`](conc-combine-to-async.md) - Replace Combine publishers with async/await
- [`conc-mainactor-isolation`](conc-mainactor-isolation.md) - Use @MainActor instead of DispatchQueue.main
- [`conc-swift6-sendable`](conc-swift6-sendable.md) - Adopt Sendable and Swift 6 strict concurrency
- [`conc-task-id-pattern`](conc-task-id-pattern.md) - Use .task(id:) for reactive data loading
- [`conc-actor-for-shared-state`](conc-actor-for-shared-state.md) - Replace lock-based shared state with actors
- [`conc-asyncsequence-streams`](conc-asyncsequence-streams.md) - Replace NotificationCenter observers with AsyncSequence

### 2. Render & Scroll Performance (HIGH)

- [`perf-view-decomposition`](perf-view-decomposition.md) - Decompose views to limit state invalidation blast radius
- [`perf-instruments-profiling`](perf-instruments-profiling.md) - Profile with SwiftUI Instruments before optimizing
- [`perf-lazy-containers`](perf-lazy-containers.md) - Use lazy containers for large collections
- [`perf-canvas-timeline`](perf-canvas-timeline.md) - Use Canvas and TimelineView for high-performance rendering
- [`perf-drawinggroup`](perf-drawinggroup.md) - Use drawingGroup for complex graphics
- [`perf-equatable-views`](perf-equatable-views.md) - Add Equatable conformance to prevent spurious redraws
- [`perf-task-modifier`](perf-task-modifier.md) - Use .task modifier instead of .onAppear for async work
- [`perf-async-image`](perf-async-image.md) - Use AsyncImage with caching strategy for remote images

### 3. Animation Performance (MEDIUM)

- [`anim-spring`](anim-spring.md) - Use spring animations as default
- [`anim-matchedgeometry`](anim-matchedgeometry.md) - Use matchedGeometryEffect for shared transitions
- [`anim-gesture-driven`](anim-gesture-driven.md) - Make animations gesture-driven
- [`anim-with-animation`](anim-with-animation.md) - Use withAnimation for state-driven transitions
- [`anim-transition-effects`](anim-transition-effects.md) - Apply transition effects for view insertion and removal
