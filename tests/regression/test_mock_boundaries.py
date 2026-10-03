"""General source/ownership patterns revealed by synthetic career debugging."""
import unittest
from datetime import datetime, timezone
from scripts.actions import artifact_contents
from scripts.context import extract
from scripts.decision import decide
from scripts.models import audit_claim, ContractError


def leadership_claim(words):
    return {"id": "component", "claim": words, "stage": "completed", "confidence": "VERIFIED",
            "ownership": {"scope": "team", "contribution": "产品定义和跨团队决策"},
            "evidence": [{"source": "synthetic:decision-log", "kind": "direct", "supports": ["claim", "leadership"],
                          "checked_by": "synthetic reviewer", "checked_at": "2026-10-03T12:00:00Z"}]}


class MockBoundaryTests(unittest.TestCase):
    def test_compound_technical_creation_needs_distinct_authorship(self):
        for words in ["主导项目并完成客户端插件实现和部署脚本", "主导交付，设计系统架构并实现数据模块"]:
            with self.subTest(words=words):
                result = audit_claim(leadership_claim(words))
                self.assertIn("missing_evidence:authorship", result["risk"])
                self.assertNotEqual(result["confidence"], "VERIFIED")

    def test_coordination_preserves_supported_leadership_without_code_credit(self):
        for words in ["主导产品规划，协调团队完成插件实现和部署脚本", "主导交付，协调团队设计架构并完成部署", "主导项目并协调团队设计架构并完成部署"]:
            result = audit_claim(leadership_claim(words))
            self.assertNotIn("missing_evidence:authorship", result["risk"])
            self.assertEqual(result["confidence"], "VERIFIED")

    def test_scoped_authorship_receipt_allows_technical_clause(self):
        value = leadership_claim("主导交付，设计系统架构并实现数据模块")
        value["evidence"][0]["supports"].append("authorship")
        self.assertEqual(audit_claim(value)["confidence"], "VERIFIED")

    def test_unknown_personal_claim_is_not_an_accomplishment_assertion(self):
        raw = "现有材料不说明哪些架构由本人设计。"
        packet = {"schema_version": "1", "sources": [{"source_id": "narration", "source_type": "user_report", "text": raw}],
                  "statements": [{"id": "unresolved", "text": "个人架构贡献范围未知", "source_id": "narration", "source_type": "user_report", "source_span": raw, "epistemic": "UNKNOWN", "confidence": "unknown", "kind": "claim", "modality": "unknown"}],
                  "situation": {"mode": "positioning", "summary": "审阅贡献", "goal": "真实表述", "claims": []}}
        result = extract(packet)
        self.assertEqual(result["facts"], [])
        self.assertIn("个人架构贡献范围未知", result["unknowns"])
        packet["statements"][0].update(epistemic="FACT", confidence="direct")
        with self.assertRaises(ContractError):
            extract(packet)

    def test_unresolved_claim_cannot_use_direct_confidence(self):
        raw = "个人实现范围未知"
        packet = {"schema_version": "1", "sources": [{"source_id": "cv", "source_type": "resume", "text": raw}],
                  "statements": [{"id": "u", "text": raw, "source_id": "cv", "source_type": "resume", "source_span": raw, "epistemic": "UNKNOWN", "confidence": "direct", "kind": "claim", "modality": "unknown"}],
                  "situation": {"mode": "positioning", "summary": "审阅", "claims": []}}
        with self.assertRaises(ContractError):
            extract(packet)

    def test_supplied_interview_documents_without_claims_are_not_missing(self):
        value = {"mode": "interview", "summary": "准备第二轮", "goal": "防守项目", "claims": [],
                 "facts": [{"text": "跨职能项目经历", "source": "cv", "source_type": "resume"},
                           {"text": "岗位要求说明技术取舍", "source": "jd", "source_type": "jd"}]}
        result = decide(value, now=datetime(2026, 10, 3, tzinfo=timezone.utc))
        self.assertNotIn("资料尚未给齐", result["recommended_move"])
        self.assertFalse(any("简历 / JD 原文" in u["text"] for u in result["unknowns"]))
        self.assertIn("尚未结构化", result["recommended_move"])
        artifact = artifact_contents(result)["claim-risk-map.md"]
        self.assertNotIn("需要实际简历、JD", artifact)

    def test_only_the_absent_document_is_requested(self):
        value = {"mode": "interview", "summary": "准备面试", "claims": [],
                 "facts": [{"text": "用户已给简历", "source": "cv", "source_type": "resume"}]}
        result = decide(value)
        unknowns = " ".join(u["text"] for u in result["unknowns"])
        self.assertIn("JD 原文", unknowns)
        self.assertNotIn("简历原文", unknowns)
