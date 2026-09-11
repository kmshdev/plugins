# Source-qualified Rust 0.63.0 evidence

Research date: 2026-09-11. These original summaries use official documentation
first, then connected declarations, callers, reducers and tests in a 0.63.0
source snapshot. Source coordinates are optional audit evidence, not paths the
skill must open. No source checkout is required to use this skill.

The snapshot declares Rust 1.98.0, edition 2024. Its upstream commit is unknown;
the [local hash manifest](source-manifest.json) identifies cited files, not a
whole release or proof of byte identity with published crates.

Read [Rust concepts](https://nautilustrader.io/docs/latest/concepts/rust/),
[actor how-to](https://nautilustrader.io/docs/latest/how_to/write_rust_actor/),
[strategy how-to](https://nautilustrader.io/docs/latest/how_to/write_rust_strategy/),
[message bus](https://nautilustrader.io/docs/latest/concepts/message_bus/),
[data](https://nautilustrader.io/docs/latest/concepts/data/),
[backtesting](https://nautilustrader.io/docs/latest/concepts/backtesting/), and
[Rust live](https://nautilustrader.io/docs/latest/how_to/run_rust_live_trading/)
only as relevant. Moving docs can show 0.62 or Python signatures: prefer the
compiler-visible 0.63.0 declaration. The snapshot's fixture feature is `stubs`,
not the moving docs' `test-support`.

| ID | Snapshot coordinates and connected symbols |
| --- | --- |
| V1 | `Cargo.toml:50-100`: workspace version/MSRV/crates; `crates/model/Cargo.toml:23-37`, `crates/common/Cargo.toml:23-79`, `crates/backtest/Cargo.toml:23-76`, `crates/live/Cargo.toml:23-36`: feature surfaces |
| A1 | `crates/common/src/actor/data_actor.rs:119-280,733-855,976-1040,1270-1435,2547-2580,2854-3039,3800-4089,5024-5060`: config, facade/native, dispatch, requests, registration, publication |
| A2 | `crates/common/src/actor/registry.rs:16-99,171-230`: actor guard and aliasing/thread limitation; `crates/common/src/component.rs:117-226,480-563`: guarded component lifecycle |
| A3 | `crates/common/src/msgbus/api.rs:948-977,1303-1328,1373-1402`: synchronous publication and one-shot response handling; `crates/common/src/runner.rs:609-640`: buffered backtest commands |
| A4 | `crates/common/src/clock.rs:94-237,457-590,889-979,1337-1403`: facade timer signatures, TestClock advance/match/execute |
| A5 | `crates/common/src/actor/tests.rs:509-527,1533-1580,3328-3397`: registration, custom delivery, historical scalar/vector/empty coverage |
| D1 | `crates/model/src/data/custom.rs:285-372,386-525`: trait, constructor, JSON envelope; `crates/model/src/data/mod.rs:519-557,714-738,946-950`: topic/metadata/equality |
| D2 | `crates/model/src/data/registry.rs:33-245`: process-wide registration, strict/ensure behavior and decoding |
| D3 | `crates/persistence/macros/src/custom.rs:801-832,896-941,1131-1176,1427-1495`: generated schema/constructor and no_arrow |
| D4 | `crates/serialization/src/arrow/custom.rs:59-112,145-188,204-251`: Arrow registration, first-row DataType restoration |
| B1 | `crates/backtest/src/engine.rs:420-483,650-895`, `crates/backtest/src/data_iterator.rs:29-145`, `crates/backtest/src/data_client.rs:292-321`: validation, replay order, historical no-ops |
| M2 | `crates/common/src/actor/indicators.rs:28-92,128-178`, `crates/indicators/src/average/ema.rs:51-139`: registration/readiness and EMA input contracts |
| Q1 | `crates/model/src/instruments/currency_pair.rs:113-160,262-330`: checked instrument construction used by the original quickstart |
| CF1 | `crates/trading/src/examples/strategies/grid_mm/config.rs:35-72`, `crates/trading/src/examples/strategies/composite_market_maker/config.rs:35-84`: typed parameters and separate signal/execution instruments |
| Q2 | `crates/model/src/instruments/equity.rs:104-162,215-280`: checked equity construction and fluent builder |
| CP1 | `crates/trading/src/examples/strategies/composite_market_maker/config.rs:35-84`, `crates/model/src/orders/list.rs:35-150`: composition configuration and representative order-list instrument |
| T1 | `crates/execution/src/reconciliation/proptests.rs:1-180`: generated report invariants |
| T2 | `crates/network/tests/common/turmoil.rs:20-110`, `crates/network/tests/turmoil_websocket.rs:1-130`, `crates/network/Cargo.toml:20-38`: bounded seed loop and injected network tests |
| T3 | `crates/common/src/live/dst.rs:16-180`, `crates/common/Cargo.toml:30-66`, `crates/live/tests/stress.rs:1-100`: madsim facade feature and native stress harness boundaries |
| T4 | `crates/common/Cargo.toml:164-173`, `crates/execution/Cargo.toml:80-87`, `crates/serialization/Cargo.toml:94-104`: registered native benchmark targets |
| RP1 | `crates/system/src/event_store.rs:249-299`, `crates/system/src/kernel.rs:586-641,687-724`: writer settings and state-only startup |
| RP2 | `crates/event_store/src/replay.rs:16-22,815-974`: sealed reconstruction, forensics and catalog replay input helpers |
| RP3 | `crates/event_store/src/replay/catalog.rs:40-108`: catalog query type coverage |
| AX1 | `crates/common/src/clients/data.rs:150-222`, `crates/adapters/databento/src/data.rs:1124-1164`: default methods and implemented node request surface |

Source tests were inspected, not all executed. An offline quickstart demonstrates
local composition only; it cannot prove provider entitlement, broker state,
profitability, production recovery or live protective-order behavior.
