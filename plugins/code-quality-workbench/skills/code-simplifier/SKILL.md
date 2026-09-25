---
name: code-simplifier
description: Simplify existing code while preserving behavior during an explicitly requested cleanup pass.
---

# Community Code Simplification Best Practices

Comprehensive code simplification guide for AI agents and LLMs. Contains 47 rules across 8 categories, prioritized by impact from critical (context discovery, behavior preservation) to incremental (language idioms). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics.

## Core Principles

1. **Context First**: Understand project conventions before making any changes
2. **Behavior Preservation**: Change how code is written, never what it does
3. **Scope Discipline**: Focus on recently modified code, keep diffs small
4. **Clarity Over Brevity**: Explicit, readable code beats clever one-liners

## When to Apply

Reference these guidelines when:
- Simplifying or cleaning up recently modified code
- Reducing nesting, complexity, or duplication
- Improving naming and readability
- Applying language-specific idiomatic patterns
- Reviewing code for maintainability issues

## Rule Categories by Priority

| Priority | Category | Impact | Prefix | Rules |
|----------|----------|--------|--------|-------|
| 1 | Context Discovery | CRITICAL | `ctx-` | 4 |
| 2 | Behavior Preservation | CRITICAL | `behave-` | 6 |
| 3 | Scope Management | HIGH | `scope-` | 5 |
| 4 | Control Flow Simplification | HIGH | `flow-` | 9 |
| 5 | Naming and Clarity | MEDIUM-HIGH | `name-` | 6 |
| 6 | Duplication Reduction | MEDIUM | `dup-` | 5 |
| 7 | Dead Code Elimination | MEDIUM | `dead-` | 5 |
| 8 | Language Idioms | LOW-MEDIUM | `idiom-` | 7 |

## Reference routing

Use the category table above to choose a topic. Open [the rule index](references/quick-reference.md) only to locate the specific rule, then read that rule’s reference file.

## Workflow

1. **Discover context**: Read CLAUDE.md, lint configs, examine existing patterns
2. **Identify scope**: Focus on recently modified code unless asked to expand
3. **Apply transformations**: Use rules in priority order (CRITICAL first)
4. **Verify behavior**: Ensure outputs, errors, and side effects remain identical
5. **Keep diffs minimal**: Small, focused changes that are easy to review

## How to Use

Read individual reference files for detailed explanations and code examples:

- [Section definitions](references/_sections.md) - Category structure and impact levels
- [Rule template](assets/templates/_template.md) - Template for adding new rules

## Reference Files

| File | Description |
|------|-------------|
| [references/_sections.md](references/_sections.md) | Category definitions and ordering |
| [assets/templates/_template.md](assets/templates/_template.md) | Template for new rules |
