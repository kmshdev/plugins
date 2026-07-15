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
