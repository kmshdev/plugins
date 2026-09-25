---
name: engineering-research-and-planning
description: Select a focused research or planning method for a defined engineering question or deliverable.
---

# Engineering research and planning

Use this router when the user asks for a research finding, plan, specification, or proposal. Identify the actual deliverable first, then read only the relevant specialist. Do not create a planning artifact as a prerequisite to ordinary implementation unless the user requested one or the task genuinely spans sessions.

## Planning

| Desired deliverable | Specialist |
|---|---|
| iOS app concept organized into implementable design milestones | [App Planner](../app-planner/SKILL.md) |
| Technical decision with alternatives and tradeoffs | [Dev RFC](../dev-rfc/SKILL.md) |
| Living plan for multi-session implementation | [ExecPlan](../exec-plan/SKILL.md) |
| Feature scope, requirements, and acceptance criteria | [Feature Specification](../feature-spec/SKILL.md) |

## Research

| Question | Specialist |
|---|---|
| How a focused pattern works in a named external codebase | [Code Distill](../code-distill/SKILL.md) |
| Which algorithms can map modules or feature domains in a codebase | [Codebase Comprehension Algorithms](../codebase-comprehension-algorithms/SKILL.md) |
| Which user capabilities and vertical slices exist in a Swift product | [Domain Architect](../domain-architect/SKILL.md) |
| How to define a deterministic software metric | [Deterministic Metric Design](../deterministic-metric-design/SKILL.md) |
| Whether a candidate metric survives empirical checks | [Metric Validation Harness](../metric-validation-harness/SKILL.md) |

Use more than one specialist only when the requested outcome needs both, such as designing a metric and validating it. Distinguish source facts from inferences, record the source or revision for external research, and keep the final artifact in the location the user or project conventions specify. The metric validation harness is read-only; other specialists retain their own side-effect boundaries.
