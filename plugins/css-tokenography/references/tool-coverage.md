# Developer-tool coverage

Canonical inventory retrieved from the live design.dev tools index on 2026-07-16. Detailed inputs, outputs, evidence, and downgrade tasks are in `tool-coverage.json`.

Coverage fails closed: a non-procedural tool must use a single-link, non-symlink Python CLI under its owner's `scripts/` directory whose filename is the normalized tool slug (`-` becomes `_`), whose content differs from every shared `design_tool.py`, and whose parsed source does not import or delegate to that shared wrapper. It must declare an exact command that runs the canonical artifact against a JSON-object fixture. The validator substitutes `{plugin}` and `{fixture}`, executes the command, requires exit 0, and requires JSON-object stdout. These identity gates establish shared-wrapper isolation, not arbitrary semantic quality.

| Tool | Category | Owner | Classification | Status | Artifact |
|---|---|---|---|---|---|
| Color Contrast Checker | Colors | css-variables | deterministic | implemented-core | `color_contrast_checker.py` (WCAG 2.2 color-pair thresholds; APCA explicitly excluded) |
| CSS Gradient Generator | Colors | css-gradients | deterministic | implemented-core | `gradient_mixer.py` (typed geometry and ordered stops; advanced stop/interpolation grammar disclosed) |
| OKLCH Color Converter | Colors | css-variables | deterministic | implemented-full | `oklch_color_converter.py` (six/eight-digit sRGB; unclamped binary64 channels; no contrast/APCA claim) |
| Liquid Glass CSS Generator | Effects | css-transforms | deterministic | procedural | liquid-glass contract task required |
| CSS Box Shadow Generator | Effects | css-transforms | deterministic | implemented-core | `box_shadow_generator.py` (typed ordered layers; explicit signed offsets/spread, nonnegative blur, bounded colors) |
| CSS Hover Effects Generator | Effects | css-transitions | deterministic | procedural | hover-state contract task required |
| CSS Clip-Path Generator | Effects | css-transforms | deterministic | procedural | shape contract task required |
| Neumorphism CSS Generator | Effects | css-transforms | deterministic | procedural | output and contrast task required |
| CSS Filter Effects | Effects | css-transforms | deterministic | procedural | filter grammar task required |
| CSS Backdrop Filter Generator | Effects | css-transforms | deterministic | procedural | backdrop semantics task required |
| CSS Border Radius Generator | Effects | css-functions | deterministic | implemented-core | `border_radius_playground.py` (one-to-four nonnegative horizontal radii; optional slash and vertical radii) |
| CSS Tooltip Generator | Effects | css-transitions | deterministic | procedural | accessible interaction task required |
| Custom CSS Cursor Generator | Effects | css-functions | deterministic | procedural | cursor grammar task required |
| CSS Background Pattern Generator | Effects | css-gradients | deterministic | procedural | pattern contract task required |
| CSS Transform Playground | Effects | css-transforms | deterministic | procedural | owner CLI and transform semantics task required |
| Cubic Bezier Generator | Effects | css-transitions | deterministic | implemented-full | `cubic_bezier_studio.py` (finite points; x constrained to `[0,1]`; y overshoot supported) |
| CSS Loaders | Effects | css-animations | deterministic | procedural | loader model task required |
| CSS Grid Area Mapper | Layout | css-grid | deterministic | implemented-full | `grid_area_mapper.py` |
| CSS Subgrid Visualizer | Layout | css-grid | deterministic | implemented-full | `subgrid_visualizer.py` |
| CSS Flexbox Playground | Layout | css-flexbox | deterministic | implemented-core | `flexbox_playground.py` (bounded container enums, logical axes, source/order-modified item order; no browser sizing prediction) |
| Z-Index Visualizer | Layout | css-grid | deterministic | procedural | stacking-context task required |
| CSS Clamp Generator | Typography | css-functions | deterministic | implemented-full | `clamp_generator.py` (finite endpoints, fluid slope/intercept, CSS) |
| CSS Text Shadow Generator | Typography | web-typography | deterministic | procedural | shadow and legibility task required |
| Metallic Text Effect Generator | Typography | css-gradients | deterministic | procedural | effect composition task required |
| PX to REM Converter | Typography | web-typography | deterministic | implemented-full | `px_to_rem_converter.py` (finite conversion, explicit positive root) |
| Code Screenshot Generator | Utilities | web-performance-optimization | browser-dependent | procedural | pinned renderer task required |
| ASCII Code Generator | Utilities | css-functions | asset-dependent | procedural | source glyph task required |
| CSS Specificity Calculator | Utilities | css-selectors | deterministic | implemented-core | `specificity_calculator.py` (per-member Selectors Level 4 tuples, spans, and notes) |
| nth-child Selector Generator | Utilities | css-selectors | deterministic | implemented-full | `nth_child_selector.py` (token-boundary-aware An+B normalization and safe selector generation) |
| Browser Feature Detection | Utilities | css-media-queries | browser-dependent | procedural | target-browser probe task required |
| Image Optimizer | Utilities | web-performance-optimization | codec-dependent | procedural | pinned codec task required |
| Favicon Generator | Utilities | web-performance-optimization | codec-dependent | procedural | icon rendering task required |
| Aspect Ratio Calculator | Utilities | css-functions | deterministic | implemented-full | `aspect_ratio_calculator.py` (exact integral reduction, normalized decimals) |

`implemented-full` and `implemented-core` are executable-evidence claims. `serializer-only`, if used later, must satisfy the same executable contract and also name its limitations. `procedural` and `serializer-only` entries carry a structured `coverage_gap` with missing behaviors, an owner-bound restoration artifact, restoration tests, and observable acceptance outcomes. The validator checks schema and path ownership; it does not infer semantic quality from prose.
