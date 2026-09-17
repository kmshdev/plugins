# Databento data with IBKR execution: native 0.64.0

This is construction and lifecycle guidance, not permission to connect or trade.
Read the official [Rust live how-to](https://nautilustrader.io/docs/latest/how_to/run_rust_live_trading/),
[IBKR](https://nautilustrader.io/docs/latest/integrations/interactive_brokers/)
and [Databento](https://nautilustrader.io/docs/latest/integrations/databento/)
guides for context. [Source evidence](sources.md), AR1-AR4 and AD1-AD6, qualifies
the native paths below; moving Python examples are not Rust declarations.

## Construction boundary

Use exact `=0.64.0` dependencies with defaults disabled:
`nautilus-live` feature `node`, `nautilus-databento` features
`live, high-precision`, `nautilus-interactive-brokers` feature `execution`,
and matching `nautilus-common`/`nautilus-model` (`high-precision`).
No Python, `extension-module` or IB `gateway` orchestration is required for
externally managed TWS/Gateway.

The following original sketch accepts explicit config rather than discovering
credentials or assuming a paper account/port. It is source-qualified, not a
separately compiled/provider-qualified example:

```rust
use nautilus_common::enums::Environment;
use nautilus_databento::{
    data::DatabentoDataClientConfig,
    factories::DatabentoDataClientFactory,
};
use nautilus_interactive_brokers::{
    config::InteractiveBrokersExecutionClientConfig,
    factories::InteractiveBrokersExecutionClientFactory,
};
use nautilus_live::{
    config::{LiveRiskEngineConfig, RoutingConfig},
    node::LiveNode,
};
use nautilus_model::identifiers::TraderId;

fn construct_only(
    trader: TraderId,
    data: DatabentoDataClientConfig,
    execution: InteractiveBrokersExecutionClientConfig,
) -> anyhow::Result<LiveNode> {
    LiveNode::builder(trader, Environment::Live)?
        .with_reconciliation(true)
        .with_risk_engine_config(LiveRiskEngineConfig {
            bypass: false,
            ..Default::default()
        })
        .add_data_client_with_routing(
            None,
            Box::new(DatabentoDataClientFactory::new()),
            Box::new(data),
            RoutingConfig::builder().default(true).build(),
        )?
        .add_exec_client_with_routing(
            None,
            Box::new(InteractiveBrokersExecutionClientFactory::new()),
            Box::new(execution),
            RoutingConfig::builder().default(true).build(),
        )?
        .build()
}
```

Data and execution have independent default routes. Default names are DATABENTO
and IB. Build can read publisher metadata and construct clients, but this sketch
does not call `start` or `run`. Do not execute upstream execution testers to
check APIs: some deliberately open positions and close them on stop.

Nautilus sandbox uses local matching against live data. IB paper is an external
broker session. `Environment::Live`, delayed market data, and conventional
paper ports do not establish an authorized paper account.

## Admit only with evidence

Live startup prepares state, connects data, processes instruments, connects
execution, waits for engines, reconciles and starts the trader.
`start().await` is not a substitute for `run().await` servicing the event loop.

IB configuration can normalize a provided account string without broker
discovery. Confirm real account identity and mode. Qualify the IB execution
contract separately from the Databento signal instrument, retaining expiry,
exchange, currency, multiplier, tick and conId. Resolve mapping before order
admission; an equal-looking native ID is insufficient.

IB startup may warn and continue after account-summary or position initialization
failure. Native reconciliation may warn and continue on `Ok(None)` mass status.
Databento's connected flag does not establish an active dataset session:
subscriptions are lazy and precision can fall back. Require actual correct
instrument metadata and fresh expected data.

| IB report | Coverage limitation |
| --- | --- |
| Order status | Open-order basis; non-open queries may synthesize filled reports from positions, not a complete closed-order ledger |
| Fills | Execution/commission join; unmatched executions skipped with warnings |
| Positions | Account/instrument resolution; targeted absence can become a synthetic flat report |
| Mass status | Combines report families; `Some` does not remove their coverage limitations |

The inspected fill-report filter uses the normalized Nautilus account string
directly as the IB account code; submission strips an issuer prefix and positions
use a raw-account helper. Treat historical fill coverage for that exact route as
unresolved until broker-qualified. Do not work around it with inferred trades.
Missing, unsupported, failed and complete-empty reports are different outcomes.
Gate new exposure on the coverage required by the application, not merely
`with_reconciliation(true)`.

## Recover without inventing continuity

Databento runs one feed handler per dataset. Default retries are bounded to ten
minutes with exponential delay/jitter; unbounded mode permits longer delays.
Subscriptions are restored but replay start anchors are stripped.
Reconnect is not proof of backfill or gap closure. Granular unsubscribe warns
and is ignored; node MBO subscriptions do not request an initial snapshot.
Quarantine incomplete books/intervals until continuity is re-established.

IB data/execution/history share the connection keyed by `(host, port, client_id)`.
The active path is `shared_client::get_or_connect`; utility watchdog types alone
do not prove that every client is wired into watchdog recovery.
Data-farm recovery and historical-bar resubscription exist. They do not establish
complete order/account recovery after arbitrary socket or Gateway restart.

Preserve stable intent IDs and possible-send state, reconstruct local state,
obtain sufficiently complete external reports, resolve discrepancies, then
re-admit. Never retry an ambiguous submit merely because a callback was lost.
Do not flush recovery Cache or replace native reducers with inferred broker state.

Shutdown must service late execution events, save configured component state,
disconnect and close recording resources. A cancel/flatten request is not its
confirmation. Report remaining orders and exposure explicitly.

No live entitlement, account, restart, order acceptance, bracket/OCA protection
or broker completeness claim is established by this document or local tests.
