# Planning documentation

Write plans as restartable execution contracts. Separate current facts, accepted
decisions, working assumptions, and unresolved owner choices.

Required sections:

- `## Outcome`: one measurable end state.
- `## Scope`: included work, exclusions, invariants, and mutation boundary.
- `## Execution plan`: dependency-ordered vertical slices with concrete artifacts.
- `## Acceptance evidence`: requirement-to-command or requirement-to-probe mapping.

Name owners only when evidence identifies them. Include rollback or stop conditions
for irreversible steps. Do not call implementation complete because the plan exists.
