# Standards audit checkpoint — 2026-07-19

This checkpoint freezes the primary-source semantics that must govern the next implementation phase. It distinguishes standards contracts from observed design.dev behavior and from implementation inference. No existing green test is treated as proof of external fidelity.

## Evidence hierarchy

1. W3C Recommendations and CSSWG specifications define normative behavior.
2. Current W3C Working Drafts and CSSWG Editor's Drafts are labeled by maturity.
3. Official APCA project material defines APCA terminology, implementation constraints, and licensing caveats; APCA is not treated as a W3C standard.
4. MDN and web.dev are implementation-oriented secondary sources.
5. design.dev defines requested topic and interactive-tool coverage, not standards authority.

Raw research artifacts remain outside the plugin under the operator's Codex work-notes directory:

```text
$CODEX_HOME/work-notes/css-tokenography/standards-verification-2026-07-19/.firecrawl
$CODEX_HOME/work-notes/css-tokenography/live-audit-2026-07-16/.firecrawl
```

## Verified contracts and current gaps

### WCAG contrast and APCA labeling

- WCAG 2.2 relative luminance uses the sRGB `0.04045` transfer breakpoint and the ratio `(L1 + 0.05) / (L2 + 0.05)`.
- Threshold comparisons use the unrounded ratio. A calculated `4.499:1` does not satisfy a `4.5:1` threshold.
- AA and AAA labels apply to WCAG 2.x criteria, not APCA.
- A two-color calculation reports threshold results; it does not establish page, component, or product conformance without context such as text size/weight, states, adjacent colors, graphical boundaries, and exceptions.
- WCAG 3 is a Working Draft. Its current contrast method is not settled, so no APCA result may be labeled “WCAG 3 compliant.”
- APCA reports polarity-sensitive `Lc`, not a ratio. The official implementation remains beta and carries terminology, presentation, currentness, and licensing constraints.

Current plugin gap: `scripts/design_tool.py` rounds the ratio before threshold comparison, causing false passes near boundaries. The source design.dev tool exposes APCA, while plugin coverage records do not disclose that deterministic omission.

### Selector specificity and cascade

- Selector specificity is the three-component tuple `(A, B, C)`: ID selectors; class/attribute/pseudo-class selectors; type selectors/pseudo-elements.
- Inline style is a separate cascade sorting stage, not a fourth selector-specificity component.
- Selector-list members retain separate specificity values.
- `:where()` contributes zero.
- `:is()`, `:not()`, and `:has()` contribute the maximum specificity of their selector-list arguments.
- `:nth-child(... of S)` and `:nth-last-child(... of S)` contribute the pseudo-class plus the maximum specificity in `S`.
- Origin/importance, encapsulation context, style attributes, layers, specificity, scope proximity, and order are distinct cascade stages.

Current plugin gap: the regex implementation is not a CSS parser. It miscounts pseudo-elements, attribute strings, nesting, namespaces, Unicode identifiers, top-level selector lists, and `nth-* of S`.

### Stacking contexts and containing blocks

- A stacking context is atomic within its parent; numeric `z-index` values are local to their context.
- Context creation, containing-block creation, and paint ordering are separate contracts.
- `position: fixed` and `position: sticky` create stacking contexts regardless of `z-index`.
- Non-`none` transforms and filters create stacking contexts and containing blocks for absolute and fixed descendants, subject to documented root exceptions.
- Opacity below one creates a stacking context but does not itself establish the same containing-block trap.
- Layout/paint containment, corresponding `will-change` values, flex/grid item positioning, individual transform properties, top-layer participation, and retained animations require explicit modeling.

Current plugin gap: the z-index tool only serializes a declaration and accepts invalid values. It does not accept a tree, computed-style facts, trigger metadata, containing-block facts, or paint phases, so `implemented-core` is not currently justified.

### Transform order, perspective, and compositing

- CSS transform functions are multiplied from left to right when the transformation matrix is constructed. Explanations of the apparent operation order must name the coordinate/vector convention rather than saying only “right-to-left.”
- An explicit `transform: none` differs from a non-`none` identity list because any computed value other than `none` creates transform-related stacking-context and containing-block effects.
- `perspective()` participates in the transformed element's transform list. The `perspective` property establishes perspective for transformed descendants; they are not interchangeable.
- Transforms and `will-change` do not normatively guarantee a compositor/GPU layer.
- `will-change` is a measured hint: apply with lead time, restrict its scope, remove it when no longer needed, and account for pre-created stacking/containing-block effects.

Current plugin gap: named transform fields are emitted in a hard-coded order even when callers provide a different order. The current test only exercises that hard-coded order. Perspective property/function semantics and `none` versus identity are not modeled.

### Filter and backdrop-filter

- Filter functions are order-sensitive and execute in the supplied order.
- Filter grammar, arity, units, negative restrictions, and used-value clamping must be validated.
- A non-`none` `filter` renders the element and descendants as a group, creates a stacking context and containing block, and does not change box geometry.
- `drop-shadow()` uses the input image's alpha mask; it is not semantically interchangeable with `box-shadow` and has no universal performance advantage.
- `backdrop-filter` uses a Backdrop Root image, clips to the element's border box including radius, and generally requires transparency for the result to be visible.
- Filter Effects Level 2 is an exploring Editor's Draft; its Backdrop Root definition lacks Working Group consensus and must be labeled accordingly.

Current plugin gap: opaque strings pass through with almost no grammar validation, function injection is possible, backdrop function order is hard-coded, and liquid-glass coverage omits deterministic source controls while claiming `implemented-core`.

## Coverage-gate finding

The current suite passes 21 tests and the inventory validator reports 17 guides, 33 tools, and 7 migrated source skills. Those checks establish internal inventory consistency only.

`validate_coverage.py` currently verifies that a referenced test file exists. It does not prove that:

- the CLI tool name exists;
- the named test anchor exists;
- a unique test exercises the claimed tool;
- declared deterministic inputs and outputs are covered;
- tracked fixtures are used;
- live behavior was compared for the current implementation.

The next phase must make coverage evidence executable before restoring or retaining `implemented-core` and `implemented-full` claims.

## Primary sources

- https://www.w3.org/TR/WCAG22/
- https://www.w3.org/TR/wcag-3.0/
- https://www.w3.org/TR/selectors-4/#specificity-rules
- https://www.w3.org/TR/css-cascade-6/
- https://www.w3.org/TR/CSS22/zindex.html
- https://www.w3.org/TR/css-transforms-1/
- https://drafts.csswg.org/css-transforms-2/
- https://www.w3.org/TR/css-will-change-1/
- https://www.w3.org/TR/filter-effects-1/
- https://drafts.csswg.org/filter-effects-2/
- https://www.w3.org/TR/css-contain-2/
- https://git.apcacontrast.com/documentation/minimum_compliance.html
- https://github.com/Myndex/apca-w3

## Implementation gate

Implementation may begin only from `standards-hardening-execplan.md`. Claims must be downgraded before a tool is materially rewritten, then restored only after its dedicated fixtures, failure paths, primary-source oracle, aggregate tests, plugin validation, and marketplace smoke test pass.
