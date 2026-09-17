# Nautilus Trader for Codex

Five self-contained skills for **NautilusTrader 0.64.0 in Rust**, with original
icons, implementation guides and executable examples. Start small, compile,
run a native scenario, then add evidence for the boundary you change.

| Skill | Use it for |
| --- | --- |
| [Actors](skills/building-nautilus-actors/SKILL.md) | Order-free observers, indicators, Clock and custom observations |
| [Strategies](skills/building-nautilus-strategies/SKILL.md) | Configurable decisions, sizing, advanced orders and execution workflows |
| [Data](skills/integrating-nautilus-data/SKILL.md) | Identity, requests/subscriptions, codecs, catalogs and adapter extensions |
| [Backtesting](skills/backtesting-nautilus-strategies/SKILL.md) | Native replay, repeatable experiments and economic comparisons |
| [Live nodes](skills/running-nautilus-live/SKILL.md) | Rust composition, routing, reconciliation, recovery and shutdown |

Strategy APIs are instrument/venue generic. Provider recipes cover only
**Databento and Interactive Brokers**. Instrument metadata, adapter capabilities
and account qualification remain specific to the selected route. The skill
content needs no hidden source checkout, sibling skill or Python trading runtime.

## Install

Install `nautilus-trader@kmshdev` from the
[kmshdev marketplace](https://github.com/kmshdev/plugins). The Codex manifest is
[.codex-plugin/plugin.json](.codex-plugin/plugin.json); it discovers exactly the
five child directories. There is no sixth root skill or compatibility alias.
You can also copy any child directory into a skill-capable host independently.

For a repository-only activation, install the plugin into Codex's cache, keep
it disabled in user configuration, and enable it in the trusted project's
`.codex/config.toml`:

```toml
[plugins."nautilus-trader@kmshdev"]
enabled = true
```

The corresponding user-level entry must use `enabled = false` to prevent
activation outside that project. Project trust and host configuration precedence
apply. Installation/cache scope and enabled scope are distinct. See
[OpenAI plugin documentation](https://learn.chatgpt.com/docs/build-plugins) and
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

## Run the examples

Use Rust 1.98.1+ and the included lockfiles. Crates are pinned to `=0.64.0`.
The first build may fetch dependencies; cached builds can use `--offline`.

- [Configurable backtest](examples/quickstart/README.md): the same binary runs
  a currency pair and an equity on different synthetic venues; tests assert
  actual native fill/position quantities. Includes immutable Actor-to-Strategy
  observation delivery and causal timestamps.
- [Order-free actor](skills/building-nautilus-actors/assets/quickstart/README.md):
  native registration and dispatch with zero orders/positions.
- [Live composition](examples/live-composition/README.md): constructs/disposes
  Databento plus IB clients without starting them or reading credentials.

These are local executable checks. They do not claim provider delivery,
profitable trading, full durable-log acceptance, network soaks or benchmark results.

## Learn and extend

| Guide | Practical outcome |
| --- | --- |
| [Runtime foundation](references/foundation.md) and [architecture](references/architecture.md) | Clock, Cache, MessageBus, Portfolio and engine ownership |
| [Configuration](references/configuration.md) | Typed run parameters and cross-instrument experiments |
| [Composition](references/composition.md) | Quoter/hedger, portfolio admission and execution algorithms |
| [Orders](references/execution.md) | Exact orders, post/reduce-only, contingencies and event races |
| [Adapter development](references/adapter-development.md) | Extend Databento/IB at native client boundaries |
| [Testing](references/rust-testing.md) | Unit, integration, acceptance, proptest, turmoil, DST and benchmarks |
| [Event replay](references/event-replay.md) | Durable capture, state reconstruction and strategy reruns |
| [Connection recipes](references/connections.md) | Eight coupled runtime paths |
| [Source ledger](references/sources.md) and [hash inventory](source-manifest.json) | Official docs first, version-qualified source evidence |
| [Version and integration](references/version-and-integration.md) | Upgrade dependencies or qualify a native alternative before a framework workaround |

Read only the guide relevant to the work. Each child carries its own referenced
resources. The evidence targets upstream Rust 0.64.0 at commit
`1b0a49d2792a9432a3aca3fcb617ce7a630d905e`; source/compiler differences remain
explicit. Hashes identify cited files, while the examples' lockfiles identify
registry artifacts. Original summaries are not a vendored upstream distribution.
Upstream crates retain their own licensing obligations; this bundle assigns no
new license to them.

## Maintain

From the plugin root:

```sh
python3 scripts/sync_resources.py
python3 scripts/check.py
uv run --with-requirements scripts/requirements-maintenance.txt python -m unittest discover -s scripts -p 'test_*.py'
```

The first two commands use Python's standard library as maintenance tooling.
The full suite declares PyYAML explicitly through uv. The optional external
SkillEvaluator wrapper uses POSIX locking and is Unix-only; it is not required
to use the skills, run the Rust examples or check offline portability. Evaluation
services/toolchains have separate prerequisites documented in [evals](evals/README.md).
Historical model grades are not results for this revision.

The five `agents/openai.yaml` files configure skill discovery and appearance;
they are not custom subagents. Implicit invocation permits selection, not a
mandatory runtime hook. Choose the workflow for the affected owner and reuse
sufficient inherited guidance across delegated work. No root router, subagent
pipeline or all-reference reading requirement is needed.

After changing canonical guides/examples/evals, regenerate resources and check
for drift with `python3 scripts/sync_resources.py --check`. Individual routers and
workflow guides are maintained directly. `check.py --source-root PATH` verifies
source hashes read-only. `--record-source PATH` refreshes them only after a
version-qualified source review. Upgrade pins, recheck affected API chains and
rerun examples together. Follow the [current build log](BUILD-LOG.md) and
[packaging decision](decisions/003-codex-plugin.md); earlier
[build history](BUILD_LOG.md) remains a dated record.
