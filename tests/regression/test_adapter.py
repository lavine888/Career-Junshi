import unittest

from scripts.method_adapter import method_plan, review_pattern


class MethodAdapterRegression(unittest.TestCase):
    def test_urgent_interview_uses_defense_not_build(self):
        self.assertEqual(method_plan("interview", urgent=True), ["proof", "position", "interview", "offer"])
        self.assertNotIn("build", method_plan("job", evidence_gap=True, urgent=True))
        self.assertIn("build", method_plan("job", evidence_gap=True, urgent=False))

    def test_single_feedback_does_not_pivot(self):
        f = {"role_family": "AI PM", "gap": "technical depth", "source": "case-1", "comparable": True}
        self.assertEqual(review_pattern([f])["move"], "KEEP")
        self.assertEqual(review_pattern([f] * 10)["move"], "KEEP")

    def test_comparable_repeated_gaps_only(self):
        entries = [{"role_family": "AI PM", "gap": "technical depth", "source": f"case-{i}", "comparable": True} for i in range(5)]
        self.assertEqual(review_pattern(entries)["move"], "REFINE")
        self.assertEqual(review_pattern([{**e, "comparable": False} for e in entries])["move"], "KEEP")
