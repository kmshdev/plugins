# Strategy intent, execution and accounting

## Deliver the requested result

Lead with the requested Rust change or diagnosis, then give a short evidence
summary. Include only the relevant contracts, rather than narrating every source
read. For a bracket or lifecycle task, make these decisions explicit:

- Name the native builder/submission path and chosen OTO/OUO relationships;
  distinguish configured reduce-only legs from acknowledged live protection.
- Show where leg IDs, reservations and possible-send state are established
  before commands. Keep risk bypass false and state route-specific limitations.
- State grid/size validation, pending-command versus filled exposure, and the
  callback stage used for Cache/Portfolio reads when those affect the result.

Point to produced artifacts and separate source inspection, compilation,
simulated events and externally observed execution. Do not replace a requested
implementation with a long list of caveats, or suppress an unresolved risk.

## Wiring

Import `DataActor` from `nautilus_common::actor` and
`nautilus_trading::{nautilus_strategy, strategy::{Strategy, StrategyConfig,
StrategyCore}}`. Store one core, implement Debug and DataActor for market/custom
callbacks. Validate config with `StrategyConfig::builder()...build()?`, then
`StrategyCore::new_checked(config)?`. Checked core construction does not replace
full configuration validation.

Use unique strategy/tag identities; `order_id_tag` cannot contain `-`.
`nautilus_strategy!(Type, { /* order/position hooks */ })` already implements
Strategy. A separate `impl Strategy` conflicts. A custom core field is supported.
Access `order()`, `cache()`, `clock()`, `portfolio()` after registration.
`strategy_id()` returns `Option<StrategyId>`.

Data hooks return `anyhow::Result<()>`. Strategy hooks return `()`.
`on_order_filled`, `on_order_canceled`, `on_order_fill_voided` take borrowed events;
rejected/denied/modify-rejected/cancel-rejected hooks take owned events.
Position opened/changed/closed hooks take owned events. Specific hooks precede
generic hooks; user dispatch gates on Running.

## Common order methods

```text
submit_order(OrderAny, Option<PositionId>, Option<ClientId>, Option<Params>)
submit_order_list(Vec<OrderAny>, Option<PositionId>, Option<ClientId>, Option<Params>)
modify_order(ClientOrderId, Option<Quantity>, Option<Price>,
             Option<Price>, Option<ClientId>, Option<Params>)
cancel_order(ClientOrderId, Option<ClientId>, Option<Params>)
cancel_all_orders(InstrumentId, Option<OrderSide>, Option<ClientId>,
                  strategy_only: bool, Option<Params>)
```

All return `anyhow::Result<()>`. Modify's prices are limit and trigger.
Command `Params` is from `nautilus_core`; it is not execution-algorithm parameters.
Cancel-all with `strategy_only=false` broadens ownership scope intentionally.
Close methods create opposite-side market orders; they do not prove flatness.

`order().market(instrument, side, quantity, tif, reduce_only, quote_quantity,
algorithm_id, algorithm_params, tags, client_order_id)` returns `OrderAny`.
The last seven values are optional. Other constructors have different
positional contracts; consult source instead of guessing.

## A limit-entry bracket

Inside a registered strategy, after validating geometry and quantity:

```rust
use nautilus_model::{
    enums::{ContingencyType, OrderSide, OrderType},
    orders::Order,
};
let orders = self.order().bracket()
    .instrument_id(instrument_id)
    .order_side(OrderSide::Buy)
    .quantity(quantity)
    .contingency_type(ContingencyType::Ouo)
    .entry_order_type(OrderType::Limit)
    .entry_price(entry_price)
    .sl_trigger_price(stop_price)
    .tp_price(target_price)
    .tp_post_only(false)
    .call();
// Application field: Option<[ClientOrderId; 3]>, not a framework API.
self.pending_bracket = Some([
    orders[0].client_order_id(),
    orders[1].client_order_id(),
    orders[2].client_order_id(),
]);
self.submit_order_list(orders, None, None, None)?;
```

The vector is entry, stop, target. Entry is OTO; exits are reduce-only and OUO
by default, parent-linked and list-correlated. OCO requires an explicit different
choice. Entry expiry does not propagate to exits. TP defaults post-only true;
false above is an explicit execution choice.

`.call()` can panic on invalid type-specific inputs; there is no public fallible
bracket facade or `sl_price` setter. Supported entries are Market, Limit,
MarketIfTouched, LimitIfTouched and StopLimit. Stops are StopMarket or
TrailingStopMarket; targets additionally support touch/trailing variants.
Validate type-specific triggers/offsets before constructing.

The inspected strategy OrderManager is created with `active_local=false` and
does not provide the documented non-local management guarantee.
`manage_contingent_orders=true` is therefore not proof of child protection.
Emulated submissions/release can route directly to emulator/execution; do not
claim universal pre-hold and post-release RiskEngine checks. Qualify the selected
route, adapter and venue rather than trusting bracket metadata.

## Lifecycle and ordering

Initialization/pending events can publish inline. Record IDs, reservations and
possible-send state before issuing commands. Routing can precede a GTD timer
error: `Err` is not always no-send and must not trigger a blind retry.

Fill events are increments. Re-read cached cumulative filled/leaves quantities
and position. Partial fills may coexist with PendingCancel/PendingUpdate.
Cancel/modify rejection can leave the original order working; canceled orders
can receive late fills. Fill corrections can revise economics. Keep pending
commands, unresolved leaves, exposure and acknowledged protection separate.

Execution updates cached order/position before publishing the fill. Portfolio's
net-position aggregate follows the position event; use fresh Cache for immediate
exposure and the position hook for post-position accounting.
Do not create a competing authoritative position reducer.

## Risk and instrument correctness

Import `Instrument`. `try_make_*_from_decimal` controls decimal precision, not
arbitrary grid alignment. A two-decimal 100.13 is not on a 0.25 grid.
Choose directional rounding and use `try_normalize_price` /
`try_normalize_qty` to reject off-grid values. Check size/notional limits,
currencies, multiplier, stop direction, capital and stale valuation.

RiskEngine's `bypass=false` is necessary but not a complete application policy;
its checks do not repair every off-tick value or deny every missing-account path.
Keep explicit readiness and reservations where the application owns them.

`calculate_fixed_risk_position_size` in `nautilus_risk::sizing` accepts instrument,
entry, stop, equity, risk fraction, commission rate, exchange rate, hard limit,
unit batch size and units. It uses absolute stop distance and multiplier, then
limits/batches. It does not validate stop direction, FX meaning, risk <= 1,
inverse-contract loss or complete venue admission. Zero output is not an order.

Portfolio reads such as `unrealized_pnl(&InstrumentId)` return `Option<Money>`;
`equity(&Venue, Option<&AccountId>)` is currency-keyed. Missing is not zero,
and a configured account is not discovered broker identity.
Effective Netting uses instrument-plus-strategy position IDs; hedging is distinct.

## Algorithms and stop

Native execution algorithms use `ExecutionAlgorithmCore`,
`nautilus_execution_algorithm!` and required `on_order(OrderAny) -> Result<()>`.
Register the algorithm in the runtime and select its ID on primaries.
TWAP accepts Market primaries, string-map `horizon_secs` / `interval_secs`,
positive finite schedule values, and uses framework timers.
It can send the whole quantity if slices are below minimum increments.
Spawn IDs/primary reduction must not be counted twice; algorithm submission
routes to risk rather than recursively selecting the algorithm.

`manage_stop` defaults false. Choose a coherent stop policy; managed market
exits or cancellations remain requests. Allow residual fills and retain
unresolved exposure. Unsubscription alone does not flatten a position.
Exercise the smallest relevant native scenario without changing trading rules.

Evidence: [sources.md](sources.md).

## Additional implementation paths

- [Typed configuration](configuration.md)
- [Complex component composition](composition.md)
- [Rust testing and benchmarks](rust-testing.md)
- [Durable capture and replay](event-replay.md)
- [Databento and IB adapter extension](adapter-development.md)
