# Crate ownership and coupled runtime paths

Nautilus is a Rust runtime, not just an order API. Keep the boundaries intact
when extracting signals, optimizing hot paths or adding persistence.

| Crate | Owning responsibility |
| --- | --- |
| `nautilus-core` | Timestamps, IDs/utilities and common parameter vocabulary |
| `nautilus-model` | Instruments, data, fixed-point types, orders, events, positions |
| `nautilus-common` | Actor/component lifecycle, bus, Cache, clocks, order factory |
| `nautilus-data` | Data clients, subscriptions, normalization, aggregation and publication |
| `nautilus-indicators` | Stateful calculations and readiness |
| `nautilus-trading` | Strategy facade/core, execution algorithms and authoring examples |
| `nautilus-risk` | Pre-trade gates on routed commands, rate limits and sizing helpers |
| `nautilus-execution` | Execution clients, order-event reduction, positions, emulator and matching |
| `nautilus-portfolio` | Account/position-derived financial calculations |
| `nautilus-system` | Kernel, trader/component registration and shared lifecycle |
| `nautilus-backtest` | Simulated venues, replay ordering, engine/node and results |
| `nautilus-live` | Async clients, command/data ingress, readiness, reconciliation and shutdown |
| `nautilus-persistence` | Historical catalog and recording/readback machinery |
| `nautilus-serialization` / `nautilus-persistence-macros` | Native codecs and generated custom schemas |
| `nautilus-infrastructure` / `nautilus-event-store` | Cache backends and event history/reconstruction |
| Adapter crate | Provider translation, transport, instrument/client configuration |

Not every crate is needed as a direct dependency. Import a crate directly when
the application uses its API; let transitive implementation dependencies remain
transitive. The inspected source distribution omits several workspace members
and adapters. A workspace listing is not evidence their implementation was read.

## Market-data to execution

```text
DataClient -> DataEngine -> Cache / MessageBus
                              -> DataActor / Strategy
Strategy -> cached initialization + published event
         -> RiskEngine queue -> ExecutionEngine queue -> ExecutionClient
ExecutionClient events -> ExecutionEngine -> cached order and position
                                         -> order event -> Strategy hook
                                         -> position event -> Portfolio / Strategy
```

The submission line is for ordinary non-emulated, non-algorithm orders.
Emulator and algorithm branches are described in [Execution](execution.md);
they do not all pass through an identical chain.

The execution engine updates cached positions before publishing a fill order
event. Portfolio's position-event aggregate follows later. This explains why a
cached position and a portfolio read can disagree during the fill hook without
either API being a replacement for the other.

## Ownership under concurrency

The mutable kernel, actor registry and bus are owner-thread structures.
`LiveNode` has an async outer loop; that does not make every component Send/Sync
or give every actor a mailbox. Backtest queues also defer commands for controlled
draining, but some event publication remains synchronous.

Keep pure calculations separable from runtime adapters. Transfer owned immutable
data to workers, not native `Rc<RefCell<_>>` state or actor guards. Bound queue
length and result age if introducing asynchronous research/inference work.
Use the supported runtime ingress/control handle to return to the owner thread.

## Debug the boundary that can explain the symptom

| Symptom | Trace |
| --- | --- |
| No callback | Instrument/route -> subscription -> Running state -> typed handler |
| Indicator differs live/backtest | Feed identity -> update owner -> warm-up -> availability time |
| Order not accepted | Local initialization -> selected branch -> risk -> client -> event |
| Wrong size after fill | Fill increment -> cached cumulative quantity -> position -> portfolio stage |
| Restart duplicates intent | Stable component identity -> persisted state -> reconciliation -> admission |
| Catalog exceeds memory | Data-config count -> query materialization -> equal-time chunk expansion |

Read the relevant declarations and callers together. A config field or comment
is not proof that the runtime consumes it. Specific observed discrepancies are
listed in [Pitfalls](pitfalls.md), with [source evidence](sources.md).
Use the [connection recipes](connections.md) to implement and qualify an
end-to-end path rather than treating this component map as execution evidence.
