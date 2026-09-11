# Cross-component recipes: Rust 0.63.0

Select the path that explains the task; do not load every recipe before editing.
These recipes connect the workflow guides, not new engines or new skills.
Use [the runtime contract](foundation.md) for shared ownership and
[source evidence](sources.md) for the anchor IDs below.

Record the input identities, command/correlation IDs, causal timestamps,
component lifecycle and observed outcome at each boundary. A request return,
callback count or startup flag alone is not completion evidence. The checks
below are acceptance specifications, not claims that every scenario was run.

## C1: Input to actor to observation to strategy

**Owners:** DataEngine delivers; an order-free actor derives; a Strategy consumes
the immutable observation and alone decides whether to request orders.

1. Register instruments and both concrete components with the native runtime.
   Subscribe in lifecycle hooks. Give producer and consumer compatible type and
   topic metadata; a storage identifier does not isolate a subscription.
2. Feed only native market input. In the actor callback, finish local state
   updates, construct a fresh payload with causal event/availability times and
   publish through `publish_data`.
3. Downcast and validate in the Strategy's `on_data`. Avoid self-subscription,
   cyclic dispatch and native borrows held across publication. Publication may
   finish the consumer callback before returning to the producer.
4. Assert exact derived values, input-to-output timestamps and consumer sequence,
   not just nonzero callbacks. A separately injected custom input cannot prove
   actor publication. No order is needed to establish this delivery path.

**Failure control:** remove publication or mismatch the consumer topic; the
expected derived sequence must be absent. Keep JSON/Arrow round trips separate.

Source anchors: A1, A3, D1.

## C2: Order intent to partial fill to accounting

**Owners:** Strategy admits intent; RiskEngine checks its applicable route;
ExecutionEngine reduces native orders/positions; Portfolio derives accounting.

1. Validate instrument grid, size, account/currency and capital readiness.
   Record IDs, reservations and possible-send state before requesting submission.
2. Trace the actual order branch. Ordinary, emulated and algorithm submissions
   do not promise identical risk checks or timing.
3. On partial fills, inspect cached cumulative filled/leaves quantity and current
   position. Fill quantity is incremental, not the new total position.
4. Compare exposure in Cache during the fill hook with Portfolio accounting at
   the subsequent position-event stage. Do not build a second authoritative
   position reducer to compensate for that stage difference.

**Check:** reconcile fill increments, cached quantities, account currency and
post-position accounting. A rejection must not create a fill-derived position;
missing valuation remains unknown, not zero.

Source anchors: E1, E3, E4, R1, R3.

## C3: Historical request to warm-up to live handover

**Owners:** DataEngine/client supply history; the actor owns indicator readiness,
bounded buffering and the application's admission handover.

1. Declare stream identity, requested interval, warm-up requirement, timeout and
   maximum buffered live input. Keep new decisions gated.
2. Retain the UUID returned by a historical request. The bus correlates the
   response, but `on_historical_bars(&[Bar])` does not expose that UUID. Serialize
   otherwise indistinguishable requests or design an explicit attribution
   protocol; do not infer correlation from response arrival order.
3. Distinguish no response, logged acquisition failure and an empty response.
   Verify coverage against the request and merge buffered live input by declared
   identity and availability. Deduplicate overlap without deleting distinct
   equal-time observations.
4. Assign one indicator update owner, release the warm-up gate only when the
   required coverage/readiness is established, and record the handover watermark.

**Check:** overlapping history/live input is consumed exactly once, a delayed
response cannot activate the wrong warm-up, and overflow/timeouts keep admission
closed. Backtest market-data requests are no-ops; use an explicit warm-up prefix
there rather than claim the live request protocol was exercised.

Source anchors: A1, A3, M2, B1.

## C4: Cancel or submit uncertainty to late fill

**Owner:** Strategy owns admission/reservations; native execution owns observed
order and position state.

1. Mark the intended operation before calling submit, modify or cancel.
   A submit error can follow routing, including GTD timer setup failure.
2. Keep pending commands, unresolved leaves, filled exposure and acknowledged
   protective quantity distinct. Requesting cancellation does not release them.
3. Process partial fill, cancel/modify rejection, cancel acknowledgement and
   late fill against current native state. A canceled order can receive a fill;
   a correction can revise previously reported economics.
4. Resolve uncertainty through native events/reports before retrying or releasing
   obligations. Preserve unresolved state across stop/restart.

**Check:** exercise fill-before-cancel and fill-after-cancel, rejection that
leaves the order working, and an error after possible send. Assert economic
quantities and no blind duplicate submission, not a single linear status label.

Source anchors: S3, E4.

## C6: Same components in replay and connected operation

**Owners:** BacktestEngine/BacktestNode or LiveNode compose the same actor/Strategy
behavior; the kernel owns the chosen clock, engines, Cache and lifecycle.

1. Keep signal and execution-state logic independent of the composition root.
   Select simulated venues or authorized client factories at that root.
2. Freeze instrument identity, precision, schemas, indicator update ownership,
   readiness and equal-availability tie policy.
3. Record what changes: historical versus received availability, TestClock versus
   live scheduling, historical request support, fill/liquidity/latency models,
   external reports and persistence.
4. Compare native delivery and canonical economics only under the recorded
   assumptions. Constructing a live node without starting it establishes wiring,
   not behavioral equivalence with replay.

**Check:** reproduce a bounded input/decision sequence offline; qualify connected
delivery/execution separately. Similar PnL or a shared Strategy type is not proof
of live parity, provider completeness or profitability.

Source anchors: B1, B2, L1, L2.

## C8: Custom schema to catalog to causal replay

**Owners:** data integration owns representation and admitted inputs; persistence
provides catalog APIs; the native backtest runtime owns replay.

1. Define type/schema identity, normalized topic metadata, storage identifier and
   causal timestamps. Construct `CustomData` with payload first, then DataType.
2. Qualify JSON envelope reconstruction separately from Arrow. Register decoders
   in the reading process, keep custom type/route batches homogeneous, and check
   storage identifiers explicitly rather than relying on wrapper equality.
3. Write/read the admitted catalog interval with instrument definitions. Confirm
   row counts, payload identity and timestamps after decoding.
4. Merge by `ts_init` and the declared tie rule before direct-engine replay.
   Arbitrary custom types are not BacktestDataConfig variants; dynamic queries
   materialize. Node chunk sizes do not cap prior materialization or equal-time
   group size.

**Check:** a JSON-only success must not be labeled an Arrow/catalog round trip.
Assert restored identity, availability and exact consumer sequence; preserve
complete equal-time groups and report memory obligations without dropping rows.

Source anchors: D1, D2, D4, M3, B2.
