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
    def test_disagreement_retains_both_observations(self) -> None:
        envelope = EvidenceEnvelope(core={"value": "rotate(1turn)"})
        envelope.add(
            OracleObservation(
                "lightningcss", "ok", {"value": "rotate(360deg)"}
            )
        )
        envelope.add(
            OracleObservation("chromium", "ok", {"value": "rotate(360deg)"})
        )

        report = envelope.to_dict()

        self.assertEqual(report["classification"], "equivalent")
        self.assertEqual(len(report["observations"]), 2)

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

    def test_provenance_and_observations_are_immutable(self) -> None:
        provenance = Provenance(source="wpt")
        observation = OracleObservation("chromium", "ok", {"value": "x"})

        with self.assertRaises(FrozenInstanceError):
            provenance.source = "other"
        with self.assertRaises(FrozenInstanceError):
            observation.status = "error"

    def test_errors_take_precedence_over_available_results(self) -> None:
        observations = [
            OracleObservation("chromium", "ok", {"value": "x"}),
            OracleObservation("lightningcss", "error", None),
        ]

        self.assertEqual(
            classify_observations({"value": "x"}, observations), "error"
        )

    def test_differing_available_results_are_divergence(self) -> None:
        observations = [
            OracleObservation("chromium", "ok", {"value": "x"}),
            OracleObservation("lightningcss", "ok", {"value": "y"}),
        ]

        self.assertEqual(
            classify_observations({"value": "x"}, observations), "divergence"
        )

    def test_unsupported_without_available_results_is_unsupported(self) -> None:
        observations = [
            OracleObservation("lightningcss", "unsupported", None),
            OracleObservation("chromium", "unavailable", None),
        ]

        self.assertEqual(
            classify_observations({"value": "x"}, observations), "unsupported"
        )

    def test_explicit_bounded_subset_is_retained(self) -> None:
        observations = [
            OracleObservation(
                "wpt", "bounded-subset", {"covered": ["rotate", "translate"]}
            )
        ]

        self.assertEqual(
            classify_observations({"value": "x"}, observations), "bounded-subset"
        )


if __name__ == "__main__":
    unittest.main()
