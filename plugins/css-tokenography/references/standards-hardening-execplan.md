# CSS Tokenography Standards Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace overstated serializer-level tool coverage with standards-correct, independently tested semantic models for contrast, selectors, stacking contexts, transforms, filters, and backdrop filters.

**Architecture:** Keep each deterministic CLI with its owning skill and use dependency-free Python modules with explicit JSON schemas. Browser-dependent facts enter through explicit computed-style or oracle fixtures; the plugin will not pretend to parse and cascade arbitrary HTML/CSS. Coverage claims become executable contracts that name a unique CLI and test.

**Tech Stack:** Python 3 standard library, `unittest`, JSON fixtures, Markdown skill references, plugin-creator validation, skill-creator quick validation, and an optional preinstalled browser for oracle-only smoke tests.

## Global Constraints

- Preserve the 17 independently triggerable guide skills and the complete live design.dev tool inventory.
- Prefer W3C/CSSWG normative behavior over design.dev wording while retaining topic coverage.
- Keep runtime CLIs deterministic, network-free, dependency-free, and explicit about browser-dependent results.
- Do not copy APCA code into the MIT plugin or claim WCAG 3 compliance; record APCA as an intentional exclusion unless licensing and integration requirements are separately approved.
- Do not emit `translateZ(0)`, `will-change`, prefixed backdrop declarations, or GPU-promotion claims automatically.
- Compare thresholds using unrounded values; round only presentation fields.
- Do not implement a second browser cascade for stacking analysis. Consume explicit element/computed-style facts.
- Every CLI must provide `--help`, JSON output, actionable invalid-input errors, and non-zero failure status.
- Every non-procedural tool must name one unique executable test or fixture in `tool-coverage.json`.
- Use `plugin-creator` cachebuster/update mechanics; do not hand-edit marketplace cache metadata.

---

## Planned file structure

- Create `plugins/css-tokenography/skills/css-variables/scripts/color_contrast.py` for WCAG 2.2 calculations and explicit APCA exclusion metadata.
- Create `plugins/css-tokenography/skills/css-selectors/scripts/selector_tokens.py`, `selector_ast.py`, and `specificity_calculator.py` for balanced CSS syntax and per-selector specificity.
- Create `plugins/css-tokenography/skills/css-grid/scripts/stacking_context_model.py` for computed-fact context trees, containing blocks, and paint phases.
- Create `plugins/css-tokenography/skills/css-transforms/scripts/transform_model.py` and `transform_matrix.py` for ordered transforms, perspective modes, identity semantics, and matrices.
- Create `plugins/css-tokenography/skills/css-transforms/scripts/filter_model.py` for ordered typed filters and backdrop metadata.
- Split domain tests into `tests/test_color_contrast.py`, `test_specificity.py`, `test_stacking_contexts.py`, `test_transforms.py`, `test_filters.py`, and `test_coverage_contracts.py`.
- Keep `scripts/design_tool.py` only for unaffected generic tools; remove migrated handlers after each dedicated CLI is verified.
- Update the owning `SKILL.md` files, `tool-coverage.json`, `tool-coverage.md`, `live-comparisons.md`, `standards-divergences.md`, and `maintenance.md` in the same tasks as behavior changes.

### Task 1: Make current coverage claims fail closed

**Files:**
- Modify: `plugins/css-tokenography/references/tool-coverage.json`
- Modify: `plugins/css-tokenography/references/tool-coverage.md`
- Modify: `plugins/css-tokenography/scripts/validate_coverage.py`
- Create: `plugins/css-tokenography/tests/test_coverage_contracts.py`

**Interfaces:**
- Consumes: existing tool rows with `status`, `implementation_artifact`, and `validation_fixture`.
- Produces: tool rows whose non-procedural status resolves to a real CLI choice and unique unittest method or fixture.

- [ ] **Step 1: Add failing coverage tests**

```python
def test_non_procedural_tools_name_unique_evidence(self) -> None:
    rows = load_tool_rows()
    evidence = [row["validation_fixture"] for row in rows if row["status"] != "procedural"]
    self.assertEqual(len(evidence), len(set(evidence)))

def test_cli_artifacts_name_existing_tools(self) -> None:
    for row in implemented_tool_rows():
        result = run_artifact(row, "--help")
        self.assertEqual(result.returncode, 0, row["url"])
        if " --tool " in row["implementation_artifact"]:
            self.assertIn(tool_name(row), result.stdout)
```

- [ ] **Step 2: Run the focused tests and confirm the existing broad anchors fail**

Run: `python3 -m unittest -v tests.test_coverage_contracts`

Expected: FAIL because multiple tools share `tests/test_cli_contracts.py#ToolModelTests` and several rows do not have dedicated behavior tests.

- [ ] **Step 3: Downgrade unsupported claims before implementation**

Set the current specificity, z-index, transform, filter, backdrop-filter, liquid-glass, and APCA-related surfaces to `procedural` or `serializer-only` using an allowed status added to the validator. Each reason must state the missing semantic contract and the task that restores it.

- [ ] **Step 4: Validate the fail-closed inventory**

Run: `python3 plugins/css-tokenography/scripts/validate_coverage.py --plugin plugins/css-tokenography --format json`

Expected: exit 0 with 17 guides, 33 tools, 7 sources, unique evidence for every still-implemented tool, and explicit reasons for downgraded rows.

- [ ] **Step 5: Commit**

```bash
git add plugins/css-tokenography/references/tool-coverage.json \
  plugins/css-tokenography/references/tool-coverage.md \
  plugins/css-tokenography/scripts/validate_coverage.py \
  plugins/css-tokenography/tests/test_coverage_contracts.py
git commit -m "Make CSS tool coverage fail closed"
```

### Task 2: Correct WCAG contrast and disclose APCA scope

**Files:**
- Create: `plugins/css-tokenography/skills/css-variables/scripts/color_contrast.py`
- Create: `plugins/css-tokenography/tests/test_color_contrast.py`
- Create: `plugins/css-tokenography/tests/fixtures/contrast-threshold-fail.json`
- Modify: `plugins/css-tokenography/skills/css-variables/SKILL.md`
- Modify: `plugins/css-tokenography/references/tool-coverage.json`
- Modify: `plugins/css-tokenography/references/standards-divergences.md`
- Modify: `plugins/css-tokenography/scripts/design_tool.py`

**Interfaces:**
- Consumes: `{ "foreground": "#RRGGBB", "background": "#RRGGBB" }`.
- Produces: exact ratio, display ratio, WCAG 2.2 threshold results, calculation scope, and an explicit APCA exclusion record.

- [ ] **Step 1: Add boundary-first tests**

```python
def test_unrounded_ratio_controls_threshold(self) -> None:
    report = run_contrast("#6e7978", "#ffffff")
    self.assertAlmostEqual(report["ratio"], 4.4975956604, places=9)
    self.assertEqual(report["display_ratio"], 4.50)
    self.assertFalse(report["thresholds"]["aa_normal_text"])

def test_result_is_not_a_conformance_claim(self) -> None:
    report = run_contrast("#000000", "#ffffff")
    self.assertEqual(report["method"], "wcag2-relative-luminance")
    self.assertEqual(report["standard"], "WCAG 2.2")
    self.assertEqual(report["scope"], "color-pair-thresholds-only")
    self.assertEqual(report["apca"]["status"], "not-implemented")
```

- [ ] **Step 2: Confirm the rounding regression fails with the current CLI**

Run: `python3 -m unittest -v tests.test_color_contrast`

Expected: FAIL because the current implementation compares a ratio rounded to two decimals.

- [ ] **Step 3: Implement full-precision WCAG 2.2 output**

```python
def contrast_report(foreground: str, background: str) -> dict[str, object]:
    ratio = contrast_ratio(parse_hex(foreground), parse_hex(background))
    return {
        "method": "wcag2-relative-luminance",
        "standard": "WCAG 2.2",
        "ratio": ratio,
        "display_ratio": round(ratio, 2),
        "scope": "color-pair-thresholds-only",
        "thresholds": {
            "aa_normal_text": ratio >= 4.5,
            "aa_large_text": ratio >= 3.0,
            "aaa_normal_text": ratio >= 7.0,
            "aaa_large_text": ratio >= 4.5,
            "non_text": ratio >= 3.0,
        },
        "apca": {
            "status": "not-implemented",
            "reason": "APCA is beta, polarity-sensitive, and not the adopted WCAG 3 contrast method.",
        },
    }
```

- [ ] **Step 4: Run valid, invalid, symmetry, and threshold tests**

Run: `python3 -m unittest -v tests.test_color_contrast`

Expected: PASS for black/white, symmetry, invalid hex, the near-threshold false-pass regression, and non-text thresholds.

- [ ] **Step 5: Restore only WCAG coverage**

Update the color-contrast row to name WCAG 2.2 outputs and the dedicated test. Record APCA under `unsupported_behavior` with the official project and WCAG 3 links.

- [ ] **Step 6: Commit**

```bash
git add plugins/css-tokenography/skills/css-variables \
  plugins/css-tokenography/tests/test_color_contrast.py \
  plugins/css-tokenography/tests/fixtures/contrast-threshold-fail.json \
  plugins/css-tokenography/references/tool-coverage.json \
  plugins/css-tokenography/references/standards-divergences.md \
  plugins/css-tokenography/scripts/design_tool.py
git commit -m "Correct WCAG contrast threshold semantics"
```

### Task 3: Replace regex specificity with a bounded CSS selector parser

**Files:**
- Create: `plugins/css-tokenography/skills/css-selectors/scripts/selector_tokens.py`
- Create: `plugins/css-tokenography/skills/css-selectors/scripts/selector_ast.py`
- Create: `plugins/css-tokenography/skills/css-selectors/scripts/specificity_calculator.py`
- Create: `plugins/css-tokenography/tests/test_specificity.py`
- Modify: `plugins/css-tokenography/skills/css-selectors/SKILL.md`
- Modify: `plugins/css-tokenography/skills/css-cascade-layers/SKILL.md`
- Modify: `plugins/css-tokenography/references/tool-coverage.json`
- Modify: `plugins/css-tokenography/scripts/design_tool.py`

**Interfaces:**
- Consumes: `{ "selector": "<selector-list>" }`.
- Produces: one result per selector-list member, each with `(A,B,C)`, source span, and standards notes; inline-style metadata remains outside specificity.

- [ ] **Step 1: Add the normative regression table**

```python
CASES = {
    "a::before": [[0, 0, 2]],
    "[href=\"#x\"]": [[0, 1, 0]],
    ":is(:not(#x), .a)": [[1, 0, 0]],
    ":where(:is(:not(#x)))": [[0, 0, 0]],
    ":nth-child(odd of .a, #b)": [[1, 1, 0]],
    ".a, #b": [[0, 1, 0], [1, 0, 0]],
    "svg|a": [[0, 0, 1]],
    "é": [[0, 0, 1]],
}
```

- [ ] **Step 2: Confirm current failures**

Run: `python3 -m unittest -v tests.test_specificity`

Expected: FAIL for pseudo-elements, attribute strings, nested functional pseudo-classes, `nth-* of S`, selector lists, namespaces, and Unicode identifiers.

- [ ] **Step 3: Implement balanced tokenization and AST nodes**

```python
@dataclass(frozen=True)
class Specificity:
    a: int = 0
    b: int = 0
    c: int = 0

@dataclass(frozen=True)
class SelectorResult:
    selector: str
    specificity: Specificity
    start: int
    end: int

def calculate_selector_list(source: str) -> list[SelectorResult]:
    tokens = tokenize_selector(source)
    selectors = parse_selector_list(tokens)
    return [fold_specificity(selector) for selector in selectors]
```

Tokenizer tests must cover escapes, Unicode, strings/comments, balanced brackets/functions, namespaces, commas, and invalid/unbalanced syntax. The specificity fold must special-case `:where`, `:is`, `:not`, `:has`, `:nth-child`, and `:nth-last-child`.

- [ ] **Step 4: Keep cascade stages separate**

Update `css-cascade-layers/SKILL.md` to trace origin/importance, encapsulation, style attributes, layers, specificity, scope proximity, and source order. State the normal/important reversals for encapsulation and layers.

- [ ] **Step 5: Run selector tests and CLI smoke tests**

Run: `python3 -m unittest -v tests.test_specificity`

Expected: PASS for all normative cases and non-zero exits for malformed syntax.

- [ ] **Step 6: Commit**

```bash
git add plugins/css-tokenography/skills/css-selectors \
  plugins/css-tokenography/skills/css-cascade-layers/SKILL.md \
  plugins/css-tokenography/tests/test_specificity.py \
  plugins/css-tokenography/references/tool-coverage.json \
  plugins/css-tokenography/scripts/design_tool.py
git commit -m "Implement Selectors Level 4 specificity"
```

### Task 4: Implement an explicit stacking-context and containing-block model

**Files:**
- Create: `plugins/css-tokenography/skills/css-grid/scripts/stacking_context_model.py`
- Create: `plugins/css-tokenography/tests/test_stacking_contexts.py`
- Create: `plugins/css-tokenography/tests/fixtures/stacking-nested-contexts.json`
- Create: `plugins/css-tokenography/tests/fixtures/stacking-containing-blocks.json`
- Modify: `plugins/css-tokenography/skills/css-grid/SKILL.md`
- Modify: `plugins/css-tokenography/skills/css-transforms/SKILL.md`
- Modify: `plugins/css-tokenography/references/tool-coverage.json`
- Modify: `plugins/css-tokenography/scripts/design_tool.py`

**Interfaces:**
- Consumes: a DOM-like element tree with parent IDs, document order, computed-style subset, and explicit layout/top-layer/animation facts.
- Produces: stacking-context tree, trigger reasons, local paint phases, containing-block roots, and warnings for facts that require browser collection.

- [ ] **Step 1: Define fixture input explicitly**

```json
{
  "elements": [
    {"id": "root", "parent": null, "order": 0, "is_root": true, "style": {}},
    {"id": "panel", "parent": "root", "order": 1, "style": {"position": "relative", "z_index": 1}},
    {"id": "modal", "parent": "panel", "order": 2, "style": {"position": "fixed", "z_index": 9999}},
    {"id": "overlay", "parent": "root", "order": 3, "style": {"position": "fixed", "z_index": 2}}
  ]
}
```

- [ ] **Step 2: Add trigger, paint-phase, and containing-block tests**

```python
def test_nested_9999_cannot_escape_parent_context(self) -> None:
    report = analyze_fixture("stacking-nested-contexts.json")
    self.assertEqual(report["contexts"]["modal"]["parent_context"], "panel")
    self.assertLess(report["contexts"]["panel"]["z_index"], report["contexts"]["overlay"]["z_index"])

def test_opacity_context_does_not_trap_fixed_descendant(self) -> None:
    report = analyze_inline(opacity_tree())
    self.assertTrue(report["elements"]["surface"]["creates_context"])
    self.assertFalse(report["elements"]["surface"]["creates_fixed_containing_block"])
```

The matrix must cover root, positioned/non-auto z-index, fixed/sticky, flex/grid items, opacity, blending, transform/scale/rotate/translate, filters, perspective, clip/mask, isolation, containment, container type, `will-change`, top layer, and retained animations.

- [ ] **Step 3: Implement separate registries**

```python
STACKING_TRIGGERS: tuple[Trigger, ...] = (...)
ABSOLUTE_CB_TRIGGERS: tuple[Trigger, ...] = (...)
FIXED_CB_TRIGGERS: tuple[Trigger, ...] = (...)

def analyze_tree(elements: list[ElementFacts]) -> Analysis:
    validate_tree(elements)
    contexts = build_context_tree(elements, STACKING_TRIGGERS)
    containing_blocks = resolve_containing_blocks(elements, ABSOLUTE_CB_TRIGGERS, FIXED_CB_TRIGGERS)
    return assign_paint_phases(contexts, containing_blocks)
```

Do not accept raw HTML/CSS. A browser workflow may export computed facts into this schema without becoming part of the deterministic analyzer.

- [ ] **Step 4: Validate z-index grammar**

Accept `auto`, integers, and global keywords only. Reject `9999px`, fractional numbers, and arbitrary identifiers with actionable errors.

- [ ] **Step 5: Run model tests**

Run: `python3 -m unittest -v tests.test_stacking_contexts`

Expected: PASS for negative/auto/zero/positive phases, equal-z document order, nested atomic contexts, transformed containing blocks, and opacity/isolation counterexamples.

- [ ] **Step 6: Restore z-index coverage and commit**

```bash
git add plugins/css-tokenography/skills/css-grid \
  plugins/css-tokenography/skills/css-transforms/SKILL.md \
  plugins/css-tokenography/tests/test_stacking_contexts.py \
  plugins/css-tokenography/tests/fixtures/stacking-*.json \
  plugins/css-tokenography/references/tool-coverage.json \
  plugins/css-tokenography/scripts/design_tool.py
git commit -m "Model CSS stacking contexts and containing blocks"
```

### Task 5: Implement ordered transform lists and perspective modes

**Files:**
- Create: `plugins/css-tokenography/skills/css-transforms/scripts/transform_matrix.py`
- Create: `plugins/css-tokenography/skills/css-transforms/scripts/transform_model.py`
- Create: `plugins/css-tokenography/tests/test_transforms.py`
- Modify: `plugins/css-tokenography/skills/css-transforms/SKILL.md`
- Modify: `plugins/css-tokenography/references/tool-coverage.json`
- Modify: `plugins/css-tokenography/references/live-comparisons.md`
- Modify: `plugins/css-tokenography/scripts/design_tool.py`

**Interfaces:**
- Consumes: explicit `transform.kind` (`none` or `list`), ordered functions, optional transform origin, and separate ancestor perspective.
- Produces: CSS, ordered functions, computed 4×4 matrix, stacking/containing-block facts, and browser-dependent compositing metadata.

- [ ] **Step 1: Add order and perspective regression tests**

```python
def test_reversed_lists_serialize_and_compose_differently(self) -> None:
    first = run_transform([fn("rotate", "20deg"), fn("translateX", "10px")])
    second = run_transform([fn("translateX", "10px"), fn("rotate", "20deg")])
    self.assertNotEqual(first["css"], second["css"])
    self.assertNotEqual(first["matrix"], second["matrix"])

def test_none_differs_from_identity_list(self) -> None:
    none = run_transform_kind("none")
    identity = run_transform([fn("translateX", "0px"), fn("rotate", "0deg"), fn("scale", 1)])
    self.assertFalse(none["creates_stacking_context"])
    self.assertTrue(identity["creates_stacking_context"])
```

- [ ] **Step 2: Define the explicit JSON contract**

```json
{
  "ancestor": {"perspective": "800px", "perspective_origin": "center"},
  "transform": {
    "kind": "list",
    "functions": [
      {"name": "perspective", "args": ["600px"]},
      {"name": "rotateY", "args": ["25deg"]},
      {"name": "translateX", "args": ["10px"]}
    ]
  },
  "transform_origin": "center"
}
```

- [ ] **Step 3: Implement strict function validation and matrix composition**

Validate arity and units for translate, scale, rotate, skew, matrix, matrix3d, and perspective functions. Multiply matrices according to CSS Transforms and preserve the source list verbatim in output.

Return:

```python
{
    "matrix_order": "multiply-functions-left-to-right",
    "compositor_layer": "browser-dependent",
    "creates_stacking_context": transform_kind != "none",
    "creates_absolute_containing_block": transform_kind != "none",
    "creates_fixed_containing_block": transform_kind != "none",
}
```

- [ ] **Step 4: Verify with independent oracles**

Use CSS Transforms specification examples for dependency-free matrix fixtures. When a browser is already available, compare representative matrices through `DOMMatrix`; do not install browser tooling implicitly.

- [ ] **Step 5: Run tests and restore coverage**

Run: `python3 -m unittest -v tests.test_transforms`

Expected: PASS for reversed order, `none` versus identity, perspective property versus function, invalid units, 2D/3D matrices, and non-guaranteed compositing metadata.

- [ ] **Step 6: Commit**

```bash
git add plugins/css-tokenography/skills/css-transforms \
  plugins/css-tokenography/tests/test_transforms.py \
  plugins/css-tokenography/references/tool-coverage.json \
  plugins/css-tokenography/references/live-comparisons.md \
  plugins/css-tokenography/scripts/design_tool.py
git commit -m "Implement ordered CSS transform semantics"
```

### Task 6: Parse filter and backdrop-filter semantics

**Files:**
- Create: `plugins/css-tokenography/skills/css-transforms/scripts/filter_model.py`
- Create: `plugins/css-tokenography/tests/test_filters.py`
- Create: `plugins/css-tokenography/tests/fixtures/filter-ordered.json`
- Create: `plugins/css-tokenography/tests/fixtures/backdrop-transparent.json`
- Modify: `plugins/css-tokenography/skills/css-transforms/SKILL.md`
- Modify: `plugins/css-tokenography/references/tool-coverage.json`
- Modify: `plugins/css-tokenography/references/live-comparisons.md`
- Modify: `plugins/css-tokenography/scripts/design_tool.py`

**Interfaces:**
- Consumes: `property` (`filter` or `backdrop-filter`), `none` or ordered typed functions, plus optional backdrop transparency/border/radius facts.
- Produces: validated CSS, ordered operations, grouping/context/containing-block metadata, color space, visibility status, and specification maturity.

- [ ] **Step 1: Add grammar and ordering tests**

```python
def test_order_is_preserved(self) -> None:
    report = run_filter([
        {"name": "contrast", "value": "150%"},
        {"name": "blur", "value": "4px"},
    ])
    self.assertEqual(report["css"], "filter: contrast(150%) blur(4px);")

def test_invalid_values_fail(self) -> None:
    for value in ("-1px", "1bananas", "1px) invert(100%"):
        result = run_filter_cli({"functions": [{"name": "blur", "value": value}]})
        self.assertNotEqual(result.returncode, 0)
```

- [ ] **Step 2: Implement typed functions**

Support `blur`, `brightness`, `contrast`, `drop-shadow`, `grayscale`, `hue-rotate`, `invert`, `opacity`, `saturate`, and `sepia`. Validate function-specific arity, unit categories, negative restrictions, and specified clamping behavior. Permit local-fragment `url(#id)` only when it can remain network-free; reject external URLs with an explicit unsupported reason.

- [ ] **Step 3: Add backdrop metadata**

```python
{
    "specification": "Filter Effects Level 2 Editor's Draft",
    "maturity": "exploring-no-wg-consensus-on-backdrop-root",
    "creates_stacking_context": True,
    "creates_absolute_containing_block": True,
    "creates_fixed_containing_block": True,
    "color_space": "sRGB",
    "visibility": "visible" if background_alpha < 1 else "not-observable-from-declared-background",
}
```

- [ ] **Step 4: Resolve source-tool scope honestly**

Implement the observed backdrop background, border, radius, and function controls or keep the row downgraded with enumerated missing controls. Keep liquid glass procedural/serializer-only unless gradients, shadows, layers, content color, fallbacks, and dedicated fixtures are implemented.

- [ ] **Step 5: Run tests and commit**

Run: `python3 -m unittest -v tests.test_filters`

Expected: PASS for every canned function, ordering, invalid units/ranges, injection rejection, backdrop transparency, drop-shadow grammar, and draft-maturity metadata.

```bash
git add plugins/css-tokenography/skills/css-transforms \
  plugins/css-tokenography/tests/test_filters.py \
  plugins/css-tokenography/tests/fixtures/filter-ordered.json \
  plugins/css-tokenography/tests/fixtures/backdrop-transparent.json \
  plugins/css-tokenography/references/tool-coverage.json \
  plugins/css-tokenography/references/live-comparisons.md \
  plugins/css-tokenography/scripts/design_tool.py
git commit -m "Validate CSS filter and backdrop semantics"
```

### Task 7: Harden packaging, validation, and marketplace release

**Files:**
- Modify: `plugins/css-tokenography/.codex-plugin/plugin.json`
- Modify: `.agents/plugins/marketplace.json` only through plugin-creator-supported marketplace flow when a marketplace field must change
- Modify: `README.md`
- Modify: `plugins/css-tokenography/references/maintenance.md`
- Modify: `plugins/css-tokenography/scripts/validate_coverage.py`
- Modify: `plugins/css-tokenography/tests/test_coverage_contracts.py`
- Create: `.github/workflows/css-tokenography.yml`

**Interfaces:**
- Consumes: completed tool models, dedicated tests, skill validators, plugin manifest, and marketplace entry.
- Produces: reproducible aggregate gate, consistent provenance/category metadata, cachebuster version, and install smoke evidence.

- [ ] **Step 1: Correct public identity and catalog metadata**

Set author/developer identity to `kmshdev`, align the manifest and marketplace category, and add only manifest fields accepted by the current plugin-creator validator. Confirm repository/homepage/license support from `plugin-json-spec.md` before adding fields.

- [ ] **Step 2: Run every dedicated test and fixture smoke path**

```bash
python3 -m unittest discover -s plugins/css-tokenography/tests -v
python3 plugins/css-tokenography/scripts/validate_coverage.py \
  --plugin plugins/css-tokenography --format json
```

Expected: all tests pass; the coverage report has 17 guides, 33 tools, 7 sources, zero errors, unique evidence, valid statuses, and no unused tracked fixtures.

- [ ] **Step 3: Run all 17 skill validators**

```bash
for skill in plugins/css-tokenography/skills/*; do
  python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
```

Expected: all skill directories pass in a development environment that provides the validator's PyYAML dependency. If PyYAML is unavailable, record the exact blocker and do not claim publish readiness.

- [ ] **Step 4: Run plugin validation**

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/css-tokenography
```

Expected: `Plugin validation passed`.

- [ ] **Step 5: Update the cachebuster and install from the intended marketplace**

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py \
  plugins/css-tokenography
codex plugin add css-tokenography@kmshdev
```

Expected: Codex reports a successful add/update from the `kmshdev` marketplace. Start a new thread before testing skill discovery.

- [ ] **Step 6: Smoke-test installed discovery and representative CLIs**

Verify one prompt/CLI each for WCAG contrast, specificity, stacking contexts, transforms, filters, grid areas, subgrid, performance budgets, and typography. Record lab/browser-dependent gaps separately.

- [ ] **Step 7: Add CI and commit**

The workflow must run the standard-library test suite and coverage validator without network collection. Skill/plugin validation may use a pinned PyYAML development dependency in CI without adding a runtime dependency to the plugin.

```bash
git add .github/workflows/css-tokenography.yml README.md \
  .agents/plugins/marketplace.json \
  plugins/css-tokenography/.codex-plugin/plugin.json \
  plugins/css-tokenography/references/maintenance.md \
  plugins/css-tokenography/scripts/validate_coverage.py \
  plugins/css-tokenography/tests/test_coverage_contracts.py
git commit -m "Add CSS tokenography release gates"
git push -u origin "$(git branch --show-current)"
```

## Self-review

- Spec coverage: WCAG/APCA labeling, selector specificity, cascade stages, stacking contexts, containing blocks, transform order/perspective/compositing, filter/backdrop semantics, tool evidence, packaging, and release validation each have an owned task.
- Placeholder scan: every task contains concrete files, interfaces, commands, expected outcomes, and failure behavior.
- Interface consistency: dedicated owner scripts replace the affected shared handlers; JSON contracts are named once and consumed by their corresponding tests and coverage rows.
- Scope boundary: APCA implementation, arbitrary HTML/CSS cascade parsing, browser installation, and faithful liquid-glass raster appearance are excluded unless separately authorized and evidenced.
