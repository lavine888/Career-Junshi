import copy
import unittest
from datetime import datetime, timezone

from scripts.context import extract, freshness
from scripts.models import ContractError


def packet(raw="LLM evaluation experience preferred", **fields):
    s = {"id": "F1", "text": "LLM evaluation preferred", "source_id": "JD1", "source_type": "jd",
         "source_span": raw, "epistemic": "FACT", "confidence": "direct", "kind": "requirement", "modality": "preferred"}
    s.update(fields)
    return {"schema_version": "1", "sources": [{"source_id": s["source_id"], "source_type": s["source_type"], "text": raw}],
            "statements": [s], "situation": {"mode": "job", "summary": "synthetic raw context", "goal": "choose next move", "claims": []}}


class ExtractionContractTests(unittest.TestCase):
    def test_resume_jd_provenance_not_truth_upgrade(self):
        p = packet("Led development of AI education platform", source_id="CV1", source_type="resume", kind="claim", confidence="self_reported", modality="observed")
        p["sources"].append({"source_id": "PROJECT1", "source_type": "project_readme", "text": "Built by a team of four"})
        p["statements"].append({"id": "F2", "text": "Team of four", "source_id": "PROJECT1", "source_type": "project_readme", "source_span": "Built by a team of four", "epistemic": "FACT", "confidence": "direct", "kind": "observation", "modality": "observed"})
        out = extract(p)
        self.assertEqual(out["facts"][0]["confidence"], "self_reported")
        self.assertTrue(all(s["source_id"] and s["source_span"] for s in out["facts"]))
        p["statements"][0]["text"] = "Sole ownership of all code"
        with self.assertRaises(ContractError): extract(p)

    def test_preferred_not_required(self):
        self.assertEqual(extract(packet())["facts"][0]["modality"], "preferred")
        with self.assertRaises(ContractError): extract(packet(modality="required"))

    def test_hr_process_update_not_pass(self):
        p = packet("我们还在推进，后面有消息联系你。", source_type="hr_chat", kind="recruiting_signal", modality="observed", text="candidate passed")
        with self.assertRaises(ContractError): extract(p)
        p["statements"][0]["text"] = "流程仍在推进，结果未知"
        self.assertEqual(len(extract(p)["facts"]), 1)

    def test_feeling_is_interpretation(self):
        p = packet("我感觉面试官不喜欢我", source_type="user_report", kind="feeling", confidence="interpretation", text="我感觉不被喜欢", modality="observed")
        with self.assertRaises(ContractError): extract(p)
        p["statements"][0]["epistemic"] = "INFERENCE"
        self.assertEqual(len(extract(p)["inferences"]), 1)
        self.assertEqual(extract(p)["facts"], [])

    def test_missing_or_forged_span_rejected(self):
        for span in ("", "unseen source"):
            with self.assertRaises(ContractError): extract(packet(source_span=span))
        p = packet(); p["statements"][0]["source_type"] = "resume"
        with self.assertRaises(ContractError): extract(p)

    def test_unicode_locator_and_no_raw_sources_in_result(self):
        p = packet("优先评测经验", source_span="", source_locator="chars:0-6")
        result = extract(p)
        self.assertEqual(result["facts"][0]["source_span"], "优先评测经验")
        self.assertNotIn("sources", result)

    def test_stale_market_current_history_and_salary_region(self):
        now = datetime(2026, 10, 3, 12, tzinfo=timezone.utc)
        f = {"category": "market", "observed_at": "2025-01-01T12:00:00Z"}
        self.assertEqual(freshness(f, now=now)["status"], "STALE")
        self.assertEqual(freshness({**f, "category": "personal_history"}, now=now)["status"], "STABLE_HISTORY")
        self.assertEqual(freshness({"category": "headcount"}, now=now)["status"], "CHECK_REQUIRED")
        self.assertEqual(freshness({"category": "salary", "observed_at": now.isoformat()}, now=now)["status"], "CHECK_REQUIRED")
