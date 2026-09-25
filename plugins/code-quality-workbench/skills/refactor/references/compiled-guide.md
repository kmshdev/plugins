# Code Refactoring

**Version 0.1.0**
Fowler/Martin
January 2026

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring codebases. Humans may also find it useful,
> but guidance here is optimized for automation and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive code refactoring guide based on Martin Fowler's refactoring catalog and Robert C. Martin's Clean Code principles, designed for AI agents and LLMs. Contains 43+ rules across 8 categories, prioritized by impact from critical (structure decomposition, reducing coupling) to incremental (micro-refactoring). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.

---

## Table of Contents

1. [Structure & Decomposition](./_sections.md#1-structure-&-decomposition) — **CRITICAL**
   - 1.1 [Apply Single Responsibility Principle](./struct-single-responsibility.md) — CRITICAL (reduces change impact radius by 60-90%)
   - 1.2 [Compose Method for Readable Flow](./struct-compose-method.md) — CRITICAL (reduces cognitive load by 40-60%)
   - 1.3 [Extract Class from Large Class](./struct-extract-class.md) — CRITICAL (improves testability and reduces cognitive load by 40-60%)
   - 1.4 [Extract Method for Long Functions](./struct-extract-method.md) — CRITICAL (reduces function complexity by 50-80%)
   - 1.5 [Introduce Parameter Object](./struct-parameter-object.md) — CRITICAL (reduces parameter count and enables behavior grouping)
   - 1.6 [Keep Functions Under 20 Lines](./struct-function-length.md) — CRITICAL (reduces cognitive load and bug density by 30-50%)
   - 1.7 [Replace Method with Method Object](./struct-replace-method-with-object.md) — CRITICAL (enables extraction from complex methods with many local variables)
2. [Coupling & Dependencies](./_sections.md#2-coupling-&-dependencies) — **CRITICAL**
   - 2.1 [Apply Interface Segregation Principle](./couple-interface-segregation.md) — CRITICAL (prevents unnecessary dependencies and enables focused testing)
   - 2.2 [Fix Feature Envy by Moving Methods](./couple-feature-envy.md) — CRITICAL (improves cohesion and reduces cross-class dependencies)
   - 2.3 [Hide Delegate to Reduce Coupling](./couple-hide-delegate.md) — CRITICAL (eliminates chain dependencies and reduces ripple effects)
   - 2.4 [Preserve Whole Object Instead of Fields](./couple-preserve-whole-object.md) — CRITICAL (reduces parameter coupling and simplifies method signatures)
   - 2.5 [Remove Middle Man When Excessive](./couple-remove-middle-man.md) — CRITICAL (eliminates unnecessary indirection and reduces code bloat)
   - 2.6 [Use Dependency Injection](./couple-dependency-injection.md) — CRITICAL (enables testing and reduces coupling by 70-90%)
3. [Naming & Clarity](./_sections.md#3-naming-&-clarity) — **HIGH**
   - 3.1 [Avoid Abbreviations and Acronyms](./name-avoid-abbreviations.md) — HIGH (eliminates guesswork and reduces onboarding time)
   - 3.2 [Avoid Type Encodings in Names](./name-avoid-encodings.md) — HIGH (prevents name staleness and reduces visual clutter)
   - 3.3 [Use Consistent Vocabulary](./name-consistent-vocabulary.md) — HIGH (eliminates confusion from synonyms and reduces mental mapping)
   - 3.4 [Use Intention-Revealing Names](./name-intention-revealing.md) — HIGH (reduces code comprehension time by 40-60%)
   - 3.5 [Use Searchable Names](./name-searchable-names.md) — HIGH (enables quick codebase navigation and reduces debugging time)
4. [Conditional Logic](./_sections.md#4-conditional-logic) — **HIGH**
   - 4.1 [Consolidate Duplicate Conditional Fragments](./cond-consolidate.md) — HIGH (reduces code duplication by 30-50%)
   - 4.2 [Decompose Complex Conditionals](./cond-decompose.md) — HIGH (reduces cognitive complexity by 40-60%)
   - 4.3 [Introduce Special Case Object](./cond-special-case.md) — HIGH (eliminates repeated null checks throughout codebase)
   - 4.4 [Replace Conditional with Lookup Table](./cond-lookup-table.md) — HIGH (reduces cyclomatic complexity and improves maintainability)
   - 4.5 [Replace Conditional with Polymorphism](./cond-polymorphism.md) — HIGH (eliminates repeated switch statements and enables Open-Closed Principle)
   - 4.6 [Replace Nested Conditionals with Guard Clauses](./cond-guard-clauses.md) — HIGH (reduces nesting depth and cognitive load by 50-70%)
5. [Abstraction & Patterns](./_sections.md#5-abstraction-&-patterns) — **MEDIUM-HIGH**
   - 5.1 [Apply Open-Closed Principle](./pattern-open-closed.md) — MEDIUM-HIGH (enables extension without modifying existing tested code)
   - 5.2 [Extract Strategy for Algorithm Variants](./pattern-strategy.md) — MEDIUM-HIGH (enables runtime algorithm swapping and isolated testing)
   - 5.3 [Extract Superclass for Common Behavior](./pattern-extract-superclass.md) — MEDIUM-HIGH (eliminates duplication across related classes)
   - 5.4 [Prefer Composition Over Inheritance](./pattern-composition-over-inheritance.md) — MEDIUM-HIGH (enables flexible behavior combination without class explosion)
   - 5.5 [Use Factory for Complex Object Creation](./pattern-factory.md) — MEDIUM-HIGH (reduces duplication by 40-60% and enables isolated testing)
   - 5.6 [Use Template Method for Shared Skeleton](./pattern-template-method.md) — MEDIUM-HIGH (eliminates duplicate control flow across similar algorithms)
6. [Data Organization](./_sections.md#6-data-organization) — **MEDIUM**
   - 6.1 [Encapsulate Collection](./data-encapsulate-collection.md) — MEDIUM (prevents uncontrolled modifications and enforces invariants)
   - 6.2 [Encapsulate Record into Class](./data-encapsulate-record.md) — MEDIUM (enables derived data and controlled mutation)
   - 6.3 [Replace Primitive with Object](./data-replace-primitive.md) — MEDIUM (enables validation and domain-specific behavior)
   - 6.4 [Replace Temp with Query](./data-replace-temp-with-query.md) — MEDIUM (enables reuse and makes intent explicit)
   - 6.5 [Split Variable with Multiple Assignments](./data-split-variable.md) — MEDIUM (clarifies intent and prevents confusion from reused variables)
7. [Error Handling](./_sections.md#7-error-handling) — **MEDIUM**
   - 7.1 [Create Domain-Specific Exception Types](./error-custom-exceptions.md) — MEDIUM (enables precise error handling and better error messages)
   - 7.2 [Fail Fast with Preconditions](./error-fail-fast.md) — MEDIUM (reduces debugging time by 50-70%)
   - 7.3 [Separate Error Handling from Business Logic](./error-separate-concerns.md) — MEDIUM (reduces function complexity by 30-50%)
   - 7.4 [Use Exceptions Instead of Error Codes](./error-exceptions-over-codes.md) — MEDIUM (separates error handling from happy path and prevents ignored errors)
8. [Micro-Refactoring](./_sections.md#8-micro-refactoring) — **LOW**
   - 8.1 [Inline Trivial Variables](./micro-inline-variable.md) — LOW (reduces indirection and visual clutter)
   - 8.2 [Remove Dead Code](./micro-remove-dead-code.md) — LOW (reduces cognitive load and maintenance burden)
   - 8.3 [Rename for Clarity](./micro-rename-for-clarity.md) — LOW (makes code self-documenting and reduces need for comments)
   - 8.4 [Simplify Boolean Expressions](./micro-simplify-expressions.md) — LOW (improves readability and reduces cognitive load)

---

## References

1. [https://refactoring.com/catalog/](https://refactoring.com/catalog/)
2. [https://refactoring.guru/refactoring/smells](https://refactoring.guru/refactoring/smells)
3. [https://martinfowler.com/books/refactoring.html](https://martinfowler.com/books/refactoring.html)
4. [https://en.wikipedia.org/wiki/SOLID](https://en.wikipedia.org/wiki/SOLID)

---

## Source Files

This document was compiled from individual reference files. For detailed editing or extension:

| File | Description |
|------|-------------|
| [references/_sections.md](./_sections.md) | Category definitions and impact ordering |
| [assets/templates/_template.md](../assets/templates/_template.md) | Template for creating new rules |
| [SKILL.md](../SKILL.md) | Quick reference entry point |
