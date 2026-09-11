# Native live composition and recovery

This reference explains construction and lifecycle, not permission to connect
an account or submit orders. Use an explicitly qualified test/paper path before
real-capital operation. Environment labels and port numbers do not prove account
mode.

## Composition

Use `nautilus-live` with `default-features=false, features=["node"]`.
Add a matching adapter crate and its required data/execution features.
`LiveNode` owns the native event loop; there is no Python `TradingNode` here.

The builder accepts:

```text
add_data_client(Option<String>, Box<dyn DataClientFactory>,
                Box<dyn ClientConfig>) -> anyhow::Result<Self>
add_exec_client(Option<String>, Box<dyn ExecutionClientFactory>,
                Box<dyn ClientConfig>) -> anyhow::Result<Self>
```

These signatures explain the boundary, not a substitute for the adapter's
validated config. Factories downcast to their matching config type. Configure
default and venue routing intentionally, particularly when data and execution
come from different providers. Use the actual instrument mapping, currency,
multiplier, expiry and account identity.

Build the node, register native actor/strategy instances, and use `run().await?`
for the owned loop. `start().await` alone performs startup, not continued event
processing. Concrete [adapter factory evidence](sources.md) covers Interactive
Brokers in the inspected source; other listed adapters were not assumed audited.

IB execution constructs a netting margin client. A configured raw account is
normalized with its client issuer; absent configuration can yield `IB-001`.
That fallback is not broker discovery and must not satisfy account admission.

## Startup and readiness

```text
build clients/routing -> prepare persisted Cache -> kernel start
 -> connect data clients/process instrument events
 -> connect execution clients/check connection readiness
 -> startup mass-status reconciliation
 -> restore component state/start trader
 -> event loop and maintenance
```

Keep reconciliation enabled. Still, `Ok(None)` mass-status can warn and continue
in the inspected startup path. Successful startup alone does not establish known
orders, positions, account identity or complete report coverage.

Define admission around actual facts: required instruments, authorized account,
fresh market input, account/position/order report coverage, recovered unresolved
intent and no contradictory execution state. Unsupported adapter report methods
and empty successful responses are different from verified absence.

## Persistence is several contracts

| Surface | Purpose |
| --- | --- |
| Parquet catalog | Historical research input |
| Cache backing | Persisted current domain state |
| Component save/load | Actor/strategy-owned versioned state |
| Event store | Recorded history and cache reconstruction |
| Portfolio | Derived valuation, not a replacement for source evidence |

Stable component IDs and compatible state schemas matter on restart.
Do not enable `flush_on_start` on a recovery path: it removes the recovery basis.
Cache creation/loading can happen during startup, not just builder construction.
Component save/load requires configured backing; merely implementing callbacks
is not durable persistence.

Event-store replay is not a strategy backtest. The kernel skips ordinary engine,
client, trader startup and reconciliation in that mode. Never use it as a second
trading authority or assume it reruns strategy decisions. Cache-only replay does
not replay Strategy callbacks or restore application-owned strategy state;
component snapshot/load is separate. Neither substitutes for broker
reconciliation or repairs a feed gap.

When possible-send state survives a crash, reconcile before retrying. A local
submission error or missing callback cannot prove the broker never received
the command. Keep application intent records separate from native position truth.

## Stop

Request stop, execute component stop policy, process residual events during the
grace period, disconnect clients, persist state, stop engines/cancel timers and
seal the event store. Immediate process termination does not provide these
guarantees. Observe unresolved orders/exposure; cancellation and managed market
exit are requests, not guaranteed fills.

Long-running blocking work in a callback delays market/execution processing.
Use the supported node control/ingress handle across threads, not actor guards or
native shared Cache handles. Bound queues and fail explicitly on stale input.

`LiveNodeConfig.streaming` does not automatically record Feather: this snapshot
rejects it. Read [Market data](market-data.md) before designing native recording.

Evidence: [L1-L4, E1, R1-R4 in the source ledger](sources.md).
