# Native runtime composition and evidence

## Deliver the requested result

Lead with the requested construction artifact or readiness/recovery diagnosis.
Make the relevant operational decisions visible in a compact summary:

- State data and execution routes separately, with reconciliation enabled,
  risk bypass false and the exact boundary exercised: build, start or observed
  provider operation.
- Distinguish configured account/port from confirmed identity; missing or
  unsupported reports from complete empty reports; and local connection flags
  from required instrument/data/report readiness.
- On recovery, name what restores Cache, what restores application-owned
  component state and what establishes external truth. On stop, report remaining
  exposure and persistence outcome, not just requested cancellation.

Link produced artifacts rather than repeat the entire source investigation.
No concise summary may turn an unqualified external condition into success.

## Scope and environment

Compose native `LiveNode` with feature `node`, validated client factories and
concrete actors/strategies. Keep the kernel's clock, Cache, Portfolio, engines
and lifecycle rather than adding parallel runtime owners.
Adapter recipes are restricted to Databento and Interactive Brokers.

Construction-only checks do not start connections. Sandbox means real-time
data with simulated execution; Live includes paper or real external execution.
Neither a port nor an environment enum proves account mode.
Do not run a provider example just to learn its types: execution testers can
open positions and request exits on stop.

## Client wiring

The builder accepts factory/config pairs through `add_data_client` and
`add_exec_client`, each with an optional name. Factories downcast to their
matching typed configs. Configure data and execution routing independently;
default data client and default execution client are not mutually exclusive.

Use the source-qualified construction sketch in [adapters.md](adapters.md).
It keeps reconciliation enabled and risk bypass false.
Map signal instruments to qualified execution contracts explicitly; data from
Databento does not supply IB contract metadata automatically.

After build and component registration, `run().await` owns the event loop.
`start().await` performs startup but does not replace continued processing.
Callbacks must stay bounded; a live async outer loop does not make actor guards
or `Rc<RefCell<_>>` safe to send across threads.

## Built-in sandbox composition

Sandbox is native simulated execution, not another external provider adapter.
Add `nautilus-sandbox = { version = "=0.63.0", default-features = false,
features = ["high-precision"] }` when this path is requested.
Its factory implements `SimulatedExecutionClientFactory`, not the live
execution-factory trait. Register it with `add_simulated_exec_client`.
This source-qualified fragment replaces IB execution in the construction sketch:

```rust
use nautilus_sandbox::{
    SandboxExecutionClientConfig, SandboxExecutionClientFactory,
};

fn construct_sandbox(
    trader: TraderId,
    data: DatabentoDataClientConfig,
    simulation: SandboxExecutionClientConfig,
) -> anyhow::Result<LiveNode> {
    let venue = simulation.venue.to_string();
    LiveNode::builder(trader, Environment::Live)?
        .with_reconciliation(true)
        .with_risk_engine_config(LiveRiskEngineConfig {
            bypass: false,
            ..Default::default()
        })
        .add_data_client(None, Box::new(DatabentoDataClientFactory::new()), Box::new(data))?
        .add_simulated_exec_client(
            Some(venue),
            Box::new(SandboxExecutionClientFactory::new()),
            Box::new(simulation),
        )?
        .build()
}
```

Reuse the imports from the construction sketch in [adapters.md](adapters.md).
This fragment was source-inspected, not compiled or connected. The native
example uses `Environment::Live` with simulated execution: environment labels
alone do not select the order destination.

Specify synthetic `account_id`, the actual decoded instrument venue,
`starting_balances`, OMS/account type, base currency, leverage and book/fill
assumptions. The default balance list is empty. Match the sandbox venue to the
Databento instrument venue; simulation subscribes to that venue's native bus
data and needs its instrument in Cache. Setting `use_exchange_as_venue` on the
data config may be necessary for the intended MIC identity.
Fee/fill models are runtime-only values, not serializable config objects.

Do not also register an IB execution route for the same intended simulation
universe. Verify the installed client map before authorizing runtime startup.
The sandbox uses the native matching engine and generates local account state;
it provides no broker report, market impact or live protective-order proof.
Databento data access still requires separate authorization and entitlement.

## Readiness is an admission policy

Startup prepares persisted Cache, starts the kernel, connects data clients and
processes instruments, connects execution clients, reconciles reports, restores
component state and starts the trader.
The inspected startup path can warn and continue after an absent mass-status
report. Successful startup is not complete broker truth.

Require the actual evidence the application needs: authorized account identity,
qualified instruments, fresh data, order/position/account coverage, unresolved
intent reconciliation and no contradictory state. Distinguish an unsupported
report API, an error, a missing response and a complete empty report.
Databento's local connected flag alone does not prove a dataset session or data
entitlement; first valid expected data matters.

Configured IB account normalization can produce an ID without broker discovery.
Never admit from a default/fallback account value.
Keep reconciliation enabled but do not treat that setting as evidence itself.

## Persistence and restart

Cache backing preserves current domain state; catalogs hold research inputs;
component save/load preserves application state; event stores record/reconstruct
history. Portfolio is derived accounting, not a persistence substitute.

Keep stable component IDs and explicit snapshot schemas. Save/load callbacks
need runtime backing configured. Cache loading may occur during startup.
Do not flush the Cache on a recovery path: it removes the recovery basis.

Event-store replay reconstructs Cache and skips normal engines/clients/trader
startup and live reconciliation. It is not a strategy backtest or a second
trading authority. Cache-only replay does not replay Strategy callbacks or
restore application-owned strategy state; component snapshot/load is a separate
contract. Neither Cache reconstruction nor component restoration substitutes
for broker reconciliation or repairs a missing market-data interval.
Reconcile possible-send intent before retrying. A missing callback or local
submit error does not prove the broker never saw a command.

## Shutdown and diagnostics

Request stop, execute component policy, drain residual execution events during
the grace period, disconnect clients, save configured state, stop engines,
cancel timers and seal event history. A process kill does not establish these
outcomes. Report unresolved orders/exposure; requests to cancel or flatten are
not confirmed terminal facts.

Trace readiness failures through client creation -> connection -> instruments ->
reports -> recovered application state. Trace a stale callback through owner
thread dispatch and lifecycle, not a new background trading task.
Use supported owner-thread ingress/control for bounded external work.

Live `streaming=Some(...)` is rejected by this inspected Rust snapshot.
Feather's convenience subscriber blocks and logs errors; it is not automatic
durable, fail-closed live recording. Any recording path needs explicit ownership,
backpressure/error policy and flush/close evidence.

No infrastructure platform, secret manager, database provisioning or real account
access is implied by this skill. Return exactly the construction/operation
evidence requested and identify externally unqualified claims.

## Operational decision table

| Observation | Next action | Required outcome before continuing |
| --- | --- | --- |
| Construction fails | Fix the named config/metadata error; do not start clients | Successful native build with intended client map |
| Authorized start returns but no processing continues | Let the native `run` lifecycle service events | Ongoing expected input and complete admission evidence |
| Account/report coverage is missing or contradictory | Keep new exposure gated; use the authorized report path | Account identity plus sufficient order/fill/position coverage |
| Reconnect restores subscriptions | Detect gaps, restore required inputs and reconcile possible-send intent | Fresh data and no unresolved admission-critical discrepancy |
| Stop requested with open intent | Use native stop policy and grace-period event draining | Report actual terminal orders/exposure and persistence outcome, or an explicit unresolved state |

Evidence: [sources.md](sources.md).

## Additional implementation paths

- [Typed configuration](configuration.md)
- [Complex component composition](composition.md)
- [Rust testing and benchmarks](rust-testing.md)
- [Durable capture and replay](event-replay.md)
- [Databento and IB adapter extension](adapter-development.md)
