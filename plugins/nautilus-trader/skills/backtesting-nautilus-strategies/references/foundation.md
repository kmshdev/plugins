# Native runtime contract: 0.64.0

Use this reference when a task crosses components, not before every edit.
Bundled examples pin 0.64.0, Rust 1.98.1 and edition 2024. Existing applications
retain their lockfile, features and source overrides unless an upgrade is in scope.
A version label is not proof of artifact equality: consult the source evidence
when compiler-visible APIs and moving documentation disagree. No Python runtime
is needed. For upgrades or proposed workarounds, use
[version and native integration](version-and-integration.md).

## Messages and state are different things

Data clients translate provider data. DataEngine manages subscriptions,
requests, aggregation and typed delivery. Actors observe/transform; strategies
create order intent. The execution engine reduces reports/fills into native
order and position state. Portfolio derives accounting. The kernel owns the
runtime, clock, engines, Cache, Trader and lifecycle.

MessageBus provides publication, addressed endpoints and correlated response
delivery. Commands ask for actions; events describe facts; queries read state.
In-process publication may call subscribers inline. It is not a durable log,
an actor mailbox, a timestamp sorter or proof of delivery to a broker.
External transport, where supported, does not replace recovery backing.

Runtime queues can defer commands, but initialization/pending events can still
publish synchronously. Establish correlation and application admission state
before submit/modify/cancel. Avoid synchronous actor cycles and retained native
borrows across dispatch. Actor registry handles do not enforce all aliasing
constraints. Mutable runtime state belongs to its owner thread.

## Choose the communication contract

| Path | Responsible component | Evidence to inspect |
| --- | --- | --- |
| Provider input -> native data -> subscriber | Client translation, DataEngine, actor/Strategy | Instrument/type/topic, subscription, Running state, payload and causal time |
| Subscribe or request -> response | Addressed data command and correlated response handling | Selected client, returned request ID, actual response and admitted coverage |
| Strategy command -> execution feedback | Applicable risk/execution route and execution client | IDs established before send, native events/reports, cached quantities |
| Restore -> reconcile -> admission | Kernel/node backing plus application admission policy | Stable identity, restored intent and actual external report coverage |

Publishing an observation is not issuing a historical request or submitting an
order. A native market-data path can update Cache; an arbitrary custom
publication does not thereby acquire a cache record, codec or durable log.
Typed historical hooks can hide the response envelope's correlation ID: do not
substitute arrival order for attribution. When a task crosses these boundaries,
select its [connection recipe](connections.md) rather than guessing from a
component diagram.

## Temporal and financial invariants

Messages stay immutable after publication. `ts_event` describes the mapped source
event; `ts_init` describes availability according to the specific adapter/decoder.
Do not assume every adapter's bar timestamp is transport-arrival evidence.
Derived values retain causal input time and cannot become available in the past.
Replay uses availability ordering, with a declared equal-time tie policy.

Use `Price`, `Quantity`, `Money` and `Decimal` for discrete financial values.
Decimal precision is not tick/lot alignment. Resolve instrument metadata,
explicit rounding, currencies, multiplier and limits before creating orders.
Missing account or stale valuation is not zero. Keep risk bypass disabled.

Cache facade reads are owned snapshots: retain IDs and re-query, not stale
copies. On the inspected fill path, cached order/position changes precede order
events; Portfolio's net-position aggregate follows the position event.
Native execution owns position reduction, not a competing application ledger.

## Evidence boundaries

Order submission success is not venue acceptance. Errors may follow side
effects; cancellation does not prohibit a late fill. Bracket relationships are
not proof of atomic live protection. A successful node start does not prove
complete account/order/position reconciliation.

Backtest uses historical/synthetic input and simulated execution. Sandbox uses
real-time data with simulated execution. Live connects execution clients to
paper or real venues/accounts. A port or environment label does not prove
account mode. Common components do not make execution assumptions identical.

Cache backing, component snapshots, historical catalogs and event-store replay
serve different purposes. Cache-only event-store reconstruction does not replay
Strategy callbacks or restore application-owned strategy state. Component
snapshot/load is separate; neither replaces broker reconciliation or feed-gap
repair.
Orderly stop must allow residual execution events and configured persistence.

## Scope

Follow the target application's established ownership and strategy semantics.
Examples do not authorize provider connections, market-data purchases, live
orders, destructive recovery, account changes or publishing credentials.
Adapter-specific recipes cover only Interactive Brokers and Databento.
No skill requires another skill or a hidden source checkout to be useful.
