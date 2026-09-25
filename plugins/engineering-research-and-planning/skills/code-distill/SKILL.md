---
name: code-distill
description: Extract a reusable implementation pattern from a specific external codebase for a focused question.
---

# Code Distill

Answer a focused implementation question using source from the named repository. Establish the repository and revision, then locate the relevant implementation, its tests, and its public use sites. Cite the files and revision that support the extracted pattern.

## Reference routing

- To narrow the query and locate code, read [query classification](references/find-classify-query.md) and [search before reading](references/find-grep-before-read.md).
- To confirm intended behavior, read [tests as evidence](references/find-tests-show-intent.md).
- To trace the API and variants, read [imports](references/trace-imports-outward.md) and [usages](references/trace-usages-inward.md).
- To separate the useful mechanism from scaffolding, read [load-bearing code](references/filter-load-bearing.md).
- If the user requests a reusable record and provides a location, read [capture format](references/capture-registry-record.md).

Keep the result scoped to the user's question. Record findings only in a location the user requested or the current project already maintains.
