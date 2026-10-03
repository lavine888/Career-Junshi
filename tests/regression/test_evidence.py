import copy
import unittest

from scripts.models import ContractError, audit_claim


def claim(**changes):
    c = {"id": "C1", "claim": "Implemented an evaluation prototype", "stage": "demo",
         "confidence": "VERIFIED", "ownership": {"scope": "team", "contribution": "evaluation script"},
         "evidence": []}
    c.update(changes)
    return c


def checked(*supports):
    return {"kind": "direct", "source": "synthetic:reviewed-artifact", "supports": list(supports),
            "checked_by": "synthetic-test-operator", "checked_at": "2026-10-03T12:00:00+08:00"}


class EvidenceRegression(unittest.TestCase):
    def test_planned_cannot_be_completed(self):
        result = audit_claim(claim(stage="planned", evidence=[checked("claim", "authorship")]))
        self.assertEqual(result["confidence"], "PLANNED")
        self.assertIn("尚不能", result["safe_wording"])

    def test_team_cannot_be_sole(self):
        result = audit_claim(claim(claim="独立完成所有代码", evidence=[checked("claim")]))
        self.assertIn("ownership_conflict:team_or_unclear_is_not_sole", result["risk"])
        self.assertNotEqual(result["confidence"], "VERIFIED")
        self.assertNotIn("独立完成", result["safe_wording"])

    def test_demo_cannot_be_production(self):
        result = audit_claim(claim(claim="Production system serving 100 用户", evidence=[checked("claim")]))
        self.assertIn("missing_evidence:production", result["risk"])
        self.assertIn("原型", result["safe_wording"])

    def test_backtest_is_not_real_result(self):
        result = audit_claim(claim(stage="backtest", claim="实盘盈利", evidence=[checked("claim")]))
        self.assertIn("stage_conflict:backtest_is_not_real_world", result["risk"])

    def test_source_code_is_not_authorship(self):
        result = audit_claim(claim(evidence=[checked("claim")]))
        self.assertIn("missing_evidence:authorship", result["risk"])
        self.assertNotEqual(result["confidence"], "VERIFIED")

    def test_participation_is_not_award(self):
        result = audit_claim(claim(claim="Hackathon winner", evidence=[checked("claim")]))
        self.assertIn("missing_evidence:award", result["risk"])

    def test_weak_evidence_never_verified(self):
        for evidence in ([], [{"kind": "direct", "source": "https://example.org/repo", "supports": ["claim"]}],
                         [{"kind": "self_report", "source": "candidate", "supports": ["claim", "authorship"]}]):
            self.assertNotEqual(audit_claim(claim(evidence=evidence))["confidence"], "VERIFIED")

    def test_complete_narrow_receipt(self):
        self.assertEqual(audit_claim(claim(evidence=[checked("claim", "authorship")]))["confidence"], "VERIFIED")

    def test_low_requested_level_not_upgraded(self):
        self.assertEqual(audit_claim(claim(confidence="SELF_REPORTED", evidence=[checked("claim", "authorship")]))["confidence"], "SELF_REPORTED")

    def test_ownership_unclear(self):
        result = audit_claim(claim(claim="主导架构", ownership={"scope": "unclear", "contribution": ""}))
        self.assertIn("ownership_unclear:leadership_needs_personal_decisions", result["risk"])

    def test_bad_receipt_is_rejected(self):
        bad = copy.deepcopy(checked("claim")); bad["checked_at"] = "yesterday"
        with self.assertRaises(ContractError):
            audit_claim(claim(evidence=[bad]))

    def test_contribution_does_not_prove_leadership(self):
        result = audit_claim(claim(claim="主导架构", evidence=[checked("claim")]))
        self.assertIn("missing_evidence:leadership", result["risk"])
        self.assertNotEqual(result["confidence"], "VERIFIED")
