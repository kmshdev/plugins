---
name: clean-architecture
description: Apply Clean Architecture boundaries during an explicitly requested architecture review or redesign.
---

# Clean Architecture Best Practices

Comprehensive guide to Clean Architecture principles for designing maintainable, testable software systems. Based on Robert C. Martin's "Clean Architecture: A Craftsman's Guide to Software Structure and Design." Contains 42 rules across 8 categories, prioritized by architectural impact.

## When to Apply

Reference these guidelines when:
- Designing new software systems or modules
- Structuring dependencies between layers
- Defining boundaries between business logic and infrastructure
- Reviewing code for architectural violations
- Refactoring coupled systems toward cleaner structure

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Dependency Direction | CRITICAL | `dep-` |
| 2 | Entity Design | CRITICAL | `entity-` |
| 3 | Use Case Isolation | HIGH | `usecase-` |
| 4 | Component Cohesion | HIGH | `comp-` |
| 5 | Boundary Definition | MEDIUM-HIGH | `bound-` |
| 6 | Interface Adapters | MEDIUM | `adapt-` |
| 7 | Framework Isolation | MEDIUM | `frame-` |
| 8 | Testing Architecture | LOW-MEDIUM | `test-` |

## Reference routing

Use the category table above to choose a topic. Open [the rule index](references/quick-reference.md) only to locate the specific rule, then read that rule’s reference file.

## How to Use

Read individual reference files for detailed explanations and code examples:

- [Section definitions](references/_sections.md) - Category structure and impact levels
- [Rule template](assets/templates/_template.md) - Template for adding new rules

## Reference Files

| File | Description |
|------|-------------|
| [references/_sections.md](references/_sections.md) | Category definitions and ordering |
| [assets/templates/_template.md](assets/templates/_template.md) | Template for new rules |
