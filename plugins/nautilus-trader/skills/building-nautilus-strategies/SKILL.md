---
name: building-nautilus-strategies
description: Implement or repair Nautilus Rust trading rules, sizing, brackets, order and position callbacks, and execution races. Not data ingestion or node operations.
metadata:
  author: kmshdev
  version: "0.64.0"
---

# Build a Nautilus strategy

**Input:** trading rules, instrument constraints, admission/exit policy and
existing strategy code when present. **Output:** a native strategy whose order
intent and lifecycle match those rules, with focused execution evidence.

For compilation, use Rust 1.98.1+ and locked `=0.64.0` crates.

## Instructions

1. Separate signal rules, admission, requested orders and observed execution.
   Read [the strategy guide](references/guide.md) for the affected contract.
2. Implement data hooks through `DataActor` and order/position hooks through
   `nautilus_strategy!`. Use facades and the target application's order owner.
3. Validate exact financial values and instrument grids. Establish IDs and
   conservative possible-send state before commands; preserve risk gates.
4. Exercise the relevant execution sequence, including partial fills or
   cancel/modify races when affected. Compare economic state, not merely
   command return values. Leave unresolved execution uncertainty explicit.

Use [runtime contracts](references/foundation.md) for Cache/Portfolio staging,
[connection recipes](references/connections.md) for signal, fill and cancel paths,
[the bounded example](assets/quickstart/README.md) for native composition, and
[source evidence](references/sources.md) for **0.64.0** API discrepancies.

Use [typed run configuration](references/configuration.md),
[component composition](references/composition.md), and the
[Rust test ladder](references/rust-testing.md) when those concerns are affected.

## Examples

- "Build a limit-entry bracket": follow the guide's `order().bracket()` recipe,
  record leg IDs before `submit_order_list`, and qualify OUO/OTO protection.
- "Cancel raced with a partial fill": retain uncertain leaves/exposure until
  native events resolve them; a cancel request does not release all capital.
- For the synthetic baseline, run `cargo test --locked` and `cargo run --locked`
  in `assets/quickstart`; expect one simulated order and position, not a bracket.
  Provider-history ingestion is a separate job.

Deliver the requested artifact with focused verification and material limits.
Follow the user's authorized scope and the target application's ownership.
