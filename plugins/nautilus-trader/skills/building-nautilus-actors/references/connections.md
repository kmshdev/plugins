# Cross-component recipes: Rust 0.64.0

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
