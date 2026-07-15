# Library documentation

Write library, API, CLI, SDK, and integration documentation from the current exported
surface and official upstream contract. Prefer executable examples and typed boundaries.

Required sections:

- `## Purpose`: supported use cases and explicit non-goals.
- `## Installation`: package, feature flags, versions, and prerequisites.
- `## API`: stable entry points, inputs, outputs, errors, and lifecycle.
- `## Examples`: minimal runnable examples with expected behavior.
- `## Compatibility`: supported versions, platforms, and breaking-change boundaries.

Do not document private helpers as public API. Parse external data at the boundary and
identify which behavior belongs to the library versus the caller or provider.
