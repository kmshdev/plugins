# Five-skill build log

> Superseding diagnosis: the earlier Tier 3 "unsupported provider" conclusion
> was incorrect. The final API-probe correction below identifies a wrong
> Responses base path and a separate GPT-6 temperature-capability defect.
> The corrected Tier 3 run subsequently completed all 20 cases in both arms;
> see the final corrected Tier 3 execution receipt below. Earlier blocked runs
> remain history. The subsequent improvement pass changes that frozen candidate;
> its historical scores are not fresh qualification of the revised skills.

## Run contract

User request: build the discussed five skills, rename preparing-data to
integrating-data, restrict adapters to Interactive Brokers and Databento, use
NVIDIA SkillEvaluator in parallel tiers, and track the work in a build log.

This is an on-demand local build/evaluate loop, not a scheduled or published
loop. The finite worklist is the five workflows plus the component/connection
coverage cases in [coverage.md](coverage.md). Each pass repairs a concrete gap,
records the same relevant acceptance evidence and continues only while progress
is observable. Stop at completion, blocked prerequisites, approval-required
actions or no measurable progress; failed/incomplete evaluation is never success.

Edits stay within this bundle. Preserve the compatibility alias and unrelated
application changes. No provider connection, order, production change,
publication, global agent configuration change or credential disclosure.
Only the portable skill material and declared synthetic fixtures may enter
evaluation sandboxes. Evaluator/grader credentials remain process inputs.

## Acceptance contract

- Exactly five discoverable workflow skills under `skills/`, with distinct jobs.
- Each skill resolves its local references independently after relocation.
- Framework APIs remain 0.63.0 source-qualified; adapter examples cover IBKR and
  Databento only, with explicit availability and qualification limits.
- Components and cross-component failure scenarios have explicit owners.
- Frozen positive, negative and boundary evaluation cases are defined before
  optimization. Fresh acceptance prompts remain separate from working feedback.
- Tier 1, Tier 2 and two-arm Tier 3 results are recorded without silently
  skipping unavailable scanners, bypassing baselines or weakening findings.
- Passing local evidence does not become a claim of broker or trading safety.

## Pass 1: observe and design

The existing single skill and its working-tree changes are the starting point.
The initial quickstart and ten portability regressions had passed previously;
those are baseline evidence, not qualification of this split.

Selected five workflows: building actors, building strategies, integrating data,
backtesting strategies, and running live. Keep architecture knowledge as a
reference, not a sixth overlapping trigger. Choose the portable root
`plugin.json` format and a `skills/` discovery directory; no MCP, hooks or service.
The old root SKILL remains an explicit compatibility entry, excluded from
implicit selection where the host supports that metadata.

NVIDIA SkillEvaluator 0.2.1 is already installed (source revision
`3bfba44e754be87073b2344233f9569b06509ce1`), with Harbor 0.13.2.
Docker is available. The initial fixed dataset lacks `expected_output`, required
by this evaluator: new datasets will use its current schema rather than claiming
the old set is valid. Semgrep, SkillSpector and Gitleaks were initially missing.

The configured evaluator uses an OpenAI-compatible route. Codex's native route
was not established; the supported OpenCode compatible route preserves the
configured endpoint/key/model. OpenCode 1.18.30 was installed in ignored task
scratch, not global configuration. No model call occurred during setup.

Adapter research read official integration guides before native configs,
factories, data, history, contract resolution and reports. Important gaps include
Databento node symbology/bar support, historical empty-response ambiguity,
IB contract qualification and adapter-specific timestamp semantics.

Raw command evidence and evaluator configuration stay in ignored task scratch.
Subsequent passes and the final receipt are appended below.

## Pass 2: implement and freeze

Authored all five short routers and their primary guides. Added two
source-qualified adapter references covering native configs, factory routing,
history, bar support, identity/contract translation, provider timestamps,
reconnect, account/report coverage and construction-only composition.
Extended the source ledger/hash inventory without claiming an upstream commit.

Added ADR-002, the portable plugin manifest and the component/connection map.
Each workflow now carries local foundation/evidence and selected original
examples, produced by a deterministic package-owned generator. These are
maintenance scripts, not trading runtime tools. No installed skill requires
the generator or another workflow directory.

Before model feedback, froze fifteen working cases (explicit tasks, implicit
diagnosis and negative scope) plus five separately phrased acceptance cases.
Each declares no external task-input files. The held-out set is not used to
write or repair the first candidate.

The initial Tier 1 baseline failed on absent generated links, one unquoted YAML
colon, missing scanners and author-email policy. Fixed the YAML and resource
closure. Installed scoped Semgrep 1.176.1, SkillSpector 2.11.1 and Gitleaks 8.30.1
after the missing-tool failure. Did not fabricate contact information.
The source-record command also initially reported links before synchronization;
after generation, the offline bundle check passed. These intermediate failures
are retained as build feedback, not final passing evidence.

## Pass 3: independent parallel evaluation

Launched Tier 1/scanners/rubric, Tier 2 overlap/context and Tier 3 isolated
two-arm evaluation as three independent Terra tasks with disjoint report
directories. Parent work during evaluation added package-contract regressions,
checked the published portable plugin schema and made coverage-case IDs explicit.
No runtime skill guidance changed during these runs.

Before any held-out result, direct Clock source inspection corrected one
acceptance assertion: `match_handlers` needs clock access; release the clock
borrow before **executing** handlers, not necessarily before matching them.
The actor guide was already correct. Working cases were unchanged.

Offline source/hash verification, generated-resource drift detection, eighteen
checker regressions and repository documentation contracts passed. Relocation
tests copy each skill outside the package and check it independently. The
published plugin schema accepts the manifest's fields; no host installation or
automatic-discovery benchmark was performed.

### Tier 2 receipt

SkillEvaluator 0.2.1 completed all seven final checks:

| Check | Threshold | Outcome |
| --- | --- | --- |
| Five descriptions, pairwise | 0.75 | Passed; no findings |
| Five full routers, pairwise | 0.75 | Passed with one medium advisory |
| Context optimization, each of five skills | 0.80 | All passed; no intra-skill redundancy |

The advisory is backtesting versus strategy authoring at cosine **0.7974**.
These workflows intentionally share strategy/runtime vocabulary but have
distinct deliverables. Retain the useful guidance rather than game the metric;
there is no description overlap or blocking duplicate finding.

Initial context calls using `SKILL.md` paths failed with the installed CLI's
`unsafe_path` input validation. Retried once using supported skill-directory
paths; all passed. This was an invocation mismatch, not an embedding failure.
No thresholds, models or provider routes were changed.
JSON/HTML reports and sanitized commands are retained in task scratch under
`tier2-final/`; the durable outcome is recorded here so using the skills does
not require that scratch directory.

### Tier 3 initial runtime receipt

All five working datasets and all five held-out datasets passed strict schema
validation in isolated scratch copies. The first real Docker/OpenCode preflight
then returned HTTP 404 on the configured compatible service's Responses route,
before task execution. Both evaluation arms were configured, but **zero task
trials and zero comparative scores** were produced by this attempt.

Stopped the four identical working attempts and left acceptance unexecuted.
The initial failure is not a skill failure or a passing behavioral result.
A bounded follow-up is checking whether the supported OpenCode compatible SDK
can use Chat Completions with the same configured service/model/credentials;
no fallback provider, model substitution, proxy or skipped preflight is allowed.

### Tier 1 initial receipt and bounded repair

All five full static/scanner commands ran, and all five rubric commands were
attempted. The external author policy still rejects `kmshdev` without an email.
Three SkillSpector outputs were internally inconsistent (severity versus risk
recommendation), so their security scans are incomplete, not passing.
The actor and strategy scans flagged scope concerns in the shared full-runtime
example. Every rubric was blocked without a score because the configured service
rejected the evaluator's fixed temperature setting.

Acted on the useful scope feedback: the actor skill now bundles an **actor-only**
replay, with no Strategy registration/submission and assertions for zero orders
and zero positions. Extracted shared observer code rather than maintaining two
copies of its logic. The other examples explicitly identify the observer as a
synthetic verification fixture, not a provider adapter or ingestion job; a
Strategy's consumption of native data is not itself a scope violation.

Both Rust variants passed their existing JSON test and native replay:

| Example | Observed output |
| --- | --- |
| Actor-only | `inputs=5 quotes=4 signals=1 orders=0 positions=0` |
| Combined observer/Strategy | `inputs=5 quotes=4 signals=1 orders=1 positions=1` |

Used `cargo test --offline --locked`, `cargo run --offline --locked` and
`cargo fmt --check` for the two manifests. Formatting passed with only existing
stable-toolchain warnings about nightly-only import settings. The original
dependency lock remains unchanged. Nineteen offline checker regressions and
source-hash verification passed, including a new actor-example authority guard.
Moved generated Cargo targets into ignored task scratch, preserving the caches
without including build artifacts in any distributable skill.

Requested affected Tier 1/context reruns against the new assets. A supported
temperature configuration/API is being investigated for the rubric; no package
monkeypatch, altered grader threshold or substituted model is allowed.
Held-out behavioral cases remain unused for content optimization.

### Tier 2 affected-candidate confirmation

Re-ran context optimization for all four skills whose example resources changed.
All four passed at the unchanged 0.80 threshold with zero findings. The live
skill's passing result and the pairwise router results remain applicable because
their inputs did not change. Pass-2 JSON/HTML receipts are retained in scratch.

### Tier 3 terminal outcome: blocked

The supported scratch-only OpenCode configuration selected
`@ai-sdk/openai-compatible`, preserving the exact configured service, model and
credentials. Strict policy validation passed. The one recovery preflight failed
before task execution: OpenCode's built-in `openai` route still called
`.responses()`, which the compatible SDK does not implement.

Read-only runtime/source diagnosis established the incompatibility rather than
leaving an unexplained `UnknownError`. A custom provider alias would select Chat
Completions, but SkillEvaluator 0.2.1 rejects non-`openai` OpenCode namespaces for
its compatible provider. Its other allowed agents do not resolve the constraint:
Codex uses the Responses wire API; Claude Code requires independent Anthropic
credentials/model. Other Harbor runners are rejected by this evaluator's matrix.

There is no supported same-service/model/key Chat-Completions runner in this
installed harness. No monkeypatch, proxy, agent restriction bypass, model change,
third blind preflight or skipped baseline was used. Working and acceptance
execution remain **unperformed**, with no assertion scores or claimed uplift.
The frozen datasets and clean, non-graded snapshots are retained for resumption
with a compatible supported harness or an explicitly changed provider setup.
Any resumed run must create fresh copies of the final skill assets.

## Pass 4: discriminate content feedback from evaluator limitations

Recovered the rubric using the evaluator's public `RubricJudge(temperature=1.0)`
parameter, preserving its nine criteria, threshold, configured model and service.
The standard CLI failures remain recorded. The corrected-resource scores were
74.5 (backtesting), 76.4 (actors), 75.0 (strategies), 72.7 (data), and 71.8 (live).
All exceeded the weighted 70 threshold, but **all failed** the additional
per-criterion gate; these are not passes.

Used concrete feedback to add compact query-to-output examples, Rust/toolchain
prerequisites and visible example commands to the five routers. They remain
under 400 words each. Made Rust explicit in the live description. Added the
previously missing native sandbox composition path and an operational decision
table. Sandbox uses Nautilus's built-in simulated factory, not another external
provider or a replacement matching engine; external adapters remain IBKR and
Databento only.

Traced sandbox config -> simulated factory trait -> node builder -> venue-scoped
bus delivery/account initialization, with source hashes and a construction-only
fragment. The dedicated guessed sandbox integration URL returned 404, so it is
not cited as evidence. A source range ending past the factory file was rejected
and corrected to its inspected last line before recording the manifest.
The sandbox fragment is source-qualified, not compiled or provider-qualified.

Some rubric findings instead allege malformed front matter and unavailable
examples despite valid local YAML, closed references and compiled assets.
Requested diagnosis of the judge's context assembly/truncation rather than
changing valid metadata or deleting useful guides. Analyzer partial inspection
is not proof that a local guide is unavailable or unsafe.

The final candidate passed source/hash and generated-resource checks, all
nineteen regression cases, individual relocation checks for all five skills and
the repository documentation contract. All 152 local Markdown links resolved.
Requested a final unchanged-policy Tier 1 and Tier 2 pass; no further content
tuning will use the same rubric without a new material defect. The fresh
behavioral acceptance set remains unexecuted because Tier 3 is blocked.

### Final Tier 2 receipt

All five current descriptions passed pairwise checking at 0.75 with no overlap
findings. All five context checks passed at 0.80 without redundancy findings.
The final full-router comparison passed with these retained advisories:

| Pair | Cosine |
| --- | --- |
| Backtesting / strategies | 0.8168 |
| Actors / strategies | 0.7641 |
| Strategies / live runtime | 0.7585 |

The actor's final framework-version wording was included in its refreshed
context check and the current-byte full-router comparison. All final checks
completed without execution errors. Shared framework vocabulary is intentional;
no threshold was weakened to remove these advisory relationships.

### Final Tier 1 receipt

The final static/scanner collection and supported-temperature rubric used the
current skill bytes, including the actor version-wording correction.

| Skill | Static quality | Weighted rubric | Rubric gate |
| --- | --- | --- | --- |
| Backtesting | 80.8 | 80.0 | Failed: documentation completeness |
| Actors | 82.0 | 83.6 | Failed: documentation completeness |
| Strategies | 82.0 | 78.2 | Failed: documentation completeness |
| Data integration | 82.0 | 77.7 | Failed: documentation completeness |
| Live runtime | 86.8 | 79.1 | Failed: documentation and workflow completeness |

All five rubric requests executed successfully. Weighted scores improved after
the concrete example/prerequisite refinements, but the all-criteria gate still
failed and is retained as failed. All five security stages remain incomplete
because of SkillSpector recommendation-contract errors or LLM failures/partial
local-reference inspection. Other static checks passed except the external
author-contact policy; the catalog-layout convention also differs from this
nested portable-plugin location. No contact information or license was invented.

Read-only inspection of the installed rubric established its presentation
limitations: it adds delimiter lines around already-valid YAML front matter,
excludes `assets/` from supplementary evidence, and truncates references at
3 KB per file / 30 KB total. This explains the false malformed-frontmatter claim
and the unavailable/truncated-example claims. Its public API exposes no control
to include assets or increase that evidence budget. The live workflow diagnosis
is based on this bounded view, not proof that its source procedures are absent.
Kept valid metadata and complete local guides rather than modifying them to
match an incorrect presentation. No finding, prompt, severity or grade was edited.

## Terminal run receipt

**Implementation complete; evaluator qualification partially blocked.**

Delivered five independently portable, Rust-only 0.63.0 skills in a knowledge-only
plugin, with short workflow routers, local guides/evidence, original offline
examples, IBKR/Databento integration guidance, native sandbox composition,
source hashes, ADR-002, component/connection coverage and fixed evaluation cases.
The legacy explicit entry and repository path alias remain available.

Final offline gates: source/hash consistency, generated-resource consistency,
**21** regression tests (including standalone digest/duplicate-source failures),
five independent relocation boundaries and repository documentation contracts
passed. Both Rust sample variants compiled, passed JSON tests and produced their
expected native replay summaries. No application source/dependency or unrelated
work was changed. Build caches and raw evaluation artifacts remain in ignored
task scratch, outside the distributable skills.

Tier 2 passed with recorded similarity advisories. Tier 1 preserves its policy,
scanner and rubric residuals. Tier 3 cannot execute with the installed harness
and fixed compatible-provider setup; zero task trials or held-out acceptance
grades exist. This is a named blocker, not a passing benchmark or proof of
automatic skill discovery.

Stop here because remaining work requires a compatible evaluator/harness or
an explicit provider/publication-policy decision, not further speculative skill
rewrites. No production action, provider connection, real order, global agent
configuration change, publication or schedule occurred. Live/sandbox fragments,
Arrow persistence, complete cross-component scenarios and broker/provider
behavior remain qualified only to the explicit boundaries stated above.

## API-probe correction: SkillEvaluator failure root cause

At the user's request, tested the actual configured keys/model against the
requests relevant to SkillEvaluator and checked current official Neon Gateway
documentation. No key, private endpoint, model identifier or embedding vector
was published; no environment/evaluator configuration was changed.

| Request | Observed result |
| --- | --- |
| Configured Neon chat `/v1/chat/completions`, default temperature | 200; expected `OK` completion |
| Responses composed from the chat base: `/v1/responses` | 404 |
| Documented native Responses: `/openai/v1/responses` | 200; expected `OK` output |
| Documented long Responses alias | 200; expected `OK` output |
| Chat with `temperature: 0` | 400 `unsupported_value` |
| Separately resolved native OpenAI embeddings | 200; valid embedding shape, no vectors recorded |

**Cause 1: wrong agent API dialect path.** SkillEvaluator's
`tier3/harbor/runner.py:963-975` maps the compatible-provider chat base to the
agent's `OPENAI_BASE_URL`. Neon documents the chat base as `/v1`, but its
Responses base is `/openai/v1`. The earlier 404 established only that the wrong
route was missing, not that Neon or the configured model lacked Responses.
The same key and model work on the correct route.

**Cause 2: incorrect model-capability classification.**
`provider_config.py:59-75` special-cases GPT-5 but classifies the configured
unprefixed GPT-6-family model as supporting custom temperature. The gateway
rejects temperature zero for that model. The Tier 3 grader also defaults to zero,
so fixing the agent URL alone does not resolve the subsequent grading failure.
Omit custom temperature for this model; the earlier public rubric temperature-1
workaround remains separate evidence.

**Embeddings are working and independent.**
`resolve_embedding_provider` selects `OPENAI_API_KEY` and the native OpenAI
endpoint, not the Neon LLM key/base. Dotenv-only and dotenv-plus-process
resolution matched in the probe process. No embedding reconfiguration is needed.

The correction is to keep the chat grader on `/v1`, configure the Responses
agent on `/openai/v1`, and correct default-temperature handling. Keep the native
OpenCode Responses SDK; the previous SDK-replacement workaround was unnecessary.
This supersedes the earlier claim that preserving the configured service, key
and model could not support Tier 3. It does not retroactively create any
benchmark or held-out results: the full evaluator run still needs to be resumed
with corrected routing and temperature handling.

Evidence: [Neon Responses API](https://neon.com/docs/ai-gateway/openai-responses),
[Neon authentication/base URLs](https://neon.com/docs/ai-gateway/authentication),
the installed evaluator source, and sanitized request receipts retained in
ignored `neon-gateway-diagnosis/probes/` task scratch.

## Authorized corrected Tier 3 run

The user requested the required adjustments and actual Tier 3 execution.
The new run keeps the five skill trees and all working/held-out cases frozen.
Its finite worklist is fifteen working cases and five held-out cases, each
with both the with-skill and without-skill arms.

Apply compatibility changes only to a separately recorded evaluator copy:
default-temperature handling for GPT-6 in the host and generated grader code,
plus the documented Neon Responses base in agent-only OpenCode configuration.
Keep the grader's chat base, model, credentials, embeddings, scoring rules,
thresholds and baseline intact. Do not replace the native Responses SDK.
No global evaluator installation, application file or `.env.skills` edit is
needed. Record the precise patch and verify actual runtime preflight before
attributing any result to the skills.

### Compatibility implementation and independent review

The isolated evaluator changes exactly two temperature-family conditions:
`provider_config.py` and `tier3/harbor/templates/eval.py`. Both now omit custom
temperature for GPT-6 as they already did for GPT-5. Parent review confirmed no
grading or threshold changes. Independent patch application to clean temporary
source copies reproduced the running evaluator's bytes exactly, and installed
global source hashes remained unchanged. The portable
[recorded patch](evals/skillevaluator-0.2.1-gpt6.patch) and
[environment procedure](evals/README.md#reproducing-the-corrected-tier-3-environment)
make the adjustment reproducible.

Real Docker/OpenCode runtime preflight succeeded with the native SDK and the
agent-only Neon Responses base. The host grader retained its chat base;
credentials, configured model and independent embeddings were unchanged.

### Completed working matrix

All fifteen working cases completed in both arms: **30/30 expected attempts
scored**, with each original evaluator report marked `succeeded` / `complete`.
Parent inspection checked those original reports, not only the launcher's exit.

| Skill | With-skill aggregate | Without-skill aggregate |
| --- | --- | --- |
| Backtesting | 0.9148 | 0.7548 |
| Actors | 0.9696 | 0.8272 |
| Strategies | 0.8583 | 0.7414 |
| Data integration | 0.9130 | 0.7195 |
| Live runtime | 0.9185 | 0.7254 |

These are the evaluator's six-dimension aggregates, **not assertion pass rates
or pure accuracy**. They include security, skill execution and skill efficiency
alongside accuracy, goal accuracy and behavior checks. The without-skill arm
receives lower skill-use scores by construction, so overall lift alone cannot
establish better answers.

| Working-set dimension, equal case weighting | With skill | Without skill |
| --- | --- | --- |
| Aggregate | 91.5% | 75.4% |
| Accuracy | 90.7% | 100.0% |
| Goal accuracy | 84.3% | 94.7% |
| Behavior check | 77.2% | 74.4% |

The lower working-set accuracy/goal scores remain visible; no source content was
tuned to these results during the run. These small fixed-case judge scores do
not replace compiler or trading qualification.

Held-out execution initially completed backtesting, actors and strategies.
Data integration encountered a judge rate limit and then a Docker environment
startup timeout. Those incomplete/unpaired retries are retained but excluded
from aggregate results. Data/live were subsequently completed independently
after scoped infrastructure diagnosis, as recorded in the final receipt below.

### Final corrected Tier 3 execution receipt

**Execution complete: all 20 cases, 40/40 scored benchmark attempts.**
The parent independently reopened the ten canonical `result.json` files:
each has `execution_status=succeeded`, `report_status=complete`, matching
expected/scored counts and complete with-skill/without-skill pairs.
The working set contributes 30 attempts and the five held-out cases contribute
10. Failed retries and runtime preflights are separate, not additional scored
benchmark cases.

| Held-out skill | With-skill aggregate | Without-skill aggregate |
| --- | --- | --- |
| Backtesting | 1.0000 | 0.6374 |
| Actors | 0.9792 | 0.7685 |
| Strategies | 1.0000 | 0.7955 |
| Data integration | 0.8167 | 0.5921 |
| Live runtime | 0.9111 | 0.7069 |

| Held-out dimension, equal case weighting | With skill | Without skill |
| --- | --- | --- |
| Aggregate | 94.1% | 70.0% |
| Accuracy | 100.0% | 100.0% |
| Goal accuracy | 96.0% | 99.0% |
| Behavior check | 73.3% | 60.0% |

Completion is not a claim that every behavior passed. In particular, the data
held-out behavior-check score is zero in both arms. The aggregate's skill-use
and efficiency dimensions favor using the installed skill; retain the separate
accuracy/goal/behavior scores rather than presenting overall lift as universal
quality improvement. One held-out case per skill is a small benchmark, not a
statistical or trading qualification.

#### Infrastructure recovery

Kept all completed runs immutable. Recovered rate-limited judge attempts without
combining partial scores from separate runs. For the remaining data/live cases,
used the supported `--n-concurrent 1` scheduling override. Docker health showed
adequate CPU, memory and disk, with no owned stale containers to remove.
The independent live case then completed.

The data retry's retained setup trace identified Harbor's ordinary OpenCode
installation command, `apt-get update && apt-get install -y curl`, exceeding the
360-second setup deadline. Installed Harbor source confirmed that the supported
`--timeout-multiplier 2` extends that deadline to 720 seconds. A fresh paired
data run with that time allowance completed 2/2 expected attempts. Neither
timeout nor scheduling adjustments changed prompts, grading or thresholds, and
both arms in the paired run used the same settings.

#### Provenance and scope

The final manifest identifies all ten canonical complete report paths under
ignored `nautilus-tier3-corrected/results/`; original failures, exact source
diffs, hashes and command receipts remain retained separately.
The launcher kept the configured model arguments unchanged. Earlier sanitized
reports no longer retain the model identifier, so those identifiers cannot be
independently re-compared; the latest checked model metadata matched its request.
OpenCode 1.18.30 is a host pin, not an independently retained per-trial version.

No skill content or frozen cases were tuned during this run. No global evaluator
installation, `.env.skills`, embedding configuration or application source was
modified. The two-file compatibility patch is retained with this bundle; private
runtime configuration and raw artifacts remain outside the distributable skills.
No real market-data connection, broker order or production action was performed.
Earlier Tier 1 policy/scanner/rubric findings are not retroactively cleared by
successful Tier 3 execution.

## Post-evaluation improvement pass: 2026-09-10

The user requested evidence-backed evaluation improvements and completion of the
quoted five-workflow architecture proposal. All five entry points already
existed. Kept those five jobs and implemented their missing connection-reference
layer rather than duplicate skills or quietly add the explicitly deferred
adapter/backend/transport/matching-engine extension jobs.

### Architecture follow-through

Added [eight connection recipes](references/connections.md): publication,
partial-fill accounting, historical/live handover, cancel/send uncertainty,
restart/shutdown, replay/live composition, Databento-to-IBKR identity, and custom
catalog replay. Each states owners, implementation steps, failure controls and
required evidence. The shared foundation now distinguishes the four message and
state paths explicitly.

The generator includes only the relevant recipes and source anchors in each
standalone skill. Routers link them conditionally, remain below 400 words, and
the data description now explicitly covers subscriptions, historical requests,
live delivery and provider-independent custom/local data.
No reference requires another installed skill or the research checkout.

Rechecked historical request attribution against A1/A3: the request returns a
UUID and its response wrapper carries correlation, but `on_historical_bars`
receives the data slice without that ID. The C3 recipe consequently requires
serialization of indistinguishable requests or an explicit attribution protocol,
not assumed response-arrival ordering.

### Native C1 evidence

Added [observation_chain.rs](examples/quickstart/tests/observation_chain.rs),
using the existing independent package and unchanged dependency lock. The engine
receives four quotes and no injected custom input. An order-free actor publishes
four immutable observations; a native Strategy receives the exact sequence,
source timestamps and availability timestamps. The result asserts zero orders
and positions. This closes the previous local C1 delivery gap without claiming
a trading decision, codec/catalog round trip or provider behavior.

Terra ran `cargo test --offline --locked`: the existing JSON unit case and new
native integration case passed. `cargo run --offline --locked` preserved
`inputs=5 quotes=4 signals=1 orders=1 positions=1` for the separate original
binary. Reused the external Cargo target cache; installed no dependencies and
left the lockfile unchanged. The integration test is distributed with strategy,
data and backtesting skills, never with the order-free actor-only package.

The first 24-case maintenance run failed
`test_connection_recipes_and_evidence_are_local`: Strategy's new C1 recipe
needed D1, but its local evidence selection omitted that anchor. Added D1 to
the generator rather than weaken the assertion. New regressions also reject a
missing C1-C8 recipe and order authority hidden in nested actor asset tests.
Final maintenance results and evaluation-feedback disposition follow below.

### Evaluation-feedback disposition

Terra inspected actual per-trial `reward.json` rationales, not just aggregate
scores or successful execution flags. These distinguish an observable-answer
problem from a framework-guidance defect:

| Observed feedback | Disposition |
| --- | --- |
| Live `restart-continuity` goal score 0.8: Strategy callbacks/state restoration distinction was implicit | Made it explicit in the live guide, legacy live reference, shared foundation and C5 recipe. Rechecked kernel L3's early return before ordinary startup. Cache-only replay does not replay Strategy callbacks or restore application-owned state; snapshot/load, broker reconciliation and feed-gap repair are separate. |
| Bracket, provider-timestamp, replay and live behavior clauses were not visible in truncated conversations | Added compact task-result/evidence checklists at the start of the Strategy, data, replay and live guides. Lead with the requested artifact or diagnosis, not a source-investigation transcript. This improves usability without claiming to repair grader truncation. |
| Working Strategy/data/replay accuracy reductions came from negative cases expecting exact sibling skill selection | Recorded the isolated-inventory mismatch. Those non-trigger responses had no skill tool calls; the absent sibling could not be selected. Retained the ownership boundaries and original cases instead of claiming the trading/data implementation was wrong or injecting siblings into the benchmark. |
| Data `custom-catalog` behavior was zero in both arms, while accuracy and goal were perfect | All three compound behavior assertions cited insufficient visibility in the truncated conversation. This is not evidence that the response omitted or contradicted the technical distinctions. Kept correct codec/catalog guidance and documented the measurement limitation. |
| Tier 1 author email, wrapped frontmatter, excluded assets, reference caps and partial scanner findings | Did not invent identity/contact metadata, weaken criteria or remove valid local guides. Historical failures/incomplete findings remain recorded. |

The precise corrected Tier 3 trial receipts are under the canonical result
directories already recorded above:
`restart-continuity__UDdUfE2/reward.json`,
`negative-ingestion__qrukngh/reward.json`,
`negative-order-lifecycle__ibCJaCS/reward.json`,
`negative-live__8NhKwUR/reward.json`,
`deterministic-replay__eu7FWrQ/reward.json`,
`construct-only__RGeqhdD/reward.json`,
`missing-report__PTUZspn/reward.json`, and
`custom-catalog__jrjQex9/reward.json`, each below
`opencode/with-skill/trials/`. The raw reports remain ignored evidence, not
runtime dependencies of these skills.

No historical evaluator input/result was rewritten or rescored. The exposed
acceptance cases are no longer fresh for this revision. New model acceptance
would require a separate unseen set and recorded candidate; the earlier scores
are not presented as measurements of these changes.

### Final revised-candidate qualification

Terra's final frozen-candidate run passed all 25 maintenance regressions,
source/hash validation against the inspected 0.63.0 snapshot, generated-resource
drift detection and repository documentation contracts. All five children remain
independently closed; no distributed `target` or `__pycache__` directory exists,
and the compatibility symlink still resolves to this package.

An isolated temporary copy of only `building-nautilus-strategies`, with no parent
or sibling files, passed `cargo test --offline --locked --test observation_chain`
using its own Cargo manifest and the existing external target cache. The worker
removed that named temporary copy and retained the cache. Together with the
canonical package run recorded above, this establishes local native C1 delivery
and portable source packaging, not connected-system qualification.

The validation wrapper initially attempted a nonexistent `bundle/scripts` path
and resolved the source checkout relative to the bundle instead of the repository.
Those invocation errors were corrected; no gate was skipped or weakened.
The successful repository-root commands used the literal package path for
`scripts/check.py --source-root .context/nautilus_trader`,
`scripts/sync_resources.py --check`, and unittest discovery, plus
`scripts/check-doc-contracts.sh`.

No new NVIDIA/model evaluation was run for this revision, and no higher score is
claimed. Tier 1's external policy/scanner/evidence limitations remain open.
The application workspace, its dependencies and its trading semantics were not
changed; application-wide Rust gates were not run for this independent example
package. C2-C8 runtime/provider qualification remains bounded by the evidence
already recorded, not inferred from the newly written recipes.

Terminal result: the justified content improvements and proposed five-workflow
architecture-reference layer are implemented. Historical evaluator findings
remain intact and distinguish tool visibility from actual content defects.
