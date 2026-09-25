---
name: code-quality-review
description: Select a focused maintainability, architecture, simplification, refactoring, or DDD pass for a completed coding milestone.
---

# Code quality review

Use this workbench when the user requests a review or refactoring pass on a defined target. Choose only the method that answers the request; do not run every catalog at the end of an unrelated session.

| Question | Skill |
|---|---|
| Are naming, functions, and local code structure clear? | [Clean Code](../clean-code/SKILL.md) |
| Are dependencies and use cases crossing architecture boundaries? | [Clean Architecture](../clean-architecture/SKILL.md) |
| Can this code become simpler without changing behavior? | [Code Simplifier](../code-simplifier/SKILL.md) |
| Which structural refactoring fits an identified smell? | [Refactor](../refactor/SKILL.md) |
| Does domain language and model integrity pass a formal gate? | [Adversarial DDD](../adversarial-ddd/SKILL.md) |

Apply the selected skill's own constraints. Keep any edits within the requested target and verify behavior afterward. The DDD gate renders verdicts; do not treat its review as authorization to change unrelated domain surfaces.
