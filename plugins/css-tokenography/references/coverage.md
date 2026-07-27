# Coverage inventory

Retrieved on 2026-07-16 with Firecrawl.

- The current design.dev guides index exposes 39 detail URLs; 17 are in this plugin's required scope.
- The current tools index exposes 33 detail URLs. A sitemap-backed map also returned 33; a direct no-sitemap crawl returned 32. The supplied screenshot's category badges total 34 and are treated as stale visual evidence.
- `guide-coverage.json` owns the one-guide-to-one-skill mapping.
- `tool-coverage.json` records all 33 tools, including inputs, outputs, ownership, deterministic boundaries, artifacts, fixture-driven validation commands, status, and structured coverage gaps.
- `source-migration.json` records the preserve, rewrite, split, or retirement destination for each substantive source-skill section.

`implemented-full` means an owner-bound clean-room CLI has fixture-driven executable evidence for the observed tool's complete non-visual contract. `implemented-core` means the same evidence boundary covers named deterministic semantics while leaving presentation out. `procedural` makes no implementation-coverage claim; its structured gap names missing behavior, the future owner CLI and tests, and observable restoration outcomes.

## Phase 2 promoted backlog

Relative to the Phase 2 baseline at `587cc12`, exactly these ten formerly
procedural rows are promoted. The status and canonical owner-bound artifact
columns are part of the aggregate inventory contract.

| Tool slug | Status | Canonical artifact |
|---|---|---|
| `clamp-generator` | `implemented-full` | `skills/css-functions/scripts/clamp_generator.py` |
| `px-to-rem-converter` | `implemented-full` | `skills/web-typography/scripts/px_to_rem_converter.py` |
| `aspect-ratio-calculator` | `implemented-full` | `skills/css-functions/scripts/aspect_ratio_calculator.py` |
| `cubic-bezier-studio` | `implemented-full` | `skills/css-transitions/scripts/cubic_bezier_studio.py` |
| `nth-child-selector` | `implemented-full` | `skills/css-selectors/scripts/nth_child_selector.py` |
| `gradient-mixer` | `implemented-core` | `skills/css-gradients/scripts/gradient_mixer.py` |
| `oklch-color-converter` | `implemented-full` | `skills/css-variables/scripts/oklch_color_converter.py` |
| `border-radius-playground` | `implemented-core` | `skills/css-functions/scripts/border_radius_playground.py` |
| `box-shadow-generator` | `implemented-core` | `skills/css-transforms/scripts/box_shadow_generator.py` |
| `flexbox-playground` | `implemented-core` | `skills/css-flexbox/scripts/flexbox_playground.py` |

The eight tools that were already non-procedural at the baseline remain
promoted with their existing canonical artifacts. The resulting 33-row
inventory contains 8 `implemented-full`, 10 `implemented-core`, and 15
`procedural` rows. None of the ten Phase 2 artifacts uses `design_tool.py`.

These promotions are backed by unique JSON fixtures and direct validation
commands that execute the declared CLI and require a JSON object. They establish
the bounded deterministic contracts named in `tool-coverage.json`; they do not
establish browser rendering, interaction, pixel parity, or whole-page standards
conformance.

## Evidence-envelope pilot

The canonical `color_contrast_checker.py` and `css_transform_playground.py` CLIs
accept an opt-in `--evidence` flag. Without that flag, their JSON and readable
outputs and exit behavior remain unchanged. With it, each CLI emits the same
deterministic report under `EvidenceEnvelope.core`; it does not run an optional
oracle. Therefore the empty observation set is classified as `unavailable`,
not as agreement, passing, or conformance evidence.
