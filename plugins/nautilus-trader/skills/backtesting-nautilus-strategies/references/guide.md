# Reproducible native experiments

## Deliver the requested result

Lead with the runnable setup or experiment result and its evidence boundary.
For reproducibility, state the `ts_init` ordering and equal-time tie policy,
explicit warm-up, simulator assumptions, expected input/result coverage and
canonical economic comparison. For catalog work, state whether data materialize
before chunking. Keep these relevant conclusions visible in a short summary
beside the artifact paths; a raw log or successful `run()` is not the answer.

## Choose the engine boundary

Use direct `BacktestEngine` for in-memory, mixed/custom or explicitly controlled
replay. Construct config, add simulated venues and instruments, register concrete
actors/strategies, load data, run, inspect results and dispose.

```text
BacktestEngine::new(BacktestEngineConfig) -> anyhow::Result<Self>
add_venue(SimulatedVenueConfig) -> anyhow::Result<()>
add_instrument(&InstrumentAny) -> anyhow::Result<()>
add_data(Vec<Data>, Option<ClientId>, validate: bool, sort: bool) -> Result<()>
run(Option<UnixNanos>, Option<UnixNanos>, Option<String>, streaming: bool) -> Result<()>
```

The bundled independent Cargo example uses explicit synthetic instruments and
quotes/custom data. It asserts native delivery and one simulated position;
it is not a profitable or production-protected strategy.

`add_data(validate=true)` validates the first item and assumes homogeneous input.
Validate the entire source and keep type/identity batches coherent.
Record OMS, account, balances, book/fill type, fees, margin and liquidity policy.

## Replay chronology

Startup drains subscriptions before first input. The engine advances clocks,
feeds the simulated exchange, routes data through DataEngine/Cache/bus,
drains commands, settles the venue, then completes equal-time timers/modules.
Input ordering is by `ts_init`; stable input order and stream insertion priority
matter on ties. Preserve a declared tie policy.

The bar's simulated price sweep precedes strategy bar delivery. OHLC traversal
is an assumption, not observed tick order or a universal next-bar-open guarantee.
Default and adaptive extreme ordering may produce different stop/target results.
Do not fix discrepancies by moving completed-bar availability into the past.

Replay a warm-up prefix with trading gated until ready; the basic backtest
client's historical quote/trade/bar request methods are no-ops.
Reset indicators and application state deliberately if reusing components;
fresh processes avoid unqualified thread-local residue.

## Catalog node

Enable `nautilus-backtest/streaming`. Create venue/data/run configs and
`BacktestNode::new(vec![run])?`, call `build()?`, find
`get_engine_mut(run_id): Option<&mut BacktestEngine>`, register native components,
then `run()? -> Vec<BacktestResult>`.

Exactly one run config is supported despite the vector constructor.
One data config can stream from an iterator; multiple configs load and merge
before chunk execution. `chunk_size` is not a hard memory cap: equal-time
groups expand it. Run bounds intersect data bounds.
With `raise_exception=false`, failed runs/builds may be omitted; require the
expected result count and outcome.

Arbitrary custom payloads are not BacktestDataConfig variants. Register native
Arrow codecs, dynamically query custom data into `Vec<Data>`, causally merge
with market data and use the direct engine. Materialization remains a memory
obligation, not a new lazy-streaming capability.

Engine `streaming=true` means incremental-run lifecycle without ordinary final
finalization between batches. It does not enable Feather recording.

## Compare the right output

`get_result()` includes run IDs and wall-clock metadata; do not byte-compare it
as a determinism test. The inspected snapshot exposes
`get_canonical_result() -> Result<CanonicalBacktestResult>`, then
`to_bytes()`, `digest()` and `first_divergence(&other)`.
Preserve source/config/input hashes, features/precision, instrument universe and
equal-time ordering beside canonical economics.

Use the first economic divergence to choose the next investigation: input
coverage, readiness, command timing, fill model or application state.
Do not keep rerunning an unchanged failing scenario without new evidence.

## Research validity

Keep point-in-time instruments, universe and delistings. Separate fitting,
warm-up, validation and holdout periods. Record searches and rejected variants,
not just the best curve. Include spread, commission, funding/borrow, multiplier,
margin, latency, queueing and liquidity assumptions appropriate to the strategy.
Book replay is not a counterfactual market-impact model.

Cross-provider signals require explicit contract/session/freshness/basis rules.
Adapter-specific data guidance covers only Databento and IBKR; a synthetic
venue requires neither provider nor credentials.

## Acceptance boundaries

Hook tests establish pure math/state. Registered replay establishes simulated
delivery and execution. JSON and Arrow each establish their own representations.
Construction-only adapter checks do not establish broker reports or fills.

For affected lifecycle behavior include partial fill -> pending cancel -> late
fill, rejection without fill, child-quantity mismatch and residual stop events.
Assert economic fields, not merely no panic or positive callback counts.
Return the experiment result and unresolved assumptions, not a profitability
promise or a claim of live parity.

Evidence: [sources.md](sources.md).

## Additional implementation paths

- [Typed configuration](configuration.md)
- [Complex component composition](composition.md)
- [Rust testing and benchmarks](rust-testing.md)
- [Durable capture and replay](event-replay.md)
- [Databento and IB adapter extension](adapter-development.md)
