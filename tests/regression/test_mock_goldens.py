"""Replay each public synthetic core decision case without calling a model in CI."""
import importlib.util
import json
import unittest
from pathlib import Path

DATASET = Path(__file__).resolve().parents[2] / "benchmark/mock-career-cases"
spec = importlib.util.spec_from_file_location("mock_replay", DATASET / "replay.py")
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)
GOLDENS = json.loads((DATASET / "golden-properties.json").read_text(encoding="utf-8"))


class CoreDecisionGoldenTests(unittest.TestCase):
    def check_case(self, index):
        result = replay.run_case(GOLDENS[index])
        self.assertTrue(result["source_identity"])
        self.assertTrue(result["property_pass"], result)

    def test_interview_bottleneck_boundaries(self):
        self.check_case(0)

    def test_recruiting_uncertainty_boundaries(self):
        self.check_case(1)

    def test_offer_uncertainty_boundaries(self):
        self.check_case(2)

    def test_direction_routing_boundaries(self):
        self.check_case(3)

    def test_ownership_evidence_boundaries(self):
        self.check_case(4)
