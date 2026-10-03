"""Synthetic regression inputs; no observed recruiting outcomes."""
import copy
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from scripts.context import extract
from scripts.calibration import select_similar, recurrent_signal
from scripts.decision import decide
from scripts.feedback_loop import decision_record
from scripts.memory_store import MemoryStore
from scripts.models import ContractError
from tests.extraction.test_contract import packet
from tests.v02.test_intelligence import meta, scenario, claim


class RecruitingPolarityTests(unittest.TestCase):
    def signal(self, original, assertion, **kwargs):
        return packet(original, text=assertion, source_type="hr_chat", kind="recruiting_signal", modality="observed", **kwargs)

    def test_denial_cannot_become_pass(self):
        for original in ("本轮未通过", "没有通过本轮", "You did not pass", "You have not been hired"):
            with self.subTest(original=original), self.assertRaises(ContractError):
                extract(self.signal(original, "Candidate passed"))
        for original, assertion in (("No offer has been issued", "Offer received"), ("没有收到offer", "已拿到offer"), ("Not rejected", "Rejected")):
            with self.subTest(original=original), self.assertRaises(ContractError):
                extract(self.signal(original, assertion))

    def test_pending_cannot_become_pass(self):
        for original in ("尚未通过", "如果审批通过，才会录用", "You might have passed", "If approved, an offer would follow"):
            with self.subTest(original=original), self.assertRaises(ContractError):
                extract(self.signal(original, "Candidate passed" if "offer" not in original else "Offer received"))
        p = self.signal("如果审批通过才会录用", "如果审批通过才会录用")
        p["situation"].update(mode="recruiting", recruiting={"status":"passed"})
        with self.assertRaises(ContractError): extract(p)

    def test_hearsay_cannot_become_direct_result(self):
        for original in ("听说候选人通过了", "Reportedly the candidate passed"):
            with self.subTest(original=original), self.assertRaises(ContractError):
                extract(self.signal(original, "Candidate passed"))

    def test_qualified_source_report_can_be_preserved(self):
        for original in ("本轮未通过", "如果审批通过才会录用", "Reportedly the candidate passed", "本轮通过了"):
            with self.subTest(original=original):
                self.assertEqual(extract(self.signal(original, original))["facts"][0]["text"], original)
        p = self.signal("本轮通过了", "本轮通过了")
        p["situation"].update(mode="recruiting", recruiting={"status":"passed"})
        self.assertEqual(extract(p)["recruiting"]["status"], "passed")

    def test_explicit_pass_cannot_become_rejected(self):
        with self.assertRaises(ContractError): extract(self.signal("本轮通过了", "本轮未通过"))

    def test_conflicting_sources_require_unknown_scope(self):
        p = self.signal("本轮通过了", "本轮通过了")
        q = self.signal("本轮未通过", "本轮未通过")
        q["sources"][0]["source_id"] = "HR2"
        q["statements"][0].update(id="F2", source_id="HR2")
        p["sources"] += q["sources"]; p["statements"] += q["statements"]
        with self.assertRaises(ContractError): extract(p)
        for s in p["statements"]: s["epistemic"] = "UNKNOWN"
        result = extract(p)
        self.assertEqual(result["facts"], [])
        self.assertEqual(len(result["unknowns"]), 2)


class IndependentHistoryTests(unittest.TestCase):
    def pairs(self, events, *, origins=None):
        now = datetime.now(timezone.utc)
        pairs = []
        for i, event in enumerate(events):
            pairs.append({"decision": {"id": str(i), "created_at": (now-timedelta(minutes=i+1)).isoformat(), "data": {"metadata": meta()}},
                          "outcome": {"id": "O"+str(i), "data": {"event_id": event, "source": "fixture://recap-"+event,
                           "origin": origins[i] if origins else "real_world", "observations": [{"topic": "ownership", "attention": "high",
                            "risk_observed": True, "text": "Synthetic contribution gap", "source": "fixture://recap-"+event}]}}})
        return now, pairs

    def test_duplicate_does_not_crowd_third_independent_event_out(self):
        now, pairs = self.pairs(["A", "A", "B", "C"])
        selected = select_similar(meta(), pairs, now=now)
        self.assertEqual([p["outcome"]["data"]["event_id"] for p in selected], ["A", "B", "C"])
        self.assertEqual(recurrent_signal(selected)["status"], "RECURRENT_SIGNAL")

    def test_same_source_with_different_event_aliases_deduplicated(self):
        now, pairs = self.pairs(["A", "A-copy", "B", "C"])
        pairs[1]["outcome"]["data"]["source"] = pairs[0]["outcome"]["data"]["source"]
        self.assertEqual(len(select_similar(meta(), pairs, now=now)), 3)
        self.assertEqual(recurrent_signal(select_similar(meta(), pairs, now=now))["comparable_outcomes"], 3)

    def test_newer_synthetic_record_does_not_crowd_real_events_out(self):
        now, pairs = self.pairs(["S", "A", "B", "C"], origins=["synthetic", "real_world", "real_world", "real_world"])
        selected = select_similar(meta(), pairs, now=now)
        self.assertTrue(all(p["outcome"]["data"]["origin"] == "real_world" for p in selected))
        self.assertEqual(recurrent_signal(selected)["status"], "RECURRENT_SIGNAL")

    def test_wrong_role_or_old_event_cannot_backfill_independence(self):
        now, pairs = self.pairs(["A", "A", "B", "C", "D"])
        pairs[3]["decision"]["data"]["metadata"] = meta("quant-ai")
        pairs[4]["decision"]["created_at"] = (now-timedelta(days=181)).isoformat()
        self.assertEqual(recurrent_signal(select_similar(meta(), pairs, now=now))["comparable_outcomes"], 2)


class CrossOpportunityCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.store = MemoryStore(self.tmp.name); self.store.consent(confirmed=True)

    def store_claim(self, project):
        self.store.put("claim", project, {"summary": "synthetic claim", "source": "fixture://claim", "epistemic": "UNKNOWN", "claim": claim()})

    def decision(self, opportunity, project=None):
        s = scenario()
        if project: s["claim_refs"] = [{"project_id": project, "claim_id": "C1"}]
        return self.store.record_decision(opportunity, decision_record(decide(s), source="fixture://decision", expected_outcome="Observe real contribution questions"))

    def outcome(self, opportunity, decision):
        self.store.record_outcome(opportunity, {"decision_id": decision["id"], "hard_outcome": "waiting", "observed_facts": [],
            "source": "fixture://"+opportunity, "user_interpretation": "", "agent_interpretation": "", "unknowns": ["Result"],
            "origin": "real_world", "event_id": "fixture-"+opportunity, "observations": []})

    def test_unique_legacy_claim_tracks_cross_opportunity_decision(self):
        self.store_claim("project-A")
        d = self.decision("interview-X")
        before = self.store.read(kind="decision")[0]
        result = self.store.correct_claim("project-A", "C1", claim(), source="fixture://correction")
        self.assertIn(d["id"], result["affected_decisions"])
        self.assertEqual(self.store.read(kind="decision")[0], before)

    def test_scoped_reference_affects_only_its_project_across_opportunities(self):
        self.store_claim("project-A"); self.store_claim("project-B")
        a, b = self.decision("interview-X", "project-A"), self.decision("interview-Y", "project-B")
        self.outcome("interview-X", a); self.outcome("interview-Y", b)
        result = self.store.correct_claim("project-A", "C1", claim(), source="fixture://correction")
        self.assertIn(a["id"], result["affected_decisions"])
        self.assertNotIn(b["id"], result["affected_decisions"] + result["unresolved_decisions"])
        current_b = self.store.read(kind="claim", subject="project-B")[0]["data"]["claim"]
        self.assertEqual(current_b["confidence"], "SUPPORTED")
        pairs = self.store.similar(meta(), now=datetime.now(timezone.utc)+timedelta(seconds=2))
        self.assertEqual([p["decision"]["id"] for p in pairs], [b["id"]])

    def test_ambiguous_legacy_reference_flagged_for_review(self):
        self.store_claim("project-A"); self.store_claim("project-B")
        d = self.decision("interview-X")
        self.outcome("interview-X", d)
        result = self.store.correct_claim("project-A", "C1", claim(), source="fixture://correction")
        self.assertEqual(result["affected_decisions"], [])
        self.assertIn(d["id"], result["unresolved_decisions"])
        self.assertEqual(self.store.similar(meta(), now=datetime.now(timezone.utc)+timedelta(seconds=2)), [])

    def test_invalid_or_ambiguous_claim_reference_rejected(self):
        s = scenario(); s["claim_refs"] = [{"project_id": "P1", "claim_id": "missing"}]
        with self.assertRaises(ContractError): decide(s)
        s["claim_refs"] = [{"project_id": "P1", "claim_id": "C1"}, {"project_id": "P2", "claim_id": "C1"}]
        with self.assertRaises(ContractError): decide(s)

    def test_unconsented_cross_correction_stays_blocked(self):
        self.store_claim("project-A"); self.decision("interview-X", "project-A")
        self.store.set_state("paused")
        with self.assertRaises(ContractError): self.store.correct_claim("project-A", "C1", claim(), source="fixture://correction")
