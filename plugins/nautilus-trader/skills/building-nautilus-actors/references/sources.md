# Source-qualified Rust 0.64.0 evidence

Research date: 2026-09-17. These original summaries connect
official documentation with declarations, callers, reducers and tests at upstream
revision `1b0a49d2792a9432a3aca3fcb617ce7a630d905e`. Source coordinates are audit evidence, not paths the
skill must open. No source checkout is required to use this skill.

The release declares Rust 1.98.1, edition 2024;
the [local hash manifest](source-manifest.json) identifies cited files, not a
whole release or proof of byte identity with published crates.

Read [Rust concepts](https://nautilustrader.io/docs/latest/concepts/rust/),
[actor how-to](https://nautilustrader.io/docs/latest/how_to/write_rust_actor/),
[strategy how-to](https://nautilustrader.io/docs/latest/how_to/write_rust_strategy/),
[message bus](https://nautilustrader.io/docs/latest/concepts/message_bus/),
[data](https://nautilustrader.io/docs/latest/concepts/data/),
[backtesting](https://nautilustrader.io/docs/latest/concepts/backtesting/), and
[Rust live](https://nautilustrader.io/docs/latest/how_to/run_rust_live_trading/)
only as relevant. Moving docs can differ from the application: its locked
compiler-visible declarations govern APIs. The published model fixture feature
is `test-support`; enable it only when fixtures require it.

| ID | Snapshot coordinates and connected symbols |
| --- | --- |
| V1 | `Cargo.toml:50-114`: workspace version/MSRV/crates; `crates/model/Cargo.toml:21-36`, `crates/common/Cargo.toml:21-77`, `crates/backtest/Cargo.toml:21-75`, `crates/live/Cargo.toml:21-34`: feature surfaces |
| A1 | `crates/common/src/actor/data_actor.rs:124-288,747-868,989-1053,1283-1448,2579-2612,2886-3078,4107-4421,5387-5423`: config, facade/native, dispatch, requests, registration, publication |
| A2 | `crates/common/src/actor/registry.rs:16-99,182-241`: actor guard and aliasing/thread limitation; `crates/common/src/component.rs:117-234,486-569`: guarded component lifecycle |
| A3 | `crates/common/src/msgbus/api.rs:939-959,1285-1310,1344-1373`: synchronous publication and one-shot response handling; `crates/common/src/runner.rs:667-706`: buffered backtest commands |
| A4 | `crates/common/src/clock.rs:95-249,442-582,922-1009,1367-1433`: facade timer signatures, TestClock advance/match/execute |
| A5 | `crates/common/src/actor/tests.rs:617-635,2687-2782,4883-4952`: registration, custom delivery, historical scalar/vector/empty coverage |
| D1 | `crates/model/src/data/custom.rs:282-369,383-522`: trait, constructor, JSON envelope; `crates/model/src/data/mod.rs:533-571,728-752,959-963`: topic/metadata/equality |
| D2 | `crates/model/src/data/registry.rs:33-245`: process-wide registration, strict/ensure behavior and decoding |
| D3 | `crates/persistence/macros/src/custom.rs:801-832,896-941,1131-1176,1427-1495`: generated schema/constructor and no_arrow |
| D4 | `crates/serialization/src/arrow/custom.rs:70-123,149-241,254-287`: Arrow registration, first-row DataType restoration |
| B1 | `crates/backtest/src/engine.rs:398-501,667-928`, `crates/backtest/src/data_iterator.rs:31-219`, `crates/backtest/src/data_client.rs:286-290`: validation, replay order, historical no-ops |
| M2 | `crates/common/src/actor/indicators.rs:28-92,128-178`, `crates/indicators/src/average/ema.rs:51-139`: registration/readiness and EMA input contracts |
| Q1 | `crates/model/src/instruments/currency_pair.rs:103-151,190-258`: checked instrument construction used by the original quickstart |
| CF1 | `crates/trading/src/examples/strategies/grid_mm/config.rs:35-72`, `crates/trading/src/examples/strategies/composite_market_maker/config.rs:35-84`: typed parameters and separate signal/execution instruments |
| Q2 | `crates/model/src/instruments/equity.rs:91-150,150-215`: checked equity construction and fluent builder |
| CP1 | `crates/trading/src/examples/strategies/composite_market_maker/config.rs:35-84`, `crates/model/src/orders/list.rs:35-150`: composition configuration and representative order-list instrument |
| T1 | `crates/execution/src/reconciliation/proptests.rs:1-177`: generated report invariants |
| T2 | `crates/network/tests/integration/common/turmoil.rs:20-110`, `crates/network/tests/integration/turmoil_websocket.rs:1-129`, `crates/network/Cargo.toml:18-36`: bounded seed loop and injected network tests |
| T3 | `crates/common/src/live/dst.rs:16-180`, `crates/common/Cargo.toml:28-64`, `crates/live/tests/integration/stress.rs:1-105`: madsim facade feature and native stress harness boundaries |
| T4 | `crates/common/Cargo.toml:166-175`, `crates/execution/Cargo.toml:83-89`, `crates/serialization/Cargo.toml:96-106`: registered native benchmark targets |
| RP1 | `crates/system/src/event_store.rs:249-299`, `crates/system/src/kernel.rs:682-737,783-820`: writer settings and state-only startup |
| RP2 | `crates/event_store/src/replay.rs:16-22,815-974`: sealed reconstruction, forensics and catalog replay input helpers |
| RP3 | `crates/event_store/src/replay/catalog.rs:40-108`: catalog query type coverage |
| AX1 | `crates/common/src/clients/data.rs:150-222`, `crates/adapters/databento/src/data.rs:1120-1160`: default methods and implemented node request surface |

Source tests were inspected, not all executed. An offline quickstart demonstrates
local composition only; it cannot prove provider entitlement, broker state,
profitability, production recovery or live protective-order behavior.
