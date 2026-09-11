# Qualification record

The record below covers the initial single-entry package and its original
offline Rust example. For the later actor-only variant, shared-source extraction,
five-workflow plugin's structural checks and
NVIDIA tier results, use [BUILD_LOG.md](../BUILD_LOG.md). Do not interpret this
historical smoke as qualification of the new evaluation cases.

Candidate: `nautilus-trader`, NautilusTrader 0.63.0, 2026-09-09.

## Executed example

The independent quickstart resolved installed registry dependencies offline
with Rust/Cargo 1.98.0 and reused an existing target cache.

| Command, from the package directory | Observed result |
| --- | --- |
| `cargo test --offline` | One JSON round-trip test passed |
| `cargo run --offline --locked` | `inputs=5 quotes=4 signals=1 orders=1 positions=1` |

The actual invocation supplied `--manifest-path` and an external target-cache
directory. No root application manifest/source edits or dependency downloads
were needed. The generated lockfile records resolution, not proof that all
registry code equals the source snapshot used for the knowledge references.

The lockfile is included with SHA-256
`bedb51c9bf1699277fcd8de6235d044065f59808cd347fadd815331a8d196f69`.
The active dependency-feature tree contained no Python/PyO3 integration.

## Bundle checks

| Boundary | Observed result |
| --- | --- |
| Offline bundle checker | Passed |
| Optional source-root hash comparison | Passed for the cited snapshot files |
| Standard-library checker regression suite | 10 passed, including a relocated subprocess without a source checkout |
| Repository Markdown link contract | Passed, including legacy-name compatibility |
| Standalone Rust formatting | Passed; stable rustfmt warned that inherited nightly-only import settings were unavailable |

Initial source-manifest generation rejected five out-of-range citation endings.
Those source endings were inspected and the ledger corrected before recording
hashes. The first checker regression run had two failures because its temporary
test root used macOS's unresolved `/var` alias while resolved paths use
`/private/var`. The fixture now resolves its root and also launches the actual
checker in the relocated bundle; the final ten-case run passes. These were
corrected evidence/test-fixture defects, not waived checks.

## Model-content smoke

A separate GPT-5.6 Terra consumer read the root and selected bundled references
without access to assertions, hosting application source or upstream source.
Four prompts were exercised in one non-isolated context:

| Case | Observed content |
| --- | --- |
| `custom-routing` | Correct identifier/topic distinction and envelope JSON registration; not a compiled generated-code evaluation |
| `fill-accounting-stage` | Correct Cache-before-Portfolio staging and immediate-exposure boundary |
| `catalog-memory` | Correct multi-config materialization, equal-time expansion and custom-type limitation |
| `bracket-protection` | Correct lack of live-protection guarantee; initial answer omitted pre-submit ID tracking and used imprecise OCO wording |

The bracket recipe was improved to put explicit OUO selection and pre-submit
application-owned ID tracking in the same fragment. A fresh consumer then
returned `.call()`/`Vec<OrderAny>`, entry-stop-target ordering, OUO/OTO semantics,
pre-submit correlation, reduce-only exits and the manager/venue qualifications.
That retry passed the bracket case's content assertions.

This is a narrow content smoke, not a measured improvement over the old skill,
an isolated thirteen-case benchmark, or proof of automatic skill discovery.
The nine other defined prompts were not run as model evaluations. Example
execution and structural checks above provide separate evidence.

## Unperformed qualification

The full upstream test suite, no-Python Arrow persistence, live adapter/report
coverage, real account reconciliation, venue bracket protection and performance
were not exercised. No claim of production or financial qualification is made.
The host application's broad Rust gates were not run for this documentation
and independent-example change; its application crate and dependency files
were not modified.
