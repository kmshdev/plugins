# Evidence ledger: 0.64.0

Research date: **2026-09-17**. References synthesize official documentation first,
then the connected Rust source paths below. They are not copied API pages.

## Provenance

The inspected upstream workspace declares version 0.64.0, edition 2024, MSRV 1.98.1,
at commit `1b0a49d2792a9432a3aca3fcb617ce7a630d905e` (Rust 0.64.0 release).
The published crates' `.cargo_vcs_info.json` records the same upstream revision.
The accompanying [manifest](../source-manifest.json) records SHA-256 of cited files.
Coordinates refer to that commit, not a required local checkout. Cargo.lock records
the separately resolved registry artifacts; a source hash is not a crate checksum.

The [example qualification](../evals/qualification.md) separately records
compilation against resolved registry packages. Passing it does not establish
byte identity between those packages and every source file below.
Upstream source navigation is available at the
[Nautilus repository](https://github.com/nautechsystems/nautilus_trader);
`develop` is navigation, not immutable evidence.

## Official documentation, read before implementation

| Family | Pages and knowledge used |
| --- | --- |
| Starting points | [Rust concepts](https://nautilustrader.io/docs/latest/concepts/rust/), [write an actor](https://nautilustrader.io/docs/latest/how_to/write_rust_actor/), [write a strategy](https://nautilustrader.io/docs/latest/how_to/write_rust_strategy/): facades, macros, lifecycle, capability boundaries |
| Actor/runtime | [Actors](https://nautilustrader.io/docs/latest/concepts/actors/), [message bus](https://nautilustrader.io/docs/latest/concepts/message_bus/), [Rust developer guide](https://nautilustrader.io/docs/latest/developer_guide/rust/): registry, threading, requests, lifecycle |
| Values/data | [Data](https://nautilustrader.io/docs/latest/concepts/data/), [custom data](https://nautilustrader.io/docs/latest/concepts/custom_data/): timestamps, aggregation, catalog and schemas |
| Trading | [Strategies](https://nautilustrader.io/docs/latest/concepts/strategies/), [orders](https://nautilustrader.io/docs/latest/concepts/orders/), [execution](https://nautilustrader.io/docs/latest/concepts/execution/): lifecycle and component roles |
| Contingencies | [Advanced orders](https://nautilustrader.io/docs/latest/concepts/orders/advanced/), [emulated orders](https://nautilustrader.io/docs/latest/concepts/orders/emulated/): vocabulary, qualified by source routing |
| Financial state | [Positions](https://nautilustrader.io/docs/latest/concepts/positions/), [portfolio](https://nautilustrader.io/docs/latest/concepts/portfolio/): OMS, fill-derived state and valuation |
| Replay how-to | [Run a Rust backtest](https://nautilustrader.io/docs/latest/how_to/run_rust_backtest/): engine/node composition |
| Simulation | [Backtesting index](https://nautilustrader.io/docs/latest/concepts/backtesting/), [bar execution](https://nautilustrader.io/docs/latest/concepts/backtesting/bar-execution/), [fill models](https://nautilustrader.io/docs/latest/concepts/backtesting/fill-models/): execution assumptions and evidence limits |
| Live how-to | [Run Rust live trading](https://nautilustrader.io/docs/latest/how_to/run_rust_live_trading/): factories, builder and loop; example reconciliation settings are not production policy |
| Tutorial discovery | [Tutorial index](https://nautilustrader.io/docs/latest/tutorials/): separate Rust-native examples from Python-only workflows |
| Rust actor tutorial | [Betfair book imbalance](https://nautilustrader.io/docs/latest/tutorials/backtest_book_imbalance_betfair/): L2 loading/actor analysis; status dropping limits replay claims |
| Rust signal tutorial | [Kraken Hurst/VPIN](https://nautilustrader.io/docs/latest/tutorials/hurst_vpin_kraken/): trades -> value bars -> regime/flow -> quote decisions; warm-up and precision |
| Rust multi-feed tutorial | [Lighter composite market making](https://nautilustrader.io/docs/latest/tutorials/lighter_rwa_composite_mm/): signal/execution separation; missing freshness/session guards are explicit limitations |

The requested conceptual searches for standalone `risk`, `data_catalog` and
`indicators` pages returned 404. Use the execution risk section, Data's catalog
section and indicator source instead. A guessed URL was not treated as evidence.
Python signatures in mixed-language concepts were not used as Rust declarations.

## Source anchors

Each row groups declarations with callers/reducers/tests, rather than inferring
behavior from a single config field. Line ranges are snapshot coordinates.

| ID | Source coordinates and relevant symbols |
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
| S1 | `crates/trading/src/macros.rs:18-112,157-202`: actor/strategy/algorithm wiring; `crates/trading/src/strategy/config.rs:49-201`: fields/defaults/validation |
| S2 | `crates/trading/src/strategy/core.rs:150-209,282-346,1133-1156`: identity, registration, manager construction, bracket example |
| S3 | `crates/trading/src/strategy/mod.rs:148-333,339-467,600-935,1106-1504,1625-1671`: command facade, cache/publication/routing, hooks and stop |
| S4 | `crates/trading/src/strategy/api.rs:78-131,160-228,258-472,496-606,700-940`: order constructors, bracket builder and portfolio facade |
| E1 | `crates/execution/src/engine/mod.rs:169-197,1912-2003,2201-2291,2888-2938,3189-3310,3832-3938,4221-4279`: queues/client denial, fill/cache/event order and OMS |
| E2 | `crates/common/src/factories/order.rs:1122-1136,1227-1743`: bracket legs, supported types, defaults and relationships |
| E3 | `crates/execution/src/order_emulator/emulator.rs:505-588,1338-1415,1524-1550`: local hold/release routes; `crates/execution/src/order_manager/manager.rs:183-208`: manager selection predicate |
| E4 | `crates/model/src/orders/mod.rs:201-285,802-995,1236-1338,3578-3712`: pending states, fills, corrections, rejection restoration |
| E5 | `crates/execution/src/matching_engine/config.rs:47-89`, `crates/execution/src/matching_engine/mod.rs:2937-2961`, `crates/execution/tests/integration/matching_engine.rs:920-1006`: contingent activation and simulated path |
| E6 | `crates/trading/src/algorithm/mod.rs:43-189,443-506,719-1084,1496-1554,3957-4110`, `crates/trading/src/algorithm/twap.rs:55-76,116-259,300-445`: spawn accounting and TWAP scheduling |
| R1 | `crates/risk/src/engine/config.rs:47-64`, `crates/risk/src/engine/mod.rs:147-182,597-771,1049-1078,1160-1239,1647-1682,2115-2182,2359-2371`: gates, missing-account behavior and event processing |
| R2 | `crates/risk/src/sizing.rs:16-145`: fixed-risk arithmetic and limits; `crates/model/src/instruments/mod.rs:309-537`: precision versus normalization |
| R3 | `crates/portfolio/src/portfolio.rs:348-372,1567-1573,3754-3806`, `crates/system/src/trader.rs:462-486`: position accounting and subscription priority |
| R4 | `crates/common/src/cache/mod.rs:406-427,2050-2060`: owned order/account reads; `crates/model/src/types/fixed.rs:83-91`: precision modes |
| B1 | `crates/backtest/src/engine.rs:398-501,667-928`, `crates/backtest/src/data_iterator.rs:31-219`, `crates/backtest/src/data_client.rs:286-290`: validation, replay order, historical no-ops |
| B2 | `crates/backtest/src/node.rs:143-181,309-321,402-594`: one run, streaming/materialization and aligned chunks; `crates/backtest/src/result.rs:177-234`: canonical result methods |
| B3 | `crates/backtest/tests/integration/backtest_engine.rs:1072-1145,4517-4556`: custom input and equal-time timer tests; `crates/backtest/tests/integration/backtest_node.rs:1527-1570`: equal-time chunk coverage |
| B4 | `crates/backtest/tests/integration/ema_cross.rs:63-126`, `crates/trading/src/examples/strategies/ema_cross/strategy.rs:55-149`: native replay and manual EMA ownership |
| M1 | `crates/data/src/engine/mod.rs:1814-1879,2548-2589,4901-5085`, `crates/data/src/engine/config.rs:35-78`: data variants, book batching and aggregation |
| M2 | `crates/common/src/actor/indicators.rs:28-92,128-178`, `crates/indicators/src/average/ema.rs:51-139`: registration/readiness and EMA input contracts |
| M3 | `crates/persistence/src/backend/catalog.rs:218-235,580-630,1650-1663,1977-2044`, `crates/persistence/src/backend/feather.rs:903-959,992-1259,1823-1899`: catalog queries, writer behavior and gated custom test |
| L1 | `crates/live/src/node/builder.rs:444-548,568-723`, `crates/live/src/node/config.rs:848-856,1291-1308`: client construction/routing and recording rejection |
| L2 | `crates/live/src/node/mod.rs:848-986,1921-1977,2361-2415,6288-6415`: reconciliation, cache startup, grace-period/state-persistence tests |
| L3 | `crates/system/src/kernel.rs:682-737,783-820,875-908`: startup, cache-only event replay, trader state, final stop |
| L4 | `crates/adapters/interactive_brokers/src/factories.rs:84-111,143-235,332-351`, `crates/adapters/interactive_brokers/examples/node_exec_tester.rs:96-155`: account normalization and native factories |
| Q1 | `crates/model/src/instruments/currency_pair.rs:103-151,190-258`: checked instrument construction used by the original quickstart |
| AD1 | `crates/adapters/databento/src/data.rs:75-143,188-219,256-300,408-416,494-723,1002-1104,1437-1462`, `crates/adapters/databento/src/factories.rs:168-240`: config, node subscription/history routing and readiness |
| AD2 | `crates/adapters/databento/src/loader.rs:989-1010`, `crates/adapters/databento/src/symbology.rs:24-177`, `crates/adapters/databento/src/live.rs:179-224,397-437,469-540,636-654,717-732,777-821,1293-1314`: datasets, symbology, reconnect and precision |
| AD3 | `crates/adapters/databento/src/historical.rs:53-122,198-225,759-831`, `crates/adapters/databento/src/decode/market_data.rs:36-62,530-539,711-739`: historical request shape, bar step and timestamps |
| AD4 | `crates/adapters/interactive_brokers/src/config.rs:88-265`, `crates/adapters/interactive_brokers/src/providers/instruments.rs:304-332,946-1003,1484-1501`: config and contract qualification |
| AD5 | `crates/adapters/interactive_brokers/src/historical/client.rs:123-146,200-254,413-440,463-488`, `crates/adapters/interactive_brokers/src/data/core.rs:1321-1435`, `crates/adapters/interactive_brokers/src/data/core_streams.rs:194-217,546-610,1027-1042,1345-1363`, `crates/adapters/interactive_brokers/src/data/convert.rs:185-257`: historical bounds, bar subscription/recovery and time semantics |
| AD6 | `crates/common/src/clients/data.rs:219-222`, `crates/common/src/actor/data_actor.rs:1790-1806`, `crates/data/src/engine/mod.rs:4834-4848,4980-5031`: unsupported external bars versus native internal aggregation |
| AR1 | `crates/adapters/databento/Cargo.toml:21-47`, `crates/adapters/interactive_brokers/Cargo.toml:21-50`, `crates/adapters/databento/examples/node_data_tester.rs:28-87`: native features and construction |
| AR2 | `crates/adapters/interactive_brokers/src/execution/core.rs:638-647,720-774,837-895,1004-1162,1266-1344`, `crates/adapters/interactive_brokers/src/execution/core_orders.rs:117-122`: report limitations, initialization warnings and account-filter discrepancy |
| AR3 | `crates/adapters/interactive_brokers/src/common/shared_client.rs:103-180`, `crates/live/src/node/mod.rs:386-502,961-969`: shared connection and startup/reconciliation limits |
| AR4 | `crates/adapters/sandbox/src/lib.rs:16-19`, `crates/adapters/interactive_brokers/examples/node_exec_tester.rs:183-215`: local sandbox versus external execution and non-harmless tester |
| SB1 | `crates/adapters/sandbox/Cargo.toml:21-45`, `crates/adapters/sandbox/src/config.rs:35-188`, `crates/adapters/sandbox/src/factory.rs:24-105`: native sandbox features, config and simulated-factory trait |
| SB2 | `crates/adapters/sandbox/examples/databento_cme.rs:28-164`, `crates/live/src/node/builder.rs:530-558`, `crates/adapters/sandbox/src/execution.rs:959-1023,1192-1273,1344-1349`: Databento composition, native simulated registration and venue-scoped delivery/account initialization |

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

## Material documentation/source differences

| Observation | Resolution in this bundle |
| --- | --- |
| Moving Rust dependency snippets can differ from the requested release | Examples pin 0.64.0; the published model fixture feature is test-support; application lockfiles govern APIs |
| Strategy how-to simplifies tag/config construction | Checked builder plus checked core; no assumed config revalidation |
| Advanced-order prose promises managed non-local contingencies | Source manager selection/actions qualify that promise |
| Emulation prose promises two risk gates | Trace command routes rather than treating risk event notification as validation |
| Some tutorial prose excludes instrument status | Snapshot DataEngine handles it; dropping records still limits the tutorial |
| Live how-to disables reconciliation for simplicity | Not promoted to a production default |
| Catalog/recording fields suggest broad streaming | Explicit node memory and live recording limits |

Source tests in this ledger were **inspected**, not all executed. The local
quickstart and bundle checks are recorded separately. No broker/provider path,
performance claim, no-Python Arrow round trip, or exhaustive adapter matrix was
qualified by this research.
