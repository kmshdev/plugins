# Compose complex native strategies

Start with the smallest component chain that implements the requested behavior.
Nautilus already provides Clock, Cache, MessageBus, Portfolio, data/risk/execution
engines and lifecycle. Reuse them and place only strategy-specific decisions in
application components. The framework supports multiple Strategies; an
application may deliberately choose a single order owner.

## Quoter and hedger on one engine

| Component | Owns | Native interaction |
| --- | --- | --- |
| Market observer Actor | Fair-value inputs, indicators, availability and staleness | Subscribe to quotes/bars; publish immutable custom observations |
| Quoter Strategy | Quote intent, its own order IDs, outstanding replacements | Read instrument/Cache; submit/modify/cancel native limit orders |
| Hedger Strategy | Hedge targets and its own working hedge orders | Observe portfolio/position changes and signal; create hedge orders |
| Execution algorithm | Child scheduling for a selected primary order | Native algorithm ID, timer callbacks, spawn identity and risk submission |
| Portfolio | Account/position accounting | Native events update accounting; strategies query the facade |
| Clock/kernel | Time, dispatch and component lifecycle | Native timers, registration, start/stop/reset |

Give Strategies distinct StrategyIds and order tags, even on the same instrument.
Make the observer's output independent of order events to avoid an inline
publication cycle. A hedge policy can map a signal instrument to a separate
execution instrument and currency. Use actual multiplier/FX conversion and
explicit maximum exposure; a quantity of one has different economic meaning
for a share, future or option.

Implementation sequence:

1. Add the observer and assert one immutable observation per admitted input.
   Keep indicator updates in one owner; attach causal timestamps and source IDs.
2. Add the quoter with configurable spread/size and a finite staleness timeout.
   Read exact tick/lot metadata. Record IDs and intended replacement state before
   commands, then resolve pending changes using native events.
3. Add the hedger using fresh Cache position facts at the relevant position
   boundary and Portfolio for valuation. Compute target minus actual exposure
   minus possible outstanding hedge quantity, so repeated notifications do not
   submit the same hedge repeatedly. Test delayed/partial fills and cancel races.
4. If both consume a shared capital budget, choose one application admission
   coordinator for reservations. It models pending intent only; Portfolio and
   execution remain the authorities for account balances and positions. Release
   reservations on proved outcomes, including uncertain-send and late-fill paths.
5. Register the components in the same BacktestEngine, feed a short deterministic
   scenario and inspect quoter and hedger outcomes independently. Reuse their
   configuration/logic in LiveNode; change adapter wiring at the composition root.

The snapshot's grid market maker and composite market maker configurations show
instrument IDs, sizing, position limits and separate signal/execution identity.
They are source patterns, not an adapter recommendation. Provider-specific
recipes in this package remain Databento and Interactive Brokers.

## Execution workflows

Use native `TwapAlgorithm` for a supported market primary when time slicing is
needed. Configure and register its algorithm ID, attach `horizon_secs` and
`interval_secs` as string-valued algorithm parameters on the order, and account
for the primary/child relationship through `exec_spawn_id`. Test intervals,
minimum child size, cancellation and partial execution. TWAP scheduling does
not by itself manage a protective bracket or prove liquidity.

For maker quotes, choose post-only limit orders and handle rejection without a
busy retry loop. For exposure reduction, choose reduce-only where the selected
route supports it and size using native exposure. For entry-plus-protection use
the order guide's OTO/OUO bracket path. An OCO pair cancels its sibling when the
triggering lifecycle action occurs; OUO updates sibling quantity; OTO releases
children. Those relationships are separate from exchange support and atomicity.

An `OrderList` can contain mixed instruments on one venue in the inspected model,
but its representative instrument is the first order. Risk aggregation and
adapter routing must support your intended combination. Do not infer a native
exchange combo/spread from a generic multi-order list.

## Minimal useful acceptance scenario

Replay a fair-value change, quote acceptance, partial quote fill, hedge creation,
partial hedge fill and late quote fill. Assert per-Strategy IDs, total native
exposure, outstanding leaves and no duplicate hedge. Repeat with the same input
and config; report the first divergent economic event. Add recovery or timer
simulation only when that boundary is part of the task.

Official basis: [architecture](https://nautilustrader.io/docs/latest/concepts/architecture/),
[strategies](https://nautilustrader.io/docs/latest/concepts/strategies/),
[orders](https://nautilustrader.io/docs/latest/concepts/orders/).
Source evidence: CP1 and the existing S/E/R anchors in the local ledger.
