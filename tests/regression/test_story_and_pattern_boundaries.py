"""Synthetic regressions for project attribution and independent gap counts."""
import unittest
from datetime import datetime, timezone

from scripts.decision import decide
from scripts.method_adapter import review_pattern
from scripts.models import ContractError, audit_claim
from scripts.role_story import map_story


def claim(claim_id="C1"):
    return {"id": claim_id, "claim": "Designed evaluation cases", "confidence": "SUPPORTED",
            "stage": "demo", "ownership": {"scope": "team", "contribution": "Evaluation cases"},
            "evidence": [{"source": "fixture://evaluation", "kind": "supporting", "supports": ["claim"]}]}


def story():
    return {"project_id": "PROJECT-A", "source": "fixture://project", "claim_ids": ["C1"],
            "story": {"tension": "Unclear failure modes", "personal_decision": "Selected evaluation cases",
                      "ownership": "Evaluation cases only", "tradeoff": "Coverage versus cost",
                      "result_evidence": "fixture://evaluation", "learning": "Review failures"}}


class StoryProjectBoundaryTests(unittest.TestCase):
    def test_decide_rejects_claim_from_another_explicit_project(self):
        value = {"mode": "interview", "summary": "Defend evaluation work", "claims": [claim()],
                 "claim_refs": [{"project_id": "PROJECT-B", "claim_id": "C1"}], "project_story": story()}
        with self.assertRaisesRegex(ContractError, "story project"):
            decide(value, now=datetime(2026, 10, 19, tzinfo=timezone.utc))

    def test_matching_scoped_claim_produces_a_defensible_draft(self):
        result = map_story(story(), [audit_claim(claim())], "ai-product",
                           claim_refs=[{"project_id": " PROJECT-A ", "claim_id": " C1 "}])
        self.assertEqual(result["project_id"], "PROJECT-A")
        self.assertEqual(result["story_quality"], "DEFENSIBLE_DRAFT")

    def test_legacy_unscoped_claim_remains_compatible(self):
        result = map_story(story(), [audit_claim(claim())], "ai-product")
        self.assertEqual(result["story_quality"], "DEFENSIBLE_DRAFT")

    def test_another_projects_unselected_claim_does_not_block_story(self):
        result = map_story(story(), [audit_claim(claim()), audit_claim(claim("C2"))], "ai-product",
                           claim_refs=[{"project_id": "PROJECT-B", "claim_id": "C2"}])
        self.assertEqual(result["claim_ids"], ["C1"])


class FeedbackPatternBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.entries = [{"role_family": "ai-product", "gap": "technical depth",
                         "source": f"fixture://interview-{i}", "comparable": True} for i in range(5)]

    def test_empty_feedback_cannot_erase_an_observed_pattern(self):
        empty = [dict(r, gap="") for r in self.entries]
        expected = review_pattern(self.entries)
        self.assertEqual(expected["move"], "REFINE")
        self.assertEqual(review_pattern(self.entries + empty), expected)
        self.assertEqual(review_pattern(empty + self.entries), expected)

    def test_independent_gaps_from_same_sources_survive_reordering(self):
        other = [dict(r, gap="ownership") for r in self.entries]
        expected = review_pattern(self.entries + other)
        self.assertEqual({r["gap"]: r["count"] for r in expected["repeated_gaps"]},
                         {"technical depth": 5, "ownership": 5})
        self.assertEqual(review_pattern(other + self.entries), expected)
        self.assertEqual(review_pattern(list(reversed(self.entries + other))), expected)

    def test_reimports_do_not_inflate_the_same_gap(self):
        self.assertEqual(review_pattern(self.entries * 3), review_pattern(self.entries))
        self.assertEqual(review_pattern(self.entries[:1] * 10)["move"], "KEEP")

    def test_incomparable_feedback_does_not_complete_a_pattern(self):
        entries = self.entries[:4] + [dict(self.entries[4], comparable=False)]
        self.assertEqual(review_pattern(entries)["move"], "KEEP")


if __name__ == "__main__":
    unittest.main()
