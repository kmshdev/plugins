# Deployment source evidence

Qualified against Rust 0.64.0 at
`1b0a49d2792a9432a3aca3fcb617ce7a630d905e`, with Rust 1.98.1.
[Hashes](source-manifest.json) identify reviewed source files, not a requirement
to open a hidden checkout or a proof of cloud execution.

Official entry points: [Parquet/DataFusion backend](https://nautechsystems.github.io/nautilus_docs/rust-api-latest/nautilus_persistence/backend/index.html),
[live node](https://nautechsystems.github.io/nautilus_docs/rust-api-latest/nautilus_live/index.html),
[infrastructure](https://nautechsystems.github.io/nautilus_docs/rust-api-latest/nautilus_infrastructure/index.html).
Moving documentation is qualified by these pinned declarations and callers.

| ID | Snapshot coordinates and connected symbols |
| --- | --- |
| V1 | `Cargo.toml:50-114`: workspace version/MSRV/crates; `crates/model/Cargo.toml:21-36`, `crates/common/Cargo.toml:21-77`, `crates/backtest/Cargo.toml:21-75`, `crates/live/Cargo.toml:21-34`: feature surfaces |
| RP1 | `crates/system/src/event_store.rs:249-299`, `crates/system/src/kernel.rs:682-737,783-820`: writer settings and state-only startup |
| RP2 | `crates/event_store/src/replay.rs:16-22,815-974`: sealed reconstruction, forensics and catalog replay input helpers |
| RP3 | `crates/event_store/src/replay/catalog.rs:40-108`: catalog query type coverage |
| DP1 | `crates/live/Cargo.toml:29-105`, `crates/backtest/Cargo.toml:28-58`, `crates/system/Cargo.toml:28-47`, `crates/persistence/Cargo.toml:28-56`, `crates/infrastructure/Cargo.toml:24-45`: node/streaming, cloud and database feature boundaries |
| DP2 | `crates/system/src/config.rs:267-359`, `crates/system/src/kernel.rs:378-416,984-1045`, `crates/persistence/src/backend/feather.rs:280-338,1004-1258`: native Feather configuration, built-in subscriptions, flush and disposal |
| DP3 | `crates/persistence/src/backend/catalog.rs:306-342,580-627,1650-1698,1833-1864,3926-3971,4198-4248`, `crates/persistence/src/backend/session.rs:101-139,164-205`, `crates/persistence/src/parquet.rs:501-517,667-977`: Parquet/DataFusion, explicit stream conversion, object-store clients and HTTP limits |
| DP4 | `crates/common/src/cache/config.rs:37-80`, `crates/common/src/cache/database.rs:59-87`, `crates/infrastructure/src/redis/cache.rs:144-211,1307-1334`, `crates/infrastructure/src/sql/cache.rs:81-178`: Cache factory ownership, namespaces and destructive Redis flush semantics |
| DP5 | `crates/cli/Cargo.toml:24-53`, `crates/cli/src/opt.rs:26-73`, `crates/cli/src/database/postgres.rs:28-82`, `crates/infrastructure/src/sql/pg.rs:156-350`, `schema/sql/types.sql:1-30`, `schema/sql/tables.sql:1-393`, `schema/sql/functions.sql:1-50`, `schema/sql/partitions.sql:1-85`: CLI executable, explicit schema path, ownership/role mutations and upstream SQL files |
| DP6 | `crates/live/src/node/builder.rs:139-192,206-216,306-328,344-356,744-766`, `crates/live/src/node/mod.rs:491-574,2578-2588`, `crates/backtest/src/node.rs:137-181,311-318`: one run per node, Cache factory startup ownership and native shutdown |
| DP7 | `crates/live/src/node/config.rs:1278-1312`, `crates/live/src/node/mod.rs:990-1050`, `crates/persistence/src/backend/feather.rs:654-746,1004-1258,1770-1785`, `crates/common/src/msgbus/api.rs:1042-1049`: live config rejection, async callback restrictions, native writer subscription/close and quote publication |

Source tests were inspected, not all executed. An offline quickstart demonstrates
local composition only; it cannot prove provider entitlement, broker state,
profitability, production recovery or live protective-order behavior.
