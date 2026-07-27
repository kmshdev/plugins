# Router success rubric

## Outcome

- The requested CSS, typography, or performance task is completed or reviewed.
- The selected specialists cover every material topic.
- Explicit specialist invocation remains available.

## Process

- Broad prompts use `$css-tokenography`.
- The router opens and follows each selected specialist's `SKILL.md`.
- The router never selects itself, duplicates a specialist, or retries a semantic selection.

## Style

- Routed work starts with exactly one `CSS Tokenography route:` disclosure.
- The disclosure names selected skills and gives a short rationale.
- The final answer does not repeat the disclosure.

## Efficiency

- Each evaluation completes in one semantic attempt.
- One retry is permitted only for an infrastructure failure.
- Live evaluations record duration and token usage.

## Evaluation protocol

Implicit-router cases use `css-tokenography-routing/v1`. A case passes only when
all required skills are selected, every forbidden skill is absent, the
disclosure occurs exactly once, selected skills are unique, and no semantic
retry occurs. Additional plausible skills are allowed unless forbidden.
