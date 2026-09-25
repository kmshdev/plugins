---
name: refactor
description: Apply Fowler refactoring patterns during an explicitly requested structural refactor.
---

# Fowler/Martin Code Refactoring Best Practices

Comprehensive code refactoring guide based on Martin Fowler's catalog and Clean Code principles, designed for AI agents and LLMs. Contains 43 rules across 8 categories, prioritized by impact to guide automated refactoring and code generation.

## When to Apply

Reference these guidelines when:
- Refactoring existing code to improve maintainability
- Decomposing long methods or large classes
- Reducing coupling between components
- Simplifying complex conditional logic
- Reviewing code for code smells and anti-patterns

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Structure & Decomposition | CRITICAL | `struct-` |
| 2 | Coupling & Dependencies | CRITICAL | `couple-` |
| 3 | Naming & Clarity | HIGH | `name-` |
| 4 | Conditional Logic | HIGH | `cond-` |
| 5 | Abstraction & Patterns | MEDIUM-HIGH | `pattern-` |
| 6 | Data Organization | MEDIUM | `data-` |
| 7 | Error Handling | MEDIUM | `error-` |
| 8 | Micro-Refactoring | LOW | `micro-` |

## Reference routing

Use the category table above to choose a topic. Open [the rule index](references/quick-reference.md) only to locate the specific rule, then read that rule’s reference file.

## How to Use

Read individual reference files for detailed explanations and code examples:

- [Section definitions](references/_sections.md) - Category structure and impact levels
- [Rule template](assets/templates/_template.md) - Template for adding new rules
- Individual rules: `references/{prefix}-{slug}.md`

## Full Compiled Document

For the complete guide with all rules expanded: `references/compiled-guide.md`
