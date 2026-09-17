# Select the smallest useful Rust test

Compile and run a short native scenario early. Add stronger tests when the
changed boundary needs them; do not require the upstream certification matrix
for every strategy edit. Keep synthetic runs, source-inspected tests and actual
provider evidence separate in the run receipt.

| Layer | Useful test | Failure artifact |
| --- | --- | --- |
| Unit | Pure sizing, exact grid/rounding, config validation, custom serialization | Minimal input and expected invariant |
| Integration | Actor registration, MessageBus dispatch, data-to-Strategy delivery, fill/position stages | Ordered native input/output trace |
| Acceptance | Signal through native risk/execution to simulated fill and economics | Config, data digest, seed and canonical outcomes |
| Property | Duplicated/reordered/dropped reports; bounded prices/sizes; idempotence | Minimized failing case and persisted proptest regression seed |
| Network simulation | Reconnect, partition, retry and backpressure using turmoil transport | Finite seed, fault schedule, termination reason |
| Runtime simulation | Time/task interleavings through madsim-based DST | Build flags, seed, replay/divergence artifact |
| Performance | Matching, MessageBus and serialization on native runtime | Machine/build/input metadata and distributions |

## Local application loop

For the bundled example run `cargo test --locked` and its documented config
commands in separate processes. For an existing application use its own focused
filter and required gates. `cargo check` proves type/feature compatibility; a
build-only client test proves construction, not delivery. Test a callback wiring
bug through native registration and dispatch, not by directly invoking only the
callback. Include valid empty data and unsupported responses in ingestion tests.

Use `proptest` in the owning test crate for a concrete invariant, for example:
quantity never increases after a terminal duplicate fill; normalized prices are
on-grid; replay results are independent of irrelevant report duplicates. Bound
the generated domains so they model valid native values; keep invalid-input
rejection as a separate property. Persist and rerun minimized failures before
changing the generator. The upstream reconciliation proptests supply report
reordering/drop patterns. Do not invent a second execution reducer in a test.

## Upstream source tests: optional, version-qualified

These commands require an upstream 0.64.0 checkout with its dependencies and are
not bundled-example acceptance commands. Select the package/test affected by a
change. The official testing guide uses nextest for process isolation; doctests
are separate. Do not copy Python-enabled full-workspace flags into a Rust-only app.

```sh
cargo nextest run --locked -p nautilus-execution reconciliation
cargo test --locked -p nautilus-common --doc
cargo test --locked -p nautilus-network --features turmoil --test integration turmoil_websocket::test_turmoil_real_websocket_basic_connect
```

The network helper accepts `NAUTILUS_TURMOIL_SOAK_START` and
`NAUTILUS_TURMOIL_SOAK_COUNT`. Set a finite COUNT for a bounded soak; absence can
mean an unbounded loop in the inspected helper. Preserve failing seed and fault
schedule. A transport must actually be injected through turmoil for its network
faults to matter; enabling a feature does not intercept all sockets.

Runtime DST requires both the package's `simulation` feature and
`RUSTFLAGS="--cfg madsim"`. The common runtime facade substitutes time, task,
runtime and signal pieces. Some sync/I/O/network operations remain Tokio and
transitive clients are not automatically virtualized. Build the selected test
under those flags, record the selected harness seed, and
verify the affected code imports the facade. A passing unrelated DST test does
not qualify adapter connectivity. Check the chosen test's harness/seed handling
before constructing a soak command. Do not measure native performance in DST.

## Benchmarks

Registered upstream targets include:

```sh
cargo bench --locked -p nautilus-common --bench msgbus
cargo bench --locked -p nautilus-execution --bench matching_engine
cargo bench --locked -p nautilus-serialization --bench serialization_comparison
```

Run comparable optimized builds on the same machine, record crate features,
input distribution, sample count and baseline revision, and compare uncertainty
as well as central tendency. Calculate throughput from measured time:
`events_per_second = event_count / elapsed_seconds`; for one event taking `t`
nanoseconds, throughput is `1_000_000_000 / t`. Include allocation and tail
latency if the question concerns stalls. Do not turn website throughput claims
or a zero-test compile into a local performance result.

The official quality page describes broader certification including 24-hour
soaks. That is an upstream claim, not a test this plugin has run or a required
24-hour gate for every application change. Its numbers are not provider SLAs.

Official basis: [testing](https://nautilustrader.io/docs/latest/developer_guide/testing/)
and [quality](https://nautilustrader.io/quality/). Source evidence: T1–T4.
