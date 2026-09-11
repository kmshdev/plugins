# Actors, clocks and historical delivery

An actor owns computation and lifecycle state, not orders. Use
`nautilus_common::{actor::{DataActor, DataActorConfig, DataActorCore}, nautilus_actor}`.
The [complete example](../examples/quickstart/src/lib.rs) contains `QuoteCounter`.

## Authoring contract

Store one `DataActorCore`, implement `Debug`, invoke `nautilus_actor!(Type)`,
and implement `DataActor`. A differently named core uses
`nautilus_actor!(Type, field_name)`. Do not implement the blanket `Actor` or
`Component` traits yourself. There is no deref into runtime internals.

Construct the core with `DataActorCore::new(DataActorConfig {
actor_id: Some(actor_id), ..Default::default() })`. Use unique explicit IDs:
an omitted ID defaults to `DataActor`, not the concrete type name.
`log_events` and `log_commands` are booleans, not optional fields.

Register with `engine.add_actor(actor)?` or `node.add_actor(actor)?`.
Constructors initialize plain state; clock/cache access requires registration.
Runtime identity and the original configuration are not interchangeable.

| Lifecycle hook | Application responsibility |
| --- | --- |
| `on_start` | Resolve required instruments, subscribe, establish warm-up/timers |
| `on_stop` | Retire subscriptions and owned timers; no assumed flattening |
| `on_resume` | Re-establish resources retired on stop/degrade |
| `on_reset` | Clear counters, indicator state, buffers and replay-specific flags |
| save/load hooks | Explicitly version component-owned recovery state when needed |

## Callback signatures

Data/lifecycle hooks return `anyhow::Result<()>`. Market and timer inputs are
borrowed; order hooks belong to `Strategy`, not the `DataActor` implementation.

| Hook | Input |
| --- | --- |
| `on_quote` | `&QuoteTick` |
| `on_trade` | `&TradeTick` |
| `on_bar` | `&Bar` |
| `on_book_deltas` | `&OrderBookDeltas` |
| `on_book` | `&OrderBook` |
| `on_instrument` | `&InstrumentAny` |
| `on_data` | `&CustomData` |
| `on_time_event` | `&TimeEvent` from `nautilus_common::timer` |
| `on_historical_quotes` | `&[QuoteTick]` |
| `on_historical_bars` | `&[Bar]` |
| `on_historical_data` | `&dyn std::any::Any` |

Additional typed hooks cover marks, indices, funding, instrument status,
option greeks and option chains. Python names such as `on_quote_tick` and
`on_custom_data` are not Rust hooks.

Quote/trade/bar dispatch updates registered indicators before checking Running
and invoking the user hook. Custom and timer hooks also gate on Running.
Historical responses do not use the same Running gate. Data-handler errors are
logged by dispatch wrappers: `Err` does not automatically fault the actor or
propagate to a publisher. A fail-closed application needs an explicit state
transition/admission policy, not just a returned error.

## Facades and synchronous dispatch

Prefer `clock()`, `cache()`, `config()`, `actor_id()`, `trader_id()`,
`is_registered()`, `subscribe_*`, `unsubscribe_*`, `request_*`, `publish_data`.
Subscription does not prove a provider delivered anything.

The registry and bus are thread-local. Publication invokes subscribers inline,
after releasing the bus borrow. That does not make actor aliasing safe:
the inspected `ActorRef` implementation does not enforce unique mutable access.
Avoid direct registry access, self-publication to a subscribed topic, and
synchronous cycles A -> B -> A. Never retain an actor guard across a callback,
thread boundary or `.await`. Scope native Cache/clock borrows before dispatch.

`DataActorNative` supplies `core`, `core_mut`, `clock_mut`, `clock_rc`,
`cache_ref`, `cache_rc`. These are useful in runtime/testkit or explicitly
native hot paths, not a reason to duplicate the engine's state. Off-thread work
uses owned inputs and a supported owner-thread ingress, with stale-result checks.

## Timers

Inside an existing `DataActor` implementation:

```rust
fn on_start(&mut self) -> anyhow::Result<()> {
    let name = format!("{}.heartbeat", self.actor_id());
    self.clock().set_timer_ns(
        &name, 1_000_000_000, None, None, None, Some(false), Some(false),
    )?;
    Ok(())
}
```

Arguments after the interval are start, stop, callback, allow-past, fire-immediately.
`set_time_alert_ns(name, timestamp, callback, allow_past)` schedules one alert.
The facade borrows internally; native `Clock` methods take mutable access.
Names share the clock namespace and collisions replace timers. Use owned names,
cancel them on stop, and reinstall on resume. Do not cancel every timer on a
shared clock. `None` callback uses the existing named or registered default hook.

`TestClock::advance_time` returns events; it does not execute their handlers.
Obtain events and `match_handlers` under the clock borrow, drop that borrow,
then run handlers. Large time jumps can produce large batches and expose the
final clock time to every callback.

## Historical warm-up

```text
request_bars(
  BarType, Option<jiff::Timestamp>, Option<jiff::Timestamp>,
  Option<NonZeroUsize>, Option<ClientId>, Option<Params>
) -> anyhow::Result<UUID4>
```

`request_data(DataType, ClientId, start, end, limit, params)` requires a client
ID. Request bounds use `jiff::Timestamp`, unlike replay's `UnixNanos` bounds.
The returned UUID identifies registration, not response completion.
The historical hook does not receive the request ID; overlapping same-type
requests require an explicit attribution policy.

A custom response can contain a scalar `CustomData` or a `Vec<CustomData>`;
the vector, including an empty one, is delivered as one historical callback,
not expanded into `on_data`. Reject unexpected shapes explicitly.

Bound warm-up by time/count, buffer or deliberately defer live input, then merge
by declared identity and availability time. Separate empty success from a
missing response. The built-in backtest client's historical market-data request
methods are no-ops: a replay warm-up prefix is the simple offline alternative.

Evidence: [A1-A5, D1-D4, B1 in the source ledger](sources.md).
