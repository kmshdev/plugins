# Brackets, execution and lifecycle races

## Bracket construction

Inside a registered strategy, with instrument-validated values:

```rust
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

// Application-owned field: Option<[ClientOrderId; 3]>, not a framework API.
self.pending_bracket = Some([
    orders[0].client_order_id(),
    orders[1].client_order_id(),
    orders[2].client_order_id(),
]);
self.submit_order_list(orders, None, None, None)?;
```

Import `ContingencyType`, `OrderSide`, `OrderType` from `nautilus_model::enums`, and `Order`
from `nautilus_model::orders` to read `client_order_id()`.
The result is `Vec<OrderAny>` in **entry, stop-loss, take-profit** order.
The shown application field preserves ID correlation before submission; establish
any required risk reservation at that same pre-submit boundary.
Entry linkage is OTO; exit-to-exit linkage is **OUO**, not OCO, in this example.

This snippet is construction, not proof of live protection. Stop/target direction,
quantity, tick alignment, min/max and account admission are caller obligations.

| Builder option | Default / meaning |
| --- | --- |
| `instrument_id`, `order_side`, `quantity` | Required |
| `entry_order_type` | Market |
| `entry_price`, `entry_trigger_price` | Optional; required for applicable entry types |
| `time_in_force`, `expire_time` | GTC / no expiry; entry expiry does not propagate to exits |
| `contingency_type` | OUO, not OCO |
| `tp_order_type`, `tp_price` | Limit / caller-supplied price |
| `tp_post_only` | True; false in this example is a deliberate execution choice |
| `sl_order_type`, `sl_trigger_price` | StopMarket / caller-supplied trigger |
| `tp_time_in_force`, `sl_time_in_force` | GTC |
| `emulation_trigger`, `trigger_instrument_id` | Optional local emulation |
| `entry/tp/sl_client_order_id` | Optional explicit IDs |
| `entry/tp/sl_exec_algorithm_id`, corresponding params | Optional slicing/routing |

Optional setters accept a value (`entry_price(price)`); generated `maybe_*`
setters accept `Option`. `.call()` is not fallible: unsupported types and missing
required type-specific inputs can panic. The underlying `try_bracket` is not
a public fallible facade. Validate before construction rather than catching panics.

| Leg | Supported order types in the inspected bracket factory |
| --- | --- |
| Entry | Market, Limit, MarketIfTouched, LimitIfTouched, StopLimit |
| Target | Limit, LimitIfTouched, MarketIfTouched, TrailingStopMarket, TrailingStopLimit |
| Stop | StopMarket, TrailingStopMarket |

Trailing variants require offsets, offset type and applicable activation/trigger
values. There is no `sl_price`, `sl_post_only` or bracket-level `reduce_only`.
Entry is OTO and not reduce-only; exits are reduce-only, reference entry as parent,
link to each other and share the list ID. `order().create_list(&mut orders, ts)`
only assigns list identity; it is not bracket construction.

## Who enforces what

Ordinary strategy submit caches initialization, publishes it, then queues risk
and execution. For a list, all legs and list metadata are cached before initial
events publish. A method return is local evidence, not an adapter acknowledgment.

Emulated submissions route directly to `OrderEmulator`; release without an
execution algorithm can route directly to execution. A released event sent to
risk's event processor is not a command-level pre-trade gate. Thus the moving
docs' universal "risk checked before hold and again on release" description is
not supported by this inspected call chain.

The snapshot also constructs the strategy `OrderManager` with `active_local=false`;
its selection requires active-local management, and strategy dispatch expects
no manager actions. Do not rely on `manage_contingent_orders=true` to supply the
documented non-local contingency management. Matching-engine, emulator, adapter
and venue behavior must be qualified independently.

Local bracket metadata is not an atomic exchange bracket. Test child release
after partial entry fills, actual child quantities, sibling cancellation and
late dual fills. A "release only after full fill" matching option is not itself
a proportional-sizing policy.

## Reconcile facts, not a single active flag

Track intended quantity, cumulative execution, unresolved leaves, pending command,
position exposure and acknowledged protection as different facts.

| Event or result | Correct response |
| --- | --- |
| `OrderFilled` | Inspect incremental fill and fresh cached cumulative quantities |
| Partial fill while pending cancel/update | Status may remain pending; economics still changed |
| Cancel requested | Retain possible exposure until native facts resolve it |
| Modify/cancel rejected | Prior order may remain working; this is not entry rejection |
| Late fill after cancel | Supported by the model; update exposure and protection |
| `OrderFillVoided` | Corrections can change economics and reopen allowed states |
| Duplicate trade ID | Native duplicate-fill checks prevent counting it twice |
| Submit error | Inspect possible side effects; GTD setup can fail after routing |

Cache order and position updates precede fill publication. Position-event hooks
and Portfolio aggregates occur later. Use fresh Cache for immediate exposure;
use the position-event boundary for post-position accounting.

Do not hold native borrows across commands or publications. Backtest's
`SyncTradingCommandSender` buffers commands, but direct endpoint fallbacks and
initialization/pending events can still be synchronous. Initialize correlation
before calling into the framework.

## Execution algorithms

`nautilus_trading::algorithm` exposes `ExecutionAlgorithm`,
`ExecutionAlgorithmCore`, `ExecutionAlgorithmConfig`, `TwapAlgorithm`,
`TwapAlgorithmConfig`. A custom algorithm implements `DataActor` and uses
`nautilus_execution_algorithm!` with required
`on_order(&mut self, order: OrderAny) -> anyhow::Result<()>`.
Register the algorithm with the runtime as well as selecting its ID on the order.

TWAP accepts market primaries and string-valued algorithm parameters
`horizon_secs` and `interval_secs` in `IndexMap<Ustr, Ustr>`, not command `Params`.
Times must be finite/positive with horizon at least interval. It sends an
immediate slice, uses framework timers, and submits the remainder/primary last.
If slicing falls below increment/minimum it can submit the whole amount.

Spawned orders identify the primary through `exec_spawn_id`; optional primary
reduction must not be counted twice. A pre-acceptance denial/rejection can
restore deducted unexecuted quantity. Cancellation is not blanket permission to
restore and retry. Algorithm submission goes to risk rather than back through
algorithm selection. Slicing and bracket contingencies are different lifecycles;
combining them needs coverage of both.

Evidence: [S1-S4, E1-E6, R1 in the source ledger](sources.md).
