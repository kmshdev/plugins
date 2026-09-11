# Custom data: values, routes and persistence

Three contracts are independent: the payload implements `CustomDataTrait`,
`DataType` determines routing/storage identity, and codecs reconstruct serialized
values. Local pub/sub does not require JSON or Arrow registration.

## A native payload

```rust
use nautilus_core::UnixNanos;
use nautilus_persistence_macros::custom_data;

#[custom_data(no_arrow)]
pub struct SignalV1 {
    pub value: i64,
    pub ts_event: UnixNanos,
    pub ts_init: UnixNanos,
}
```

Macro expansion needs direct `anyhow`, `serde` with `derive`, and `serde_json`
dependencies as well as core/model. It generates the constructor, timestamp
traits, custom trait and conversions. `no_arrow` still supports JSON.
Constructor arguments follow field order; the Rust struct name becomes the
serialized type name. Renaming a deployed type is therefore a schema change.

```rust
use std::sync::Arc;
use nautilus_model::data::{CustomData, CustomDataTrait, DataType};

let route = DataType::new(SignalV1::type_name_static(), None, None);
let data = CustomData::new(
    Arc::new(SignalV1::new(7, event_time, available_time)),
    route,
);
```

This is a fragment: `event_time` and `available_time` are validated `UnixNanos`
from the caller. Rust takes payload before `DataType`.
`CustomData::from_arc(payload)` instead creates metadata-free routing.
An `Arc` does not prohibit interior mutation: immutable publication is your
payload design obligation.

## Pub/sub

In the consumer's `on_start`, call
`self.subscribe_data(route, None, None)`. `None` client installs a local
subscription only; `Some(client)` additionally requests an external subscription.
Retire it with `unsubscribe_data` and restore it on resume.

In a different registered producer:

```rust
self.publish_data(&data.data_type, &data);
```

This publishes the `CustomData` envelope, not a raw signal. The explicit first
argument determines the topic, so a mismatched route can silently misroute a
valid payload. The consumer uses `on_data(&CustomData)` and
`data.data.as_any().downcast_ref::<SignalV1>()`; reject unexpected payload types.
Use a one-way actor graph; publication is synchronous, not an actor mailbox.

## Identity traps

`DataType::new(type_name, metadata, identifier)` uses the derived topic for
equality. The optional identifier scopes persistence, **not subscriptions**.
Metadata keys are sorted and values stringified: numeric `1` and string `"1"`
can collide. Use normalized, unambiguous metadata without wildcard/delimiter
ambiguity for isolation. Test routing, payload identity and storage identifier
separately; wrapper equality will not detect every persistence-identity change.

Preserve source `ts_event`; set `ts_init` to when the derived value was available.
Neither custom publication nor `Arc` establishes chronological ordering.

## JSON

```rust
use nautilus_model::data::ensure_custom_data_json_registered;

ensure_custom_data_json_registered::<SignalV1>()?;
let encoded = serde_json::to_vec(&data)?;
let decoded = CustomData::from_json_bytes(&encoded)?;
```

The envelope contains `type`, `data_type` and `payload`.
`data.data.to_json()` produces only the inner payload and is not interchangeable
with serializing `CustomData`. Registration must happen in decoding processes.
Names are process-global; an `ensure_*` call keeps an existing registration and
does not prove two same-named Rust types share a schema.

## Arrow and catalogs

Use `#[custom_data]` without `no_arrow`, a matching direct Arrow dependency,
and `nautilus-serialization` with `arrow`. Do not pick an unrelated Arrow major
version: generated trait signatures must match the resolved framework graph.

```rust
nautilus_serialization::ensure_custom_data_registered::<SignalV1>();
```

This returns `()`, not `Result`. The type must supply schema, encode/decode,
clone and Send/Sync contracts. Register all types before reading or writing.
Avoid partial registry installation: an existing Arrow schema can cause this
helper to return before JSON registration.

Use supported scalar fields first; Serde-backed nested fields require the
macro's `#[custom_data_field(serde)]` support. Keep each batch homogeneous in
type and intended routing identity. The dynamic decoder restores persisted
`DataType` metadata from the first row. A low-level registry `Ok(None)` means
"not registered", not successful decoding.

The direct engine accepts `Data::Custom`. Catalog
`query_custom_data_dynamic` materializes `Vec<Data>`; it is not a lazy stream.
`BacktestDataConfig` cannot name arbitrary custom types. Merge custom and market
inputs by causal availability and use the low-level engine.

## Boundary evidence

The [example](../examples/quickstart/src/lib.rs) includes a JSON round trip.
Separately exercise native registration/start -> publish -> dispatch, metadata
isolation, scalar/vector/empty historical responses, and Arrow/catalog identity.
Drop actor and clock guards before delivering a message back into the runtime.
A hook-only test does not qualify transport; JSON does not qualify Arrow.

Evidence: [D1-D4, A1-A4, B1-B3 in the source ledger](sources.md).
