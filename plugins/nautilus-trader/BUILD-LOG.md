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

## 2026-09-17 — Rust 0.64.0 executable baseline

The examples now resolve registry Nautilus 0.64.0 with Rust 1.98.1. The release
source is pinned to upstream `1b0a49d2792a9432a3aca3fcb617ce7a630d905e`;
all 103 cited files were rehashed, and moved integration-test coordinates were
updated. Source verification rejects a different revision or edited cited bytes.
Registry lockfiles identify the separately packaged artifacts.

The native runtime check caught private `Price.raw` and `Quantity.raw` fields;
the configurable example now uses their public `raw()` accessors without changing
its exact financial/grid checks. Model fixtures use `test-support`, and the
optional upstream network command selects the current `integration` test target.

Executed locally with the installed Rust 1.98.1 toolchain:

- Combined quickstart: four tests passed; the executable produced
  `inputs=5 quotes=4 signals=1 orders=1 positions=1` and quantity 1000.
- Independent actor: one test passed; the executable produced
  `inputs=5 quotes=4 signals=1 orders=0 positions=0`.
- Databento/IB node: built and disposed successfully; no clients started.
- Maintenance: 54 tests passed; source hashes, resource closure, plugin/skill
  validators, rustfmt check and `git diff --check` passed.
- `codex review --uncommitted` in a read-only session reported no actionable
  regressions. It independently checked source/bundle consistency; the author
  ran the executable checks above.

Evidence is in ignored `.agent/codex-nautilus-rust-workflows/` at the repository
root. This checkpoint qualifies the executable baseline, not every source recipe,
automatic workflow selection, provider delivery, broker fills or profitability.
Historical 0.63 evaluation prompts and receipts retain their original version.

## 2026-09-17 — Workflow boundaries and independent qualification

The five workflows now distinguish bundled example pins from application-owned
lockfiles, features and source overrides. A portable, on-demand version/integration
reference covers dependency upgrades and checking native alternatives before
framework workarounds. Descriptions include review work and provider-independent
node persistence. No root router, automatic hook or custom subagent pipeline was
introduced. Project routing and delegated handoff guidance were updated separately
on the strategy repository's existing branch.

The independent source review covered all five workflow guides plus adapter,
execution, event-replay and Rust-testing references against the pinned release.
It identified the timer's required `DurationNanos` argument, the Event Store
`halt_threshold` field name and preservation of inherited `RUSTFLAGS` for DST.
All three were corrected. The canonical actor timer recipe was corrected too.
A native registered-actor regression proves typed timer scheduling, no callback
on clock advancement alone, and dispatch after releasing the clock borrow.

Runtime and packaging evidence on Rust 1.98.1:

- Combined example: five tests passed, including the new timer regression and
  existing native observation delivery and economic assertions.
- Independently built actor: two tests passed, then zero orders/positions in the
  executable. Its build target was isolated from the same-named combined package;
  an earlier shared-target filter selected zero tests and was not accepted as evidence.
- Live composition again built/disposed Databento and IB clients without starting
  them. These checks do not establish provider delivery or broker behavior.
- Maintenance: 54 tests passed; source verification, generated closure, the
  official plugin/skill validators, rustfmt and diff checks passed.
- `codex review --uncommitted` reported no actionable regressions for this pass.
  Its read-only process did not run Rust tests; the author ran those above.

Fresh Codex 0.154.0 app-server discovery found five enabled candidate skills in
an isolated repository fixture and no loading errors. Installed-scope checks
found five skills in the trusted strategy project and zero in a neutral directory;
that installed cache was still the previous 0.63 release at this checkpoint.

The same nine collection-routing requests were run in separate read-only Codex
sessions with `gpt-6-astra`, low reasoning effort, and the real discovered baseline
or candidate inventory, without expected selections in the prompt. Both matched
9/9 expectations, including three non-trading negatives. This is selection/plan
smoke evidence, not measured routing improvement or complete task qualification.
Current regression datasets target 0.64; original 0.63 prompts are preserved in
`evals/history/` and no historical model grade is reassigned to this revision.

Receipts remain under ignored `.agent/codex-nautilus-rust-workflows/` at the
repository root. Publication and installed-cache refresh are separate from these
local commits and checks; a new thread must load the refreshed plugin afterwards.

## 2026-09-18 — Persistent run delivery skill

Added `deploying-nautilus-runs` as a sixth independently portable workflow.
It supplies an existing-runner delivery overlay (Dockerfile, private local
PostgreSQL/Redis Compose fixture, reusable GitHub Actions build, application run
registry schema) and non-executing isolated run-plan generation. No root router,
deployment hook, provider-specific orchestrator or new agent pipeline was added.

Research followed the requested live and persistence Rust API pages into pinned
0.64 source at `1b0a49d2792a9432a3aca3fcb617ce7a630d905e`. DP1–DP7 record
feature gates, Cache factories, native Feather/Parquet/DataFusion, object-store
construction, CLI schema ownership and node lifecycle. Important qualifications:

- Rust 0.64 rejects `LiveNodeConfig.streaming`. The built-in Feather subscriber
  also panics inside Tokio callbacks; it is not a drop-in live recording solution.
  The skill requires application-owned async native writer integration for live
  runners. The sample demonstrates synchronous API behavior, not a running node.
- Redis Cache flush is destructive. PostgreSQL Cache ignores instance/trader
  namespacing and needs a separate database per independent Cache namespace.
- Native streaming captures Feather; Parquet conversion and decoded readback
  are explicit. Converter success alone is insufficient acceptance evidence.
- Kernel streaming cannot supply the account options required for Azure `az`
  addressing; plans reject that backtest combination. ABFS still requires actual
  identity/write qualification. Local paths preserve spaces, percent signs and
  Unicode rather than feeding encoded filenames to the native path converter.

Executed checks on Rust 1.98.1:

- Three native tests passed: exact quote/timestamp Feather-to-Parquet/DataFusion
  round trip, live-config rejection, and the async subscriber panic boundary.
  The executable separately wrote/read one quote under a unique artifact prefix.
- 61 maintenance tests passed, including seven scaffold regressions for isolation,
  overwrite protection, URI handling, mode-specific capture and command inputs.
- Source/hash and generated-resource closure, official plugin/skill validators,
  rustfmt, Compose configuration validation and whitespace checks passed.
- Fresh signed-out local-marketplace installation discovered six enabled skills
  with no loading errors. The installed skill generated an overlay and sandbox
  plan, and its Compose configuration validated without starting services.
- An independent forward-test produced an HTTP-input/Azure-output delivery plan
  using only the skill. That pre-review exercise was planning evidence, not a
  deployment or qualification of the later async integration corrections.
- Azure-profile read-only autoreview identified four actionable issues: async
  subscriber context, PostgreSQL isolation, Azure kernel account options and
  encoded local paths. All were addressed with source-qualified guidance and
  focused regressions where executable locally. A second Azure static review
  confirmed the four fixes and found no actionable regressions in scope.

Receipts are under ignored `.agent/codex-nautilus-rust-workflows/deployment/`.
No PostgreSQL/Redis service, cloud job, migration, registry publication or broker
connection was executed. Cloud durability, a complete strategy runner and actual
live async capture/shutdown remain application integration requirements, not
claims established by scaffold generation or successful local compilation.
