# Configure a run without changing strategy code

Use one typed application configuration to construct native components. Separate
strategy parameters from instrument definitions, venue simulation assumptions,
data provenance and live-client settings. Configuration changes inputs; the
same Strategy implementation consumes native IDs and exact values in every mode.

## First runnable experiment

The bundled quickstart accepts a JSON run file. Its two supplied configurations
exercise a currency pair and an equity on different synthetic venues. Run each
configuration in its own process; this also isolates native thread-local state.
The executable validates the configuration before building the engine. See the
local quickstart README for exact commands, fields and expected outcomes.

A production config should carry these concerns explicitly:

| Section | Values and translation |
| --- | --- |
| Identity | TraderId, distinct StrategyId and order_id_tag per Strategy; stable IDs for recovery |
| Strategy | Input/output InstrumentId, side, exact quantity, thresholds and timer intervals |
| Instruments | Authoritative instrument definitions, price/size increments, currency, multiplier, expiry |
| Data | ClientId, provider symbol/contract mapping, schema, time range, source identity and ts_init policy |
| Execution | Venue routing, account type/currency, OMS mode, order capability requirements |
| Backtest | Initial balances, fill/fee/latency models, data identity and random seeds |
| Live | Explicit adapter settings, reconciliation and recovery backing; secrets supplied at runtime |

For another instrument class, construct that native `InstrumentAny` variant
from complete metadata. Do not coerce a future, option or spread into an equity
because its symbol parses. The generic strategy can trade different variants;
qualification, settlement and sizing depend on their actual metadata. A
Databento feed instrument and IB execution contract may have different IDs.
Bind them explicitly at the strategy boundary rather than relabeling events.

## Parse, validate, construct

1. Parse an application-owned serializable struct; use `serde(deny_unknown_fields)`
   for your strict application envelope and explicit defaults for optional fields.
   Use decimal strings for financial inputs. Reject non-finite time/ratio values.
2. Resolve instrument definitions and validate tick/lot alignment, bounds,
   currencies, multiplier and side. Parse exact types fallibly; decide whether
   rounding is allowed instead of silently accepting an off-grid value.
3. Translate once into native `StrategyConfig`, `BacktestEngineConfig` or
   `LiveNodeConfig` builders and adapter configs. Call checked builders/cores;
   avoid carrying raw strings through callbacks.
4. Register actors, strategies, algorithms and instruments, then start the native
   runtime. Change configuration, not the Strategy, for a new experiment.
5. Record the effective non-secret config, lockfile/framework version, data
   digest and seed with results. Re-run from that record in a clean process.

Native `Default`, builder defaults and deserialization defaults are separate
contracts. Unknown-field handling and the meaning of `None` are type-specific:
inspect the actual config rather than assuming one framework-wide policy.
A missing value is not automatically zero or disabled. Use startup validation
for cross-field requirements such as selected execution route versus account.

## Fast parameter sweeps

Generate a finite list of configs, assign each a run ID, and launch the same
binary once per config. Compare canonical economics (orders, fills, positions,
fees and cash) separately from wall-clock timings. Choose a bounded worker count
based on measured memory and CPU use; keep equal-time ordering fixed. Preserve
failed runs and the config that produced them. Increasing trials changes the
research question and requires out-of-sample evaluation; it is not an API fix.

Official basis: [configuration](https://nautilustrader.io/docs/latest/concepts/configuration/),
[Rust backtest](https://nautilustrader.io/docs/latest/how_to/run_rust_backtest/).
Snapshot evidence: source anchors CF1, Q1 and Q2 in the local source ledger.
