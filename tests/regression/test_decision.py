import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.decision import decide, render
from scripts.models import ContractError
from scripts.router import ROUTES, route
from tests.regression.test_evidence import claim

NOW = datetime(2026, 10, 3, 12, tzinfo=timezone.utc)


def situation(mode="interview", **extra):
    s = {"mode": mode, "summary": "synthetic situation", "goal": "defensible next move",
         "facts": [{"text": "明天面试", "source": "synthetic:user", "source_type": "user_report"}],
         "unknowns": ["final assessment unknown"], "claims": [claim()]}
    s.update(extra)
    return s


class DecisionRegression(unittest.TestCase):
    def test_all_modes_have_action_observation_and_provenance(self):
        root = Path(__file__).resolve().parents[2]
        for mode in ROUTES:
            with self.subTest(mode=mode):
                d = decide(situation(mode), now=NOW)
                self.assertTrue(d["recommended_move"])
                self.assertTrue(1 <= len(d["actions"]) <= 3)
                self.assertTrue(d["observation_window"] and d["stop_condition"] and d["pivot_condition"])
                self.assertEqual(d["facts"][0]["label"], "FACT")
                self.assertTrue(d["unknowns"])
                self.assertTrue(1 <= len(d["references"]) <= 3)
                self.assertTrue(all((root / p).is_file() for p in d["references"]))

    def test_silence_never_rejected(self):
        d = decide(situation("recruiting", recruiting={"working_days": 3}), now=NOW)
        self.assertEqual(d["application_status"], "waiting")
        self.assertIn("跟进一次", d["recommended_move"])
        self.assertTrue(d["draft"])

    def test_calendar_days_not_assumed_workdays(self):
        d = decide(situation("recruiting", recruiting={}), now=NOW)
        self.assertIn("确认", d["recommended_move"])
        self.assertIsNone(d["draft"])

    def test_promised_date_before_default(self):
        d = decide(situation("recruiting", recruiting={"working_days": 3, "promised_date": "下周五"}), now=NOW)
        self.assertIn("先等", d["recommended_move"])

    def test_no_repeated_chasing(self):
        d = decide(situation("recruiting", recruiting={"working_days": 6, "followups": 1}), now=NOW)
        self.assertFalse(any(a["kind"] == "send_message" for a in d["actions"]))

    def test_no_contact_stops(self):
        d = decide(situation("recruiting", recruiting={"no_contact": True}), now=NOW)
        self.assertIn("停止联系", d["recommended_move"])

    def test_pass_does_not_prove_strategy(self):
        d = decide(situation("recruiting", recruiting={"status": "passed"}), now=NOW)
        self.assertIn("不证明", d["recommended_move"])
        self.assertTrue(any("因果" in u["text"] for u in d["unknowns"]))

    def test_one_feedback_not_universal(self):
        d = decide(situation("recruiting", recruiting={"status": "rejected", "feedback": "technical depth"}), now=NOW)
        self.assertTrue(any("单次反馈" in f["text"] for f in d["inferences"]))
        self.assertIn("rejection.md", d["references"][-1])

    def test_deadline_timezone_and_overdue(self):
        d = decide(situation(deadline="2026-10-04T20:00:00+08:00"), now=NOW)
        self.assertEqual(d["urgency"]["hours_remaining"], 24)
        self.assertTrue(d["urgency"]["within_72h"])
        d = decide(situation(deadline="2026-10-02T20:00:00+08:00"), now=NOW)
        self.assertTrue(d["urgency"]["overdue"])
        self.assertIn("已过期", d["recommended_move"])
        with self.assertRaises(ContractError):
            decide(situation(deadline="tomorrow"), now=NOW)

    def test_user_labels_not_rendered_as_internal_scores(self):
        rendered = render(decide(situation(), now=NOW))
        self.assertNotIn("VERIFIED", rendered)
        self.assertNotIn("/proof", rendered)

    def test_offer_unknown_goals_not_brand_ranking(self):
        d = decide(situation("offer", goal="", offer={"options": []}), now=NOW)
        self.assertIn("先确认", d["recommended_move"])

    def test_offer_missing_manager_not_imputed(self):
        offer = {"weights": {"manager": 1}, "constraints": [], "options": [
            {"name": "A", "constraint_status": "pass", "ratings": {}},
            {"name": "B", "constraint_status": "pass", "ratings": {"manager": 4}}]}
        d = decide(situation("offer", offer=offer), now=NOW)
        self.assertIsNone(d["comparison"][0]["score"])
        self.assertIn("先确认", d["recommended_move"])

    def test_offer_constraint_overrides_score(self):
        offer = {"weights": {"learning": 2, "compensation": 1}, "constraints": ["本地"], "options": [
            {"name": "A", "constraint_status": "fail", "ratings": {"learning": 5, "compensation": 5}},
            {"name": "B", "constraint_status": "pass", "ratings": {"learning": 4, "compensation": 3}}]}
        d = decide(situation("offer", offer=offer), now=NOW)
        self.assertIn("首选 B", d["recommended_move"])
        self.assertFalse(d["comparison"][0]["eligible"])

    def test_nonfinite_or_unknown_input_rejected(self):
        with self.assertRaises(ContractError):
            decide(situation("offer", offer={"weights": {"learning": float("nan")}}), now=NOW)
        with self.assertRaises(ContractError):
            route("invented")
        with self.assertRaises(ContractError):
            decide(situation(execute_shell="unexpected"), now=NOW)
