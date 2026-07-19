import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "css-transforms" / "scripts"
CLI = SCRIPTS / "css_transform_playground.py"
sys.path.insert(0, str(SCRIPTS))


def fn(name, *args):
    return {"name": name, "args": list(args)}


def run_transform(functions, **extra):
    from transform_model import build_transform_report

    return build_transform_report({"transform": {"kind": "list", "functions": functions}, **extra})


def run_cli(payload):
    return subprocess.run(
        [sys.executable, str(CLI), "--format", "json"],
        input=json.dumps(payload), text=True, capture_output=True, check=False,
    )


class TransformTests(unittest.TestCase):
    def test_reversed_lists_serialize_and_compose_differently(self):
        first = run_transform([fn("rotate", "20deg"), fn("translateX", "10px")])
        second = run_transform([fn("translateX", "10px"), fn("rotate", "20deg")])
        self.assertNotEqual(first["css"], second["css"])
        self.assertNotEqual(first["matrix"], second["matrix"])
        self.assertEqual(first["ordered_functions"], [fn("rotate", "20deg"), fn("translateX", "10px")])
        self.assertEqual(first["matrix_order"], "multiply-functions-left-to-right")

    def test_none_differs_from_identity_list(self):
        from transform_model import build_transform_report

        none = build_transform_report({"transform": {"kind": "none"}})
        identity = run_transform([fn("translateX", "0px"), fn("rotate", "0deg"), fn("scale", 1)])
        self.assertFalse(none["creates_stacking_context"])
        self.assertTrue(identity["creates_stacking_context"])
        self.assertFalse(none["creates_fixed_containing_block"])
        self.assertTrue(identity["creates_fixed_containing_block"])
        self.assertEqual(none["css"], "transform: none;")
        self.assertEqual(identity["matrix"], none["matrix"])

    def test_ancestor_perspective_is_separate_from_function_perspective(self):
        property_mode = run_transform([fn("rotateY", "25deg")], ancestor={"perspective": "800px", "perspective_origin": "center"})
        function_mode = run_transform([fn("perspective", "800px"), fn("rotateY", "25deg")])
        self.assertEqual(property_mode["perspective"]["mode"], "ancestor-property")
        self.assertEqual(function_mode["perspective"]["mode"], "transform-function")
        self.assertNotEqual(property_mode["matrix"], function_mode["matrix"])
        self.assertIn("perspective: 800px;", property_mode["ancestor_css"])
        self.assertNotIn("perspective(", property_mode["transform_css"])

    def test_known_two_dimensional_matrix_uses_css_list_multiplication(self):
        report = run_transform([fn("translate", "10px", "20px"), fn("scale", 2)])
        self.assertEqual(report["matrix"], [
            [2.0, 0.0, 0.0, 10.0],
            [0.0, 2.0, 0.0, 20.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ])

    def test_matrix_and_matrix3d_are_preserved(self):
        matrix = run_transform([fn("matrix", 1, 2, 3, 4, 5, 6)])
        self.assertEqual(matrix["matrix"][0], [1.0, 3.0, 0.0, 5.0])
        self.assertEqual(matrix["matrix"][1], [2.0, 4.0, 0.0, 6.0])
        values = list(range(1, 17))
        matrix3d = run_transform([fn("matrix3d", *values)])
        self.assertEqual(matrix3d["matrix"][0], [1.0, 5.0, 9.0, 13.0])
        self.assertEqual(matrix3d["matrix"][3], [4.0, 8.0, 12.0, 16.0])

    def test_invalid_arity_units_and_injection_fail(self):
        invalid = [
            [fn("translateX", "10deg")],
            [fn("rotate", "10px")],
            [fn("scale", "2px")],
            [fn("perspective", "0px")],
            [fn("translate3d", "1px", "2px")],
            [fn("rotate", "1deg) translateX(2px")],
            [fn("unknown", 1)],
        ]
        for functions in invalid:
            with self.subTest(functions=functions):
                result = run_cli({"transform": {"kind": "list", "functions": functions}})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("css-transform-playground", result.stderr)

    def test_compositing_is_never_promised(self):
        report = run_transform([fn("translateZ", "0px")])
        self.assertEqual(report["compositor_layer"], "browser-dependent")
        self.assertEqual(report["gpu_acceleration"], "not-guaranteed")
        self.assertIn("does not guarantee", report["warnings"][0])


if __name__ == "__main__":
    unittest.main()
