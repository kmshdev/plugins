# ADR-001: Portable, versioned Rust authoring skill

Historical decision; compatibility discovery is superseded by [ADR-003](003-codex-plugin.md).


Status: accepted for this bundle, 2026-09-09.

## Context

The previous skill routed readers into its hosting application's source,
architecture and commands. That made its framework guidance nonportable and
mixed general Rust APIs with one strategy's policy. The requested replacement
must serve first-time authors and advanced developers without requiring that
application or a hidden source tree.

The research started with the official Rust concepts and actor/strategy how-tos,
expanded through data, execution, backtesting, live guides and Rust tutorials,
then followed connected crate implementations. The source declares 0.63.0 but
has no independently established upstream revision. Current docs show some
different dependency/feature names and stronger guarantees than the inspected
runtime implements. Provenance and discrepancy handling are therefore part of
the product, not footnotes.

## Decision

Publish one skill, **`nautilus-trader`**, with a minimal root router and
task-specific references. Keep source evidence, the ADR and evaluation machinery
off the normal task-loading path. Bundle an independent offline Rust example and
an explicit qualification record. External URLs and source coordinates support
audits but are not prerequisites for normal use.

A plugin is not justified: the current need is knowledge and reproducible
examples, not credentialed tools, a persistent index, runtime state, UI,
background execution or automatic account operations. Adding those facilities
would introduce installation coupling, privileges and maintenance without
improving the authoring contract.

The skill does not prescribe a role pipeline, model identity, compulsory
step-by-step reasoning, full-library reads, repeated broad tests, provider,
database, strategy or application folder layout. It states only boundaries
whose omission predictably changes correctness.

## Prompting design

The requested [skill-design discussion](https://x.com/pvncher/status/2095991462416490862)
motivates a concise trigger and progressive disclosure, not a long itinerary.
The [second discussion](https://x.com/sairahul1/status/2096902575035683147)
reinforces removing stale, conflicting and redundant instructions. These are
design commentary, not framework API evidence.

The [OpenAI Astra article](https://developers.openai.com/blog/how-to-build-games-with-astra)
demonstrates outcome constraints, inspectable state and repeatable scenarios.
Here that becomes an offline scenario with explicit observed counts and
boundary-focused cases, not a copy of a game-development workflow.
No empirical claim that this packaging improves every model is made.

## Boundary and compatibility

All guidance, runnable example sources, source hashes and evaluation definitions
live below the canonical skill directory. No script requires a specific cwd
outside it. No default maintenance command downloads data or connects an account.
Compiler dependencies are external software, not hidden knowledge prerequisites.

The legacy directory name remains a relative symlink so existing repository
links resolve without editing concurrently owned documents. Install only the
canonical directory; the alias can be retired when those inbound links are
migrated by their owners. The former `nodes` and `this-crate` pages remain small
internal compatibility routes; the latter no longer embeds host policy.

Legacy evaluation output was not adopted as evidence for the replacement.
Fresh qualification distinguishes structural checks, model responses, compiler
execution, simulation and external venue evidence.

## Consequences

The bundle can be relocated and read offline. Its knowledge is deliberately
bounded: it is not a replacement for every crate's API docs, an exhaustive
adapter certification, or a profitability guide. Detailed claims identify
source symbols and hashable files; version labels alone do not establish
artifact equality.

Maintainers must re-audit source/doc mismatches when updating the pin.
The basic checker can detect broken local links, escaping paths, missing
evidence hashes and unpinned example dependencies; it cannot prove financial
correctness or semantic accuracy of every paragraph.

## Reconsider a plugin when

A concrete requirement appears for a version-addressed symbol service,
compiler-backed API queries, sandboxed scenario execution or authenticated
provider tooling across projects. Keep any future plugin a thin optional tool
layer around this skill, with explicit input/output schemas and permissions.
Do not grant trading, destructive recovery or secret access as a consequence of
installing authoring knowledge.

## Completion criteria

One canonical skill name; no required local link outside the bundle; Rust-only
examples; exact framework pins; official-doc and source evidence; explicit
discrepancies; a tested offline path; evaluation cases for both basic and
advanced failure modes; no application-code or trading-policy changes.
