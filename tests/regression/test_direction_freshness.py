"""Current-market sources condition direction decisions without erasing history."""
import unittest

from scripts.decision import decide
from tests.regression.test_decision_quality import candidate
from tests.regression.test_decision import NOW


class DirectionFreshnessTests(unittest.TestCase):
    def scenario(self, primary_category="current_jd", primary_date="2024-01-01T00:00:00+00:00"):
        a, b = candidate("A", "ai-product"), candidate("B", "technical-product", "medium")
        for c, sid in ((a, "A-source"), (b, "B-source")):
            c.update(source_ids=[sid], constraint_status="pass", largest_gap="")
        return {"mode": "job", "summary": "Compare supplied career directions", "goal": "Choose a bounded application direction",
                "facts": [{"text": "Reported basis for A", "source": "A-source", "source_type": "jd",
                           "freshness": {"category": primary_category, "observed_at": primary_date}},
                          {"text": "Reported basis for B", "source": "B-source", "source_type": "jd",
                           "freshness": {"category": "current_jd", "observed_at": NOW.isoformat()}}],
                "direction": {"candidates": [a, b]}}

    def test_stale_primary_is_conditional_in_decision_and_trace(self):
        d = decide(self.scenario(), now=NOW)
        self.assertEqual(d["primary_choice"], ["A"])
        self.assertEqual(d["recommendation_type"], "CONDITIONAL")
        self.assertEqual(d["decision_sufficiency"]["state"], "DECISION_CONDITIONAL")
        self.assertTrue(d["decision_sufficiency"]["reversal_unknowns"])
        self.assertEqual(d["recommendation"]["supporting_evidence"], [])
        self.assertEqual(d["decision_trace"]["chosen"], d["recommended_move"])
        self.assertIn("核实", next(a["description"] for a in d["actions"] if a["kind"] == "apply"))

    def test_undated_current_primary_also_requires_check(self):
        s = self.scenario()
        del s["facts"][0]["freshness"]["observed_at"]
        self.assertEqual(decide(s, now=NOW)["recommendation_type"], "CONDITIONAL")

    def test_stale_sources_cannot_relax_an_expired_deadline_block(self):
        s = self.scenario()
        s["deadline"] = "2026-10-02T00:00:00Z"
        d = decide(s, now=NOW)
        self.assertTrue(d["urgency"]["overdue"])
        self.assertEqual(d["recommendation_type"], "BLOCKED")
        self.assertEqual(d["decision_sufficiency"]["state"], "DECISION_BLOCKED")
        self.assertEqual(d["decision_sufficiency"]["blocking_unknowns"], ["机会是否仍有效"])
        self.assertIn("先确认已过期", d["recommendation"]["move"])

    def test_stable_personal_history_is_not_expired(self):
        d = decide(self.scenario("personal_history"), now=NOW)
        self.assertEqual(d["recommendation_type"], "SUFFICIENT")
        self.assertEqual(d["recommendation"]["supporting_evidence"][0]["source"], "A-source")

    def test_unrelated_stale_secondary_does_not_downgrade_current_primary(self):
        s = self.scenario(primary_date=NOW.isoformat())
        s["facts"][1]["freshness"]["observed_at"] = "2024-01-01T00:00:00+00:00"
        self.assertEqual(decide(s, now=NOW)["recommendation_type"], "SUFFICIENT")
