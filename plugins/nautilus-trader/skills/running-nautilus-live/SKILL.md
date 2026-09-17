---
name: running-nautilus-live
description: Compose, diagnose, or review native Nautilus Rust nodes, routing, readiness, persistence, reconciliation, recovery, and shutdown. Databento and IBKR recipes; excludes strategy rules and CI/container deployment scaffolding.
metadata:
  author: kmshdev
  version: "0.64.0"
---

# Compose and operate a native node

**Input:** intended data/execution clients, environment, authorized account and
recovery/readiness requirements. **Output:** supported native composition and
an evidence-based readiness or failure assessment.

Bundled examples use `=0.64.0` and Rust 1.98.1+. Existing applications retain
their lockfile, features and source overrides unless an upgrade is requested.
For upgrades or framework workarounds, use
[version and integration](references/version-and-integration.md).

Native node compilation needs `nautilus-live/node`. Accept explicit typed config; never discover account credentials.

## Instructions

1. Identify the requested boundary: construction-only, real-time simulated
   execution, or explicitly authorized paper/live connectivity. Read
   [the runtime guide](references/guide.md).
2. Configure native client factories and independent data/execution routes
   using [IBKR and Databento composition](references/adapters.md). Preserve the
   kernel's lifecycle and the application's existing order owner.
3. Establish readiness from actual required instruments, account and report
   coverage. Restore unresolved intent and reconcile before new admission.
4. Exercise the authorized construction/startup/recovery/stop boundary.
   Distinguish configured intent, native state and observed provider facts;
   record missing reports, residual exposure or incomplete persistence.

Use [runtime contracts](references/foundation.md) and
[connection recipes](references/connections.md) for restore, reports and runtime parity;
[source evidence](references/sources.md) for **0.64.0** behavior. No hidden
checkout, Python runtime or unrelated adapter is required by this guide.

Use [typed run configuration](references/configuration.md),
[component composition](references/composition.md), and the
[Rust test ladder](references/rust-testing.md) when those concerns are affected.
For durable capture or reruns, use [event replay](references/event-replay.md).
For supported provider extensions, use [adapter development](references/adapter-development.md).
Run the [construction-only example](assets/live-composition/README.md) for executable wiring.

## Examples

- "Wire Databento plus IB without connecting": use the construction sketch;
  stop at `.build()`, with reconciliation enabled and risk bypass false.
- "Simulate execution against Databento": use the guide's
  `add_simulated_exec_client` path, not an IB paper-account assumption.
- "Restart succeeded but mass status is missing": withhold new admission,
  retain unresolved intent and establish report coverage before resuming.
- "Stop with pending fills": drain native residual events and report confirmed
  orders/exposure and persistence outcomes, not merely a stop request.

Deliver the requested artifact with focused verification and material limits.
Follow the user's authorized scope and the target application's ownership.
