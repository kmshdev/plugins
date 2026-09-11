# IBKR and Databento data: native 0.63.0

Read the official [IBKR integration](https://nautilustrader.io/docs/latest/integrations/interactive_brokers/)
and [Databento integration](https://nautilustrader.io/docs/latest/integrations/databento/)
for provider terminology. Use the source anchors in [sources.md](sources.md)
(AD1-AD6) for this snapshot's Rust implementation. Documentation and decoder
coverage alone do not establish a supported node operation.

## Choose the actual API

Databento supplies data, not execution. Native imports include:

```rust
use nautilus_databento::{
    common::Credential,
    data::DatabentoDataClientConfig,
    factories::DatabentoDataClientFactory,
    historical::{DatabentoHistoricalClient, RangeQueryParams},
    loader::DatabentoDataLoader,
};
use nautilus_interactive_brokers::{
    common::enums::IbHistoricalTickType,
    config::{
        InteractiveBrokersDataClientConfig,
        InteractiveBrokersInstrumentProviderConfig,
        MarketDataType, SymbologyMethod,
    },
    factories::InteractiveBrokersDataClientFactory,
    historical::HistoricalInteractiveBrokersClient,
};
```

`DatabentoDataClientConfig::new(key, publishers_path, use_exchange_as_venue,
bars_timestamp_on_close)` is the constructor. Configure `venue_dataset_map`
for routing. The inspected builder's `dataset()` field is not forwarded to the
final config: do not use it as an effective dataset override.
`reconnect_timeout_mins` defaults to `Some(10)`; `None` means indefinite retries.

IB config includes host, port, API client ID, instrument provider, RTH filtering,
market-data type, quote batching, revised-bar policy and timeouts.
Defaults enable RTH and batched quotes, request realtime data, and disable
revised bars. Keep the Python-only provider `filter_callable` unset.
For a reproducible request, state these policies rather than relying on defaults.

## Map identities before joining feeds

Dataset, publisher, venue, provider symbol, native `InstrumentId` and broker
contract are distinct. The Databento loader maps GLBX/XCME/XCBT/XCEC/XNYM to
`GLBX.MDP3`; EQUS defaults to `EQUS.MINI`. Venue-dataset overrides route requests;
they do not necessarily change decoded instrument identity.
`use_exchange_as_venue` allows definitions to refine GLBX venues.
Numeric Databento IDs require date-specific symbology metadata.

Direct Databento live/historical clients infer raw, numeric, parent and continuous
symbology. Factory-backed node subscriptions construct upstream subscriptions
without `stype_in`, then forward them unchanged. Therefore direct-client support
for `ES.c.0` does not prove equivalent node support. Prefer dated raw symbols
until that node path is qualified.

IB provider `load_ids`, JSON `load_contracts`, MIC overrides and
`SymbologyMethod::{Simplified, Raw}` control qualification/naming.
Cached instruments carrying IB `info["contract"]` can seed contract resolution.
An arbitrary Databento instrument does not carry a qualified IB contract.
Maintain an explicit signal-to-execution mapping with dated expiry, exchange,
currency, multiplier, tick size and IB conId. Routing is not qualification.
IB `CONTFUT` is not an orderable dated future.

## Select supported base data

| Path | Supported or limited behavior |
| --- | --- |
| Databento node quotes/trades | Default `mbp-1`/`trades`; supported combined schemas can emit both types |
| Databento node definitions/status/book | Definitions, instrument status and MBO deltas implemented |
| Databento node external live bars/depth10 | No subscription implementation; historical decoders do not change this |
| IB external bars | Five-second realtime-bar API; other supported durations use historical streaming |
| IB revisions | Controlled by `handle_revised_bars`; define consumer revision policy |

Use DataEngine's native internal aggregation for Databento live bars. Inside a
registered actor, after the required instrument is actually in Cache:

```rust
self.subscribe_bars(
    "ESZ6.XCME-1-MINUTE-LAST-INTERNAL".parse()?,
    Some(nautilus_model::identifiers::ClientId::from("DATABENTO")),
    None,
);
```

This is a source-qualified callback fragment, not a subscription to run without
authorization. LAST uses trades; other price types use quotes. The actor still
consumes Bars. Do not duplicate aggregation inside the application.
Require definitions with the right precision before accepting values; subscription
ordering is not proof that definitions arrived.

## Request and qualify history

Databento `DatabentoHistoricalClient::new(Credential, PathBuf,
&'static AtomicTime, bool)` loads publisher metadata and constructs an HTTP client.
`RangeQueryParams` supplies dataset, symbols, `UnixNanos` start/end, limit and
precision. `get_range_bars(params, aggregation, timestamp_on_close)` selects
supported one-second/minute/hour/day OHLCV. Missing precision requires explicit
precision or definitions.

IB `HistoricalInteractiveBrokersClient::connect(data_config).await` actually
connects to TWS/Gateway. Its `request_bars` uses `jiff::Timestamp`, bar-spec
strings, start or duration, contract/ID lists, RTH and timeout; tick requests
use `IbHistoricalTickType`, pagination and limits.

Databento node historical bar requests forward aggregation, not step or price
type. Decoding produces one-unit LAST-EXTERNAL bars. Obtain supported base bars
and aggregate deliberately; requesting five minutes does not prove provider-native
five-minute output. Some request errors are logged and become empty responses.
Distinguish verified empty intervals from failure or unproven completeness.

IB continuous-future historical bar requests drop the end bound and keep only
the first duration segment anchored to now. Results may fall outside a requested
historical interval. Use dated contracts for bounded, reproducible history.
Validate returned identifiers, bounds, gaps, revisions and duplicate policy
before committing catalog data.

## Preserve actual time semantics

Databento trade/quote-like `ts_event` uses capture `ts_recv`; live `ts_init`
is local receipt. OHLCV normally timestamps events at close; historical init
is still close even when the event timestamp is configured at open.

IB tick-by-tick data pairs broker event time with local receipt. Its bar conversion
instead sets both timestamps to computed close, including realtime bars.
Daily conversion subtracts one nanosecond; weekly/monthly values remain unchanged.
Do not interpret all bar `ts_init` as transport arrival. Preserve source-specific
availability semantics and use a separate receipt observation when required.

Databento `connect()` sets a local flag; dataset sessions start lazily with
subscriptions. Debug-logged acknowledgments are not an application readiness
guarantee. The precision lookup can ultimately fall back to USD precision.
Require correct definitions and fresh expected input, not a connected flag.

Entitlements, schema availability, full historical coverage, exchange calendars,
contract qualification and live-feed behavior remain externally unqualified
until demonstrated against the authorized provider. Offline examples cannot
establish any of these facts.
