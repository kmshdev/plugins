---
name: deterministic-metric-design
description: Design a deterministic software metric with explicit construct, unit, invariants, and validation criteria.
---
# dot-skills Deterministic Metric Design Best Practices

Design metrics that are deterministic, computable, provable, and valid — measures an agent can trust and *optimize against* without gaming them. The 44 rules across 8 categories take a metric from a fuzzy construct to an adoptable, machine-checkable number: define the construct, confront computability limits with sound proxies, ground it in measurement theory, prove its properties, pin its determinism, validate it empirically, harden it against optimization pressure, and package it for adoption.

A running example threads through every category — **a deterministic measure of behavior-preserving codebase-size reduction** (shrink code without changing how the app works). It is the ideal stress test because its ideal form is provably out of reach (Kolmogorov complexity is uncomputable; program equivalence is undecidable by Rice's theorem), so the whole craft is building a deterministic, tractable proxy with a proven guarantee.

This is the measurement-design layer that the `*-algorithms` skills *apply* (Big-O, NDCG, cyclomatic, MoJoFM) but never *teach*.

## When to Apply

Use this skill when:

- Designing a new metric, score, or index — or reviewing someone's proposed metric for rigor
- Asked to "quantify", "measure", "score", or "rank" a property that has no agreed measure yet
- Building a deterministic optimization target an agent will push on (e.g., reduce code size without changing behavior)
- Auditing an existing metric that "feels off" — it suspiciously tracks LOC, jumps between runs, or gets gamed
- Turning a research idea or formula into something computable, reproducible, and adoptable

## Workflow: Define → Make Computable → Prove → Validate → Harden

The categories are ordered by cascade severity — an upstream mistake poisons everything below it. Work top-down, and jump straight to a category using this table:

| If you are… | Start in | First rule |
|-------------|----------|------------|
| Starting from a fuzzy property | `def-` | [def-name-the-latent-construct](references/def-name-the-latent-construct.md) |
| Worried the ideal is uncomputable / undecidable | `comp-` | [comp-do-not-define-metric-as-uncomputable-ideal](references/comp-do-not-define-metric-as-uncomputable-ideal.md) |
| Unsure whether you can average or take ratios | `meas-` | [meas-declare-the-scale-type](references/meas-declare-the-scale-type.md) |
| Claiming the metric behaves a certain way | `prop-` | [prop-prove-monotonicity](references/prop-prove-monotonicity.md) |
| Getting different numbers between runs | `det-` | [det-pin-iteration-and-tie-break-order](references/det-pin-iteration-and-tie-break-order.md) |
| Unsure it measures the real thing | `valid-` | [valid-discriminant-not-just-loc](references/valid-discriminant-not-just-loc.md) |
| Letting an agent optimize the metric | `game-` | [game-hard-block-construct-violating-wins](references/game-hard-block-construct-violating-wins.md) |
| Publishing the metric for others | `agg-` | [agg-ship-reference-impl-and-test-vectors](references/agg-ship-reference-impl-and-test-vectors.md) |

Each reference file is a `{category}-{slug}.md` containing: WHY it matters, an **Incorrect** example with the failure annotated, a **Correct** example with the minimal fix, and a reference. The incorrect/correct examples are metric *definitions and procedures*, not application code — the contrast is a badly-designed measure versus the fixed one.

## Rule Categories by Priority

| # | Category | Prefix | Impact | Rules |
|---|----------|--------|--------|-------|
| 1 | Construct Definition & Operationalization | `def-` | CRITICAL | 6 |
| 2 | Computability & Tractability | `comp-` | CRITICAL | 7 |
| 3 | Measurement-Theoretic Foundations | `meas-` | HIGH | 5 |
| 4 | Proof of Metric Properties | `prop-` | HIGH | 6 |
| 5 | Determinism & Reproducibility | `det-` | HIGH | 5 |
| 6 | Construct Validity & Calibration | `valid-` | MEDIUM-HIGH | 6 |
| 7 | Optimization Safety & Anti-Gaming | `game-` | MEDIUM | 5 |
| 8 | Aggregation, Reporting & Adoption | `agg-` | LOW-MEDIUM | 4 |

See [`references/_sections.md`](references/_sections.md) for the full ordering rationale.

## Reference routing

Use the category table above to choose a topic. Open [the rule index](references/quick-reference.md) only to locate the specific rule, then read that rule’s reference file.

## How to Use

1. Identify where you are with the **Workflow** table and open the matching first rule.
2. Work the categories top-down — `def-` and `comp-` are CRITICAL because a fuzzy construct or an uncomputable ideal makes everything downstream noise or unusable.
3. When proposing or critiquing a metric, quote the rule by file path so reviewers can check the reasoning.
4. For a new metric, produce a one-page spec naming: construct, proxy, scale + unit + zero, proven properties, determinism guarantees, validity evidence, guardrails, and version — one line per category here.
5. See [`references/_sections.md`](references/_sections.md) for ordering rationale and [`assets/templates/_template.md`](assets/templates/_template.md) when adding rules.

## Reference Files

| File | Description |
|------|-------------|
| [references/_sections.md](references/_sections.md) | Category definitions, impact levels, and ordering rationale |
| [assets/templates/_template.md](assets/templates/_template.md) | Template for adding new rules |

## Related Skills

- `same-results-less-code`, `code-simplifier`, `complexity-optimizer`, `knip-deadcode` — prescriptive code-reduction skills. This skill supplies the measurement layer they lack: a deterministic, behavior-preserving reduction *metric* to target and verify.
- `algorithmic-complexity-review`, `computer-science-algorithms` — apply existing measures (Big-O). This skill teaches how to design new ones.
- `opensearch-function-scoring-algorithms` — applied ranking metrics (NDCG, A/B tests). This skill is the foundational methodology beneath its `eval-` category.
