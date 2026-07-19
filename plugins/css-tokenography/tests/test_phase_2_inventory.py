import json
import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_TWO_SECTION = re.compile(
    r"^## Phase 2 promoted backlog\n(?P<body>.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
PHASE_TWO_ROW = re.compile(
    r"^\| `(?P<slug>[^`]+)` \| `(?P<status>[^`]+)` \| `(?P<artifact>[^`]+)` \|$",
    re.MULTILINE,
)
EXPECTED_PHASE_TWO_PROMOTIONS = {
    "clamp-generator": (
        "implemented-full",
        "skills/css-functions/scripts/clamp_generator.py",
    ),
    "px-to-rem-converter": (
        "implemented-full",
        "skills/web-typography/scripts/px_to_rem_converter.py",
    ),
    "aspect-ratio-calculator": (
        "implemented-full",
        "skills/css-functions/scripts/aspect_ratio_calculator.py",
    ),
    "cubic-bezier-studio": (
        "implemented-full",
        "skills/css-transitions/scripts/cubic_bezier_studio.py",
    ),
    "nth-child-selector": (
        "implemented-full",
        "skills/css-selectors/scripts/nth_child_selector.py",
    ),
    "gradient-mixer": (
        "implemented-core",
        "skills/css-gradients/scripts/gradient_mixer.py",
    ),
    "oklch-color-converter": (
        "implemented-full",
        "skills/css-variables/scripts/oklch_color_converter.py",
    ),
    "border-radius-playground": (
        "implemented-core",
        "skills/css-functions/scripts/border_radius_playground.py",
    ),
    "box-shadow-generator": (
        "implemented-core",
        "skills/css-transforms/scripts/box_shadow_generator.py",
    ),
    "flexbox-playground": (
        "implemented-core",
        "skills/css-flexbox/scripts/flexbox_playground.py",
    ),
}
EXPECTED_BASELINE_PROMOTIONS = {
    "color-contrast-checker": (
        "implemented-core",
        "skills/css-variables/scripts/color_contrast_checker.py",
    ),
    "css-filter-effects": (
        "implemented-core",
        "skills/css-transforms/scripts/css_filter_effects.py",
    ),
    "backdrop-filter-playground": (
        "implemented-core",
        "skills/css-transforms/scripts/backdrop_filter_playground.py",
    ),
    "css-transform-playground": (
        "implemented-core",
        "skills/css-transforms/scripts/css_transform_playground.py",
    ),
    "grid-area-mapper": (
        "implemented-full",
        "skills/css-grid/scripts/grid_area_mapper.py",
    ),
    "subgrid-visualizer": (
        "implemented-full",
        "skills/css-grid/scripts/subgrid_visualizer.py",
    ),
    "z-index-visualizer": (
        "implemented-core",
        "skills/css-grid/scripts/z_index_visualizer.py",
    ),
    "specificity-calculator": (
        "implemented-core",
        "skills/css-selectors/scripts/specificity_calculator.py",
    ),
}
EXPECTED_STATUS_COUNTS = Counter(
    {"implemented-full": 8, "implemented-core": 10, "procedural": 15}
)


def slug(row: dict[str, object]) -> str:
    return str(row["url"]).rstrip("/").rsplit("/", 1)[-1]


def expected_tuples(
    promotions: dict[str, tuple[str, str]],
) -> Counter[tuple[str, str, str]]:
    return Counter(
        (tool_slug, status, artifact)
        for tool_slug, (status, artifact) in promotions.items()
    )


def inventory_tuple(row: dict[str, object]) -> tuple[str, str, str]:
    return slug(row), str(row["status"]), str(row["implementation_artifact"])


def assert_phase_two_inventory(
    test_case: unittest.TestCase,
    coverage_text: str,
    rows: list[dict[str, object]],
) -> None:
    section = PHASE_TWO_SECTION.search(coverage_text)
    test_case.assertIsNotNone(section)
    documented = [
        (match.group("slug"), match.group("status"), match.group("artifact"))
        for match in PHASE_TWO_ROW.finditer(section.group("body"))
    ]
    expected_phase_two = expected_tuples(EXPECTED_PHASE_TWO_PROMOTIONS)
    expected_baseline = expected_tuples(EXPECTED_BASELINE_PROMOTIONS)
    test_case.assertEqual(
        len(documented),
        10,
        "Phase 2 documentation must contain exactly ten raw rows",
    )
    test_case.assertEqual(
        Counter(documented),
        expected_phase_two,
        "Phase 2 documentation must contain the exact promoted tuples",
    )

    test_case.assertEqual(len(rows), 33, "inventory must contain exactly 33 raw rows")
    row_slugs = [slug(row) for row in rows]
    test_case.assertEqual(
        len(row_slugs),
        len(set(row_slugs)),
        "inventory tool slugs must be unique",
    )

    phase_two_rows = [
        inventory_tuple(row)
        for row in rows
        if slug(row) in EXPECTED_PHASE_TWO_PROMOTIONS
    ]
    baseline_rows = [
        inventory_tuple(row)
        for row in rows
        if slug(row) in EXPECTED_BASELINE_PROMOTIONS
    ]
    test_case.assertEqual(len(phase_two_rows), 10, "Phase 2 must contain ten rows")
    test_case.assertEqual(
        Counter(phase_two_rows),
        expected_phase_two,
        "Phase 2 inventory must contain the exact promoted tuples",
    )
    test_case.assertEqual(len(baseline_rows), 8, "baseline must contain eight rows")
    test_case.assertEqual(
        Counter(baseline_rows),
        expected_baseline,
        "baseline promoted tuples must retain their exact status and artifact",
    )
    test_case.assertEqual(
        Counter(str(row["status"]) for row in rows),
        EXPECTED_STATUS_COUNTS,
        "aggregate status totals must remain exact",
    )

    promoted = Counter(
        inventory_tuple(row) for row in rows if row["status"] != "procedural"
    )
    test_case.assertEqual(promoted, expected_phase_two + expected_baseline)
    test_case.assertTrue(
        all("design_tool.py" not in artifact for _, _, artifact in phase_two_rows)
    )


class PhaseTwoInventoryTests(unittest.TestCase):
    def load_inputs(self) -> tuple[str, list[dict[str, object]]]:
        coverage_text = (ROOT / "references" / "coverage.md").read_text(
            encoding="utf-8"
        )
        rows = json.loads(
            (ROOT / "references" / "tool-coverage.json").read_text(encoding="utf-8")
        )
        return coverage_text, rows

    def test_phase_two_promotes_exact_backlog(self) -> None:
        coverage_text, rows = self.load_inputs()

        assert_phase_two_inventory(self, coverage_text, rows)

    def test_duplicate_documented_row_cannot_be_overwritten(self) -> None:
        coverage_text, rows = self.load_inputs()
        duplicate = (
            "| `clamp-generator` | `implemented-core` | "
            "`skills/css-functions/scripts/design_tool.py` |\n"
        )
        mutated = coverage_text.replace(
            "| `clamp-generator` |",
            duplicate + "| `clamp-generator` |",
            1,
        )

        with self.assertRaisesRegex(AssertionError, "exactly ten raw rows"):
            assert_phase_two_inventory(self, mutated, rows)

    def test_duplicate_inventory_row_cannot_be_overwritten(self) -> None:
        coverage_text, rows = self.load_inputs()
        duplicate = dict(next(row for row in rows if slug(row) == "clamp-generator"))
        duplicate["status"] = "implemented-core"
        duplicate["implementation_artifact"] = (
            "skills/css-functions/scripts/design_tool.py"
        )

        with self.assertRaisesRegex(AssertionError, "exactly 33 raw rows"):
            assert_phase_two_inventory(self, coverage_text, [duplicate, *rows])

    def test_baseline_promoted_status_drift_is_rejected(self) -> None:
        coverage_text, rows = self.load_inputs()
        mutated = [dict(row) for row in rows]
        contrast = next(row for row in mutated if slug(row) == "color-contrast-checker")
        contrast["status"] = "implemented-full"

        with self.assertRaisesRegex(AssertionError, "baseline promoted tuples"):
            assert_phase_two_inventory(self, coverage_text, mutated)


if __name__ == "__main__":
    unittest.main()
