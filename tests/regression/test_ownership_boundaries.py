"""Keep planned work, personal contribution stages and Claim attribution distinct."""
import unittest

from scripts.actions import artifact_contents
from scripts.decision import decide, render
from tests.regression.test_decision import situation
from tests.regression.test_evidence import claim
from tests.regression.test_mock_boundaries import leadership_claim


class OwnershipBoundaryTests(unittest.TestCase):
    def test_planned_claim_stays_planned_in_recommendation_and_artifacts(self):
        for changes in ({"stage": "planned"}, {"stage": "completed", "confidence": "PLANNED"}):
            with self.subTest(changes=changes):
                raw = claim(**changes)
                raw["ownership"]["contribution"] = "设计评测流程"
                d = decide(situation("positioning", claims=[raw]))
                self.assertIn("计划", d["ownership_defense"]["safe_claim"])
                self.assertIn("不能作为已完成", render(d))
                artifacts = artifact_contents(d)
                self.assertIn(d["claims"][0]["safe_wording"], artifacts["claim-risk-map.md"])
                self.assertIn("计划", artifacts["ownership-defense.md"])

    def test_explicit_planned_personal_contribution_is_not_a_completed_contribution(self):
        d = decide(situation("positioning", ownership={"project_stage": "production", "contributions": [
            {"claim_id": "C1", "claim_stage": "completed", "user_contribution_stage": "planned"}]}))
        self.assertIn("计划", d["ownership_defense"]["safe_claim"])
        self.assertIn("不能作为已完成", d["ownership_defense"]["safe_claim"])

    def test_completed_project_does_not_imply_known_personal_completion(self):
        raw = leadership_claim("主导产品规划，协调团队完成插件实现和部署脚本")
        d = decide(situation("positioning", claims=[raw], ownership={"project_stage": "production"}))
        self.assertIn("个人完成阶段待确认", d["ownership_defense"]["safe_claim"])
        self.assertIn("产品定义和跨团队决策", d["ownership_defense"]["safe_claim"])
        self.assertEqual(d["claims"][0]["confidence"], "VERIFIED")

    def test_risk_map_preserves_each_claim_and_its_own_contribution(self):
        claims = [claim(id="A", claim="Maintained parser fixtures", stage="completed",
                        ownership={"scope": "team", "contribution": "Maintained parser fixtures"}),
                  claim(id="B", claim="Designed customer research", stage="completed",
                        ownership={"scope": "team", "contribution": "Designed customer research"})]
        d = decide(situation("positioning", claims=claims))
        risk_map = artifact_contents(d)["claim-risk-map.md"]
        a = risk_map.split("## A\n", 1)[1].split("## B\n", 1)[0]
        b = risk_map.split("## B\n", 1)[1]
        self.assertIn(d["claims"][0]["safe_wording"], a)
        self.assertIn(d["claims"][1]["safe_wording"], b)
        self.assertNotIn("Designed customer research", a)
        self.assertNotIn("Maintained parser fixtures", b)

    def test_mixed_completed_and_planned_contributions_keep_separate_boundaries(self):
        done = leadership_claim("主导产品规划，协调团队完成插件实现和部署脚本")
        planned = claim(id="future", stage="planned", ownership={"scope": "team", "contribution": "新增自动评测"})
        d = decide(situation("positioning", claims=[done, planned], ownership={"contributions": [
            {"claim_id": done["id"], "claim_stage": "completed", "user_contribution_stage": "completed"}]}))
        pack = d["ownership_defense"]
        self.assertIn("产品定义和跨团队决策", pack["safe_claim"])
        self.assertIn("新增自动评测", pack["safe_claim"])
        self.assertIn("个人贡献已完成", pack["safe_claim"])
        self.assertIn("不能作为已完成", pack["safe_claim"])
        self.assertIn("主导产品规划", artifact_contents(d)["claim-risk-map.md"])

    def test_long_planned_contribution_keeps_full_qualifier_in_artifact(self):
        contribution = "x" * 370 + "；尚未实施，不是已完成贡献"
        d = decide(situation("positioning", claims=[claim(stage="planned", ownership={"scope": "team", "contribution": contribution})]))
        self.assertIn("计划", d["ownership_defense"]["safe_claim"])
        self.assertIn(contribution, artifact_contents(d)["ownership-defense.md"])


if __name__ == "__main__":
    unittest.main()
