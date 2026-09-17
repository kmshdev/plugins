# Storage contracts

## Minimum composition

| Role | Mechanism | Does not establish |
| --- | --- | --- |
| Run registry/control metadata | Application-owned PostgreSQL `run_control` schema | Automatic capture of every Nautilus event |
| Runtime Cache backing | `RedisCacheConfig` / native adapter; optionally PostgreSQL instead | Immutable research inputs or an audit log |
| Captured native data/events | Backtest kernel streaming or explicit live `FeatherWriter` | Automatic Parquet output or custom-data coverage |
| Research catalog | `ParquetDataCatalog`, DataFusion queries | Strategy callback replay or broker recovery |
| Durable ordered event log | Separately configured native event store | Every market/custom-data codec or a profitable rerun |

The minimum scaffold provisions PostgreSQL and Redis separately. Choose and
document their roles rather than calling everything “session persistence.”

## PostgreSQL and the Nautilus CLI

The `nautilus-cli` package produces the executable **`nautilus`**. Its database
commands include `nautilus database init --schema PATH` and `database drop`.
The SQL files actually live in upstream `schema/sql/`: `types.sql`, `tables.sql`,
`functions.sql`, and `partitions.sql`. Installing the CLI is not proof those
files are present. Stage the matching files from the pinned source revision,
retain their licensing/provenance, and pass an explicit `--schema` or `SCHEMA_DIR`.
Do not rely on discovery of a directory named `nautilus_trader` on the host.

For an authorized, pre-created disposable database, the command shape is:

```sh
nautilus database init --schema "$SCHEMA_DIR"
```

Resolve host/port/database/username/password through the documented
`POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DATABASE`, `POSTGRES_USERNAME`, and
`POSTGRES_PASSWORD` environment inputs. Do not print them or pass secret values
in process arguments. Reject missing production configuration instead of falling
back to upstream's development credentials.

Initialization creates/changes roles, database/schema ownership and grants and
executes schema files. It is an **administrative migration**, not a readiness
probe, not automatic database creation, and not a versioned incremental migration
runner. Use an approved migration job with appropriate privileges; managed cloud
PostgreSQL may not allow the same ownership operations. Do not run it at every
strategy startup. Never use `database drop` as a retry/cleanup mechanism.

`assets/deployment/run-schema.sql` only defines the application's run registry;
it does not replace or impersonate the upstream schema. Keep schema roles,
migration credentials and normal runner credentials separate.

## Feather capture and Parquet conversion

For supported kernel configuration (including backtests), native `streaming` creates a
`FeatherWriter` under `catalog_path/<environment>/<instance_id>`, and subscribes
the supported built-in families. Persist the actual URI reported by the kernel.
The kernel does not automatically capture arbitrary custom payloads; those need
the appropriate codec/subscription path and a coverage test.
The 0.64 live config rejects automatic streaming: use the explicit native writer
and async lifecycle integration in [run architecture](guide.md) for live capture;
the built-in synchronous subscription helper is not safe in Tokio callbacks.

Use the same base catalog to convert supported completed stream data:

```rust
catalog.convert_stream_to_data(
    &instance_id.to_string(),
    "quotes",
    Some("backtest"),
    None,
    false,
)?;
```

Use the actual environment directory and supported class name. Keep
`use_ts_event_for_ts_init=false` to preserve availability chronology. The converter
can return success for empty/missing or excluded families: verify output files,
decoded row count, identities and timestamps. Conversion is not a universal
archive of account/order/custom events, nor does it execute strategies.

`ParquetDataCatalog::from_uri(uri, storage_options, batch_size, compression,
max_row_group_size)` handles catalog storage. `write_to_parquet` requires ordered,
identity-homogeneous input; split by metadata rather than relabeling records.
`query::<T>` uses DataFusion and registers remote object stores. Direct use of
`DataBackendSession` needs `register_object_store_from_uri` for remote sources.
Neither a query chunk size nor a streaming feature proves bounded total memory.

## Object stores and credentials

| Backend | URI shape | Qualification |
| --- | --- | --- |
| Local volume | Absolute filesystem path | Persistent mount, capacity and restart/readback |
| S3 | `s3://bucket/prefix` | Region/endpoint and scoped read/write/list permissions |
| Azure Blob / ADLS | `az://container/prefix`, `abfs://container@account.dfs.core.windows.net/prefix` | Explicit account/options for `az`; account in ABFS address; qualify identity |
| GCS | `gs://bucket/prefix` or `gcs://bucket/prefix` | Workload/service-account credentials and object permissions |
| HTTP(S) | `https://host/path` | Primarily input/read access; do not assume writable durable storage or listing |

The `cloud` feature enables clients, not all operations on every endpoint. Do not
promise arbitrary HTTP PUT/WebDAV durability. The plan helper rejects HTTP output
roots while allowing HTTP input catalogs. Azure's container@account URI syntax
is a storage address, not permission to embed credentials.

Prefer workload identity or runtime secret injection supported by the selected
object_store backend; do not place keys, SAS query strings or signed URLs in run
manifests, images or CI logs. The kernel constructs its streamer with no explicit
storage-options map, so qualify its environment/identity resolution independently
from an explicitly configured catalog client. URI construction alone proves no
authentication or write capability. In particular, 0.64 builds Azure with
`MicrosoftAzureBuilder::new()`, not `from_env()`. An `az` URI requires explicit
`account_name` storage options; merely exporting Azure account variables does
not supply them. The helper rejects `az` output for backtest kernel streaming,
which has no options map. Use qualified ABFS addressing or local capture followed
by explicitly configured Azure publication. The live async writer/catalog can
receive runtime-resolved storage options; never store credentials in the plan.

The helper preserves local paths as absolute native paths (including spaces,
percent signs and Unicode), decoding a supplied file URI once. Do not re-encode
them before passing them to native config: 0.64's Unix file-URI conversion strips
the scheme without URL decoding, which would otherwise select a different path.

Use a unique output prefix for independent runs and separate read-only input
catalogs. Disable replacement/deletion by default. For cloud acceptance, use an
authorized disposable prefix: write, flush/close, read from an independent reader,
assert rows/checksums, and record credentials/permissions limitations without
recording credential values. Do not delete unrelated run prefixes.
