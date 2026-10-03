"""Ten product scenarios. Assert decisions and integrity, not exact generated prose."""
import json
import unittest
from pathlib import Path

from scripts.decision import decide
from scripts.models import audit_claim
from tests.regression.test_decision import NOW, situation
from tests.regression.test_evidence import claim

ROOT = Path(__file__).resolve().parents[2]


def case(name):
    return json.loads((ROOT / "cases" / name / "input.json").read_text(encoding="utf-8"))


class ProductScenarios(unittest.TestCase):
    def check_contract(self, d):
        self.assertTrue(d["recommended_move"] and d["why"])
        self.assertTrue(d["facts"] and d["unknowns"])
        self.assertTrue(all(f["source"] for f in d["facts"]))
        self.assertTrue(1 <= len(d["actions"]) <= 3)
        self.assertTrue(d["observation_window"] and d["stop_condition"] and d["pivot_condition"])
        self.assertTrue(1 <= len(d["references"]) <= 3)

    def test_01_resume_jd_interview_tomorrow(self):
        d = decide(case("interview"), now=NOW)
        self.check_contract(d)
        self.assertTrue(d["urgency"]["within_72h"])
        self.assertEqual(d["bottleneck"], "Evidence")
        self.assertEqual(d["highest_risk"], "CJ-DEMO-1")
        self.assertIn("risk_map", [a["kind"] for a in d["actions"]])
        self.assertNotIn("build", d["method_plan"])

    def test_02_hr_three_workdays_no_reply(self):
        d = decide(case("follow-up"), now=NOW)
        self.check_contract(d)
        self.assertEqual(d["application_status"], "waiting")
        self.assertTrue(d["draft"])
        self.assertEqual(next(a for a in d["actions"] if a["kind"] == "send_message")["execution_mode"], "human")

    def test_03_unsupported_production(self):
        s = situation("positioning", claims=[claim(claim="production product", stage="demo")])
        d = decide(s, now=NOW); self.check_contract(d)
        self.assertNotEqual(d["claims"][0]["confidence"], "VERIFIED")
        self.assertIn("missing_evidence:production", d["claims"][0]["risk"])
        self.assertEqual(d["bottleneck"], "Evidence")

    def test_04_team_ownership_unclear(self):
        c = claim(claim="主导系统", ownership={"scope": "unclear", "contribution": ""})
        d = decide(situation("positioning", claims=[c]), now=NOW); self.check_contract(d)
        self.assertNotIn("主导系统", d["claims"][0]["safe_wording"])
        self.assertIn("personal_contribution_unknown", d["claims"][0]["risk"])

    def test_05_two_offers(self):
        d = decide(case("offer"), now=NOW); self.check_contract(d)
        self.assertIn("首选 合成 Offer A", d["recommended_move"])
        self.assertGreater(d["comparison"][0]["score"], d["comparison"][1]["score"])
        flipped = case("offer"); flipped["offer"]["weights"] = {"compensation": 1}
        self.assertIn("首选 合成 Offer B", decide(flipped, now=NOW)["recommended_move"])

    def test_06_rejected_without_feedback(self):
        d = decide(situation("recruiting", recruiting={"status": "rejected"}), now=NOW); self.check_contract(d)
        self.assertIn("原因未知", d["recommended_move"])
        self.assertEqual(d["application_status"], "rejected")
        self.assertFalse(any(a["kind"] == "send_message" for a in d["actions"]))

    def test_07_rejected_with_depth_feedback(self):
        d = decide(situation("recruiting", recruiting={"status": "rejected", "feedback": "technical-depth feedback"}), now=NOW)
        self.check_contract(d)
        self.assertTrue(any(a["kind"] == "question_ladder" for a in d["actions"]))
        self.assertTrue(any("单次反馈" in x["text"] for x in d["inferences"]))

    def test_08_swe_to_ai_pm(self):
        d = decide(situation("job", job={"fit": "gap", "gap": "缺产品问题选择与评测决策证据", "gap_days": 7}), now=NOW)
        self.check_contract(d)
        self.assertEqual(d["bottleneck"], "Evidence")
        self.assertIn("build", d["method_plan"])
        self.assertFalse(any(a["kind"] == "accept_offer" for a in d["actions"]))

    def test_09_hackathon_project(self):
        c = claim(claim="Hackathon winner", stage="demo", ownership={"scope": "team", "contribution": "demo evaluation"})
        d = decide(situation("positioning", claims=[c]), now=NOW); self.check_contract(d)
        self.assertIn("missing_evidence:award", d["claims"][0]["risk"])
        self.assertNotIn("winner", d["claims"][0]["safe_wording"])

    def test_10_unknown_direction(self):
        d = decide(situation("job", goal="", claims=[]), now=NOW); self.check_contract(d)
        self.assertEqual(d["bottleneck"], "Direction")
        self.assertIn("jd_map", [a["kind"] for a in d["actions"]])
        self.assertIn("三个真实经历", d["recommended_move"])
