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
