import json
import re
import unittest
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


def slug(row: dict[str, object]) -> str:
    return str(row["url"]).rstrip("/").rsplit("/", 1)[-1]


class PhaseTwoInventoryTests(unittest.TestCase):
    def test_phase_two_promotes_exact_backlog(self) -> None:
        coverage_text = (ROOT / "references" / "coverage.md").read_text(
            encoding="utf-8"
        )
        section = PHASE_TWO_SECTION.search(coverage_text)
        self.assertIsNotNone(section)
        documented = {
            match.group("slug"): (match.group("status"), match.group("artifact"))
            for match in PHASE_TWO_ROW.finditer(section.group("body"))
        }
        self.assertEqual(documented, EXPECTED_PHASE_TWO_PROMOTIONS)

        rows = json.loads(
            (ROOT / "references" / "tool-coverage.json").read_text(encoding="utf-8")
        )
        promoted = {
            row_slug: (str(row["status"]), str(row["implementation_artifact"]))
            for row in rows
            if (row_slug := slug(row)) in documented and row["status"] != "procedural"
        }
        self.assertEqual(promoted, EXPECTED_PHASE_TWO_PROMOTIONS)
        self.assertTrue(
            all("design_tool.py" not in artifact for _, artifact in promoted.values())
        )


if __name__ == "__main__":
    unittest.main()
