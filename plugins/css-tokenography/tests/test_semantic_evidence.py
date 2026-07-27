import json
import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from css_tokenography_core import (
    EvidenceEnvelope,
    OracleObservation,
    Provenance,
    classify_observations,
)


class SemanticEvidenceTests(unittest.TestCase):
    def test_unanimous_differing_values_are_not_inferred_equivalent(self) -> None:
        envelope = EvidenceEnvelope(core={"value": "rotate(1turn)"})
        envelope.add(
            OracleObservation(
                "lightningcss",
                "ok",
                {"value": "rotate(360deg)"},
                relation_to_core="different",
            )
        )
        envelope.add(
            OracleObservation(
                "chromium",
                "ok",
                {"value": "rotate(360deg)"},
                relation_to_core="different",
            )
        )

        report = envelope.to_dict()

        self.assertEqual(report["classification"], "divergence")
        self.assertEqual(len(report["observations"]), 2)
        self.assertEqual(
            [item["relation_to_core"] for item in report["observations"]],
            ["different", "different"],
        )

    def test_explicit_rotation_equivalence_is_equivalent(self) -> None:
        envelope = EvidenceEnvelope(core={"value": "rotate(1turn)"})
        envelope.add(
            OracleObservation(
                "lightningcss",
                "ok",
                {"value": "rotate(360deg)"},
                relation_to_core="equivalent",
            )
        )

        self.assertEqual(envelope.to_dict()["classification"], "equivalent")

    def test_unavailable_is_not_agreement(self) -> None:
        envelope = EvidenceEnvelope(core={"value": "x"})
        envelope.add(OracleObservation("lightningcss", "unavailable", None))

        self.assertEqual(envelope.to_dict()["classification"], "unavailable")

    def test_observation_serializes_provenance_and_notes_as_json(self) -> None:
        envelope = EvidenceEnvelope(core={"value": "x"})
        envelope.add(
            OracleObservation(
                "chromium",
                "ok",
                {"value": "x"},
                relation_to_core="exact",
                provenance=Provenance(
                    source="chromium",
                    version="128",
                    revision="abc123",
                    browser="Chromium",
                ),
                notes=("stable",),
            )
        )

        report = envelope.to_dict()

        self.assertEqual(report["classification"], "agreement")
        self.assertEqual(
            report["observations"][0]["provenance"],
            {
                "source": "chromium",
                "version": "128",
                "revision": "abc123",
                "browser": "Chromium",
            },
        )
        round_tripped = json.loads(json.dumps(report))
        self.assertEqual(round_tripped["observations"][0]["notes"], ["stable"])
        self.assertEqual(
            round_tripped["observations"][0]["relation_to_core"], "exact"
        )

    def test_provenance_and_observations_are_immutable(self) -> None:
        provenance = Provenance(source="wpt")
        observation = OracleObservation(
            "chromium", "ok", {"value": "x"}, relation_to_core="exact"
        )

        with self.assertRaises(FrozenInstanceError):
            provenance.source = "other"
        with self.assertRaises(FrozenInstanceError):
            observation.status = "error"

    def test_errors_take_precedence_over_available_results(self) -> None:
        observations = [
            OracleObservation(
                "chromium", "ok", {"value": "x"}, relation_to_core="exact"
            ),
            OracleObservation("lightningcss", "error", None),
        ]

        self.assertEqual(
            classify_observations({"value": "x"}, observations), "error"
        )

    def test_matching_and_unavailable_results_are_partial(self) -> None:
        observations = [
            OracleObservation(
                "chromium", "ok", {"value": "x"}, relation_to_core="exact"
            ),
            OracleObservation("lightningcss", "unavailable", None),
        ]

        self.assertEqual(
            classify_observations({"value": "x"}, observations), "partial"
        )

    def test_matching_and_unsupported_results_are_partial(self) -> None:
        observations = [
            OracleObservation(
                "chromium", "ok", {"value": "x"}, relation_to_core="exact"
            ),
            OracleObservation("lightningcss", "unsupported", None),
        ]

        self.assertEqual(
            classify_observations({"value": "x"}, observations), "partial"
        )

    def test_matching_and_bounded_subset_results_are_bounded_subset(self) -> None:
        observations = [
            OracleObservation(
                "chromium", "ok", {"value": "x"}, relation_to_core="exact"
            ),
            OracleObservation(
                "wpt",
                "ok",
                {"covered": ["rotate", "translate"]},
                relation_to_core="bounded-subset",
            ),
        ]

        self.assertEqual(
            classify_observations({"value": "x"}, observations), "bounded-subset"
        )

    def test_unsupported_without_usable_results_is_unavailable(self) -> None:
        observations = [
            OracleObservation("lightningcss", "unsupported", None),
            OracleObservation("chromium", "unavailable", None),
        ]

        self.assertEqual(
            classify_observations({"value": "x"}, observations), "unavailable"
        )

    def test_ok_observation_requires_relation_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "relation_to_core is required"):
            OracleObservation("chromium", "ok", {"value": "x"})

    def test_ok_observation_rejects_invalid_relation_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid relation_to_core"):
            OracleObservation(
                "chromium", "ok", {"value": "x"}, relation_to_core="same"
            )

    def test_non_usable_observations_reject_relation_evidence(self) -> None:
        for status in ("unavailable", "unsupported", "error"):
            with self.subTest(status=status):
                with self.assertRaisesRegex(
                    ValueError, "relation_to_core must be absent"
                ):
                    OracleObservation(
                        "oracle", status, None, relation_to_core="different"
                    )


if __name__ == "__main__":
    unittest.main()
