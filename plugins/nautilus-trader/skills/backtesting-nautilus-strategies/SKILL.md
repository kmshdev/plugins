---
name: backtesting-nautilus-strategies
description: Run or diagnose reproducible Nautilus Rust backtests, replay ordering, catalog chunking, fill assumptions, and result comparisons. Not live account operations.
metadata:
  author: kmshdev
  version: "0.64.0"
---

# Backtest a Nautilus strategy

**Input:** strategy, instrument/venue configuration, admitted data and the
experiment question. **Output:** a reproducible native run and results labeled
with the simulation assumptions and evidence limitations.

For compilation, use Rust 1.98.1+ and locked `=0.64.0` crates. Require admitted
input and instrument definitions, not a provider credential for synthetic replay.

## Instructions

1. Choose direct `BacktestEngine` or catalog `BacktestNode` using
   [the replay guide](references/guide.md). Do not assume chunking bounds memory.
2. Fix input identity, availability ordering, warm-up, venue/account settings,
   fees and execution assumptions. Register the real native components.
3. Run the requested scenario; verify input coverage and outcomes, not only an
   `Ok` return. Preserve same-time batches and the declared tie policy.
4. Compare canonical economic results under recorded conditions. Diagnose the
   first meaningful divergence without changing trading rules or discarding
   inconvenient records.

Start from the [offline Rust example](assets/quickstart/README.md) when no harness
exists. Consult [runtime contracts](references/foundation.md) and
[connection recipes](references/connections.md) for coupled replay paths, and
[source evidence](references/sources.md) only when the boundary requires them.
The package targets **NautilusTrader 0.64.0**, without Python.

Use [typed run configuration](references/configuration.md),
[component composition](references/composition.md), and the
[Rust test ladder](references/rust-testing.md) when those concerns are affected.
For durable capture or reruns, use [event replay](references/event-replay.md).

## Examples

- "Run a first offline experiment": in `assets/quickstart`, run
  `cargo test --locked` then `cargo run --locked`; expect five inputs, four quotes,
  one custom signal, one simulated order and one position.
- "Prove two runs agree": compare canonical economics with the same `ts_init`
  tie policy, not wall-clock metadata.
- "A chunk size of 1000 must bound RAM": inspect materialization and equal-time
  groups; do not silently drop data. Broker restart recovery is a separate job.

Deliver the requested artifact with focused verification and material limits.
Follow the user's authorized scope and the target application's ownership.
