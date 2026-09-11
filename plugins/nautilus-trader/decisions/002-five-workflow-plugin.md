# ADR-002: Five independent workflow skills, one distribution plugin

Historical decision; compatibility discovery is superseded by [ADR-003](003-codex-plugin.md).


Status: accepted for the requested implementation. Supersedes ADR-001's
single-skill packaging choice; its Rust-only, source-qualified and portable
boundaries remain unchanged.

## Context

The user approved workflow-oriented decomposition and then requested all five
skills, limiting adapters to Interactive Brokers and Databento. A single router
would now mix distinct deliverables and weaken implicit task selection.
Crate-by-crate skills would split continuous ownership chains: a Strategy task
regularly crosses trading, model, execution, risk, Cache and Portfolio crates.

## Decision

Distribute a knowledge-only plugin with exactly five entries under `skills/`:
actors, strategies, data integration, backtesting and live runtime composition.
Use the portable root `plugin.json` format described by the
[plugin specification](https://developers.openai.com/plugins/build/plugins).
Do not add hooks, executables, MCP servers, global config or trading authority.
The plugin is a distribution unit, not a runtime requirement.

Each workflow has a compact imperative SKILL router, one primary guide and
locally bundled optional evidence/resources. Shared foundation, selected source
evidence, examples and fixed evaluator cases are generated deterministically
from this package's canonical inputs. Installed skills never run the generator
or require a sibling skill, this repository, or an upstream source checkout.
Duplicated local reference bytes buy independent installation; drift checks
prevent manual copies from diverging.

Keep the old root SKILL as an explicit compatibility entry and disable implicit
invocation in OpenAI metadata where supported. The plugin's discovery root
contains only the five workflow directories. Legacy hosts that ignore this
metadata should install the five directories individually, not the parent as
another automatic skill. Preserve the old repository path symlink.

Architecture/message-bus knowledge is a reference, not a sixth trigger.
Cross-component ownership and failure cases are explicit in
[coverage](../coverage.md). Coverage means composing the core framework,
not reimplementing every crate or supporting every adapter.

The implementation's [connection recipes](../references/connections.md) retain
one canonical C1-C8 specification. The resource generator selects task-relevant
sections and their source evidence for each skill. This is the second,
architectural reference structure beneath the five workflow triggers, not a
new discovery entry. Native fixtures qualify only the paths they actually
exercise; a coverage table is not a runtime or provider test.

## Evidence and acceptance

Use bounded build/evaluate passes recorded in [BUILD_LOG](../BUILD_LOG.md).
Freeze working and held-out cases before model feedback. Run NVIDIA
SkillEvaluator tiers independently, preserving no-skill baseline and isolated
task staging. Explain governance findings, model/scanner limitations, and
operational failures without weakening checks or inventing metadata.

## Consequences

Skill descriptions remain short and job-focused. The package can be copied as
a plugin or skills independently, at the cost of duplicated example lockfiles.
Public publication/licensing and author-contact policy require a separate
owner decision. No installation, publication, provider access or account
authorization is implied by producing the bundle.
