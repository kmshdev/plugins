# Strategies and order APIs

A strategy adds order intent and order/position hooks to `DataActor`.
Use `nautilus_trading::{nautilus_strategy, strategy::{Strategy, StrategyConfig,
StrategyCore}}` and `nautilus_common::actor::DataActor`.
The [bounded offline example](../examples/quickstart/src/lib.rs) submits once,
not on every quote.

## Construction and wiring

Store `StrategyCore`, implement `Debug`, and implement `DataActor` for data hooks.
Construct validated configuration with `StrategyConfig::builder()...build()?`,
then `StrategyCore::new_checked(config)?`. The latter checks ID composition,
but does not replace full configuration validation.

Set a unique `strategy_id` and `order_id_tag`. The tag cannot contain `-`.
Do not treat a configured ID as the final runtime ID.

```rust
nautilus_strategy!(MyStrategy, {
    fn on_order_rejected(&mut self, event: OrderRejected) {
        log::warn!("Rejected: {}", event.reason);
    }
});
```

Import `OrderRejected` from `nautilus_model::events`. The macro generates
`Strategy`, native core wiring and `config() -> &StrategyConfig`; a second
`impl Strategy` conflicts. Custom core fields use
`nautilus_strategy!(MyStrategy, field, { /* hooks */ })`.

Use `self.order()`, `self.cache()`, `self.clock()`, `self.portfolio()` and
`self.strategy_id()` in ordinary logic. `strategy_id()` returns
`Option<StrategyId>`. Order/portfolio access before registration can panic.
Cache facade reads return owned snapshots: retain IDs and re-query when state
matters instead of expecting a saved `OrderAny` to update.

## Exact common methods

All these strategy operations return `anyhow::Result<()>`.
`Params` is `nautilus_core::Params`; it is not the algorithm's string map.

```text
submit_order(OrderAny, Option<PositionId>, Option<ClientId>, Option<Params>)
submit_order_list(Vec<OrderAny>, Option<PositionId>, Option<ClientId>, Option<Params>)
modify_order(ClientOrderId, Option<Quantity>, Option<Price>,
             Option<Price>, Option<ClientId>, Option<Params>)
cancel_order(ClientOrderId, Option<ClientId>, Option<Params>)
cancel_orders(Vec<ClientOrderId>, Option<ClientId>, Option<Params>)
cancel_all_orders(InstrumentId, Option<OrderSide>, Option<ClientId>,
                  strategy_only: bool, Option<Params>)
```

For modify, the two prices are limit and trigger. `modify_orders` takes
`Vec<BatchModifyOrder>`, client and params; each tuple is
`(ClientOrderId, Option<Quantity>, Option<Price>, Option<Price>)`.
Batch modifications target one instrument and reject active-local/emulated cases.
`strategy_only = false` on cancel-all intentionally broadens ownership scope.

```text
close_position(&Position, Option<ClientId>, Option<Vec<Ustr>>,
               Option<TimeInForce>, Option<bool>, Option<bool>, Option<Params>)
close_all_positions(InstrumentId, Option<PositionSide>, Option<ClientId>,
                    Option<Vec<Ustr>>, Option<TimeInForce>,
                    Option<bool>, Option<bool>, Option<Params>)
```

The booleans are reduce-only and quote-quantity. Close requests produce market
orders; they do not synchronously prove flatness. Close-all filters this strategy.

`order().market(instrument, side, quantity, tif, reduce_only, quote_quantity,
algorithm_id, algorithm_params, tags, client_order_id)` returns `OrderAny`.
The last seven arguments are optional. Other constructors include `limit`,
`stop_market`, `stop_limit`, market/limit-if-touched, market-to-limit and trailing
stops. Their positional signatures differ: inspect the owning declaration rather
than extrapolating. Public constructors can panic on invalid inputs.

For named bracket construction and precise leg semantics, read
[Execution](execution.md). Do not fabricate `sl_price` or a `.build()?` finish.

## Hooks are not uniformly by value

| Hook | Input |
| --- | --- |
| `on_order_filled`, `on_order_canceled`, `on_order_fill_voided` | borrowed event |
| `on_order_rejected`, `on_order_denied` | owned event |
| `on_order_modify_rejected`, `on_order_cancel_rejected` | owned event |
| `on_order_event` | owned `OrderEventAny` |
| `on_position_opened`, `on_position_changed`, `on_position_closed` | owned event |
| `on_position_event` | owned `PositionEvent` |

These hooks return `()`, unlike data hooks. Specific hooks precede generic hooks.
User order/position dispatch gates on Running. `PositionAdjusted` does not reach
the generic strategy position hook on the inspected path.

Initialization and locally applied pending events can publish inline inside
submit/modify/cancel. Install correlation IDs and conservative local admission
state before the call. `Ok` is not acceptance; `Err` is not always "nothing sent":
GTD timer setup follows routing. Do not blindly retry an ambiguous submission.

## Stop and ownership

`manage_stop` defaults false. Enabling it requests managed market exits, with
interval/attempt/TIF/reduce-only configuration; it does not guarantee fills.
Choose one coherent stop policy, observe residual exposure and pending commands,
and allow the runtime to drain events. Unsubscribing alone is not flattening.

Multiple strategies and execution algorithms are supported by the framework.
Keep application-specific admission/reservations with the application's chosen
order owner rather than creating a competing execution engine.

Evidence: [S1-S4, E1-E4 in the source ledger](sources.md).
