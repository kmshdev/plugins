# Evaluation contract

## Current collection routing

[routing.json](routing.json) is a small collection-level smoke set for the six
installed workflow descriptions, including non-trading negative cases and an
upgrade boundary. Give the evaluator the requests and actual discovered inventory,
not `expected_skill`. Compare selected workflows with those expectations only
after the response. Reuse the same model/settings and requests for a baseline.

A selection/plan response is not an implemented task or proof of automatic
selection on every future request. Check live host discovery separately, then
run the native examples for executable qualification. Historical isolated-skill
prompts are preserved in [workflows-0.63.json](history/workflows-0.63.json) and
[evals-0.63.json](history/evals-0.63.json); their recorded grades do not qualify
the current 0.64 baseline. New smoke cases are regression evidence, not a fresh
independent model benchmark after they have influenced a revision.

## Workflow evaluation

[workflows.json](workflows.json) adapts the original specification to 0.64.0:
three working cases and one separate acceptance case per skill. These reused
acceptance prompts are regression cases, not fresh holdouts. The resource
generator materializes evaluator-compatible local `evals/evals.json` and
`evals/acceptance.json`. Each case has `expected_output`, assertions,
`expected_skill` (null for negative scope cases), and explicit `files: []`.
The original fifteen working cases and five acceptance cases remain regression
evidence. The deployment workflow adds three working cases and a separately
phrased acceptance case. Do not reuse evaluated cases as fresh holdouts.

Once evaluated acceptance cases inform a later revision, they are historical
regression evidence, not a fresh holdout for that revision. Preserve their
original prompts/results and define a separate unseen acceptance set before
claiming a new independent model-evaluation result. Source/compilation checks
can qualify a concrete correction without implying a higher Tier 3 score.

Run NVIDIA SkillEvaluator 0.2.1 against each skill, or its parent collection
where the command accepts a collection:

```text
validate SKILLS --type skill --no-dedup --continue-on-failure -r json,html -o OUT
rubric-eval SKILL --min-score 70 -r json,html -o OUT
similarity-check SKILLS --type skill --threshold 0.75 -r json,html -o OUT
similarity-check SKILLS --type skill --full-body --threshold 0.75 -r json,html -o OUT
context-optimization-check SKILL --threshold 0.80 -r json,html -o OUT
tier3 validate SKILL --strict --json
tier3 evaluate SKILL --agents opencode --env-mode docker --skill-workspace-mode isolated --results-dir OUT --progress plain
```

Supply the configured supported model route explicitly, with evaluator and
embedding credentials as trusted process inputs. Never embed credentials in a
skill or fixture. Semgrep, SkillSpector and Gitleaks are external prerequisites.
Run tiers concurrently with separate outputs; a failed tier does not suppress
another. Preserve the without-skill baseline and runtime preflight.
Do not use `--copy-repo`, group workspace or sibling inclusion.

For fresh acceptance, copy only the selected skill into an isolated temporary
directory and replace its working `evals/evals.json` with `acceptance.json`.
Keep the distributed source frozen. These cases measure task answers/artifacts
and scope behavior, not reliable automatic host discovery or multi-skill
selection. Runtime code execution and provider qualification are distinct;
do not turn a reasoning grade into a compilation or trading claim.

Interpret standalone negative cases accordingly: an inactive skill cannot
teach the agent the exact name of a sibling absent from that sandbox. A future
collection-routing evaluation must supply the actual candidate inventory and
measure selection separately from task correctness. Preserve the historical
cases and report this assumption; do not inject siblings into an isolated
baseline or silently rescore previous runs.

Inspect dimension rationales before changing guidance. In the corrected run,
several behavior judgments cited a truncated conversation while accuracy/goal
judgments credited the same distinctions. A zero behavior score in that situation
does not establish an absent or incorrect answer. Compact task-result summaries
improve usability but do not fix the evaluator's evidence-collection limits.

Report scanner findings, author-contact policy mismatches, model/service
failures and similarity advisories truthfully. Do not invent an author email
or assign a public license to satisfy a generic publication profile.
Record tier receipts in [the build log](../BUILD_LOG.md), not secret-bearing raw
logs. Independent offline compilation is documented separately below.

**Corrected Neon Gateway diagnosis:** the earlier claim that the configured
gateway lacked Responses support was wrong. Neon uses distinct SDK bases:
`https://<branch-host>/v1` for the chat grader and
`https://<branch-host>/openai/v1` for a Responses agent. SkillEvaluator 0.2.1
copies the chat base into the agent's `OPENAI_BASE_URL`, producing the wrong
`/v1/responses` route (404). The same credential and model succeeded at the
documented `/openai/v1/responses` route (200).
See [Neon's Responses documentation](https://neon.com/docs/ai-gateway/openai-responses)
and [authentication/base-URL mapping](https://neon.com/docs/ai-gateway/authentication).

Keep the grader's chat base unchanged and configure the agent's Responses base
separately. OpenCode's supported inline configuration can override
`provider.openai.options.baseURL` without replacing its SDK or changing the key
or model. Replacing the built-in SDK with the Chat-Completions-compatible SDK
was the wrong workaround: the built-in route still calls `.responses()`.
The corrected endpoint passed a real API probe. The subsequent corrected Tier 3
run and its actual completion status are recorded in [BUILD_LOG.md](../BUILD_LOG.md).

There is also an independent temperature defect: this evaluator's capability
detector recognizes GPT-5 restrictions but treats the configured GPT-6-family
model as accepting custom temperature. Real chat requests succeed with temperature
omitted and fail with `temperature: 0` (400 `unsupported_value`).
Default-temperature handling must cover that model in both rubric and Tier 3
grading paths. Embeddings are separate: `SKILL_EVAL_EMBEDDING_PROVIDER=openai`
resolves `OPENAI_API_KEY` and the native OpenAI embedding endpoint, which returned
200. Do not replace its base URL or key with the Neon chat configuration.

The same evaluator's rubric CLI has no temperature flag. Where the service
rejected its fixed temperature, this run used the public
`skillevaluator.validators.rubric_eval.RubricJudge(temperature=1.0)` constructor
with the unchanged `RubricEvalValidator` criteria and scoring. This is recorded
separately from the failed CLI attempts. A weighted score above 70 is insufficient:
all nine rubric criteria must also score at least 7/10. Preserve that gate and
report truncated evidence or prompt-formatting artifacts rather than rewriting
valid skill metadata to satisfy an unreliable diagnosis.

## Reproducing the corrected Tier 3 environment

The run uses SkillEvaluator 0.2.1 with the recorded
[two-file compatibility patch](skillevaluator-0.2.1-gpt6.patch) in an isolated
package copy. Apply it relative to the directory containing `skillevaluator/`,
preserve the installed distribution's license, and put that copy's parent on
the evaluator host's `PYTHONPATH`. Use the same interpreter/dependencies.
Do not modify the global installation or inject loader variables into Harbor
task environments. Verify the imported module location and generated grader
template before running.

The patch only adds GPT-6 to default-temperature handling in the host and
container grader. It does not alter criteria, prompts, scoring, thresholds,
model selection or dataset content. Check that GPT-5/GPT-6 payloads omit
temperature and an ordinary supported model still preserves it.

For Neon, add this supported configuration to each **scratch copy's**
`evals/config.yml`, replacing the branch-host placeholder with the configured
gateway host. Keep the distributed skill and its cases unchanged:

```yaml
schema_version: 1
harbor:
  runtime_env:
    OPENCODE_CONFIG_CONTENT: >-
      {"provider":{"openai":{"options":{"baseURL":"https://<branch-host>/openai/v1","apiKey":"{env:OPENAI_API_KEY}"}}}}
```

The evaluator injects the configured gateway key into the agent; the JSON uses
a reference, not a literal key. Keep the native OpenCode SDK. The host/grader
retains the chat `/v1` base. Do not globally change `OPENAI_BASE_URL`: the
independent OpenAI embedding resolver can also read that variable.
Validate the scratch policy, retain real runtime preflight and both arms, and
store each retry in a distinct result directory. A completed low score is not
an infrastructure failure; incomplete/unpaired attempts do not enter final means.

For an infrastructure timeout, inspect the retained failing phase and installer
logs before retrying. This run recovered the remaining live/data cases with
`--n-concurrent 1`; the final data case also needed `--timeout-multiplier 2`.
Harbor 0.13.2 applies that multiplier to agent setup, extending its default
360-second allowance to 720 seconds. The retained trace showed ordinary
`apt-get update && apt-get install -y curl` still executing at the old deadline.
These are supported `tier3 evaluate` options, not scoring overrides; apply them
equally to both arms in a fresh run and record the changed time/scheduling
conditions. Do not rerun successful cases or retry unchanged failures blindly.

## Legacy single-entry cases

[evals.json](evals.json) contains task prompts, minimal relevant references and
observable acceptance criteria. It is not a generated claim that all cases pass.
Actual results belong in [qualification.md](qualification.md).
This historical dataset is retained for the explicit root entry, not supplied
to NVIDIA Tier 3; it predates the required `expected_output` field.

## Structural checks

From anywhere, run the bundle's `scripts/check.py` using its absolute or relative
path. The script resolves its own directory and checks internal-link closure,
no bundle symlinks/machine-local Markdown paths, canonical name, root word budget,
exact framework dependency requirements, source inventory and evaluation routes.
It uses Python's standard library only and performs no network calls.

Run the checker regressions with
`python3 -m unittest discover -s scripts -p test_check.py` from the bundle.
They include a relocated subprocess and intentionally invalid copies; fixtures
are removed by the temporary-directory owner after each case.

Copy the canonical bundle to a temporary directory outside the application and
run that checker again. This tests relocation; a successful check from the
original repository alone does not.

With an optional source tree, `--source-root` compares the recorded hashes and
citation ranges. A missing source tree is not required for the default check.
Hash matching establishes inspected-file identity, not a release tag.

## Behavioral cases

Give an evaluation agent only `SKILL.md` and a case's prompt, not the assertions.
Allow it to load its selected bundled references. Capture the answer and paths
read. Evaluate the listed assertions against the actual answer and any artifact;
do not score "the agent said it used the skill" as task correctness.

For isolated routing measures, use a fresh context per case. A batch smoke
evaluation is useful but must be labeled non-isolated, not a trigger benchmark.
The negative case checks scope; registration/discovery behavior depends on the
host agent and is distinct from content accuracy.

`beginner-offline` requires running native replay to claim execution.
The other cases can exercise conceptual correction, then use compiler/native
tests if code is produced. Do not request broker access for an evaluation.
Keep upstream tests merely read during research separate from tests run here.

## Example qualification

The bundled crate's unit test covers native JSON reconstruction. Its binary
asserts five input events, four quote callbacks, one custom callback, one order,
and one simulated position. No actor registry guard is held across dispatch.

No profitability, real broker behavior, Arrow round trip, performance benchmark
or complete application-recovery claim follows from those assertions.
