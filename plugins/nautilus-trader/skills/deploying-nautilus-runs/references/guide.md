# Run architecture and native integration

## Ownership and identity

One independent run owns one native node/kernel in one process/container.
For backtests, construct a fresh `BacktestNode` with one `BacktestRunConfig`;
register the actual components before running. NautilusTrader 0.64 rejects multiple run
configs per node because the kernel MessageBus is thread-local. Do not use a
web worker's shared node as a concurrent multi-tenant experiment service.
A direct `BacktestEngine` is appropriate for an existing in-memory harness,
but still isolate independent jobs by process rather than sharing its state.

For sandbox/live, use `LiveNode`; it rejects `Environment::Backtest`. The native
node owns startup, its event loop, reconciliation, cancellation and shutdown.
One node may compose multiple strategies when the application permits it;
one node per run does not mean creating a node for every callback or instrument.

Record run ID, process-attempt ID, native `instance_id`, trader/strategy IDs,
image digest, source/lockfile/config hashes, input catalog snapshot and output
prefix. The generator allocates fresh UUIDs for independent jobs. A restart of
an existing live run must deliberately recover its previous identity/Cache
namespace and exclude the previous owner; blindly allocating a new namespace
would bypass restoration. Cloud retry policies cannot establish exactly-once
orders. Default run plans disable automatic retry and admission is application-owned.

## Required feature graph

Use exact versions for a new 0.64 scaffold; existing projects retain their
qualified dependency resolution. These are Cargo dependencies, not global flags:

```toml
nautilus-live = { version = "=0.64.0", default-features = false, features = ["node", "streaming"] }
nautilus-backtest = { version = "=0.64.0", default-features = false, features = ["streaming"] }
nautilus-system = { version = "=0.64.0", default-features = false, features = ["streaming"] }
nautilus-persistence = { version = "=0.64.0", default-features = false, features = ["cloud"] }
nautilus-infrastructure = { version = "=0.64.0", default-features = false, features = ["postgres", "redis"] }
```

Select live or backtest according to the executable; both are listed to show
their separate gates. Persistence's `cloud` enables object_store AWS, Azure,
GCP and HTTP clients; it neither configures identity nor creates storage.
There is no persistence `streaming` feature: the live/backtest feature forwards
to `nautilus-system/streaming`. Do not enable Python to obtain these Rust APIs.

## Wire the plan, not just environment variables

The helper's JSON is an **application-owned run plan**, not a deserializable
`LiveNodeConfig` or a universal Nautilus CLI file. Adapt the existing binary's
CLI/config loader explicitly; no generated environment name magically enables
a framework feature or persists a run.

- Map `instance_id` to `LiveNodeBuilder::with_instance_id` or the backtest
  engine config; keep it consistent with the run record.
- For backtests, map `streaming` to `nautilus_system::config::StreamingConfig`
  through `BacktestEngineConfig.streaming`.
  The template uses positive flush latency, `replace_existing=false`, and no
  rotation; choose bounded rotation/flush values for the actual volume.
- NautilusTrader 0.64 **rejects** non-empty `LiveNodeConfig.streaming`, even with the Cargo
  feature enabled and a builder setter available. For sandbox/live capture, use
  native `FeatherWriter` with application-owned async integration; leave the
  unsupported config unset. The smoke's `subscribe_builtin_to_message_bus`
  helper calls `Handle::block_on` inside callbacks: it works in the synchronous
  probe, but panics when called inside the Tokio-driven live event loop.
  Do not copy that subscription helper into `LiveNode::run`.
  For live use, bridge the required typed bus families to a bounded queue and
  await native writer operations in a same-thread async task; define overflow
  and writer-failure handling without silent drops. Keep capture active through
  native shutdown/drain, then detach, drain the queue and await `close`.
  Qualify that integration in the actual runner before deployment. Do not patch
  out the guard or silently disable capture.
- Inject `RedisCacheConfig` through `with_cache_database_factory`, and use
  `CacheConfig` with `use_trader_prefix=true`, `use_instance_id=true`,
  `flush_on_start=false`. Factory connection happens at node startup, not merely
  because a Redis container exists. Qualify `load_state`/`save_state` separately.
- If PostgreSQL is selected as native Cache backing instead, inject
  `PostgresCacheConfig`. One Cache owns one adapter; do not implicitly dual-write
  PostgreSQL and Redis adapters. Its 0.64 factory ignores trader/instance IDs and
  `CacheConfig`: use a separate database per independent Cache namespace, not
  merely a new run UUID in shared tables. The application run registry may be
  shared separately. Redis message-bus streams are another role.
- Insert/update the application PostgreSQL run record with parameterized SQL.
  The supplied `run_control.runs` table is not upstream Nautilus's domain schema.

## Completion and failure

Use planned -> running -> completed/failed/incomplete transitions. Mark completion
only after the native run succeeds, shutdown finishes, required artifact writes
are observed and readback passes. Store the actual kernel stream URI, manifest,
counts, checksums and any residual exposure. Preserve an incomplete prefix after
crashes or storage failure; do not promote partial files to a successful dataset.

Handle termination through the native lifecycle and allow a bounded drain/grace
period before container termination. `kernel.flush_streaming()` handles a
  configured kernel writer; an explicitly attached live writer needs its own
unsubscribe/flush/close path. **Do not call Redis `CacheDatabaseAdapter::flush()` to drain writes**:
the 0.64 adapter delegates it to `flushdb_sync`, a destructive database flush.
Normal node shutdown and adapter close are different operations. Test abrupt
termination/recovery only in an authorized disposable environment.

Keep broker account ownership independent from job identity. Multiple valid run
UUIDs are not permission for multiple live writers to the same account. For live
restart, reconcile reports and unresolved intent before enabling new orders.
