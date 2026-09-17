# Cross-component recipes: Rust 0.64.0

Select the path that explains the task; do not load every recipe before editing.
These recipes connect the workflow guides, not new engines or new skills.
Use [the runtime contract](foundation.md) for shared ownership and
[source evidence](sources.md) for the anchor IDs below.

Record the input identities, command/correlation IDs, causal timestamps,
component lifecycle and observed outcome at each boundary. A request return,
callback count or startup flag alone is not completion evidence. The checks
below are acceptance specifications, not claims that every scenario was run.

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

## C5: Restore to reconcile to admission to shutdown

**Owners:** kernel/node restore and service the runtime; execution clients report
external facts; the Strategy owns its admission and unresolved-intent policy.

1. Separate Cache backing, versioned component snapshots, historical catalogs
   and event history. Restore stable IDs and unresolved intent without flushing
   the recovery basis.
2. Keep reconciliation enabled. Establish actual account identity and required
   order/fill/position report coverage; a missing report is not a complete empty
   report. Successful startup may coexist with warnings and absent mass status.
3. Reopen admission only after reconciling possible-send intent, external state,
   fresh instruments/data and application-owned readiness requirements.
4. On stop, execute the chosen component policy while the native grace period
   can drain residual events. Record confirmed terminal state, unresolved
   exposure and persistence/flush outcome before declaring completion.

**Check:** missing/contradictory reports block new exposure; repeated recovery
does not duplicate intent. Cache-only event-store replay does not replay Strategy
callbacks or restore application-owned strategy state. Component snapshot/load,
broker reconciliation and feed-gap repair remain separate requirements. Do not
run connected checks without separate authorization.

Source anchors: L1, L2, L3, AR2.

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
