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

## C7: Databento symbol to IBKR execution contract

**Owners:** data integration establishes source/native identity; live composition
selects clients; the Strategy chooses the explicitly mapped execution instrument.

1. Record dataset, provider symbol, native venue and dated contract identity.
   Load definitions before precision-dependent data.
2. Qualify the IB contract and compare expiry, exchange, currency, multiplier,
   tick/lot and conId. Databento identity does not supply IB qualification.
3. Route data and execution independently. Prefer explicit dated raw symbols
   where node subscription symbology differs from direct-client capabilities.
4. Verify provider-specific timestamp and supported feed behavior. Use native
   INTERNAL aggregation over supported base data when node external bars are
   unsupported; do not invent data or a competing application aggregator.

**Check:** reject a mismatched expiry/venue or unqualified contract before order
admission. Reconnect/subscription flags do not establish data-gap recovery.
This mapping is not a credential, entitlement or live-execution qualification.

Source anchors: AD1, AD2, AD3, AD4, AD5, AD6.

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
