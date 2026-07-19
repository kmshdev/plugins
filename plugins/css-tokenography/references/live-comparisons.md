# Live tool comparisons

Observed with Firecrawl scrape plus one interactive browser fallback per required tool on 2026-07-16.

## Grid Area Mapper

The live **Sidebar Layout** preset changed the editor to two columns and three rows with:

```text
header header
sidebar main
sidebar main
```

It generated a grid container with repeated `1fr` tracks, a `1rem` gap, `grid-template-areas`, and one `.area { grid-area: area; }` rule per named area. `grid_area_mapper.py` reproduces those deterministic semantics, preserves first-occurrence area order, and additionally rejects invalid CSS identifiers, malformed dimensions, disconnected areas, and non-rectangular areas. JSON output and explicit validation are deliberate CLI extensions.

## Subgrid Visualizer

The live **Nested Subgrid** preset used parent tracks `1fr 2fr 1fr`, one `1fr` row, a `16px` gap, and three items. The middle item occupied columns `2 / 3`, rows `1 / 2`, and enabled subgrid on both axes. `subgrid_visualizer.py` preserves explicit parent track lists, line spans, gap inheritance, both subgrid axes, nested items, and structured output.

The live page also emitted an outdated comment claiming Chrome/Edge subgrid support was still in development. The plugin intentionally omits that frozen support table and directs agents to current platform data. It does not copy the page's generic fallback because a faithful fallback depends on the component's actual track and content contract.

These comparisons establish semantic parity for the dependency-free models; they do not claim pixel parity with the live drag-and-click editors.

## CSS transform playground

The typed model preserves the transform-function order supplied by the caller and composes the corresponding 4x4 matrices in CSS list order. It keeps ancestor `perspective` separate from `perspective()` in the transform list and preserves the semantic distinction between `transform: none` and an identity-valued transform list.

The output does not claim pixel parity, transformed-box geometry, browser hit testing, GPU acceleration, or compositor-layer promotion. Those require a concrete element, its containing layout, and runtime browser evidence.

## Filter and backdrop-filter controls

The filter model implements ordered controls for blur, brightness, contrast, drop shadow, grayscale, hue rotation, invert, opacity, saturate, sepia, and local-fragment filter references. The backdrop model additionally serializes the observed background, border, radius, and transparency facts and reports when an opaque declared background makes the backdrop effect unobservable from those facts.

This is serializer and semantic metadata parity, not browser visual fidelity. Backdrop-root behavior remains an unsettled Filter Effects Level 2 draft area. Liquid glass remains procedural because a faithful model still lacks gradients, shadows, layers, content-color handling, fallbacks, and dedicated reference fixtures.

## Phase 2 comparison envelope

The Phase 2 aggregate review did not run a new live browser or pixel comparison.
The retrieved design.dev inventory identifies the requested tool surfaces; the
ten Phase 2 promotions are instead supported by owner-bound CLI fixtures,
focused contract tests, and coverage validation. `implemented-full` means full
coverage of the observed non-visual contract recorded in the inventory, not
reproduction of the live editor UI.

- Clamp, PX/REM, and aspect ratio evidence covers typed numeric validation,
  stable formulas, exact integral reduction, and serialization. It does not
  observe a page's computed root font size or prove browser layout dimensions.
- nth-child evidence covers the CSS An+B microsyntax and safe selector
  generation; it does not query a live DOM. Cubic-bezier evidence covers finite
  control points and the CSS x-coordinate validity boundary; it does not sample
  an animation or compare a rendered timing curve.
- Gradient evidence covers a bounded typed grammar, source-ordered stops, and
  serialization. Lightning CSS was not installed for the recorded real oracle
  probe, so that observation is `unavailable`; a controlled fake executable
  tests adapter wiring only and is not an external agreement result. OKLCH
  evidence covers numeric conversion from six/eight-digit sRGB hex, not
  gamut-mapped pixels, rendered interpolation, contrast, APCA, or WCAG
  conformance.
- Border-radius and box-shadow evidence covers bounded grammar, slash shorthand,
  explicit typed layers, and declared layer order. It does not reproduce corner
  geometry, shadow blur kernels, compositing, or pixels.
- Flexbox evidence covers validated container controls, logical axes, DOM source
  order, and order-modified source order. Without writing mode, direction,
  dimensions, intrinsic sizes, and flex item sizing inputs, it does not predict
  physical directions, wrapping, free-space distribution, or browser-computed
  sizes.
