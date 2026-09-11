# Actor authoring and message delivery

## Native shape

Import `nautilus_common::{actor::{DataActor, DataActorConfig, DataActorCore},
nautilus_actor}`. Store one core, implement `Debug`, invoke
`nautilus_actor!(Type)` and implement `DataActor`. A nonstandard field uses
`nautilus_actor!(Type, field)`. Do not add manual blanket `Actor`/`Component`
implementations or a deref into runtime internals.

Construct with `DataActorCore::new(DataActorConfig {
actor_id: Some(actor_id), ..Default::default() })`. Set a unique ID; the default
is `DataActor`, not your concrete type. Register with
`engine.add_actor(actor)?` or `node.add_actor(actor)?`.
Clock/Cache access belongs after registration, normally in `on_start`.

Use facade `clock()`, `cache()`, `subscribe_*`, `unsubscribe_*`, `request_*`,
`publish_data`, `actor_id()`, `trader_id()` and `is_registered()`.
`DataActorNative` exposes core/clock/cache borrows only for explicit native
runtime/testkit paths. It is not needed in ordinary actor logic.

## Handlers and lifecycle

Data/lifecycle handlers return `anyhow::Result<()>`. Rust names are
`on_quote(&QuoteTick)`, `on_trade(&TradeTick)`, `on_bar(&Bar)`,
`on_data(&CustomData)` and `on_time_event(&TimeEvent)`. Import `TimeEvent` from
`nautilus_common::timer`. Order hooks are not part of your `DataActor` impl.

Subscribe and establish readiness in `on_start`; retire owned subscriptions
and timers in `on_stop`; restore them in `on_resume`; clear counters, buffers,
indicator and replay flags in `on_reset`. Persist component-owned state through
versioned save/load contracts only when the runtime has backing configured.

Typed quote/trade/bar dispatch updates registered indicators before the Running
gate. Custom/time callbacks gate on Running. Historical handlers do not share
that gate. Data-hook errors are logged by wrappers; `Err` does not automatically
fault the actor or tell the publisher it failed. Model failure/admission state
explicitly when silent continuation would be unsafe.

## Timers

```rust
self.clock().set_timer_ns(
    "actor-heartbeat", 1_000_000_000, None, None, None, Some(false), Some(false),
)?;
```

Arguments are name, interval, start, stop, callback, allow-past, fire-immediately.
Use actor-qualified names. Collisions replace timers; an omitted callback uses
the named/default callback. Cancel only the timers you own on a shared clock.
`set_time_alert_ns(name, timestamp, callback, allow_past)` is the one-shot form.

For `TestClock`, advance time and match returned events to handlers while
borrowing the clock, release the borrow, then execute handlers. Advancing alone
does not call the actor. Never retain a clock or actor guard across callbacks
that can access that same runtime state.

## Historical warm-up and indicators

```text
request_bars(BarType, Option<jiff::Timestamp>, Option<jiff::Timestamp>,
             Option<NonZeroUsize>, Option<ClientId>, Option<Params>)
  -> anyhow::Result<UUID4>
```

`request_data(DataType, ClientId, start, end, limit, params)` requires a client.
The returned UUID is not response completion. Historical hooks receive
`on_historical_bars(&[Bar])` or `on_historical_data(&dyn Any)`, not the request
ID. Overlapping requests need a deliberate attribution policy.
A vector custom response, including an empty vector, is one historical callback,
not multiple `on_data` calls.

Bound requested history and any buffered live inputs, distinguish missing
response from empty success, merge by identity/availability and activate only
when readiness is satisfied. Built-in backtest market-data requests are no-ops;
replay an explicit warm-up prefix rather than expecting automatic retrieval.

Choose manual indicator updates OR registered shared indicators, not both.
Registration requires `nautilus-common/indicators`, is not subscription, and
updates before user hooks. `indicators_initialized()` returns `Result<bool>`
and is false when nothing is registered. Reset consistently. EMA period zero
is invalid; sufficient samples and supported input handlers matter.

## Custom data

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

Add direct core/model/persistence-macros plus `anyhow`, `serde` derive and
`serde_json` dependencies. The macro supplies constructor, timestamp traits and
custom trait; field order determines constructor order. The type name is schema
identity. Use `CustomData::new(Arc::new(payload), data_type)`, payload first,
with types imported from `nautilus_model::data`.

`subscribe_data(data_type, None, None)` installs local subscription only.
`Some(client)` additionally requests provider subscription.
Publish a new immutable envelope with
`self.publish_data(&data.data_type, &data)` from a separate producer.
Downcast `data.data.as_any().downcast_ref::<SignalV1>()` in `on_data`; reject
wrong types explicitly. Publication is synchronous; avoid self/cyclic delivery.

`DataType::new(type_name, metadata, identifier)` routes by derived topic.
Identifier is storage scope, not subscription isolation; use unambiguous
normalized metadata to partition streams. Numeric and string metadata can
stringify identically. `Arc` does not itself forbid interior mutation.

JSON reconstruction needs `ensure_custom_data_json_registered::<SignalV1>()?`.
Serialize the wrapper with `serde_json::to_vec(&data)?`, then
`CustomData::from_json_bytes(&bytes)?`; payload-only `to_json` is not the envelope.
Local delivery does not need codec registration.
Arrow instead uses `#[custom_data]`, matching Arrow dependencies and
`nautilus_serialization::ensure_custom_data_registered::<T>()`, which returns
`()`. Preserve homogeneous type/route batches and register the decoder process.

## Troubleshooting boundary

For missed input, trace instrument identity -> topic -> subscription -> lifecycle
-> typed handler. For stale math, trace update owner -> history/live merge ->
availability. A direct callback unit test cannot establish registration,
correlation, gating or bus delivery. Use the bundled native example for that
boundary, and keep serialization and transport claims separate.

Evidence coordinates and source hashes are in [sources.md](sources.md).

## Additional implementation paths

- [Typed configuration](configuration.md)
- [Complex component composition](composition.md)
- [Rust testing and benchmarks](rust-testing.md)
- [Durable capture and replay](event-replay.md)
- [Databento and IB adapter extension](adapter-development.md)
