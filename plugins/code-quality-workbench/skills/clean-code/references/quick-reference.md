# Quick reference

### 1. Meaningful Names (CRITICAL)

- [`name-intention-revealing`](./name-intention-revealing.md) - Use names that reveal intent
- [`name-avoid-disinformation`](./name-avoid-disinformation.md) - Avoid misleading names
- [`name-meaningful-distinctions`](./name-meaningful-distinctions.md) - Make meaningful distinctions
- [`name-pronounceable`](./name-pronounceable.md) - Use pronounceable names
- [`name-searchable`](./name-searchable.md) - Use searchable names
- [`name-avoid-encodings`](./name-avoid-encodings.md) - Avoid encodings in names
- [`name-class-noun`](./name-class-noun.md) - Use noun phrases for class names
- [`name-method-verb`](./name-method-verb.md) - Use verb phrases for method names

### 2. Functions (CRITICAL)

- [`func-small`](./func-small.md) - Keep functions small
- [`func-one-thing`](./func-one-thing.md) - Functions should do one thing
- [`func-abstraction-level`](./func-abstraction-level.md) - Maintain one level of abstraction
- [`func-minimize-arguments`](./func-minimize-arguments.md) - Minimize function arguments
- [`func-no-side-effects`](./func-no-side-effects.md) - Avoid side effects
- [`func-command-query-separation`](./func-command-query-separation.md) - Separate commands from queries
- [`func-dry`](./func-dry.md) - Do not repeat yourself

### 3. Comments (HIGH)

- [`cmt-express-in-code`](./cmt-express-in-code.md) - Express yourself in code, not comments
- [`cmt-explain-intent`](./cmt-explain-intent.md) - Use comments to explain intent
- [`cmt-avoid-redundant`](./cmt-avoid-redundant.md) - Avoid redundant comments
- [`cmt-avoid-commented-out-code`](./cmt-avoid-commented-out-code.md) - Delete commented-out code
- [`cmt-warning-consequences`](./cmt-warning-consequences.md) - Use warning comments for consequences

### 4. Formatting (HIGH)

- [`fmt-vertical-formatting`](./fmt-vertical-formatting.md) - Use vertical formatting for readability
- [`fmt-horizontal-alignment`](./fmt-horizontal-alignment.md) - Avoid horizontal alignment
- [`fmt-team-rules`](./fmt-team-rules.md) - Follow team formatting rules
- [`fmt-indentation`](./fmt-indentation.md) - Respect indentation rules

### 5. Error Handling (HIGH)

- [`err-use-exceptions`](./err-use-exceptions.md) - Separate error handling from happy path
- [`err-write-try-catch-first`](./err-write-try-catch-first.md) - Write try-catch-finally first
- [`err-provide-context`](./err-provide-context.md) - Provide context with exceptions
- [`err-define-by-caller-needs`](./err-define-by-caller-needs.md) - Define exceptions by caller needs
- [`err-avoid-null`](./err-avoid-null.md) - Avoid returning and passing null

### 6. Objects and Data Structures (MEDIUM-HIGH)

- [`obj-data-abstraction`](./obj-data-abstraction.md) - Hide data behind abstractions
- [`obj-data-object-asymmetry`](./obj-data-object-asymmetry.md) - Understand data/object anti-symmetry
- [`obj-law-of-demeter`](./obj-law-of-demeter.md) - Follow the Law of Demeter
- [`obj-avoid-hybrids`](./obj-avoid-hybrids.md) - Avoid hybrid data-object structures
- [`obj-dto`](./obj-dto.md) - Use DTOs for data transfer

### 7. Boundaries (MEDIUM-HIGH)

- [`bound-wrap-third-party`](./bound-wrap-third-party.md) - Wrap third-party APIs
- [`bound-learning-tests`](./bound-learning-tests.md) - Write learning tests for third-party code

### 8. Classes and Systems (MEDIUM-HIGH)

- [`class-small`](./class-small.md) - Keep classes small
- [`class-cohesion`](./class-cohesion.md) - Maintain class cohesion
- [`class-organize-for-change`](./class-organize-for-change.md) - Organize classes for change
- [`class-isolate-from-change`](./class-isolate-from-change.md) - Isolate classes from change
- [`class-separate-concerns`](./class-separate-concerns.md) - Separate construction from use

### 9. Unit Tests (MEDIUM)

- [`test-first-law`](./test-first-law.md) - Follow the three laws of TDD
- [`test-keep-clean`](./test-keep-clean.md) - Keep tests clean
- [`test-one-assert`](./test-one-assert.md) - One concept per test
- [`test-first-principles`](./test-first-principles.md) - Follow FIRST principles
- [`test-build-operate-check`](./test-build-operate-check.md) - Use Build-Operate-Check pattern

### 10. Emergence and Simple Design (MEDIUM)

- [`emerge-simple-design`](./emerge-simple-design.md) - Follow the four rules of simple design
- [`emerge-expressiveness`](./emerge-expressiveness.md) - Maximize expressiveness
