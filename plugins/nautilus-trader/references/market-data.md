# Data, indicators and historical storage

## Identity and availability

Market data must match a loaded instrument definition, venue, decimal precision
and event schema. Preserve `ts_event` (source event) and `ts_init` (availability).
Replay orders primarily by `ts_init`; choosing an earlier timestamp can introduce
look-ahead even if data are perfectly sorted.

Use an `EXTERNAL` `BarType` for already built bars. An `INTERNAL` type requests
aggregation. A useful shape is `AUD/USD.SIM-1-MINUTE-MID-INTERNAL`, provided
the corresponding instrument and quote input exist.

| Requested price source | Aggregator input |
| --- | --- |
| LAST | Trades |
| BID / ASK / MID | Quotes |
| Composite bar specification | Source bars |
| Imbalance/runs | Trades with usable aggressor information |

Select interval inclusion, timestamp-on-close, partial first bars, empty bars
and build delay explicitly. Build-delay configuration is in **microseconds**.
A completed OHLC bar cannot be available at its open merely because a provider
labels it with the interval start.

DataEngine updates Cache/publishes typed data. Order-book modes need actual
book inputs: quote replay is not an L2/L3 reconstruction. Preserve snapshot/Clear
boundaries, sequence conventions and `F_LAST`; missing end-of-batch flags can
prevent buffered deltas from reaching subscribers. Status/suspension information
must be replayed if the strategy relies on it.

## One indicator update owner

Manual ownership updates the indicator inside the data hook, as the bundled
framework EMA strategy does. Registered ownership shares `Rc<RefCell<T>>` with
the actor integration so the framework updates before hooks.
Do not register and manually update the same input.

Enable `nautilus-common/indicators` for registration. Registration is not
subscription. `indicators_initialized()` returns `Result<bool>` and is false
when no indicators are registered. Bar registration keys instrument plus
specification; it is not an aggregation-source discriminator.

EMA requires period > 0 and sufficient samples; quote handling can return an
error, while bar handling uses close. Do not assume every unsupported indicator
handler is a harmless no-op. Reset and historical warm-up must follow the same
update policy as live input.

For [historical requests](actors.md), use a bounded bootstrap state and a
defined merge/deduplication policy. The basic backtest client does not fetch
historical bars for you.

## Catalog write/read

Use `nautilus_persistence::backend::catalog::ParquetDataCatalog`.
Write instruments separately, then typed batches with ascending timestamps
and a single instrument/bar identity. Record source, time range, precision,
normalization policy and content identity alongside research inputs.

```text
ParquetDataCatalog::new(&Path, storage_options, batch_size, compression,
                       max_row_group_size) -> Self
write_to_parquet<T>(&[T], Option<UnixNanos>, Option<UnixNanos>,
                    Option<bool>) -> anyhow::Result<PathBuf>
query<T>(Option<Vec<String>>, Option<UnixNanos>, Option<UnixNanos>,
         Option<&str>, Option<Vec<String>>, bool) -> anyhow::Result<QueryResult>
```

The constructor can panic on creation failure; use the fallible `from_uri`
surface when failures need propagation. Cloud backends need the `cloud` feature.
Do not infer custom schemas or precision from a file extension.

## Catalog node and memory

`nautilus-backtest/streaming` exposes `BacktestNode`. Build
`BacktestVenueConfig`, `BacktestDataConfig`, and one `BacktestRunConfig`, then:

```text
BacktestNode::new(vec![run])? -> build()?
get_engine_mut(run_id): Option<&mut BacktestEngine>
register concrete Rust actor/strategy
node.run()? -> Vec<BacktestResult>
```

The snapshot supports exactly one run config despite the vector constructor.
One data config can stream from an iterator. Multiple configs are fully loaded
and merged before chunk execution, not bounded-memory multi-source streaming.
Chunks include all values sharing their boundary `ts_init`, so chunk size is
a target rather than a hard memory cap. Run bounds intersect data-config bounds.

With `raise_exception=false`, failures can be logged and omitted. Require the
expected result count/outcome, not just an `Ok` vector.

Arbitrary custom data are not a `BacktestDataConfig` variant. Register their
Arrow codec, use the dynamic catalog query, merge the returned `Vec<Data>`
causally with market data, and use `BacktestEngine`.

## Recording is separate

Catalog replay "streaming", engine incremental run, and Feather recording are
three different mechanisms. A config field is not a running writer.
Rust `LiveNodeConfig.streaming=Some(...)` is rejected in this snapshot.
Backtest engine/node configuration does not automatically own a Feather writer.

The native writer supports built-in/custom values, flush and close, but its
convenience bus handler uses `block_on`, logs write errors and ignores unsupported
types. Do not call it nonblocking or fail-closed audit persistence.

Evidence: [B1-B4, M1-M3, D1-D4, L1 in the source ledger](sources.md).
