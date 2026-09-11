# Extend Databento or Interactive Brokers in Rust

Keep the strategy on native data/order APIs. Adapter work translates provider
identity, transport and messages into those APIs; it does not duplicate signal
logic, Portfolio or execution reduction. This package's provider-specific
extension recipes cover only Databento and Interactive Brokers.

## Implement the missing boundary

1. Reproduce one unsupported request or translation with a captured/redacted
   provider fixture or a deterministic transport stub. Write down the exact
   schema, symbol/contract identity and provider timestamp meaning.
2. Find the native `DataClient` or execution-client trait and the selected
   factory/config. Trace the implemented method, its lower-level transport,
   decoder, output sender and DataEngine/ExecutionEngine consumer. A default
   trait method can return success without doing useful provider work.
3. Implement the smallest missing route. Map identifiers and exact financial
   values using native definitions; translate timestamps deliberately. Keep
   request correlation and subscription identity through retries/unsubscribe.
4. Translate execution acknowledgments, fills, rejections and reports into
   native events/reports using stable broker/client IDs. Let ExecutionEngine
   own order/position state. Handle duplicate IDs and uncertain sends without
   silently resubmitting an order.
5. Register through the native factory and feature gates. Check the Rust-only
   dependency graph, then test the native client-to-engine delivery boundary.
   Add a finite network-fault test when changing reconnect or backpressure.
6. Update the capability table: implemented transport, node method, historical
   and live support, tested fixture and remaining provider acceptance evidence.

## Databento example: bars/depth are separate surfaces

The pinned node client implements selected subscriptions and historical
requests. Low-level DBN decoding or live-client support does not imply a matching
node `DataClient` method. In the audited snapshot external live bar and MBP-10
node subscriptions are not implemented. For supported quote/trade input and
native INTERNAL bars, use DataEngine aggregation. To extend a node subscription,
wire schema selection, lower-level delivery and native message conversion,
then assert an actual subscription receives data and unsubscribe terminates it.
Historical decoding and catalog serialization require their own round-trip test.

Preserve the Databento dataset/publisher mapping and dated instrument identity.
Do not map a continuous contract to an IB executable contract by string equality.
A provider integration test needs actual entitlement and schema availability;
the offline fixture proves translation only.

## IB example: contract and report translation

Qualify the full contract, retain conId and trading class/exchange/currency fields,
and use the existing shared-client/factory ownership when data and execution
share a connection. Trace account filters and all required report paths. A
method returning an empty collection is not evidence that no broker orders exist.
A cancel or socket-write success is not order acceptance; preserve broker
correlation so late fills and reconnect reports converge through native state.

Provider pacing and permissions are external constraints. The current Nautilus
IB page points to IB's rules without a universal numeric request-rate guarantee;
measure and cite the applicable primary rule before introducing a limiter.
Use the existing retry/pacing behavior where supported, with finite bounds and
observable rejection. Do not invent a rate from a connection timeout.

## Completion evidence

A useful extension receipt contains: version/features; the previously missing
method; fixture and native output; identity/time/precision checks; subscription
or report coverage; and provider acceptance status. Rust compilation and
synthetic dispatch are quick local gates. Account-specific capability is a
separate observation, not a reason to postpone the implementable fixture work.

Official basis: [adapter development](https://nautilustrader.io/docs/latest/concepts/adapters/),
[Databento](https://nautilustrader.io/docs/latest/integrations/databento/),
[Interactive Brokers](https://nautilustrader.io/docs/latest/integrations/ib/).
Source evidence: AX1 and AD/AR anchors in the local ledger.
