import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
RADIUS = ROOT / "skills" / "css-functions" / "scripts" / "border_radius_playground.py"
SHADOW = ROOT / "skills" / "css-transforms" / "scripts" / "box_shadow_generator.py"
SHADOW_MODEL = ROOT / "skills" / "css-transforms" / "scripts" / "shadow_model.py"


def invoke(
    script: Path,
    data: object | None = None,
    *args: str,
    raw_stdin: str | None = None,
) -> subprocess.CompletedProcess[str]:
    stdin = raw_stdin if raw_stdin is not None else None if data is None else json.dumps(data)
    return subprocess.run(
        [sys.executable, str(script), *args],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


def run_fixture(script: Path, fixture: str) -> dict[str, object]:
    result = invoke(
        script,
        None,
        "--input",
        str(FIXTURES / fixture),
        "--format",
        "json",
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class BorderRadiusPlaygroundTests(unittest.TestCase):
    def test_elliptical_radius_serializes_slash_syntax(self) -> None:
        report = run_fixture(RADIUS, "border-radius-elliptical.json")

        self.assertEqual(report["css"], "border-radius: 1rem 2rem / 50% 25%;")
        self.assertEqual(report["value"], "1rem 2rem / 50% 25%")
        self.assertEqual(report["horizontal"], ["1rem", "2rem"])
        self.assertEqual(report["vertical"], ["50%", "25%"])

    def test_radius_accepts_one_to_four_horizontal_and_vertical_values(self) -> None:
        cases = (
            ({"horizontal": ["1px"]}, "border-radius: 1px;"),
            ({"horizontal": ["1px", "2px"]}, "border-radius: 1px 2px;"),
            ({"horizontal": ["1px", "2px", "3px"]}, "border-radius: 1px 2px 3px;"),
            (
                {"horizontal": ["1px", "2px", "3px", "4px"]},
                "border-radius: 1px 2px 3px 4px;",
            ),
            (
                {
                    "horizontal": ["1px"],
                    "vertical": ["10%", "20%", "30%", "40%"],
                },
                "border-radius: 1px / 10% 20% 30% 40%;",
            ),
        )

        for data, expected_css in cases:
            with self.subTest(data=data):
                result = invoke(RADIUS, data, "--format", "json")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["css"], expected_css)

    def test_radius_rejects_invalid_arity_values_and_injection(self) -> None:
        cases = (
            ({"horizontal": []}, "horizontal must contain one to four radii"),
            (
                {"horizontal": ["1px", "2px", "3px", "4px", "5px"]},
                "horizontal must contain one to four radii",
            ),
            ({"horizontal": ["1px"], "vertical": []}, "vertical must contain one to four radii"),
            ({"horizontal": "1px"}, "horizontal must contain one to four radii"),
            ({"horizontal": ["-1px"]}, "horizontal[0] must not be negative"),
            ({"horizontal": ["1.px"]}, "horizontal[0] must be a supported CSS length or percentage"),
            ({"horizontal": ["10"]}, "horizontal[0] must be a supported CSS length or percentage"),
            (
                {"horizontal": ["1px; color: red"]},
                "horizontal[0] must be a supported CSS length or percentage",
            ),
            ({"horizontal": ["1px"], "unexpected": True}, "supports only horizontal and vertical"),
        )

        for data, message in cases:
            with self.subTest(data=data):
                result = invoke(RADIUS, data, "--format", "json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_radius_supports_file_stdin_css_human_evidence_and_help(self) -> None:
        data = {"horizontal": ["1rem", "2rem"], "vertical": ["50%", "25%"]}
        first = invoke(RADIUS, data, "--format", "json")
        second = invoke(RADIUS, data, "--format", "json")
        css = invoke(RADIUS, data, "--format", "css")
        human = invoke(RADIUS, data)
        evidence = invoke(RADIUS, data, "--format", "json", "--evidence")
        help_result = invoke(RADIUS, None, "--help")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(css.stdout.strip(), "border-radius: 1rem 2rem / 50% 25%;")
        self.assertIn("elliptical", human.stdout.lower())
        envelope = json.loads(evidence.stdout)
        self.assertEqual(envelope["core"], json.loads(first.stdout))
        self.assertEqual(envelope["classification"], "unavailable")
        self.assertEqual(envelope["observations"], [])
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("one to four", help_result.stdout)
        self.assertEqual(
            run_fixture(RADIUS, "border-radius-elliptical.json"),
            json.loads(first.stdout),
        )

    def test_radius_reports_malformed_json_and_invalid_utf8_without_tracebacks(self) -> None:
        malformed = invoke(RADIUS, None, "--format", "json", raw_stdin="{")
        self.assertNotEqual(malformed.returncode, 0)
        self.assertIn("Unable to read JSON input", malformed.stderr)
        self.assertNotIn("Traceback", malformed.stderr)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "radius.json"
            path.write_bytes(b"\xff")
            invalid_utf8 = invoke(RADIUS, None, "--input", str(path), "--format", "json")

        self.assertNotEqual(invalid_utf8.returncode, 0)
        self.assertIn("input is not valid UTF-8", invalid_utf8.stderr)
        self.assertNotIn("Traceback", invalid_utf8.stderr)


class BoxShadowGeneratorTests(unittest.TestCase):
    def test_shadow_preserves_layer_order(self) -> None:
        report = run_fixture(SHADOW, "box-shadow-multilayer.json")

        self.assertEqual([layer["id"] for layer in report["layers"]], ["ambient", "key"])
        self.assertEqual(
            report["css"],
            "box-shadow: 0 1px 2px 0 #0003, inset -2px 3px 4px -1px rebeccapurple;",
        )
        self.assertEqual(report["layer_order"], "preserved-front-to-back")

    def test_shadow_models_offset_blur_spread_inset_and_color_semantics(self) -> None:
        report = run_fixture(SHADOW, "box-shadow-multilayer.json")
        ambient, key = report["layers"]

        self.assertEqual(
            ambient,
            {
                "id": "ambient",
                "inset": False,
                "offset_x": "0",
                "offset_y": "1px",
                "blur": "2px",
                "spread": "0",
                "color": "#0003",
                "value": "0 1px 2px 0 #0003",
            },
        )
        self.assertEqual(key["value"], "inset -2px 3px 4px -1px rebeccapurple")
        self.assertTrue(key["inset"])
        self.assertEqual(report["semantics"]["negative_offsets"], "allowed")
        self.assertEqual(report["semantics"]["negative_spread"], "allowed")
        self.assertEqual(report["semantics"]["negative_blur"], "invalid")
        self.assertEqual(report["semantics"]["inset"], "required explicit boolean")
        self.assertEqual(report["semantics"]["omitted_color"], "not modeled; color is explicit")

    def test_shadow_rejects_negative_blur_and_invalid_typed_layers(self) -> None:
        valid = {
            "id": "valid",
            "inset": False,
            "offset_x": "0",
            "offset_y": "0",
            "blur": "0",
            "spread": "0",
            "color": "currentColor",
        }
        cases = (
            ({"layers": []}, "layers must contain at least one shadow layer"),
            ({"layers": ["0 1px black"]}, "layers[0] must be an object"),
            ({"layers": [{**valid, "blur": "-1px"}]}, "layers[0].blur must not be negative"),
            ({"layers": [{**valid, "offset_x": "10%"}]}, "layers[0].offset_x must be a supported CSS length"),
            ({"layers": [{**valid, "spread": "1.px"}]}, "layers[0].spread must be a supported CSS length"),
            ({"layers": [{**valid, "inset": "true"}]}, "layers[0].inset must be boolean"),
            ({"layers": [{**valid, "color": "not-a-color"}]}, "must be a valid CSS hex or named color"),
            (
                {"layers": [{**valid, "color": "rgb(0 0 0 / 50%)"}]},
                "functional colors are unsupported; use a CSS hex or named color",
            ),
            ({"layers": [{**valid, "color": "red; background: blue"}]}, "contains unsupported CSS syntax"),
            ({"layers": [{**valid, "id": "bad,shadow"}]}, "layers[0].id must be a simple identifier"),
            ({"layers": [{**valid, "extra": 1}]}, "supports only id, inset, offset_x, offset_y, blur, spread, and color"),
            ({"layers": [valid], "extra": 1}, "Input supports only layers"),
        )

        for data, message in cases:
            with self.subTest(message=message):
                result = invoke(SHADOW, data, "--format", "json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_shadow_requires_explicit_fields_and_unique_ids(self) -> None:
        complete = {
            "id": "one",
            "inset": False,
            "offset_x": "0",
            "offset_y": "0",
            "blur": "0",
            "spread": "0",
            "color": "black",
        }
        cases = (
            ({"layers": [{key: value for key, value in complete.items() if key != "inset"}]}, "layers[0].inset is required"),
            ({"layers": [{key: value for key, value in complete.items() if key != "blur"}]}, "layers[0].blur is required"),
            ({"layers": [{key: value for key, value in complete.items() if key != "color"}]}, "layers[0].color is required"),
            ({"layers": [complete, complete]}, "layer ids must be unique"),
        )

        for data, message in cases:
            with self.subTest(message=message):
                result = invoke(SHADOW, data, "--format", "json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_shadow_model_exposes_frozen_typed_ordered_records(self) -> None:
        spec = importlib.util.spec_from_file_location("shadow_model", SHADOW_MODEL)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        shadow = module.BoxShadow.from_data(
            {
                "layers": [
                    {
                        "id": "first",
                        "inset": False,
                        "offset_x": "-1px",
                        "offset_y": "2px",
                        "blur": "3px",
                        "spread": "-4px",
                        "color": "#0008",
                    },
                    {
                        "id": "second",
                        "inset": True,
                        "offset_x": "0",
                        "offset_y": "0",
                        "blur": "0",
                        "spread": "0",
                        "color": "white",
                    },
                ]
            }
        )

        self.assertIsInstance(shadow.layers, tuple)
        self.assertEqual([layer.id for layer in shadow.layers], ["first", "second"])
        with self.assertRaisesRegex(Exception, "cannot assign to field"):
            shadow.layers[0].blur = "9px"

    def test_shadow_supports_file_stdin_css_human_evidence_and_help(self) -> None:
        data = json.loads((FIXTURES / "box-shadow-multilayer.json").read_text(encoding="utf-8"))
        first = invoke(SHADOW, data, "--format", "json")
        second = invoke(SHADOW, data, "--format", "json")
        css = invoke(SHADOW, data, "--format", "css")
        human = invoke(SHADOW, data)
        evidence = invoke(SHADOW, data, "--format", "json", "--evidence")
        help_result = invoke(SHADOW, None, "--help")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(
            css.stdout.strip(),
            "box-shadow: 0 1px 2px 0 #0003, inset -2px 3px 4px -1px rebeccapurple;",
        )
        self.assertIn("2 shadow layers", human.stdout)
        envelope = json.loads(evidence.stdout)
        self.assertEqual(envelope["core"], json.loads(first.stdout))
        self.assertEqual(envelope["classification"], "unavailable")
        self.assertEqual(envelope["observations"], [])
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("ordered", help_result.stdout)
        self.assertEqual(
            run_fixture(SHADOW, "box-shadow-multilayer.json"),
            json.loads(first.stdout),
        )

    def test_shadow_reports_malformed_json_without_a_traceback(self) -> None:
        result = invoke(SHADOW, None, "--format", "json", raw_stdin="{")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unable to read JSON input", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
