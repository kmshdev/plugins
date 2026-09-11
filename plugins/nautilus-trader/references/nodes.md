# Runtime selection

This compatibility entry remains for existing links. Choose the runtime by the
task rather than importing a Python node:

| Need | Rust runtime | Read |
| --- | --- | --- |
| In-memory deterministic replay, custom mixed inputs | `BacktestEngine` | [Backtesting](backtesting.md) |
| Catalog-configured replay/chunking | `BacktestNode` with `streaming` | [Market data](market-data.md), [Backtesting](backtesting.md) |
| Native adapter event loop | `LiveNode` with `node` | [Live runtime](live.md) |

Register concrete Rust types with `add_actor` / `add_strategy`.
No Python component loader, external checkout or host-project source file is
needed to use this bundle. Runtime ownership is described in
[Architecture](architecture.md).
