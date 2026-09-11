# Version-specific pitfalls

These qualifications describe the inspected 0.63.0 snapshot. They are not claims
about every future `latest` page or every artifact declaring that version.

| Tempting assumption | Pinned Rust contract |
| --- | --- |
| Copy `0.62` from the latest Rust setup page | Exact `=0.63.0`; compare compiler source on disagreement |
| All 0.63.0 trees are identical | Snapshot hashes identify the evidence; a version alone does not |
| `test-support` is the snapshot model feature | Inspected manifest exposes `stubs`; registry examples may differ |
| `#[nautilus_actor]`, `@strategy` | Invocation `nautilus_actor!(Type)` / `nautilus_strategy!(Type)` |
| Macro plus manual `impl Strategy` | Macro already implements `Strategy`; put overrides in its block |
| `on_quote_tick`, `on_trade_tick`, `on_custom_data` | `on_quote`, `on_trade`, `on_data` |
| Orders in the `DataActor` impl | Order/position hooks go in the strategy macro |
| All order events owned | Fill/cancel/fill-void hooks borrow; rejection hooks take ownership |
| `CustomData::new(route, payload)` | Rust takes `payload, route` |
| `DataType.identifier` isolates topics | Only type/topic metadata partitions delivery |
| `ensure_custom_data_registered::<T>()?` | Arrow helper returns `()`; JSON helper returns `Result` |
| `order().bracket().build()?` | Builder finishes `.call()` and returns `Vec<OrderAny>` |
| Bracket exits default OCO | Default OUO; returned order is entry, stop, target |
| `create_list` establishes protection | It assigns list identity, not contingency relationships |
| `manage_contingent_orders=true` proves live protection | Inspected strategy manager path does not implement that guarantee |
| Emulation always risk-checks both before hold and after release | Direct emulator/release routes contradict that universal claim |
| Risk bypass false validates every tick multiple | Explicit instrument normalization is still needed |
| Cached position and Portfolio aggregate update together | Fill hook sees Cache first; position-event accounting follows |
| `Err` from submit means no effects | Routing may precede a later GTD setup error |
| Cancel acknowledgment forbids later fill | Model supports late fills; inspect cumulative economics |
| Data hook `Err` faults component | Dispatch logs it; explicit fail-closed behavior is application policy |
| `request_bars` loads replay warm-up automatically | Built-in backtest historical request methods are no-ops |
| Multiple run configs per `BacktestNode` | Snapshot validates exactly one |
| Multi-config catalog streaming bounds all memory | Inputs are materialized/merged before chunking |
| `chunk_size` is a hard cap | Same-`ts_init` batches expand it |
| Live `streaming` config records Feather automatically | Rust live runtime rejects that config |
| Event-store replay reruns trading decisions | Cache reconstruction skips normal trader/client startup |
| Successful startup proves broker truth | Missing mass-status reports can warn and continue |
| Framework example uses broker-safe production defaults | Examples are plumbing; qualification is separate |

See [Execution](execution.md), [Market data](market-data.md),
[Live runtime](live.md) and [source ledger](sources.md) for causes and evidence.
Do not work around a discrepancy by changing an application's risk or ownership
policy. Establish the exact source and choose a supported path.
