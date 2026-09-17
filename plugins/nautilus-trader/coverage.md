# Architecture and workflow coverage

Scope: compose and use NautilusTrader 0.64.0 Rust, not implement every framework
subsystem. Adapter-specific coverage is restricted to IBKR and Databento.

| Component or contract | Workflow owner | Bundled reference |
| --- | --- | --- |
| MessageBus pub/sub, commands and correlated responses | Actors, with shared foundation | [Actor guide](skills/building-nautilus-actors/references/guide.md) |
| Kernel, Trader, clocks, registration and owner thread | Backtesting / live | [Foundation](references/foundation.md) |
| Data clients, subscriptions, history and aggregation | Integrating data | [Data guide](skills/integrating-nautilus-data/references/guide.md) |
| Immutable custom data, routes, JSON and Arrow | Actors / integrating data | [Actor guide](skills/building-nautilus-actors/references/guide.md) |
| Actor lifecycle and indicator readiness | Actors | [Actor guide](skills/building-nautilus-actors/references/guide.md) |
| Strategy intent, orders, brackets and algorithms | Strategies | [Strategy guide](skills/building-nautilus-strategies/references/guide.md) |
| RiskEngine versus application admission | Strategies | [Strategy guide](skills/building-nautilus-strategies/references/guide.md) |
| ExecutionEngine, fill reduction and command races | Strategies | [Strategy guide](skills/building-nautilus-strategies/references/guide.md) |
| Cache, Portfolio and account-stage consistency | Strategies / live | [Foundation](references/foundation.md) |
| Catalog, streaming, simulator and canonical results | Backtesting | [Replay guide](skills/backtesting-nautilus-strategies/references/guide.md) |
| Databento factories/data/history and symbology | Integrating data / live | [Adapter data](references/adapter-data.md) |
| IBKR contract resolution, execution and reports | Live / integrating data | [Adapter runtime](references/adapter-runtime.md) |
| Cache persistence, event replay and shutdown | Live | [Live guide](skills/running-nautilus-live/references/guide.md) |
| Run isolation, CI/container delivery, PostgreSQL schema, Redis cache, Feather/Parquet and cloud storage | Run delivery | [Deployment guide](skills/deploying-nautilus-runs/references/guide.md), [storage](skills/deploying-nautilus-runs/references/storage.md) |

## Connection acceptance scenarios

The [connection recipes](references/connections.md) give each path's owners,
implementation sequence, failure controls and required evidence. Each installed
skill includes only its relevant recipes and their source anchors; no sibling
skill or parent checkout is required.

| ID | Finite scenario | Evaluation owner |
| --- | --- | --- |
| C1 | Quote delivery -> actor -> immutable custom observation -> strategy | Actors `actor-code`, `inline-dispatch`; native quickstart provides dispatch evidence |
| C2 | Strategy -> risk/execution -> partial fill -> Cache -> Portfolio | Strategies `native-bracket`, `cancel-fill-race` |
| C3 | Historical request -> warm-up -> live handover | Actors `indicator-history-timer`; data guide's bounded merge contract; replay `mixed-custom-history` |
| C4 | Submit uncertainty / cancel -> late fill -> exposure | Strategies `cancel-fill-race`, `gtd-error-grid` |
| C5 | Restore -> broker reports -> admission -> graceful stop | Live `missing-report`, `restart-continuity`; guide's shutdown policy |
| C6 | Same strategy in replay and connected runtime | Replay `deterministic-replay`, live `construct-only`; connected behavior remains unqualified |
| C7 | Databento symbol -> native instrument -> IB qualified dated contract | Data `databento-node-bars`, `provider-timestamps`; live `construct-only` |
| C8 | Catalog/custom schema -> availability ordering -> replay | Data `custom-catalog`; replay `chunk-memory`, `mixed-custom-history` |

Per-skill `evals/evals.json` contains working cases; `evals/acceptance.json`
holds separately phrased acceptance cases. Tier 3 needs real execution before
either can be reported as passed. Static coverage is not scenario execution.
Historical tier outcomes are in [BUILD_LOG.md](BUILD_LOG.md); current implementation checks are in [BUILD-LOG.md](BUILD-LOG.md).
The actor-only quickstart demonstrates inbound quote/custom dispatch with zero
orders. The combined default binary injects custom input separately and trades
on a quote; it does not execute the entire C1 chain. The separate
[native C1 integration test](examples/quickstart/tests/observation_chain.rs)
feeds only quotes, publishes observations from an actor, and checks the exact
Strategy callback sequence and causal times with zero orders/exposure.
Its current execution receipt is in [BUILD-LOG.md](BUILD-LOG.md).
History/live cutover, residual shutdown and connected-runtime cases also need
their own native/provider qualification beyond these reasoning cases.

Out of scope: new exchange adapters, new persistence implementations, replacing
the matching/risk engines, arbitrary external bus transports, infrastructure
platform provisioning and live financial qualification. These are not silently
claimed by mapping the corresponding core component.

## Added implementation coverage (2026-09-11)

| Concern | Guide and runnable evidence |
| --- | --- |
| Configuration across instruments/venues | [Typed config](references/configuration.md); FX and equity configs execute the same binary and assert native fills |
| Modular quoter/hedger and execution | [Composition](references/composition.md); implementation recipe, not a compiled multi-Strategy acceptance claim |
| Rust testing and performance | [Test ladder](references/rust-testing.md); exact source entry points, no claimed soak or benchmark run |
| Durable events and research replay | [Event replay](references/event-replay.md); state-only restore is separated from callback reruns |
| Databento/IB extension | [Adapter development](references/adapter-development.md); capability translation and fixture workflow |
| Executable native client wiring | [Live construction](examples/live-composition/README.md); build/dispose passes without starting clients |
