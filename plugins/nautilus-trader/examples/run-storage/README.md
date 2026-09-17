# Native run-storage smoke

Rust 1.98.1+, exact NautilusTrader 0.64.0 dependencies, with PostgreSQL/Redis,
live/backtest streaming and object_store cloud features compiled.

```sh
cargo test --locked
cargo run --locked -- /tmp/run-storage-check
```

With dependencies cached, add `--offline`. Each execution constructs one fresh
sandbox LiveNode/instance, attaches an explicit native Feather writer, publishes
one synthetic quote through the native bus, detaches/closes the writer, disposes
the node, explicitly converts
`quotes` to Parquet and reads it through DataFusion. It asserts the complete
quote, including instrument identity, values and distinct event/availability times.
It writes under a fresh UUID directory and leaves executable-run artifacts for inspection.
Rust 0.64 rejects `LiveNodeConfig.streaming`; a second regression verifies that
guard. The tested composition uses public `FeatherWriter` subscription/lifecycle
APIs instead, with the native streaming/cloud dependencies enabled. It does not
remove the guard or claim the kernel automatically owns this explicit writer.
The built-in subscription helper blocks inside its callbacks. A third regression
proves it panics inside an async Tokio context; the successful round trip runs
outside that context. A real live runner needs application-owned async writer
integration, not this synchronous helper copied into its event loop.

The Redis Cache factory is installed but the node is never started, so it does
not connect. PostgreSQL factory typing and backtest streaming configuration are
compile-checked without opening a database or another kernel. No cloud URI,
account credential, broker client or trading Strategy is used.

This is local native streaming/catalog evidence, not PostgreSQL/Redis durability,
cloud readback, provider connectivity, full live shutdown, or a production runner.
