# Developer-tool coverage

Canonical inventory retrieved from the live design.dev tools index on 2026-07-16. Detailed inputs, outputs, fixtures, and exclusion evidence are in `tool-coverage.json`.

| Tool | Category | Owner | Classification | Status | Artifact |
|---|---|---|---|---|---|
| Color Contrast Checker | Colors | css-variables | deterministic | implemented-core | `design_tool.py --tool color-contrast-checker` |
| CSS Gradient Generator | Colors | css-gradients | deterministic | implemented-core | `design_tool.py --tool gradient-mixer` |
| OKLCH Color Converter | Colors | css-variables | deterministic | implemented-full | `design_tool.py --tool oklch-color-converter` |
| Liquid Glass CSS Generator | Effects | css-transforms | deterministic | implemented-core | `design_tool.py --tool liquid-glass-generator` |
| CSS Box Shadow Generator | Effects | css-transforms | deterministic | implemented-core | `design_tool.py --tool box-shadow-generator` |
| CSS Hover Effects Generator | Effects | css-transitions | deterministic | implemented-core | `design_tool.py --tool hover-effect-generator` |
| CSS Clip-Path Generator | Effects | css-transforms | deterministic | implemented-core | `design_tool.py --tool clip-path-shapes` |
| Neumorphism CSS Generator | Effects | css-transforms | deterministic | implemented-core | `design_tool.py --tool neumorphism` |
| CSS Filter Effects | Effects | css-transforms | deterministic | implemented-core | `design_tool.py --tool css-filter-effects` |
| CSS Backdrop Filter Generator | Effects | css-transforms | deterministic | implemented-core | `design_tool.py --tool backdrop-filter-playground` |
| CSS Border Radius Generator | Effects | css-functions | deterministic | implemented-core | `design_tool.py --tool border-radius-playground` |
| CSS Tooltip Generator | Effects | css-transitions | deterministic | implemented-core | `design_tool.py --tool css-tooltips` |
| Custom CSS Cursor Generator | Effects | css-functions | deterministic | implemented-core | `design_tool.py --tool custom-cursor-generator` |
| CSS Background Pattern Generator | Effects | css-gradients | deterministic | implemented-core | `design_tool.py --tool css-background-generator` |
| CSS Transform Playground | Effects | css-transforms | deterministic | implemented-core | `design_tool.py --tool css-transform-playground` |
| Cubic Bezier Generator | Effects | css-transitions | deterministic | implemented-core | `design_tool.py --tool cubic-bezier-studio` |
| CSS Loaders | Effects | css-animations | deterministic | implemented-core | `design_tool.py --tool css-loaders` |
| CSS Grid Area Mapper | Layout | css-grid | deterministic | implemented-full | `grid_area_mapper.py` |
| CSS Subgrid Visualizer | Layout | css-grid | deterministic | implemented-full | `subgrid_visualizer.py` |
| CSS Flexbox Playground | Layout | css-flexbox | deterministic | implemented-core | `design_tool.py --tool flexbox-playground` |
| Z-Index Visualizer | Layout | css-grid | deterministic | implemented-core | `design_tool.py --tool z-index-visualizer` |
| CSS Clamp Generator | Typography | css-functions | deterministic | implemented-full | `design_tool.py --tool clamp-generator` |
| CSS Text Shadow Generator | Typography | web-typography | deterministic | implemented-core | `design_tool.py --tool text-shadow-generator` |
| Metallic Text Effect Generator | Typography | css-gradients | deterministic | implemented-core | `design_tool.py --tool metallic-effect-generator` |
| PX to REM Converter | Typography | web-typography | deterministic | implemented-full | `design_tool.py --tool px-to-rem-converter` |
| Code Screenshot Generator | Utilities | web-performance-optimization | browser-dependent | procedural | performance workflow |
| ASCII Code Generator | Utilities | css-functions | asset-dependent | procedural | functions workflow |
| CSS Specificity Calculator | Utilities | css-selectors | deterministic | implemented-core | `design_tool.py --tool specificity-calculator` |
| nth-child Selector Generator | Utilities | css-selectors | deterministic | implemented-core | `design_tool.py --tool nth-child-selector` |
| Browser Feature Detection | Utilities | css-media-queries | browser-dependent | procedural | media-query workflow |
| Image Optimizer | Utilities | web-performance-optimization | codec-dependent | procedural | performance workflow |
| Favicon Generator | Utilities | web-performance-optimization | codec-dependent | procedural | performance workflow |
| Aspect Ratio Calculator | Utilities | css-functions | deterministic | implemented-full | `design_tool.py --tool aspect-ratio-calculator` |

`implemented-core` deliberately excludes browser presentation and preset libraries. `procedural` entries name a real browser, raster, codec, or missing-asset boundary rather than silently omitting the tool.
