# Precision, admission and accounting

Use `Price`, `Quantity`, `Money` and `rust_decimal::Decimal` for discrete
financial values. Floating-point indicator math is not a reason to route order
quantities or balances through `f64`.

## Instrument admission

Fixed representation (9 decimals, or 16 with `high-precision`) is distinct from
instrument precision and grid. A `0.25` tick does not admit `100.13` simply
because both have two decimal places.

Import `nautilus_model::instruments::Instrument`:

```text
try_make_price_from_decimal(Decimal) -> anyhow::Result<Price>
try_make_qty_from_decimal(Decimal, Option<bool>) -> anyhow::Result<Quantity>
try_normalize_price(Price) -> CorrectnessResult<Price>
try_normalize_qty(Quantity) -> CorrectnessResult<Quantity>
```

The make helpers round decimal precision; they do not generally snap arbitrary
tick multiples. Normalize rejects off-grid inputs rather than rounding.
Choose explicit directional rounding for bids/asks/stops, then normalize and
check min/max quantity, notional, price, multiplier and venue-specific rules.
Do not "fix" an invalid protective stop by rounding it without a policy.

## Fixed-risk helper

`nautilus_risk::sizing::calculate_fixed_risk_position_size` accepts:

```text
(&InstrumentAny, entry: Price, stop_loss: Price, equity: Money,
 risk: Decimal, commission_rate: Decimal, exchange_rate: Decimal,
 hard_limit: Option<Decimal>, unit_batch_size: Decimal, units: usize)
 -> CorrectnessResult<Quantity>
```

`risk=0.01` means 1%. Its approximate calculation is:

```text
risk_money = equity * risk
riskable = risk_money - 2 * commission_rate * risk_money
size = riskable / exchange_rate / abs(entry - stop) / multiplier
```

It applies hard limits, per-unit division, batching, maximum quantity and
conversion. This is not a universal realized-loss model.

The function does not enforce risk <= 1, correct stop direction, equity currency
or FX direction, inverse-contract economics, minimum notional, slippage, margin
or complete fees. Zero exchange rate/equity/distance can yield zero size.
Validate inputs and reject zero/non-admissible output before constructing orders.

## RiskEngine versus strategy policy

Keep `bypass=false`. The engine checks relevant submissions/modifications,
precision, GTD, limits, balances/margin, trading state and throttles on the paths
that reach it. It does not implement every application's capital budget,
concentration, daily-loss, stale-price or reservation policy.

The inspected precision checks do not replace modulo-grid normalization.
Missing-account paths can return permissive results; missing/stale account
evidence should explicitly close application admission. Emulator routes have
additional limitations in [Execution](execution.md).
The moving documentation's `full_position_exit_venues` is absent from the
inspected risk config.

## Native position and portfolio facts

Execution owns positions derived from fills. With effective Netting OMS, IDs
are `{instrument_id}-{strategy_id}`; an incompatible explicit ID is denied.
Hedging permits separate position identities. Strategy OMS can fall through to
client OMS and then Netting fallback. Netting does not mean one global position
for every strategy in the application.

Portfolio facade examples:

```text
unrealized_pnl(&InstrumentId) -> Option<Money>
realized_pnl(&InstrumentId) -> Option<Money>
total_pnl(&InstrumentId) -> Option<Money>
net_position(&InstrumentId) -> Decimal
net_exposure(&InstrumentId, Option<&AccountId>) -> Option<Money>
equity(&Venue, Option<&AccountId>) -> IndexMap<Currency, Money>
build_snapshot(&AccountId) -> Option<PortfolioSnapshot>
```

Query accounts through Cache rather than inventing Python's portfolio API.
Keep currency buckets separate unless a declared, current FX conversion exists.
An absent valuation is not zero. Account/configured identity is not broker
discovery, and a saved owned Cache value is not live.

During a fill hook, Cache can already show the new position while the Portfolio
aggregate still awaits the position event. Avoid reserving new risk against a
stale aggregate or double-counting an incremental fill and cumulative position.
Application reservations complement native facts; they must not replace native
order/position reduction.

Evidence: [R1-R4, E1-E4 in the source ledger](sources.md).
