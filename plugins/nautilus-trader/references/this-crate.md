# Integrating with an existing application

This compatibility page replaces the former host-specific walkthrough.
The skill does not encode a particular strategy, broker, data provider,
database, message schema or risk policy.

Preserve the target application's actor/strategy ownership, causal timestamps,
recovery contract and already-reviewed strategy semantics. A framework example
does not authorize a new order owner or a new market-data path.

For a standalone start, use [Getting started](getting-started.md).
For crate responsibilities, use [Architecture](architecture.md).
For a port, compare [Pitfalls](pitfalls.md) against the compiler-visible source.
Application-specific policy remains in that application's own documentation;
it is not a dependency of this portable bundle.
