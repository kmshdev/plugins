# Nautilus Rust plugin build log

## 2026-09-11 — Review contract and starting evidence

Review the five workflow skills against current official Nautilus documentation,
then connected Rust declarations, callers and tests. Synthesize the findings,
verify runnable examples and Codex discovery, publish to `kmshdev/plugins`, and
enable only in the requesting strategy repository. Remove the legacy skill and
the in-repository plugin copy. Review the other pre-existing changes afterward.
Stay on the current branches. No provider connection or trading run is part of
this plugin acceptance boundary.

The requested source path was absent. The supplied snapshot is under
`.context/nautilus_trader` in the originating checkout. It declares 0.63.0,
Rust 1.98.0 and edition 2024. All 88 previously recorded source hashes match.
Current official Rust examples still show 0.62 and `test-support`; the snapshot
uses `stubs`. Version-specific API evidence and current documentation must be
distinguished, not silently combined.

The submitted diagram is a component overview. The audited model adds Clock,
Actors and kernel lifecycle, separates state reads from event publication, and
traces ordinary commands through risk before execution. It does not treat the
picture as a literal pipeline through Portfolio and Cache.

The earlier [build history](BUILD_LOG.md) remains historical evidence. Its
compatibility-alias and no-publication instructions are superseded by this
request; its model scores do not qualify this new candidate.

### Baseline checks

- Bundle structure, independent-resource closure and 88 source hashes: passed.
- Combined native quickstart: two tests passed; execution reported five inputs,
  four quotes, one custom signal, one order and one position.
- Order-free actor quickstart: one test passed; execution reported five inputs,
  four quotes, one signal, zero orders and zero positions.
- Maintenance unittest suite: 49 cases, two failures and five errors. Two tests
  compare unresolved macOS temporary paths with canonical paths. Five errors
  require PyYAML although the general maintenance command claims only the
  standard library. These are actual baseline failures, not skipped gates.
- Initial distribution: 114 files, 822,553 bytes excluding build/cache results;
  five routers contain 347, 327, 318, 336 and 319 whitespace-delimited words
  (data, live, strategies, actors, backtesting respectively).

### Findings recorded before implementation

| ID | Concern | Status | Direct evidence and correction |
| --- | --- | --- | --- |
| F1 | Codex packaging and deployment | Weak | Root `plugin.json` is a valid portable manifest, but lacks Codex UI metadata and no actual installation receipt exists. Add the supported `.codex-plugin/plugin.json` and test discovery using the installed CLI. [OpenAI packaging](https://learn.chatgpt.com/docs/build-plugins) supports both layouts. |
| F2 | Legacy discovery | Proved | Root `SKILL.md`, root `agents/openai.yaml`, README and ADR-002 retain a sixth compatibility entry and old alias. Remove the entry and alias, update their callers, preserve decision history. |
| F3 | Configuration-driven business logic | Weak | `examples/quickstart/src/lib.rs` hardcodes BUY/1000; `src/main.rs` hardcodes one FX instrument and venue. Add typed run configuration and two offline instrument/venue cases using the same strategy binary. [Configuration](https://nautilustrader.io/docs/latest/concepts/configuration/) defines field-specific defaults and typed composition. |
| F4 | Framework composition | Weak | Foundation describes core ownership correctly, but guides do not teach quoter/hedger, portfolio and execution-algorithm composition concretely. Add modular recipes and preserve strategy-specific IDs; the framework permits multiple Strategies. The originating repository's single-Strategy rule is application policy. |
| F5 | Rust test ladder and performance | Weak | No `proptest`, `turmoil` or `madsim` guidance in the workflow references. [Quality](https://nautilustrader.io/quality/) and [testing](https://nautilustrader.io/docs/latest/developer_guide/testing/) establish the layers; `crates/common/src/live/dst.rs`, network turmoil tests, reconciliation proptests and registered benches supply exact Rust entry points. Add selective tests, finite seeds, replay artifacts and measured benchmark guidance. |
| F6 | Event replay | Weak | Existing cache-only warning is correct but gives no constructive durable-capture/research recipe. `crates/event_store/src/replay.rs` explicitly does state-only replay; `crates/system/src/kernel.rs` skips trader startup in that mode. Explain capture, sealed-run verification, snapshot-tail restore and separate strategy reruns through BacktestEngine. Do not promise automatic callback replay. |
| F7 | Adapter extension | Weak | Data router excludes new adapters and references cover consumption only. [Adapters](https://nautilustrader.io/docs/latest/concepts/adapters/) identifies Rust traits as the extension boundary. Add extension guidance limited to Databento and IB; keep strategy logic on common APIs. |
| F8 | Platform and maintenance quality | Proved | Baseline unittest failures above; evaluator helper imports POSIX `fcntl`. Normalize fixture paths and declare reproducible optional maintenance dependencies. Distinguish portable skill content from Unix-only optional evaluator tooling. |
| F9 | Plugin and skill icons | Proved | No plugin assets or five child `agents/openai.yaml` files. Add coherent original icons and valid relative metadata paths. |
| F10 | Privileged areas and jobs | No issue / N/A | No plugin MCP, hooks, startup jobs or account access. Optional evaluator explicitly requires execution and keeps credentials out of staged skills; it is not a trading runtime. Keep that boundary. |
| F11 | Core runtime architecture | No issue | Facades/macros, order-free actors, owner-thread dispatch and cache/portfolio event stages match the current Rust how-tos and inspected source. Retain these mechanisms rather than duplicating engines or reducers. |

Source and adapter audit completion, implementation receipts, autoreview and
commit checkpoints are appended below. A status of Weak identifies a missing
plugin capability or evidence; it does not assert a framework defect.

## 2026-09-11 — Synthesis and native checks

F1–F9 are addressed in the candidate: supported Codex layout, exactly five
standalone skills, typed FX/equity run configuration, complex composition,
Rust test/simulation/benchmark guidance, constructive event replay, Databento/IB
extension recipes, declared maintenance environment, and original plugin/skill
icons. Root legacy entry/metadata are removed. ADR-003 supersedes compatibility
choices; existing historical evaluation receipts are preserved without rescoring.

- Source audit confirms Databento node external live bars and depth-10 are
  separate from lower-level/historical capabilities. Generic same-venue mixed
  instrument lists are possible, but representative-instrument/risk/adapter
  assumptions require qualification. No framework ownership defect was found.
- Configurable quickstart: four tests pass, including separate-process FX/equity
  execution and actual native quantities. Default and FX executable runs pass;
  FX records filled quantity 2000 and a Long position of 2000. Formatting passes.
- Live composition: check and build/dispose execution pass with Databento and
  IB factories. `cargo test` has zero tests; the executed construction smoke is
  the useful evidence. Clients are never started and no credentials are read.
- Maintenance: 52 regressions pass under the pinned PyYAML uv environment;
  source hashes and independently relocated five-skill closure pass.
- Plugin validation initially rejected skill icon paths relative to `agents/`;
  corrected them to skill-root `./assets/` paths and added traversal regressions.
- Native tests do not qualify full event-store acceptance, Arrow catalog round
  trips, physical provider execution, upstream simulation soaks or performance.
  Those are taught with explicit implementation/source boundaries.

Publication/discovery and independent autoreview receipts follow.

The authored distribution measured 188 files and 2,221,925 bytes (2,169.85 KiB)
before this receipt, excluding build/cache/evaluator results: 170.13% above the
822,553-byte baseline. The increase includes two live-example lockfile copies,
original PNG/SVG assets and self-contained advanced guides. Five router bodies
remain 297–340 whitespace-delimited words; references are loaded by concern.
This is distribution size, not model token consumption or runtime performance.
The official Codex plugin validator passed after metadata correction.

Independent post-implementation autoreview found no blocking issues in workflow
boundaries, versioned API guidance, provider scope, metadata or independent
resource closure. Live Codex discovery remains the next publication check.

## 2026-09-11 — Publication and installed discovery

Implementation checkpoint: commit `49b671e`, published as
[plugins PR 3](https://github.com/kmshdev/plugins/pull/3).
The relocated package again passed all 52 regressions and offline closure.
Independent autoreview found no blocking findings. A nested historical patch's
blank context and generated trailing blank lines were normalized before commit.

Direct-main publication was rejected by automatic approval review. The user
then authorized feature branches and PRs. The `kmshdev` Git marketplace now
tracks `codex/nautilus-rust-workflows` while that PR awaits review. It retains
its existing other plugins. Return its ref to main after the PR is merged.

Codex installed version `0.63.0+codex.20260911.1` from that published source.
The app-server config/read and skills/list calls proved user configuration false,
project configuration true, exactly five enabled namespaced Nautilus skills in
the requesting repository, zero in a neutral directory, and no loading errors.
This verifies actual host discovery, not just manifest validation. A new thread
is the boundary for loading the new skills into an existing conversation.

The final receipt-only cache revision is `.2`; executable guidance and examples
are unchanged. No provider connection was made. The application review passed
make check and schema gates; its image gate was blocked by the unavailable local
Dory daemon. Application details are recorded in that repository's evidence doc.
