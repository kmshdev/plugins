---
name: deploying-nautilus-runs
description: Scaffold persistent Nautilus Rust runs, CI/CD and cloud storage with PostgreSQL, Redis and Parquet. Use for run isolation and container delivery; not strategy rules or unrelated infrastructure.
metadata:
  author: kmshdev
  version: "0.64.0"
---

# Deploy persistent Nautilus runs

**Input:** target package, run mode, storage/compute platform and authorized scope.
**Output:** delivery files, native integration points, per-run identity/storage
and evidence distinguishing scaffolding from deployed behavior.

Bundled contracts target Rust 1.98.1+ and NautilusTrader 0.64.0. Preserve existing
application pins unless upgrading is requested. This skill packages an existing
runner; it does not invent trading rules or automatically operate infrastructure.
Rust 0.64 rejects `LiveNodeConfig.streaming`: live capture needs the explicit
async native writer integration below, not removal of the runtime guard.

## Workflow

1. Locate the requested package and distinguish a backtest job from an authorized
   sandbox/live service. Use [run architecture](references/guide.md) for one node
   per run, attempt/recovery identity, features and shutdown ownership.
2. Assign storage roles using [storage contracts](references/storage.md):
   PostgreSQL run metadata, a selected native Cache adapter, streamed Feather,
   and Parquet/DataFusion are not interchangeable persistence mechanisms.
3. Read [delivery](references/delivery.md) for the selected CI/container/cloud
   boundary. Generate only requested files with [the scaffold helper](scripts/scaffold.py)
   or adapt [the templates](assets/deployment/README.md). Generation performs no
   installation, migration, image push, job launch or provider connection.
4. Wire the generated application run plan into the real composition root.
   Enable native `streaming`, wire the mode-specific writer, and give each independent
   run its own process/node, instance ID and writable artifact prefix. Retain
   the native order owner, risk gates, and exclusive live-account admission.
5. Validate the changed boundary: build/features and template checks first;
   then an authorized bounded run, storage readback and failure/shutdown evidence.
   Cloud writes, migrations, image publication and trading each need their own
   authorization. Stop at missing access rather than substituting synthetic success.

For local API evidence, run [the storage smoke](assets/storage-smoke/README.md).
For provenance use [source evidence](references/sources.md); for native-vs-custom
choices use [version and integration](references/version-and-integration.md).
Load [event replay](references/event-replay.md) only for capture/recovery work.

## Examples

- “Package my runner for repeatable cloud backtests”: scaffold CI and an OCI
  image, then allocate independent run plans; do not launch paid jobs.
- “Persist every run on S3”: qualify writable object storage, enable Feather
  capture, explicitly convert supported market data to Parquet and verify rows.

Finish with paths, commands executed, storage coverage and remaining integration
or approval requirements. Neither generated YAML nor an `Ok` return proves durability.
