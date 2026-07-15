# Development documentation

Write development documentation for a reader performing a real task in the current
repository. Establish prerequisites, exact commands, expected results, failure modes,
and recovery steps from executable evidence.

Required sections:

- `## Context`: purpose, supported environment, and boundaries.
- `## Workflow`: ordered commands and observable checkpoints.
- `## Verification`: the smallest probes that prove success.
- `## Failure modes`: symptoms, likely causes, and safe recovery.

Do not turn a command catalog into a guide. Explain state transitions and the evidence
that tells a reader whether each transition completed.
