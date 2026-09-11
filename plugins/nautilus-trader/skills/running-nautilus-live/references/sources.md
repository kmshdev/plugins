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
| S3 | `crates/trading/src/strategy/mod.rs:113-365,371-499,632-969,1140-1475,1600-1646`: command facade, cache/publication/routing, hooks and stop |
| E1 | `crates/execution/src/engine/mod.rs:173-201,1940-2013,2105-2195,2796-2834,3086-3193,3630-3728,3976-4015`: queues/client denial, fill/cache/event order and OMS |
| E2 | `crates/common/src/factories/order.rs:1122-1136,1227-1745`: bracket legs, supported types, defaults and relationships |
| E3 | `crates/execution/src/order_emulator/emulator.rs:506-590,1340-1417,1526-1552`: local hold/release routes; `crates/execution/src/order_manager/manager.rs:181-200`: manager selection predicate |
| E4 | `crates/model/src/orders/mod.rs:214-294,819-995,1231-1331,3155-3210`: pending states, fills, corrections, rejection restoration |
| E5 | `crates/execution/src/matching_engine/config.rs:40-79`, `crates/execution/src/matching_engine/mod.rs:2766-2790`, `crates/execution/tests/matching_engine.rs:924-1010`: contingent activation and simulated path |
| E6 | `crates/trading/src/algorithm/mod.rs:40-179,431-489,689-842,1258-1298,3142-3295`, `crates/trading/src/algorithm/twap.rs:55-76,116-259,300-445`: spawn accounting and TWAP scheduling |
| R1 | `crates/risk/src/engine/config.rs:47-58`, `crates/risk/src/engine/mod.rs:144-179,580-651,931-955,1021-1101,1506-1540,1973-2041,2228-2240`: gates, missing-account behavior and event processing |
| R2 | `crates/risk/src/sizing.rs:16-145`: fixed-risk arithmetic and limits; `crates/model/src/instruments/mod.rs:305-534`: precision versus normalization |
| R3 | `crates/portfolio/src/portfolio.rs:347-371,1566-1572,3704-3756`, `crates/system/src/trader.rs:460-484`: position accounting and subscription priority |
| R4 | `crates/common/src/cache/mod.rs:396-417,2020-2030`: owned order/account reads; `crates/model/src/types/fixed.rs:83-91`: precision modes |
| B1 | `crates/backtest/src/engine.rs:420-483,650-895`, `crates/backtest/src/data_iterator.rs:29-145`, `crates/backtest/src/data_client.rs:292-321`: validation, replay order, historical no-ops |
| B2 | `crates/backtest/src/node.rs:145-183,327-339,420-610`: one run, streaming/materialization and aligned chunks; `crates/backtest/src/result.rs:177-234`: canonical result methods |
| M3 | `crates/persistence/src/backend/catalog.rs:216-233,582-632,1652-1665,1979-2046`, `crates/persistence/src/backend/feather.rs:776-834,867-963,1409-1485`: catalog queries, writer behavior and gated custom test |
| L1 | `crates/live/src/node/builder.rs:444-537,557-705`, `crates/live/src/node/config.rs:843-851,1296-1313`: client construction/routing and recording rejection |
| L2 | `crates/live/src/node/mod.rs:797-935,1865-1921,2281-2333,5761-5885`: reconciliation, cache startup, grace-period/state-persistence tests |
| L3 | `crates/system/src/kernel.rs:586-641,687-724,779-812`: startup, cache-only event replay, trader state, final stop |
| L4 | `crates/adapters/interactive_brokers/src/factories.rs:84-111,143-233,329-348`, `crates/adapters/interactive_brokers/examples/node_exec_tester.rs:91-150`: account normalization and native factories |
| AD1 | `crates/adapters/databento/src/data.rs:73-156,212-243,277-321,423-431,502-727,1006-1108,1441-1466`, `crates/adapters/databento/src/factories.rs:163-235`: config, node subscription/history routing and readiness |
| AD2 | `crates/adapters/databento/src/loader.rs:989-1010`, `crates/adapters/databento/src/symbology.rs:24-177`, `crates/adapters/databento/src/live.rs:178-223,396-436,468-539,635-653,716-731,776-820,1290-1311`: datasets, symbology, reconnect and precision |
| AD3 | `crates/adapters/databento/src/historical.rs:53-122,198-225,759-831`, `crates/adapters/databento/src/decode/market_data.rs:36-60,530-539,711-739`: historical request shape, bar step and timestamps |
| AD4 | `crates/adapters/interactive_brokers/src/config.rs:83-260`, `crates/adapters/interactive_brokers/src/providers/instruments.rs:304-332,946-1003,1484-1501`: config and contract qualification |
| AD5 | `crates/adapters/interactive_brokers/src/historical/client.rs:123-146,200-254,413-440,463-488`, `crates/adapters/interactive_brokers/src/data/core.rs:1246-1358`, `crates/adapters/interactive_brokers/src/data/core_streams.rs:191-214,550-614,1031-1046,1348-1366`, `crates/adapters/interactive_brokers/src/data/convert.rs:185-257`: historical bounds, bar subscription/recovery and time semantics |
| AD6 | `crates/common/src/clients/data.rs:219-222`, `crates/common/src/actor/data_actor.rs:1762-1778`, `crates/data/src/engine/mod.rs:4330-4344,4462-4507`: unsupported external bars versus native internal aggregation |
| AR1 | `crates/adapters/databento/Cargo.toml:23-49`, `crates/adapters/interactive_brokers/Cargo.toml:23-52`, `crates/adapters/databento/examples/node_data_tester.rs:28-87`: native features and construction |
| AR2 | `crates/adapters/interactive_brokers/src/execution/core.rs:610-619,692-742,796-854,963-1121,1225-1303`, `crates/adapters/interactive_brokers/src/execution/core_orders.rs:117-122`: report limitations, initialization warnings and account-filter discrepancy |
| AR3 | `crates/adapters/interactive_brokers/src/common/shared_client.rs:103-183`, `crates/live/src/node/mod.rs:340-455,910-918`: shared connection and startup/reconciliation limits |
| AR4 | `crates/adapters/sandbox/src/lib.rs:16-19`, `crates/adapters/interactive_brokers/examples/node_exec_tester.rs:178-209`: local sandbox versus external execution and non-harmless tester |
| SB1 | `crates/adapters/sandbox/Cargo.toml:23-47`, `crates/adapters/sandbox/src/config.rs:35-179`, `crates/adapters/sandbox/src/factory.rs:24-105`: native sandbox features, config and simulated-factory trait |
| SB2 | `crates/adapters/sandbox/examples/databento_cme.rs:28-157`, `crates/live/src/node/builder.rs:519-547`, `crates/adapters/sandbox/src/execution.rs:213-280,528-648,1002-1017`: Databento composition, native simulated registration and venue-scoped delivery/account initialization |
| CF1 | `crates/trading/src/examples/strategies/grid_mm/config.rs:35-72`, `crates/trading/src/examples/strategies/composite_market_maker/config.rs:35-84`: typed parameters and separate signal/execution instruments |
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
