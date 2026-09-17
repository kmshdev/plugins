# Construction-only live composition

This independent Rust package verifies that NautilusTrader `0.64.0` can build
and dispose a `LiveNode` using a Databento data factory and an Interactive
Brokers execution factory. It uses fixed placeholder values and a minimal,
public Databento publisher fixture. It does not read environment variables,
start or run the node, connect to either provider, submit orders, or load
instruments.

From this directory, run:

```sh
cargo run --locked
```

Expected output:

```text
live-node construction complete; no clients started
```

The package configures reconciliation and leaves `LiveRiskEngineConfig::bypass`
false. Passing this smoke test establishes only dependency/API compatibility and
local factory construction. It does not establish provider entitlements,
credential validity, IBKR account mode, network connectivity, reconciliation
coverage, market-data delivery, venue acceptance, or protective-order behavior.
