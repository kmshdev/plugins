# Developer-tool coverage

Canonical inventory retrieved from the live design.dev tools index on 2026-07-16. Detailed inputs, outputs, evidence, and downgrade tasks are in `tool-coverage.json`.

Coverage fails closed: a non-procedural tool must use a standalone Python CLI under its owner's `scripts/` directory and declare an exact command that runs that artifact against a JSON-object fixture. The validator substitutes `{plugin}` and `{fixture}`, executes the command, requires exit 0, and requires JSON-object stdout. Shared serializers and unittest anchors are not coverage evidence.

| Tool | Category | Owner | Classification | Status | Artifact |
|---|---|---|---|---|---|
| Color Contrast Checker | Colors | css-variables | deterministic | procedural | APCA contract task required |
| CSS Gradient Generator | Colors | css-gradients | deterministic | procedural | gradient contract task required |
| OKLCH Color Converter | Colors | css-variables | deterministic | procedural | owner CLI and fixture task required |
| Liquid Glass CSS Generator | Effects | css-transforms | deterministic | procedural | liquid-glass contract task required |
| CSS Box Shadow Generator | Effects | css-transforms | deterministic | procedural | shadow contract task required |
| CSS Hover Effects Generator | Effects | css-transitions | deterministic | procedural | hover-state contract task required |
| CSS Clip-Path Generator | Effects | css-transforms | deterministic | procedural | shape contract task required |
| Neumorphism CSS Generator | Effects | css-transforms | deterministic | procedural | output and contrast task required |
| CSS Filter Effects | Effects | css-transforms | deterministic | procedural | filter grammar task required |
| CSS Backdrop Filter Generator | Effects | css-transforms | deterministic | procedural | backdrop semantics task required |
| CSS Border Radius Generator | Effects | css-functions | deterministic | procedural | radius grammar task required |
| CSS Tooltip Generator | Effects | css-transitions | deterministic | procedural | accessible interaction task required |
| Custom CSS Cursor Generator | Effects | css-functions | deterministic | procedural | cursor grammar task required |
| CSS Background Pattern Generator | Effects | css-gradients | deterministic | procedural | pattern contract task required |
| CSS Transform Playground | Effects | css-transforms | deterministic | procedural | owner CLI and transform semantics task required |
| Cubic Bezier Generator | Effects | css-transitions | deterministic | procedural | owner CLI and fixture task required |
| CSS Loaders | Effects | css-animations | deterministic | procedural | loader model task required |
| CSS Grid Area Mapper | Layout | css-grid | deterministic | implemented-full | `grid_area_mapper.py` |
| CSS Subgrid Visualizer | Layout | css-grid | deterministic | implemented-full | `subgrid_visualizer.py` |
| CSS Flexbox Playground | Layout | css-flexbox | deterministic | procedural | flex control task required |
| Z-Index Visualizer | Layout | css-grid | deterministic | procedural | stacking-context task required |
| CSS Clamp Generator | Typography | css-functions | deterministic | procedural | owner CLI and fixture task required |
| CSS Text Shadow Generator | Typography | web-typography | deterministic | procedural | shadow and legibility task required |
| Metallic Text Effect Generator | Typography | css-gradients | deterministic | procedural | effect composition task required |
| PX to REM Converter | Typography | web-typography | deterministic | procedural | conversion contract task required |
| Code Screenshot Generator | Utilities | web-performance-optimization | browser-dependent | procedural | pinned renderer task required |
| ASCII Code Generator | Utilities | css-functions | asset-dependent | procedural | source glyph task required |
| CSS Specificity Calculator | Utilities | css-selectors | deterministic | procedural | Selectors Level 4 parser task required |
| nth-child Selector Generator | Utilities | css-selectors | deterministic | procedural | selector contract task required |
| Browser Feature Detection | Utilities | css-media-queries | browser-dependent | procedural | target-browser probe task required |
| Image Optimizer | Utilities | web-performance-optimization | codec-dependent | procedural | pinned codec task required |
| Favicon Generator | Utilities | web-performance-optimization | codec-dependent | procedural | icon rendering task required |
| Aspect Ratio Calculator | Utilities | css-functions | deterministic | procedural | ratio contract task required |

`implemented-full` and `implemented-core` are executable-evidence claims. `serializer-only`, if used later, must satisfy the same executable contract and also name its limitations. `procedural` and `serializer-only` entries carry a structured `coverage_gap` with missing behaviors, an owner-bound restoration artifact, restoration tests, and observable acceptance outcomes. The validator checks schema and path ownership; it does not infer semantic quality from prose.
