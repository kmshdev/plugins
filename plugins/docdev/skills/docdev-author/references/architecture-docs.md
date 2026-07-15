# Architecture documentation

Document the system that exists before describing a target. Trace callers, data,
persistence, transport, configuration, failure paths, and operational ownership.

Required sections:

- `## System boundary`: owned responsibilities, external systems, and exclusions.
- `## Decisions`: binding decisions with alternatives and consequences.
- `## Runtime model`: components, data flow, lifecycle, and failure behavior.
- `## Verification`: source, test, runtime, and observability evidence.

Mark diagrams and prose as current, target, or proposed. Preserve proven behavior in
redesigns unless an accepted replacement and equivalent verification exist.
