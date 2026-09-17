---
name: integrating-nautilus-data
description: Integrate Nautilus Rust market and custom data, subscriptions, historical requests, live delivery, schemas and catalogs. Provider recipes cover Databento and IBKR. Not trading rules or order execution.
metadata:
  author: kmshdev
  version: "0.64.0"
---

# Integrate data with Nautilus

**Input:** provider or local data, required instruments/schema, time range and
consumption mode. **Output:** correctly identified, causally timestamped native
data and a supported ingestion/subscription path, with explicit coverage limits.

For compilation, use Rust 1.98.1+ and locked `=0.64.0` crates. Obtain the
input's instrument definitions and timestamp semantics before translating it.

## Instructions

1. Identify provider symbols, native instrument IDs and intended consumers.
   Read [the data guide](references/guide.md); for provider differences use
   [IBKR and Databento](references/adapters.md).
2. Preserve instrument precision, source identity and availability timestamps.
   Select supported provider base data and native aggregation; do not infer
   live capability from a decoder or historical method.
3. Implement the requested subscription, historical response, custom codec or
   catalog boundary. Distinguish no response, error and valid empty data.
4. Exercise identity, chronology and decoding at that boundary. Record missing
   entitlements, unsupported feeds or incomplete history rather than silently
   substituting data.

Use [runtime contracts](references/foundation.md),
[connection recipes](references/connections.md) for handover, mapping or catalog replay,
the [native example](assets/quickstart/README.md), and
[source evidence](references/sources.md) as needed. APIs target **0.64.0**;
compiler-visible declarations win over drifting latest-doc examples.

Use [typed run configuration](references/configuration.md),
[component composition](references/composition.md), and the
[Rust test ladder](references/rust-testing.md) when those concerns are affected.
For supported provider extensions, use [adapter development](references/adapter-development.md).

## Examples

- "Give my actor Databento five-minute bars": qualify a dated instrument and
  request native INTERNAL aggregation over supported base data, not external
  node bars or an application aggregator.
- "Persist an original custom payload": follow the guide's separate JSON and
  Arrow registration paths; preserve type, route and availability on readback.
- "Manage partial fills": route to Strategy ownership rather than changing
  the ingestion adapter. Offline native/JSON commands are in the example README;
  that fixture is not a provider acquisition or catalog round-trip test.

Deliver the requested artifact with focused verification and material limits.
Follow the user's authorized scope and the target application's ownership.
