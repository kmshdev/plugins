---
name: dev-rfc
description: Draft a technical RFC when a decision needs alternatives, tradeoffs, and review.
---

# Dev RFC Skill

Write RFCs and technical proposals that serve two purposes: **aligning stakeholders on what to build and why** (RFCs), and **helping engineers understand how a system works** (architecture docs). Most real proposals blend both — the skill helps you pick the right sections for the situation.

## Reference Templates

Read `references/template.md` for the three structural templates:

- **RFC** — for pre-build alignment. Focuses on abstract, approaches (with fair comparison), service SLAs, observability, and rollout plan.
- **Architecture Doc** — for documenting built systems. Focuses on diagrams, source tree, data flow, design philosophy.
- **One-Pager** — for small changes (< 1 week). Problem, Proposed Solution, Rollout. ~20 lines.

## Step 0: Pick the Mode

Infer the mode from the request and project context. Ask only if the choice changes the deliverable and remains unclear:

| Situation | Mode | Key question the doc answers |
|-----------|------|------------------------------|
| Planning a new system or major change | **RFC** | "Should we build this, and how?" |
| Documenting an existing system | **Architecture Doc** | "How does this system work?" |
| Proposing a change to an existing system | **RFC** (with before/after diagrams in Detailed Design) | "Why are we changing this, and what will it look like?" |
| Small scoped change (< 1 week) | **One-Pager** | "What and why, briefly?" |

For changes to existing systems, use the RFC structure as the backbone but include before/after architecture diagrams in the **Detailed Design** section, with `[NEW]` and `[CHANGED]` markers on components.

### File Placement

- **Formal proposal or RFC** — `docs/rfcs/RFC-NNN-title.md` as primary location
- **Architecture doc for the whole project** — `ARCHITECTURE.md` at the repo root
- **Subsystem doc** — `docs/design/subsystem-name.md` or alongside the code it describes

If the user has not specified a location, follow the project's existing documentation layout; otherwise use the locations above.

For drafting, review, and optional live authoring, read [the RFC workflow](references/workflow.md) after choosing a mode.
