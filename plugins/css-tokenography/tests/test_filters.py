import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "css-transforms" / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"
FILTER_CLI = SCRIPTS / "css_filter_effects.py"
BACKDROP_CLI = SCRIPTS / "backdrop_filter_playground.py"
sys.path.insert(0, str(SCRIPTS))


def run_model(functions, property_name="filter", **extra):
    from filter_model import build_filter_report

    return build_filter_report({"property": property_name, "kind": "list", "functions": functions, **extra})


def run_cli(payload, backdrop=False):
    return subprocess.run(
        [sys.executable, str(BACKDROP_CLI if backdrop else FILTER_CLI), "--format", "json"],
        input=json.dumps(payload), text=True, capture_output=True, check=False,
    )


class FilterTests(unittest.TestCase):
    def test_order_is_preserved(self):
        report = run_model([{"name": "contrast", "value": "150%"}, {"name": "blur", "value": "4px"}])
        self.assertEqual(report["css"], "filter: contrast(150%) blur(4px);")
        self.assertEqual([item["name"] for item in report["ordered_operations"]], ["contrast", "blur"])

    def test_every_canned_function_has_typed_validation(self):
        functions = [
            {"name": "blur", "value": "2px"},
            {"name": "brightness", "value": 1.2},
            {"name": "contrast", "value": "120%"},
            {"name": "drop-shadow", "value": "2px 3px 4px rgba(0,0,0,0.4)"},
            {"name": "grayscale", "value": "25%"},
            {"name": "hue-rotate", "value": "0.25turn"},
            {"name": "invert", "value": 0.2},
            {"name": "opacity", "value": "80%"},
            {"name": "saturate", "value": 1.4},
            {"name": "sepia", "value": "10%"},
            {"name": "url", "value": "url(#local-filter)"},
        ]
        report = run_model(functions)
        self.assertEqual(report["ordered_operations"], functions)
        self.assertIn("drop-shadow(2px 3px 4px rgba(0,0,0,0.4))", report["css"])

    def test_invalid_values_ranges_arity_and_injection_fail(self):
        invalid = [
            {"name": "blur", "value": "-1px"},
            {"name": "blur", "value": "1bananas"},
            {"name": "blur", "value": "1px) invert(100%"},
            {"name": "brightness", "value": -0.1},
            {"name": "grayscale", "value": "-1%"},
            {"name": "hue-rotate", "value": "20px"},
            {"name": "drop-shadow", "value": "1px 2px -3px black"},
            {"name": "drop-shadow", "value": "1px black"},
            {"name": "url", "value": "url(https://example.com/filter.svg#x)"},
            {"name": "url", "value": "url(/filter.svg#x)"},
            {"name": "unknown", "value": "1"},
        ]
        for function in invalid:
            with self.subTest(function=function):
                result = run_cli({"property": "filter", "kind": "list", "functions": [function]})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("filter-effects", result.stderr)

    def test_bounded_amounts_report_clamped_effective_values(self):
        report = run_model([{"name": "grayscale", "value": "250%"}, {"name": "opacity", "value": 2}])
        self.assertEqual(report["semantics"][0]["effective_amount"], 1.0)
        self.assertEqual(report["semantics"][1]["effective_amount"], 1.0)
        self.assertIn("grayscale(250%)", report["css"])

    def test_none_has_no_grouping_or_containing_block_effect(self):
        from filter_model import build_filter_report

        report = build_filter_report({"property": "filter", "kind": "none"})
        self.assertEqual(report["css"], "filter: none;")
        self.assertFalse(report["creates_stacking_context"])
        self.assertFalse(report["creates_fixed_containing_block"])

    def test_backdrop_metadata_and_surface_controls_are_honest(self):
        result = subprocess.run(
            [sys.executable, str(BACKDROP_CLI), "--input", str(FIXTURES / "backdrop-transparent.json"), "--format", "json"],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["specification"], "Filter Effects Level 2 Editor's Draft")
        self.assertEqual(report["maturity"], "exploring-no-wg-consensus-on-backdrop-root")
        self.assertEqual(report["color_space"], "sRGB")
        self.assertEqual(report["visibility"], "visible")
        self.assertTrue(report["creates_stacking_context"])
        self.assertTrue(report["creates_absolute_containing_block"])
        self.assertTrue(report["creates_fixed_containing_block"])
        self.assertIn("background: rgba(255,255,255,0.35);", report["css"])
        self.assertIn("border-radius: 16px;", report["css"])

    def test_opaque_or_missing_backdrop_facts_do_not_claim_visibility(self):
        opaque = run_model([{"name": "blur", "value": "4px"}], "backdrop-filter", surface={"background_alpha": 1})
        missing = run_model([{"name": "blur", "value": "4px"}], "backdrop-filter")
        self.assertEqual(opaque["visibility"], "not-observable-from-declared-background")
        self.assertEqual(missing["visibility"], "browser-dependent-background-facts-missing")

    def test_backdrop_cli_rejects_wrong_property(self):
        result = run_cli({"property": "filter", "kind": "list", "functions": [{"name": "blur", "value": "2px"}]}, backdrop=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("property", result.stderr)


if __name__ == "__main__":
    unittest.main()
