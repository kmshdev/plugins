# Capture, reconstruct, and rerun

Choose the replay question first. A durable event-store reconstruction and a
strategy experiment use different entry points in Rust 0.64.0.

| Question | Native path | Result |
| --- | --- | --- |
| What happened in this run? | Event-store writer/reader and forensics replay inputs | Ordered captured commands/events/reports and provenance |
| What native state follows the log? | Sealed-run snapshot plus event-store tail replay | Cache/account/order/position reconstruction |
| Would the strategy decide the same way? | Original inputs/config into BacktestEngine/BacktestNode | Strategy callbacks through native research execution |
| Can an account resume trading? | Node restore plus adapter reports/reconciliation | Current external facts and application admission decision |

## Durable capture and audit

1. Configure the native event-store writer for the supported runtime at the
   composition root and retain its run identity. Confirm that the required
   event families are captured. Custom data, market data catalogs and component
   state have their own codecs/storage paths; a bus publication is not automatic
   durable capture of everything a strategy consumed.
2. Record effective config, instrument definitions, framework/lockfile identity,
   data provenance and any random seeds alongside the run. Keep secrets out of
   research artifacts. Observe writer errors/backpressure rather than treating
   an enqueue as a persisted commit.
3. Stop through the native lifecycle, flush/seal the run and inspect the reader's
   validation result. Keep quarantined/incomplete runs identifiable; do not edit
   a corrupt source log to force validation.
4. Use the sealed-run reader and `plan_forensics_replay_inputs` /
   `load_forensics_replay_inputs` for an ordered audit. Preserve durable sequence
   order, run identity and snapshot boundary. Compare expected captured event
   families with actual coverage before calling the audit complete.

The inspected `EventStoreConfig` defaults include channel capacity 10,000,
maximum batch 100, batch latency 5 ms and `halt_threshold` 250 ms. These are knobs,
not measured latency or losslessness guarantees. Choose bounded settings from
actual input rate and storage behavior; validate capture under failure pressure.

## State reconstruction

`replay_from_run_id` selects a sealed source run. The kernel takes a replay branch,
restores Cache from a validated snapshot plus ordered tail, then skips normal
engines/clients/Trader/reconciliation startup. The event-store
`restore_cache_from_sealed_run` entry point implements this state-only boundary.
It does not replay Strategy callbacks, restore every actor's application state,
or contact the broker. Component `on_save`/`on_load` state is a separate contract.
Validate that order/position/account state and tail sequence match the sealed
artifact; preserve a discrepancy rather than resuming admission from it.

## Research through the same native components

For a Strategy rerun, register the same Actors/Strategies and algorithms in a
BacktestEngine, restore the effective config and instrument definitions, then
feed the original admitted market/custom inputs in availability order. The
catalog replay planning/loading helpers produce ordered event entries and
catalog slices; they do not drive a Strategy or its Clock for you. In this
snapshot their catalog query support covers quotes, trades and bars. Supply
other required data through a separately qualified codec/loader path.

Run the native clock and simulated execution with declared equal-time and fill
assumptions. Compare signal/decision outputs first, then economic outcomes.
Captured execution reports may explain live fills, but do not feed them as if
they were new market signals or assume a simulated venue reproduces a historical
broker. A first divergence may be missing input, configuration, timing, custom
state or simulation assumptions. Keep these causes distinct from strategy bugs.

For an end-to-end capture test, create a bounded synthetic run, flush/seal it,
read it back, assert sequence and event-family coverage, reconstruct state, then
run the separately recorded inputs through the native backtest. The bundled
quickstart currently demonstrates the backtest leg and JSON custom-data leg;
it is not a durable event-store acceptance test.

Official basis: [architecture](https://nautilustrader.io/docs/latest/concepts/architecture/)
and [backtesting](https://nautilustrader.io/docs/latest/concepts/backtesting/).
Version-qualified source: RP1–RP3 and L3. The state-only implementation narrows
a broad “replay through the same execution path” description; it does not justify
promising automatic full strategy replay from an arbitrary captured log.
