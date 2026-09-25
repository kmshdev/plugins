---
name: ios-review-and-refactor
description: Review a completed iOS change with applicable formal gates, fix findings within the original scope, and verify the result.
---

# iOS review and refactor

Use this workflow only when the user requests a formal review and repair of completed iOS work. The three gate skills render verdicts; this workflow owns any subsequent edits. A routine feature request does not activate it automatically.

## Select gates

| Changed surface | Gate |
|---|---|
| Rendered SwiftUI screen or interaction | [iOS design](../adversarial-ios-design/SKILL.md) |
| SwiftUI implementation | [SwiftUI](../adversarial-swift-ui/SKILL.md) |
| Swift language code | [Swift](../adversarial-swift/SKILL.md) |

Select only applicable gates. The rendered design gate requires simulator evidence; a code-only judgment cannot substitute for it. Record a named blocker when evidence cannot be captured.

## Workflow

1. Identify the user's intended change, fixed diff or file set, toolchain, deployment target, and available simulator. Record the review scope before dispatch.
2. Finish implementation and affected verification first. Freeze a snapshot of the target. Do not run a gate while the target is changing.
3. Read and invoke each selected gate according to its own protocol. Preserve its blind reviewer, evidence, and verdict requirements; do not combine their rule sets into one reviewer.
4. Report each verdict. For failures, make the smallest in-scope changes that address the cited evidence. Leave out-of-scope observations for a later task.
5. Rerun affected builds, tests, and captures. Freeze a new snapshot, then dispatch fresh reviews for affected gates. Keep the original scope fixed through each round.
6. Stop when the selected gates pass, are not applicable, or have a concrete blocker. Report the final verdicts and any unresolved findings with evidence.

Treat a gate's fix list as review evidence, not permission to expand the work. Never describe an uncaptured UI gate as PASS.
