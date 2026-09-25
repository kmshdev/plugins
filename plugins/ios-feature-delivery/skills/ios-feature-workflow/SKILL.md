---
name: ios-feature-workflow
description: Implement a specified iOS app feature through repository discovery, focused implementation, simulator verification, and selected final review.
---

# iOS feature workflow

Use this skill when the user invokes its [trigger prompt](references/trigger-prompt.md) for a concrete app feature. Carry the feature through a running, verified result. The workflow adapts the discover → act → verify loop from `dx-harness` to iOS delivery; its bootstrap and reset scripts are not part of feature implementation.

## Discover

Identify the user outcome, affected screens and data, target, scheme, simulator, deployment version, existing architecture, and relevant project conventions. Read only the project documentation needed for those decisions. Establish observable acceptance criteria and the smallest test surface that can verify them. Ask only for information that cannot be found in the app or inferred from the request.

## Route and implement

Use Build iOS Apps skills for building, running, simulator inspection, and debugging when installed. The `ios-debugger-agent` is the default build/run path; use focused SwiftUI UI, performance, or leak skills when those issues arise. If that plugin is unavailable, use the project's `xcodebuild`, simulator, and test workflow directly.

Select other specialists only when the task warrants them:

- Use `$ios-interface-craft` for screen hierarchy, interaction, visual polish, design systems, navigation, or motion.
- Use `$swift-app-foundations` for SwiftData, measured performance, or an established modular MVVM-C boundary.
- Use the installed SwiftUI builder for focused controls, forms, charts, and effects when relevant.

Implement within the app's current patterns. Do not introduce an architecture or visual redesign merely because a specialist describes one.

## Verify and review

Build and run the affected app flow. Exercise meaningful states and relevant appearances or accessibility sizes; capture before/after images for UI changes and a short recording for motion changes. Run affected tests and resolve failures caused by the feature. Compare the result with the acceptance criteria.

Once implementation and verification are complete, freeze the target and invoke `$ios-review-and-refactor` for applicable formal gates if that plugin is installed. The explicit trigger prompt requests this final review. Keep the gate target and fixes within the feature scope. If a gate or simulator capture cannot run, report the blocker and the verification that did run; do not claim PASS.

Finish with the user outcome, changed behavior, build/test and rendered evidence, final gate verdicts, and remaining limitations. Do not publish or push unless separately requested.
