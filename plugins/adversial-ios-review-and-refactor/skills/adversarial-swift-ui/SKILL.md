---
name: adversarial-swift-ui
description: Run a pass/fail SwiftUI implementation gate when the user requests a formal code review.
---

# Adversarial SwiftUI Gate

A SwiftUI architecture review gate — pass/fail: a single blind reviewer subagent judges the work against this gate's rules with an adversarial mandate, and the work passes only when every rule is PASS or N/A. This skill renders verdicts; it never fixes the work.

The rules are filtered down to the checks a reviewer can decide from code evidence alone. The gate judges the failure modes agents and experienced-but-not-expert developers actually produce: legacy observation stacks, identity-destroying conditionals, work attached to the wrong lifecycle point, laziness-defeating list construction, animations that leak across generic content, and controls that opt out of the system's accessibility semantics.

Use this gate only when a formal PASS/FAIL review is requested. Routine implementation and advisory review do not invoke it.

## When to Apply

Use when the user explicitly requests a pass/fail SwiftUI implementation gate for a fixed diff or file set.

Do not apply to targets without a SwiftUI surface or to advisory review. Use `adversarial-swift` for language rules and `adversarial-ios-design` for rendered design only when those separate gates are requested. Newer-SDK remedies are N/A when the project cannot use them.

## Review Protocol

Follow these steps exactly — the gate's value is that every review runs the same way.

Two preconditions before step 1 — both exist because their violation is the gate family's recorded field-failure mode (July 2026: gates run as cleanup drivers on a moving target rendered zero verdicts while the diff grew to 33 files):

- **Frozen target.** Dispatch only against a fixed ref — a commit SHA, stash, or saved diff — recorded as the target manifest. If the code under review is still changing (the worktree keeps collecting edits, other agents are active on it), do not dispatch. A target change while the reviewer is in flight voids the run: report `GATE VOID — target changed` in place of a verdict and re-dispatch against the new frozen state. A dispatched gate must always end in a rendered verdict, a `GATE NOT APPLICABLE`, or a recorded void — never silence, which is indistinguishable from "reviewed".
- **Verdicts, not cleanup.** This gate is a terminal check on finished work. "Run the gate and fix everything aggressively" inverts the contract and is the documented path to scope explosion: implement first, freeze, then gate. After a FAIL, the caller applies fixes within the original target only, and the re-gate dispatches a fresh blind reviewer against the **same target manifest** — the surface never widens between rounds; new code means a new gate invocation with its own manifest.

When other agents may mutate the workspace mid-review, the reviewer reads the rules from an immutable snapshot (e.g. `git archive <ref> <skill-dir> | tar -x -C "$TMPDIR"`) rather than the live checkout — and skill directories are read-only infrastructure, excluded from every cleanup or fix scope.

1. **Identify the target.** Pin down exactly what is under review (a diff, a set of files, a PR) and note the ref/paths so the review runs against an unambiguous, fixed target. Record the Swift toolchain version and minimum deployment target (from `Package.swift`, the Xcode project, or availability annotations) — several rules version-gate on them. Include the repo root in the target description — `update-pass-minimal-data`, `state-own-models-in-state`, and `update-cache-expensive-derivations` can require reading whole files beyond the diff hunks.
2. **Load the rules.** Read [references/_sections.md](references/_sections.md) and every rule file in `references/` (all `state-*.md`, `update-*.md`, `identity-*.md`, `task-*.md`, `list-*.md`, `anim-*.md`, `access-*.md` files).
3. **Compose the reviewer prompt.** Fill [references/reviewer-prompt.md](references/reviewer-prompt.md) with the rules, the target, and the toolchain/deployment facts. The composed prompt must be fully self-contained — a reviewer sees no conversation history, so nothing may refer to context outside the prompt.
4. **Dispatch one blind reviewer.** Launch a single Task subagent whose entire input is the composed prompt — no conversation context, no commentary alongside it.
5. **Render fail-closed.** The reviewer's structured output is the verdict — there is no merge step. Overall verdict is PASS only when every rule is PASS or N/A; any single FAIL fails the gate. Never average, weigh severity, or waive a rule — a "minor" FAIL is a FAIL. If the reviewer returns "GATE NOT APPLICABLE" (no SwiftUI surface), stop and report that instead of a verdict.
6. **Render the verdict.** Fill [assets/templates/verdict.md](assets/templates/verdict.md). On FAIL, aggregate the reviewer's "missing for PASS" suggestions into the fix list, each with its location, ordered by category importance. Every rule whose final result is FAIL must appear in the fix list with a change concrete enough to apply as written — if the reviewer's suggestion only restates the violation, derive the fix from the rule's Correct example before rendering. The fix list is verification material — proof that each FAIL is decidable and flippable — not a work queue: every fix names the minimal change that flips its rule inside the declared target, and a fix that reaches for an unsafe escape hatch (`@unchecked Sendable`, `try!`, force-unwraps) to satisfy a rule does not flip it. Violations the reviewer noticed outside the target manifest go under the verdict's out-of-scope observations — reported for a future gate invocation, never fixed under this one, never counted in the verdict.

If the same rule flips verdicts across re-reviews of an unchanged target, or a human reads the evidence and overrides the verdict, that is a decidability bug in the rule — record it in [gotchas.md](gotchas.md) and sharpen the rule; do not override the gate.

## Verdict Format

The reviewer returns, per rule: `PASS | FAIL | N/A`, evidence (`file:line` or a quote — required for PASS as well as FAIL), and for every FAIL, the fix that flips the rule to PASS once applied — the named change plus its location, never a restatement of the violation. The final report follows [assets/templates/verdict.md](assets/templates/verdict.md).

## Rule Categories

| # | Category | Prefix | Covers |
|---|----------|--------|--------|
| 1 | Data Modeling & Observation | `state-` | `@Observable` over `ObservableObject`, `@State` ownership of view-created models, no `State(initialValue:)` from init params, identity guards on `.task(id:)` model re-creation, `callAsFunction` wrappers for environment closures, no high-frequency values in `EnvironmentValues` |
| 2 | View Update Cost | `update-` | Subview structs over computed `some View` vars, minimal data per leaf view, no side effects in view `init`, cached O(n) derivations, no collection-bearing structs on list rows |
| 3 | Structural View Identity | `identity-` | Branch inside modifier values not around views, no runtime `if/else` in modifier helpers (`applyIf`), `AnyLayout` over container branches |
| 4 | Data Loading & Task Lifecycle | `task-` | `.task` over `.onAppear`+`Task`, `.task(id:)` over `.onChange`+`Task`, scalar compared values, `@concurrent` offloading of CPU work in `@MainActor` observables |
| 5 | Lists & Geometry | `list-` | Constant per-element view count in `ForEach`, no `AnyView` rows, `onGeometryChange` over measurement `GeometryReader`, no geometry feedback loops, `visualEffect` for scroll-driven transforms |
| 6 | Animation Scope | `anim-` | `animation(_:body:)` for generic containers over value-based `.animation` on arbitrary content, built-in animatable attributes over custom `Animatable` |
| 7 | Platform Conventions & Accessibility | `access-` | Buttons built with title and icon, `Button` over `onTapGesture`, style protocols over rebuilt controls, accessibility representations for bespoke controls, semantic fonts and colors, `@ScaledMetric` for custom spacing near text |

## Gotchas

Read [gotchas.md](gotchas.md) before dispatching the reviewer — it pre-records rule-fidelity guards (patterns this gate's rules endorse that community lore condemns, such as `id: \.self` on constant collections and view models held in `@State`) so the reviewer does not import outside rules.

## Related Skills

`adversarial-swift` handles Swift language rules; `adversarial-ios-design` handles rendered design and UX; `ios-taste` handles advisory design. Run a sibling gate only when the requested review scope calls for it.

## Reference Files

| File | Description |
|------|-------------|
| [references/reviewer-prompt.md](references/reviewer-prompt.md) | Self-contained prompt template for the blind reviewer |
| [assets/templates/verdict.md](assets/templates/verdict.md) | Verdict report template |
| [references/_sections.md](references/_sections.md) | Category definitions and ordering |
| [metadata.json](metadata.json) | Version and source references |
