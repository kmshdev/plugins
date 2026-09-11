# Backtesting and research validity

The [offline example](../examples/quickstart/README.md) is a complete direct-engine
composition. It uses declared synthetic inputs, not a hidden catalog or provider.

## Direct engine

Create `BacktestEngine` with configuration, add a `SimulatedVenueConfig`, add
instrument definitions, register actors/strategies, add data, run, obtain results
and dispose. Let the engine own registration and the clock.

```text
BacktestEngine::new(BacktestEngineConfig) -> anyhow::Result<Self>
add_venue(SimulatedVenueConfig) -> anyhow::Result<()>
add_instrument(&InstrumentAny) -> anyhow::Result<()>
add_data(Vec<Data>, Option<ClientId>, validate: bool, sort: bool)
    -> anyhow::Result<()>
run(Option<UnixNanos>, Option<UnixNanos>, Option<String>, streaming: bool)
    -> anyhow::Result<()>
```

Set venue OMS, account type, book type, balances, fees/fill model and relevant
simulation policies intentionally. Netting/margin/L1 and synthetic USD capital
are example choices, not universal defaults.

`add_data` validation examines the first value and assumes a homogeneous batch.
Validate every source record before ingestion; splitting by type/identity is
safer than treating the flag as an exhaustive dataset validator.

## Replay chronology

```text
kernel/accounts/engines/trader start
 -> drain startup subscriptions
 -> advance clocks
 -> simulated exchange receives event
 -> DataEngine -> Cache/bus -> component
 -> drain commands and settle venues
 -> same-time timer/module completion
 -> stop/final settlement/save/results
```

Order is by `ts_init`, with stable input order and stream insertion priority
resolving ties. Preserve those choices. Upstream tests cover equal-time data
before a timer, but do not extrapolate that into arbitrary callback ordering.

The strategy receives a bar after the bar's synthetic execution-price sweep.
There is no universal next-bar-open fill rule. Default OHLC traversal and adaptive
extreme ordering can produce different stop/target outcomes.
Same-bar target and stop hits are simulation assumptions, not observed tick order.

For warm-up, replay a prefix with trading gated until indicators and history are
ready. `request_bars` on the basic backtest client is not an automatic catalog
preload. Reset all application state when intentionally reusing a component;
independent processes avoid unqualified thread-local/registry residue.

## Results and repeatability

`get_result()` contains run/wall-clock metadata, so byte-comparing it is not a
determinism test. The snapshot supplies:

```text
get_canonical_result() -> anyhow::Result<CanonicalBacktestResult>
canonical.to_bytes() -> anyhow::Result<Vec<u8>>
canonical.digest() -> anyhow::Result<String>
canonical.first_divergence(&other)
```

Retain the resolved dependency graph, config, input hashes, universe,
instrument metadata, feature/precision choices and tie-order policy alongside
canonical economics. Identical canonical results do not prove realistic fills.

Engine `streaming=true` defers ordinary finalization so the caller can supply
batches and finish the run. It is not Feather recording. For catalog node
chunking and its memory limits read [Market data](market-data.md).

## Evidence that answers different questions

| Boundary | What it can establish |
| --- | --- |
| Pure signal test | Formula and local state transition |
| Registered native replay | Subscription, lifecycle, causal order and simulated execution |
| JSON/Arrow round trip | The corresponding representation/identity contract |
| Catalog chunk equivalence | Chunking preserves the selected scenario's economics |
| Adapter construction | Types/configuration compose without a connection |
| Recorded broker reports/events | Observed venue behavior for that account/path/time |

For lifecycle changes, include partial fill -> pending cancel -> late fill,
rejection without fill, child protection mismatch and stop-time residual events.
Assert economic fields, not only callback counts or "no panic".

## Avoid research leakage

Use point-in-time instrument/universe definitions; preserve delistings and
session/status exclusions. Separate warm-up, fitting, validation and holdout
periods. Record parameter searches, not just the best curve.

Model spread, commission, funding/borrow, multiplier, margin, latency and
liquidity assumptions. L2/L3 needs actual book data; historical replay is not a
counterfactual market-impact model. Cross-venue proxy signals need freshness,
session and basis rules. Do not infer execution realism from deterministic code
or infer an investment edge from the educational examples.

Evidence: [B1-B4, M1, E1-E4 and the backtesting docs](sources.md).
