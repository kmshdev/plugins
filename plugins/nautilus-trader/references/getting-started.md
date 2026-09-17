# Start with an offline Rust strategy

The smallest useful system is one simulated venue, one instrument, one concrete
strategy and ordered input data in `BacktestEngine`. Learn the runtime boundary
before adding an adapter, database or parameter search.

The [bundled example](../examples/quickstart/README.md) contains an independent
Cargo package, an order-free actor, a one-shot strategy, a JSON custom payload,
and synthetic replay. It needs no data download, credentials or Python runtime.
Its artificial signal demonstrates dispatch, not a trading edge.

## The mental model

| Concept | Meaning |
| --- | --- |
| Instrument | Venue-qualified contract plus currencies, increments, limits and timestamps |
| Quote/trade/bar | Distinct information sources; a completed bar is not a sequence of known ticks |
| Actor | Stateful observer/transformer, using framework subscriptions and clock |
| Strategy | Actor-like component that creates order intent and reacts to execution events |
| Order | A lifecycle, not just a request; acceptance, fills and cancellation are separate facts |
| Position | Exposure reduced from fills by the execution engine |
| Portfolio | Derived accounting/valuation over native account and position state |
| Engine/node | Owns registration, clock, routing, Cache and orderly lifecycle |

An instrument's `Symbol` is not its `InstrumentId`. Use venue-qualified IDs and
matching instrument definitions. A futures multiplier, inverse settlement or
betting payoff is not interchangeable with a spot currency pair.

## Dependency policy

```toml
[dependencies]
anyhow = "1"
nautilus-common = { version = "=0.64.0", default-features = false }
nautilus-model = { version = "=0.64.0", default-features = false }
nautilus-trading = { version = "=0.64.0", default-features = false }
nautilus-backtest = { version = "=0.64.0", default-features = false }
```

Use Rust 1.98.1 or newer with edition 2024. Resolve and retain `Cargo.lock` for
executables; use `cargo check --locked` / `cargo test --locked` after initial
resolution. Keep all Nautilus crates on one version and source. If using source,
pin a verified full upstream revision consistently; do not use a moving branch
or pretend the hosting repository's commit identifies Nautilus.

| Optional need | Crate/feature in the inspected snapshot |
| --- | --- |
| Model fixtures | `nautilus-model/test-support` |
| Built-in strategies | `nautilus-trading/examples` |
| Registered indicator integration | `nautilus-common/indicators` and `nautilus-indicators` |
| Catalog node | `nautilus-backtest/streaming` |
| Catalog API | Direct `nautilus-persistence` dependency |
| Native live event loop | `nautilus-live`, `default-features=false`, feature `node` |
| Broker execution | Matching adapter execution feature and factory/config |
| Arrow custom payload | `nautilus-serialization/arrow` plus matching Arrow dependency |
| Higher fixed precision | Consistent `high-precision` selection across the graph |

Do not enable `python` or `extension-module` for a Rust-only application.
Fixture-feature spelling differs in the moving docs; the bundled example avoids
fixtures entirely. Feature unification means a transitive selection still counts.

## Build a strategy without an unbounded order loop

Construct plain state and validated IDs. In `on_start`, obtain the instrument,
subscribe to the required input, and establish readiness. In the data hook,
separate signal computation from admission; prevent repeated submission while
intent or exposure remains unresolved. In order/position hooks, re-query native
state using IDs and distinguish incremental fills from terminal status.

The one-shot example sets its attempted flag and client-order ID before submit.
It intentionally has no automatic retry or production exit policy. A real
strategy needs sizing, stale-data limits, stops/exits, account readiness and
recovery specific to its instrument and venue.

## Choose the next reference by the next problem

For historical indicators read [Market data](market-data.md); for contingent
entries read [Execution](execution.md); for experiment validity read
[Backtesting](backtesting.md). Only introduce [Live runtime](live.md) after the
strategy has explicit exposure and failure policies.

Compilation qualifies API use; native replay qualifies a simulated path.
Neither proves profitability, broker support or safe real-capital operation.

Evidence: [V1, A1, S1, B1 in the source ledger](sources.md).
