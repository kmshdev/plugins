---
name: building-nautilus-actors
description: Build or fix order-free Nautilus Rust actors, subscriptions, timers, indicator warm-up, and custom-data publication. Not order execution or node deployment.
metadata:
  author: kmshdev
  version: "0.63.0"
---

# Build a Nautilus actor

**Input:** the actor's input streams, derived output and lifecycle requirements,
plus existing code when repairing a component. Infer established conventions
from the target project; do not invent trading rules.
**Output:** a native order-free component with the requested delivery/state
behavior and evidence at the affected callback or runtime boundary.

For compilation, use Rust 1.98.0+ and locked `=0.63.0` crates.

## Instructions

1. Identify the missing behavior and its input/output identity. Read
   [the actor guide](references/guide.md) for the affected API, not every reference.
2. Implement `DataActor`, one `DataActorCore`, `Debug` and `nautilus_actor!`.
   Subscribe/request after registration; keep order methods out of the actor.
3. Preserve causal timestamps and one indicator update owner. Bound warm-up and
   restore subscriptions/timers on the relevant lifecycle transitions.
4. Exercise the affected path. For delivery defects, include native
   registration and dispatch rather than only directly calling the hook.
   Report what that evidence establishes and any unresolved failure.

Use [runtime contracts](references/foundation.md) for cross-component ordering,
[connection recipes](references/connections.md) for publication or history handover,
[the offline example](assets/quickstart/README.md) for native dispatch, and
[source evidence](references/sources.md) for version disagreements.

Use [typed run configuration](references/configuration.md),
[component composition](references/composition.md), and the
[Rust test ladder](references/rust-testing.md) when those concerns are affected.

## Examples

- "Count quotes and custom signals": use the order-free offline actor. In
  `assets/quickstart`, run `cargo test --locked` then `cargo run --locked`;
  expect four quotes, one signal, zero orders and zero positions.
- "My timer advances but no callback runs": match returned TestClock events
  to handlers, release the clock borrow, then execute them.
- "Submit a bracket": this is a Strategy job, not an actor extension.

Deliver the requested artifact with focused verification and material limits.
Follow the user's authorized scope and the target application's ownership.
