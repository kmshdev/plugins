---
name: css-tokenography
description: Route and coordinate CSS, layout, responsive design, design-token, typography, animation, and web-performance work across the CSS Tokenography specialist skills. Use implicitly for broad, ambiguous, or multi-topic styling requests; use a named specialist explicitly when the user already chose one.
---

# CSS Tokenography

Coordinate the plugin's specialist skills and carry the user's task through implementation or review.

## Routing workflow

1. Read [routing-map.md](references/routing-map.md).
2. Inspect the prompt and repository evidence before selecting specialists.
3. Select every specialist whose trigger contract materially applies. There is no fixed fan-out cap.
4. Use specialist names exactly as listed in the routing map. Do not invent display labels, plugin-qualified aliases, or topic-group names.
5. Never select `$css-tokenography`, and never select the same specialist twice.
6. When no useful topic signal exists, select `$css-grid`, `$css-variables`, and `$web-typography`.
7. Begin routed work with exactly one concise line:

   `CSS Tokenography route: $skill-name[, $skill-name] — short rationale.`

8. Explicitly open each selected sibling `../<skill-name>/SKILL.md` and follow its workflow. Specialist guidance is authoritative when it conflicts with general guidance here.
9. Coordinate overlapping work so each specialist owns its defined surface. Do not repeat the routing disclosure in the final answer.

For routing evaluations that request the machine contract, report protocol
`css-tokenography-routing/v1`, only the canonical sibling specialist names in
first-use order, the single disclosure line, and whether a semantic retry
occurred. Never include the router itself in `selected_skills`. A semantic miss
is a failure; do not retry by changing the selection.

## Validation

Run the static bundle validator after changing skills or routing:

```bash
python3 scripts/validate_router.py --format human
```

Preview live evaluation commands without changing marketplace state:

```bash
python3 scripts/evaluate_routes.py
```

Use `--apply` only when temporary marketplace installation is authorized. Read
[success-rubric.md](references/success-rubric.md) before interpreting results.
