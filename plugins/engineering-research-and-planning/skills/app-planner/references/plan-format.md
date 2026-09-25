# Output Format and supporting guidance

## Output Format

Save the design-plan as a markdown file. Structure it EXACTLY like this:

```markdown
# [App Name] Design Plan — [Focus]

This DesignPlan is a living document. Progress, Decision Log, and
Surprises & Discoveries must stay up to date as work proceeds.

## Purpose / Big Picture

[1-3 sentences: what the user can do AFTER this plan is executed.
Outcome-focused, not feature-list.]

## User & Moments

- **[Persona 1]**: [who, when, device context]
- **[Persona 2]**: [who, when, device context]

| Frequency | Moment | What they do |
|-----------|--------|-------------|
| 50x/day | [moment name] | [one line] |
| 10x/day | [moment name] | [one line] |
| 5x/day | [moment name] | [one line] |
| 1x/day | [moment name] | [one line] |
| 1x/week | [moment name] | [one line] |

## Progress

- [ ] Milestone 1: [screen name]
- [ ] Milestone 2: [screen name]
- [ ] Milestone 3: [screen name]
...

## Design Milestones

### Milestone 1: [Screen Name]

**User goal**: "[What the user is trying to do — in their words]"
**Pattern**: [Apple Design DNA pattern name] (from [source app])
**Priority**: Must-have
**Frequency**: [how often this screen is used]
**Existing TCA domain**: [which reducer/feature this touches]

**Features**:
- [Feature] — [why the user needs it]
- [Feature] — [why the user needs it]
- [Feature] — [why the user needs it]

**Acceptance criteria**:
1. [Observable proof — what the screen shows/does]
2. [User test — "show to [persona], they say X"]
3. [Technical — builds, tests pass, no raw design tokens]

**Implementation prompt** (use this to start the build session):
> "[Exact prompt to build this screen, including
> user context, emotional intent, and which pattern to reference]"

---

### Milestone 2: [Screen Name]
...

## Deliberate Omissions

- [Feature] — [why it's excluded]
- [Feature] — [why it's excluded]

## Decision Log

_Updated during execution._

## Surprises & Discoveries

_Updated during execution._
```

## Rules

1. **Group by user goal, not technical category.** "See my day at a
   glance" not "Calendar Module."

2. **Size each milestone for one implementation session.**
   If a milestone needs two patterns, split it into two milestones.

3. **Build order follows frequency.** The 50x/day screen is Milestone 1.

4. **Max 8 milestones.** More than 8 means over-scoping. Merge or defer.

5. **Every feature has a "why".** Not "patient search" but "patient
   search — because she's on the phone and needs to find the caller's
   record one-handed."

6. **Include an implementation prompt.** Each milestone has a pre-written
   prompt that starts the build session. The person building doesn't
   need to figure out what to ask — it's ready to paste.

7. **Reference existing code.** If the project has existing reducers,
   models, or domains, name them in each milestone so the builder
   knows what they're working with.

8. **Acceptance criteria are testable.** Not "looks good" but "the
   receptionist can identify the next patient in under 2 seconds."
