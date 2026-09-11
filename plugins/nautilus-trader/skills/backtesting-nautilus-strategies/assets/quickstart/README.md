# Offline Rust example

This independent package demonstrates native actor/strategy registration,
quote and custom-data dispatch, one simulated market order, and JSON decoding.
It defines its own synthetic instrument and data; no fixture feature, external
checkout, credentials, Python runtime, catalog or live adapter is required.

From this directory, with Rust 1.98.0 or newer:

```sh
cargo test --locked
cargo run --locked
cargo run --locked -- configs/fx.json
cargo run --locked -- configs/equity.json
```

The bundled `Cargo.lock` retains the qualified dependency resolution.
All direct Nautilus dependencies require exactly `0.63.0`; do not refresh the
lockfile merely to work around an API mismatch.
See [qualification](../../references/rust-testing.md) before treating the package as
compiler-qualified against a particular distribution.

Expected successful replay summary:

```text
inputs=5 quotes=4 signals=1 orders=1 positions=1
filled_quantity=1000 position_quantity=1000 position_side=Long
```

## Configuration

The binary takes zero or one JSON configuration path. With no argument it uses
the AUD/USD.SIM default above. The checked-in examples exercise the same
compiled `OneShot` strategy against two local synthetic venues:

- [`configs/fx.json`](configs/fx.json) buys 2,000 AUD/USD units on `FX_SIM`.
- [`configs/equity.json`](configs/equity.json) sells 7 AAPL shares on
  `EQUITY_SIM`.

Each configuration supplies its synthetic venue, instrument definition, quotes,
strategy identity, side, and quantity. The strategy receives only typed
instrument ID, side, and quantity. It resolves the configured `InstrumentAny`
from Nautilus's Cache before submitting one market order.

Configuration decoding rejects unknown fields. Prices and quantities are parsed
as Nautilus fixed-point values, must be positive, and must be on the configured
price or quantity grid. The supplied
[`invalid-zero-quantity.json`](configs/invalid-zero-quantity.json) is a
negative fixture: it exits before engine construction because an entry quantity
of zero is invalid.

After the local backtest, the binary reads the cached order and position and
prints their filled and open-position quantities. The
[`configured_runs`](tests/configured_runs.rs) integration test launches the
executable once per valid configuration and checks those actual cache-derived
metrics. It does not assert a serializer in isolation.

`QuoteCounter` observes four quotes and a `SignalV1` event through the native
engine. The shared `Observations` handle only exposes counters on the owner
thread; it is not another runtime or order owner.
`OneShot` intentionally submits at most once and retains possible-send state on
an error. It does not implement a profitable signal, retry policy, protective
bracket, account admission, or production shutdown flattening. The simulation
ends with exposure deliberately, so the example is not a live strategy template.

The default instrument and the two JSON instruments are synthetic definitions;
their zero-fee/default margin configuration is an educational assumption, not
broker metadata. Neither configuration connects to a provider.
The JSON test covers representation. Running the binary covers native dispatch
and simulated order/position creation. Neither qualifies real execution.

For bracket implementation use [Execution](../../references/guide.md);
for indicator warm-up use [Market data](../../references/guide.md).

## Actor publication to Strategy delivery

Run `cargo test --locked --test observation_chain` for the separate
[C1 integration test](tests/observation_chain.rs). It injects only four market
quotes; an order-free actor publishes four immutable custom observations and a
Strategy consumes them. It checks exact values, source and availability times,
and zero orders/positions. No custom data is injected by the harness and no hook
is called directly. This establishes the local native publication chain, not
JSON/Arrow persistence, a trading decision or live delivery.
