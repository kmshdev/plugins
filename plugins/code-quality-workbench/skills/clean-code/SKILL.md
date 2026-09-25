---
name: clean-code
description: Apply the Clean Code rule catalog during an explicitly requested maintainability review.
---

# Robert C. Martin (Uncle Bob) Clean Code Best Practices

Comprehensive software craftsmanship guide based on Robert C. Martin's "Clean Code: A Handbook of Agile Software Craftsmanship", updated with modern corrections where the original 2008 advice has been superseded. Contains 48 rules across 10 categories, prioritized by impact to guide code reviews, refactoring decisions, and new development. Examples are primarily in Java but principles are language-agnostic.

## When to Apply

Reference these guidelines when:
- Writing new functions, classes, or modules
- Naming variables, functions, classes, or files
- Reviewing code for maintainability issues
- Refactoring existing code to improve clarity
- Writing or improving unit tests
- Wrapping third-party dependencies

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Meaningful Names | CRITICAL | `name-` |
| 2 | Functions | CRITICAL | `func-` |
| 3 | Comments | HIGH | `cmt-` |
| 4 | Formatting | HIGH | `fmt-` |
| 5 | Error Handling | HIGH | `err-` |
| 6 | Objects and Data Structures | MEDIUM-HIGH | `obj-` |
| 7 | Boundaries | MEDIUM-HIGH | `bound-` |
| 8 | Classes and Systems | MEDIUM-HIGH | `class-` |
| 9 | Unit Tests | MEDIUM | `test-` |
| 10 | Emergence and Simple Design | MEDIUM | `emerge-` |

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
