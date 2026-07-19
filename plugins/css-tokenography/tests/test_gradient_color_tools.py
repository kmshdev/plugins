import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
GRADIENT = ROOT / "skills" / "css-gradients" / "scripts" / "gradient_mixer.py"
GRADIENT_MODEL = ROOT / "skills" / "css-gradients" / "scripts" / "gradient_model.py"
OKLCH = ROOT / "skills" / "css-variables" / "scripts" / "oklch_color_converter.py"
ORACLES = ROOT / "scripts" / "run_oracles.py"
LIGHTNINGCSS_ADAPTER = ROOT / "scripts" / "adapters" / "lightningcss_adapter.py"


def invoke(
    script: Path,
    data: dict[str, object] | None = None,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        input=None if data is None else json.dumps(data),
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


class GradientModelTests(unittest.TestCase):
    def test_gradient_preserves_equal_position_stop_order(self) -> None:
        report = run_fixture(GRADIENT, "gradient-linear.json")

        self.assertEqual(
            [stop["color"] for stop in report["stops"]],
            ["#000000", "#ffffff"],
        )
        self.assertEqual(
            report["value"],
            "linear-gradient(90deg, #000000 50%, #ffffff 50%)",
        )
        self.assertEqual(
            report["css"],
            "background-image: linear-gradient(90deg, #000000 50%, #ffffff 50%);",
        )
        self.assertEqual(report["interpolation"]["specification_default"], "Oklab")
        self.assertFalse(report["interpolation"]["serialized_explicitly"])

    def test_conic_gradient_uses_angular_stops_and_typed_geometry(self) -> None:
        report = run_fixture(GRADIENT, "gradient-conic.json")

        self.assertEqual(report["kind"], "conic")
        self.assertEqual(report["geometry"], {"from": "45deg", "position": "center"})
        self.assertEqual(
            report["value"],
            "conic-gradient(from 45deg at center, #ff0000 0deg, #0000ff 1turn)",
        )

    def test_conic_gradient_accepts_percentage_stops(self) -> None:
        result = invoke(
            GRADIENT,
            {
                "kind": "conic",
                "geometry": {},
                "stops": [
                    {"color": "#000", "position": "0%"},
                    {"color": "#fff", "position": "100%"},
                ],
            },
            "--format",
            "json",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout)["value"],
            "conic-gradient(#000 0%, #fff 100%)",
        )

    def test_radial_gradient_validates_shape_size_and_position(self) -> None:
        report = json.loads(
            invoke(
                GRADIENT,
                {
                    "kind": "radial",
                    "geometry": {
                        "shape": "circle",
                        "size": "closest-side",
                        "position": "left top",
                    },
                    "stops": [
                        {"color": "red"},
                        {"color": "transparent", "position": "100%"},
                    ],
                },
                "--format",
                "json",
            ).stdout
        )

        self.assertEqual(
            report["value"],
            "radial-gradient(circle closest-side at left top, red, transparent 100%)",
        )

    def test_gradient_rejects_kind_specific_geometry_mismatches(self) -> None:
        cases = (
            (
                {"kind": "linear", "geometry": {"shape": "circle"}},
                "linear geometry supports only direction",
            ),
            (
                {"kind": "radial", "geometry": {"from": "45deg"}},
                "radial geometry supports only shape, size, and position",
            ),
            (
                {"kind": "conic", "geometry": {"direction": "to right"}},
                "conic geometry supports only from and position",
            ),
        )
        stops = [{"color": "#000"}, {"color": "#fff"}]

        for partial, message in cases:
            with self.subTest(kind=partial["kind"]):
                result = invoke(GRADIENT, {**partial, "stops": stops}, "--format", "json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_gradient_rejects_css_injection_as_data(self) -> None:
        cases = (
            (
                {
                    "kind": "linear",
                    "geometry": {"direction": "90deg); color: red"},
                    "stops": [{"color": "#000"}, {"color": "#fff"}],
                },
                "geometry.direction",
            ),
            (
                {
                    "kind": "linear",
                    "geometry": {},
                    "stops": [
                        {"color": "red, url(https://example.invalid/x)"},
                        {"color": "blue"},
                    ],
                },
                "stops[0].color",
            ),
            (
                {
                    "kind": "linear",
                    "geometry": {},
                    "stops": [
                        {"color": "red", "position": "0%; color: blue"},
                        {"color": "blue"},
                    ],
                },
                "stops[0].position",
            ),
        )

        for data, message in cases:
            with self.subTest(message=message):
                result = invoke(GRADIENT, data, "--format", "json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_gradient_rejects_unvalidated_functional_colors(self) -> None:
        for color in (
            "rgb(,,,,)",
            "rgb(255 0 0)",
            "rgb(255, 0, 0)",
            "oklch(0.5 0.1 30)",
            "color(display-p3 1 0 0)",
        ):
            with self.subTest(color=color):
                result = invoke(
                    GRADIENT,
                    {
                        "kind": "linear",
                        "geometry": {},
                        "stops": [{"color": color}, {"color": "#ffffff"}],
                    },
                    "--format",
                    "json",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "functional colors are unsupported; use a CSS hex or named color",
                    result.stderr,
                )

        report = run_fixture(GRADIENT, "gradient-linear.json")
        self.assertIn(
            "Functional colors are unsupported; use validated CSS hex or named colors.",
            report["limitations"],
        )

    def test_gradient_rejects_invalid_stops_without_sorting_or_coercion(self) -> None:
        for stops, message in (
            ([{"color": "red"}], "at least two color stops"),
            (["red", "blue"], "stops[0] must be an object"),
            (
                [{"color": "red", "position": "20deg"}, {"color": "blue"}],
                "linear stops[0].position must be a length or percentage",
            ),
            (
                [{"color": "red", "position": "10px"}, {"color": "blue"}],
                "conic stops[0].position must be an angle or percentage",
            ),
        ):
            with self.subTest(message=message):
                kind = "conic" if "conic" in message else "linear"
                result = invoke(
                    GRADIENT,
                    {"kind": kind, "geometry": {}, "stops": stops},
                    "--format",
                    "json",
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_gradient_rejects_trailing_decimal_numeric_tokens(self) -> None:
        cases = (
            (
                {
                    "kind": "linear",
                    "geometry": {"direction": "1.deg"},
                    "stops": [{"color": "#000"}, {"color": "#fff"}],
                },
                "geometry.direction",
            ),
            (
                {
                    "kind": "conic",
                    "geometry": {"from": "1.deg"},
                    "stops": [{"color": "#000"}, {"color": "#fff"}],
                },
                "geometry.from",
            ),
            (
                {
                    "kind": "linear",
                    "geometry": {},
                    "stops": [
                        {"color": "#000", "position": "1.px"},
                        {"color": "#fff"},
                    ],
                },
                "stops[0].position",
            ),
            (
                {
                    "kind": "linear",
                    "geometry": {},
                    "stops": [
                        {"color": "#000", "position": "1.%"},
                        {"color": "#fff"},
                    ],
                },
                "stops[0].position",
            ),
            (
                {
                    "kind": "conic",
                    "geometry": {},
                    "stops": [
                        {"color": "#000", "position": "1.deg"},
                        {"color": "#fff"},
                    ],
                },
                "stops[0].position",
            ),
            (
                {
                    "kind": "conic",
                    "geometry": {},
                    "stops": [
                        {"color": "#000", "position": "1.%"},
                        {"color": "#fff"},
                    ],
                },
                "stops[0].position",
            ),
        )

        for data, field in cases:
            with self.subTest(kind=data["kind"], field=field):
                result = invoke(GRADIENT, data, "--format", "json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field, result.stderr)

    def test_gradient_accepts_complete_numeric_tokens(self) -> None:
        for direction in ("1deg", "1.0deg", ".5turn"):
            with self.subTest(direction=direction):
                result = invoke(
                    GRADIENT,
                    {
                        "kind": "linear",
                        "geometry": {"direction": direction},
                        "stops": [{"color": "#000"}, {"color": "#fff"}],
                    },
                    "--format",
                    "json",
                )
                self.assertEqual(result.returncode, 0, result.stderr)

        for kind, position in (
            ("linear", "1px"),
            ("linear", "1%"),
            ("conic", "1deg"),
            ("conic", "1%"),
        ):
            with self.subTest(kind=kind, position=position):
                result = invoke(
                    GRADIENT,
                    {
                        "kind": kind,
                        "geometry": {},
                        "stops": [
                            {"color": "#000", "position": position},
                            {"color": "#fff"},
                        ],
                    },
                    "--format",
                    "json",
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_gradient_model_exposes_frozen_typed_records(self) -> None:
        spec = importlib.util.spec_from_file_location("gradient_model", GRADIENT_MODEL)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        gradient = module.Gradient(
            kind="linear",
            geometry={"direction": "to right"},
            stops=[
                {"color": "#000000", "position": None},
                {"color": "#ffffff", "position": "100%"},
            ],
        )

        self.assertEqual(type(gradient.stops).__name__, "tuple")
        self.assertEqual(type(gradient.stops[0]).__name__, "ColorStop")
        with self.assertRaisesRegex(Exception, "cannot assign to field"):
            gradient.stops[0].color = "red"

        serialized = gradient.value()
        with self.assertRaises(TypeError):
            gradient.geometry["direction"] = "to left"
        self.assertEqual(gradient.value(), serialized)

    def test_gradient_help_is_available(self) -> None:
        result = invoke(GRADIENT, None, "--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("linear, radial, or conic", result.stdout)

    def test_gradient_rejects_invalid_utf8_input_without_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "gradient.json"
            path.write_bytes(b"\xff")
            result = invoke(GRADIENT, None, "--input", str(path), "--format", "json")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unable to read JSON input: input is not valid UTF-8", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


class OklchConverterTests(unittest.TestCase):
    def test_oklch_matches_reference_vector(self) -> None:
        report = run_fixture(OKLCH, "oklch-reference.json")

        self.assertAlmostEqual(report["oklch"]["l"], 0.627955, places=5)
        self.assertAlmostEqual(report["oklch"]["c"], 0.257683, places=5)
        self.assertAlmostEqual(report["oklch"]["h"], 29.234, places=3)
        self.assertAlmostEqual(report["alpha"], 128 / 255)
        self.assertTrue(report["css"].startswith("oklch("))
        self.assertIn(" / 0.5019607843137255)", report["css"])

    def test_oklch_accepts_six_digit_hex_without_alpha_clamping(self) -> None:
        result = invoke(OKLCH, {"hex": "#000000"}, "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)

        self.assertEqual(report["input"], "#000000")
        self.assertEqual(report["oklch"], {"l": 0.0, "c": 0.0, "h": 0.0})
        self.assertEqual(report["alpha"], 1.0)
        self.assertEqual(report["css"], "oklch(0 0 none)")

    def test_oklch_retains_numeric_hue_but_serializes_powerless_hue_as_none(self) -> None:
        result = invoke(OKLCH, {"hex": "#ffffff"}, "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)

        self.assertIsInstance(report["oklch"]["h"], float)
        self.assertTrue(report["powerless_hue"])
        self.assertEqual(report["css_semantics"]["powerless_hue_epsilon"], 0.000004)
        self.assertIn(" none)", report["css"])

    def test_oklch_reports_computation_scope_and_numeric_limits(self) -> None:
        report = run_fixture(OKLCH, "oklch-reference.json")

        self.assertEqual(report["scope"], "color-space-conversion-only")
        self.assertEqual(report["gamut"]["mapping"], "none")
        self.assertEqual(report["rounding"]["numeric_channels"], "unrounded-binary64")
        self.assertEqual(report["contrast"]["status"], "not-evaluated")
        self.assertEqual(report["apca"]["status"], "not-implemented")

    def test_oklch_rejects_non_hex_and_css_injection(self) -> None:
        for value in ("#fff", "#gg0000", "#ff0000; color: blue", 123, None):
            with self.subTest(value=value):
                result = invoke(OKLCH, {"hex": value}, "--format", "json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("hex must be a six- or eight-digit sRGB hex color", result.stderr)

    def test_oklch_css_serialization_round_trips_binary64_channels(self) -> None:
        report = run_fixture(OKLCH, "oklch-reference.json")
        css = report["css"]
        channels = css.removeprefix("oklch(").removesuffix(")").split(" / ")[0].split()

        self.assertNotIn("%", channels[0])
        self.assertEqual(float(channels[0]), report["oklch"]["l"])
        self.assertEqual(float(channels[1]), report["oklch"]["c"])
        self.assertEqual(float(channels[2]), report["oklch"]["h"])

    def test_oklch_help_is_available(self) -> None:
        result = invoke(OKLCH, None, "--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("sRGB", result.stdout)

    def test_oklch_rejects_invalid_utf8_input_without_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "color.json"
            path.write_bytes(b"\xff")
            result = invoke(OKLCH, None, "--input", str(path), "--format", "json")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unable to read JSON input: input is not valid UTF-8", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


class GradientOracleTests(unittest.TestCase):
    def test_optional_lightningcss_result_is_classified_not_skipped(self) -> None:
        result = invoke(
            ORACLES,
            None,
            "--input",
            str(FIXTURES / "gradient-linear.json"),
            "--format",
            "json",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertIn(report["classification"], {"agreement", "divergence", "unavailable"})
        self.assertEqual(report["observations"][0]["oracle"], "lightningcss")

    def test_run_oracles_compares_adapter_output_to_canonical_gradient_core(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = Path(temporary_directory) / "lightningcss"
            executable.write_text(
                f"#!{sys.executable}\n"
                "import sys\n"
                "from pathlib import Path\n"
                "arguments = sys.argv[1:]\n"
                "output = Path(arguments[2])\n"
                "source = Path(arguments[3])\n"
                "expected = '.oracle { background-image: linear-gradient(90deg, #000000 50%, #ffffff 50%); }\\n'\n"
                "if source.read_text(encoding='utf-8') != expected:\n"
                "    raise SystemExit(3)\n"
                "output.write_text('.oracle{background-image:linear-gradient(90deg, #000000 50%, #ffffff 50%)}', encoding='utf-8')\n",
                encoding="utf-8",
            )
            executable.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = temporary_directory
            result = subprocess.run(
                [
                    sys.executable,
                    str(ORACLES),
                    "--input",
                    str(FIXTURES / "gradient-linear.json"),
                    "--format",
                    "json",
                ],
                text=True,
                capture_output=True,
                check=False,
                env=environment,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["classification"], "agreement")
        self.assertEqual(
            report["core"],
            {"value": "linear-gradient(90deg, #000000 50%, #ffffff 50%)"},
        )
        self.assertEqual(report["observations"][0]["relation_to_core"], "exact")

    def test_lightningcss_adapter_normalizes_typed_gradient_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable = Path(temporary_directory) / "lightningcss"
            executable.write_text(
                f"#!{sys.executable}\n"
                "import sys\n"
                "from pathlib import Path\n"
                "arguments = sys.argv[1:]\n"
                "output = Path(arguments[2])\n"
                "source = Path(arguments[3])\n"
                "expected = '.oracle { background-image: linear-gradient(90deg, #000000 50%, #ffffff 50%); }\\n'\n"
                "if source.read_text(encoding='utf-8') != expected:\n"
                "    raise SystemExit(3)\n"
                "output.write_text('.oracle{background-image:linear-gradient(90deg,#000 50%,#fff 50%)}', encoding='utf-8')\n",
                encoding="utf-8",
            )
            executable.chmod(0o755)
            result = invoke(
                LIGHTNINGCSS_ADAPTER,
                {
                    "kind": "linear",
                    "geometry": {"direction": "90deg"},
                    "stops": [
                        {"color": "#000000", "position": "50%"},
                        {"color": "#ffffff", "position": "50%"},
                    ],
                },
                "--executable",
                str(executable),
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {"value": "linear-gradient(90deg,#000 50%,#fff 50%)"},
        )


if __name__ == "__main__":
    unittest.main()
