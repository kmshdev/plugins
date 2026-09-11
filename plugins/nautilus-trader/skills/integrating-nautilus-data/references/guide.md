# Native data integration

## Deliver the requested result

Lead with the requested data path, code or diagnosis. Summarize the relevant
identity, timestamp and coverage decisions explicitly:

- Distinguish provider symbol/dataset, native InstrumentId and any qualified
  execution-contract mapping. State both event-time and availability semantics.
- Name the actual subscription/request capability, response coverage and any
  unsupported feed. Empty data, missing response and logged acquisition failure
  are different observations.
- For custom persistence, state payload-first construction, JSON envelope versus
  Arrow registration, and topic metadata versus storage identifier. Report which
  representation and delivery boundary was actually exercised.

Keep this summary short and task-specific, with paths to produced artifacts.
Do not bury the result in a transcript of documentation/source exploration.

## Define the identities first

Distinguish provider symbol/dataset, native InstrumentId, source timestamp,
availability timestamp, schema and intended consumer. For broker execution,
maintain an explicit relationship to a qualified dated contract.
Venue routing is not a symbol conversion or proof of qualification.

Load instrument definitions before data that need precision, aggregation or
execution. Use exact Price/Quantity values. Record source schema and normalization
policy, including unavailable fields; never fabricate book depth or aggressors.
For adapter-specific APIs and limitations, read [adapters.md](adapters.md).

## Subscriptions, requests and DataEngine

Use DataActor facades after registration:
`subscribe_quotes(InstrumentId, Option<ClientId>, Option<Params>)`,
`subscribe_trades(...)`, `subscribe_bars(BarType, client, params)`,
`subscribe_data(DataType, client, params)`. Retire and restore subscriptions on
the relevant lifecycle transitions. A command return is not first data arrival.

Historical `request_bars` uses BarType, optional `jiff::Timestamp` bounds,
optional nonzero limit, client and params; it returns a correlation UUID.
`on_historical_bars(&[Bar])` is distinct from `on_bar(&Bar)`.
Requested custom responses may be scalar or vector in `on_historical_data(&dyn Any)`.
An empty vector is one response, not evidence that acquisition succeeded without
warnings. Attribute overlapping requests explicitly.

DataEngine routes commands to selected data clients and processes typed values.
MessageBus provides addressed commands, publications and correlated responses;
it does not sort arbitrary publication or persist everything automatically.

## Bars and order books

Already built bars use EXTERNAL. INTERNAL requests engine aggregation:
LAST uses trades; BID/ASK/MID use quotes; composite specifications use bars.
Imbalance/runs require suitable trade/aggressor information.
Choose close timestamps, interval inclusion, partial/empty bars and build delay
(microseconds) deliberately. Do not let a completed OHLC bar appear available
at its opening time.

Preserve book snapshots, Clear boundaries, sequence conventions and `F_LAST`.
Missing batch-end flags can prevent buffered delta delivery. L2/L3 replay
requires actual book data, not a quote proxy. Keep status/suspension information
when the consumer relies on it.

## Indicator and history/live handover

Choose manual or registered indicator updates, never both. Registration is not
subscription; native registered indicators update before data callbacks.
Bound warm-up and live buffering, merge/deduplicate by declared identity and
availability, and keep new decisions gated until ready.
Basic BacktestEngine historical requests are no-ops: feed an explicit warm-up
prefix for that environment.

## Custom payload and codecs

Use `CustomDataTrait` values inside `CustomData`. The Rust constructor is
`CustomData::new(Arc::new(payload), data_type)`.
`#[custom_data(no_arrow)]` from `nautilus_persistence_macros` generates a
JSON-capable payload with typed `ts_event`/`ts_init` fields; direct macro
dependencies include core/model, anyhow, serde derive and serde_json.
The generated type name is persisted schema identity.

DataType routing uses type/topic metadata; identifier only scopes storage.
Normalize metadata because stringification can collide. Publish a fresh value
through `publish_data(&data.data_type, &data)` and downcast the envelope payload
in `on_data`. Local delivery needs no JSON registration.

For JSON, call `ensure_custom_data_json_registered::<T>()?`, serialize the entire
envelope with serde_json and reconstruct with `CustomData::from_json_bytes`.
Payload-only JSON is different. Registries are process-global; ensure-style
registration does not prove compatibility of conflicting same-named types.

For Arrow, use the macro without `no_arrow`, enable serialization `arrow`, align
the direct Arrow dependency with the locked graph and call
`nautilus_serialization::ensure_custom_data_registered::<T>()` (returns unit).
Keep batches homogeneous in custom type and routing identity. Register decoding
processes and check identifiers separately from wrapper equality.

## Catalog contract

`ParquetDataCatalog` is under
`nautilus_persistence::backend::catalog`. Write definitions separately, then
ascending homogeneous typed data. `write_to_parquet(&[T], start, end, option)`
returns a result/path. Construction with `new` can panic; the fallible `from_uri`
surface is appropriate for explicit creation errors.

Do not mistake the catalog for durable live intent or account truth.
Native custom dynamic queries materialize `Vec<Data>`; arbitrary custom types
are not a BacktestDataConfig variant. Use direct-engine replay after causal
merging. Multiple catalog node configs are materialized before chunking;
equal-`ts_init` groups can exceed requested chunk size.

Feather recording is separate from catalog chunking. The inspected live node
rejects `streaming=Some(...)`. A writer's convenience bus callback blocks and
logs errors; it is not automatically nonblocking, fail-closed audit persistence.

## Output and troubleshooting

Return the configured native path plus input identity, admitted time range,
precision and missing/unsupported data. Distinguish decoder correctness,
serialization round trip, native delivery, and provider entitlement/completeness.
Investigate mismatched instrument metadata, route/topic, running state and
provider schema before creating an alternative data engine.

Evidence: [sources.md](sources.md).

## Additional implementation paths

- [Typed configuration](configuration.md)
- [Complex component composition](composition.md)
- [Rust testing and benchmarks](rust-testing.md)
- [Durable capture and replay](event-replay.md)
- [Databento and IB adapter extension](adapter-development.md)
