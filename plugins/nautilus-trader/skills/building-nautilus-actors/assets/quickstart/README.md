# Order-free actor quickstart

Independent Rust 2024 package pinned to Nautilus 0.63.0; requires Rust 1.98.0.
From this directory run `cargo test --locked`, then `cargo run --locked`.
With cached dependencies use `--offline`; an initial build may download crates.
The program is entirely synthetic and makes no provider calls.

Read [the actor and JSON test](src/lib.rs), [native replay wiring](src/main.rs),
and [dependency features](Cargo.toml). The shared manifest includes the native
backtest dependency graph; this program registers no Strategy, has no order
submission code and creates no exposure.

Expected output: `inputs=5 quotes=4 signals=1 orders=0 positions=0`.
QuoteCounter receives four native quotes and one separately injected immutable
custom signal. Native BacktestEngine owns registration, clock, Cache and dispatch.
The JSON test is not an Arrow/catalog round trip or live-provider qualification.
