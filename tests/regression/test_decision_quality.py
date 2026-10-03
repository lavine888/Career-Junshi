"""Semantic output properties, independent of company names and exact prose."""
import unittest
from scripts.actions import artifact_contents, validate_actions
from scripts.context import extract
from scripts.decision import decide
from scripts.models import ContractError
from tests.regression.test_decision import NOW, situation


def candidate(name, family, strength="high", cost="low"):
    return {"name": name, "role_family": family, "source_ids": ["synthetic:user"],
            "assessment": {k: strength for k in ["evidence_strength", "defensibility", "continuity", "role_relevance", "goal_fit", "optionality", "market_testability"]} | {"gap_cost": cost},
            "strongest_proof": "Reported repeated deliverables with personal decisions", "largest_gap": "Independent result receipts",
            "resume_case": "Preserves existing decisions and delivery evidence", "market_test": "Compare actual current duties", "constraint_status": "unknown"}


def direction(candidates):
    return situation("job", direction={"candidates": candidates})


def qualitative_offer():
    return {"weights": {}, "constraints": [], "priorities": {"learning": "high", "ownership": "high", "brand": "medium"},
            "source_ids": ["synthetic:user"], "options": [
                {"name": "Cedar", "constraint_status": "unknown", "ratings": {"learning": 3, "ownership": 2, "brand": 5}},
                {"name": "Willow", "constraint_status": "unknown", "ratings": {"learning": 4, "ownership": 4, "brand": 2}}],
            "critical_unknowns": [{"unknown": f"condition-{i}", "option": "Willow", "priority": "decisive" if i < 3 else "confidence_only", "why_it_matters": "Could change duties or downside", "how_to_verify": "Obtain a scoped written answer", "reversal_condition": "Below user's stated acceptable boundary", "source_ids": ["synthetic:user"]} for i in range(5)]}


class DecisionQualityTests(unittest.TestCase):
    def test_long_offer_checks_keep_complete_methods_without_overflow(self):
        offer = qualitative_offer()
        for u in offer["critical_unknowns"]:
            u["unknown"] = "condition " + "x" * 390
            u["how_to_verify"] = "method " + "y" * 390
        d = decide(situation("offer", offer=offer))
        validate_actions(d["actions"])
        self.assertLessEqual(len(d["actions"][1]["description"]), 1000)
        self.assertIn(offer["critical_unknowns"][0]["how_to_verify"], artifact_contents(d)["offer-comparison.md"])

    def test_offer_artifact_prioritizes_reversal_unknowns(self):
        d = decide(situation("offer", offer=qualitative_offer()))
        artifact = artifact_contents(d)["offer-comparison.md"]
        self.assertIn("condition-0", artifact)
        self.assertIn("condition-2", artifact)
        self.assertNotIn("condition-4", artifact)
        self.assertIn(d["decision_unknowns"][0]["how_to_verify"], artifact)
        self.assertIn(d["decision_unknowns"][0]["reversal_condition"], artifact)

    def test_direction_has_hierarchy_and_cuts_weak_costly_option(self):
        d = decide(direction([candidate("North", "ai-product"), candidate("East", "technical-product", "medium"), candidate("West", "quant-ai", "low", "high")]), now=NOW)
        self.assertEqual(d["direction"]["primary"], ["North"])
        self.assertEqual(d["direction"]["secondary"], ["East"])
        self.assertNotIn("West", d["direction"]["primary"])
        self.assertTrue(d["direction"]["exploratory"] or d["direction"]["deprioritized"])
        self.assertNotEqual(d["recommendation_type"], "BLOCKED")

    def test_direction_renaming_reordering_and_evidence_reversal(self):
        a = candidate("Path-1", "ai-product", "medium")
        b = candidate("Path-2", "quant-ai")
        for values in [[a, b], [b, a]]:
            self.assertEqual(decide(direction(values))["direction"]["primary"], ["Path-2"])
        a = candidate("Renamed", "technical-product")
        b = candidate("Other", "quant-ai", "low", "high")
        self.assertEqual(decide(direction([b, a]))["direction"]["primary"], ["Renamed"])

    def test_unknown_assessments_do_not_make_an_arbitrary_direction(self):
        a = candidate("One", "ai-product", "unknown", "unknown")
        b = candidate("Two", "quant-ai", "unknown", "unknown")
        d = decide(direction([a, b]))
        self.assertEqual(d["recommendation_type"], "BLOCKED")
        self.assertFalse(d["direction"]["primary"])

    def test_failed_constraint_cannot_be_primary(self):
        a = candidate("Unavailable", "ai-product")
        a["constraint_status"] = "fail"
        d = decide(direction([a, candidate("Available", "quant-ai", "medium")]))
        self.assertEqual(d["direction"]["primary"], ["Available"])

    def test_direction_rejects_unbound_source_or_fake_quality_score(self):
        for change in ["unbound", "numeric"]:
            a = candidate("One", "ai-product")
            if change == "unbound": a["source_ids"] = ["not-in-session"]
            else: a["assessment"]["evidence_strength"] = 87
            with self.assertRaises(ContractError): decide(direction([a]))

    def test_offer_can_prefer_conditionally_without_numeric_weights(self):
        d = decide(situation("offer", offer=qualitative_offer()))
        self.assertEqual(d["current_preference"], "Willow")
        self.assertEqual(d["recommendation_type"], "CONDITIONAL")
        self.assertTrue(d["reversal_conditions"])
        self.assertTrue(1 <= len(d["decision_unknowns"]) <= 3)
        self.assertTrue(all(s["score"] is None for s in d["comparison"]))

    def test_offer_ratings_reversal_changes_preference(self):
        offer = qualitative_offer()
        offer["options"][0]["ratings"], offer["options"][1]["ratings"] = offer["options"][1]["ratings"], offer["options"][0]["ratings"]
        self.assertEqual(decide(situation("offer", offer=offer))["current_preference"], "Cedar")

    def test_offer_failed_constraint_overrides_conditional_upside(self):
        offer = qualitative_offer()
        offer["options"][1]["constraint_status"] = "fail"
        d = decide(situation("offer", offer=offer))
        self.assertNotEqual(d["current_preference"], "Willow")

    def test_offer_unknown_goals_remain_blocking(self):
        d = decide(situation("offer", goal="", offer=qualitative_offer()))
        self.assertEqual(d["recommendation_type"], "BLOCKED")
        self.assertIsNone(d["current_preference"])

    def test_urgent_interview_actions_are_compressed_risk_hypotheses(self):
        value = situation(deadline="2026-10-04T20:00:00+08:00", interview={"available_hours": 5, "signals": [{"topic": "architecture", "basis": "Prior round probed architecture", "source_ids": ["synthetic:user"], "kind": "observed_signal"}]})
        d = decide(value, now=NOW)
        self.assertTrue(1 <= len(d["actions"]) <= 3)
        self.assertEqual(d["recommendation_type"], "SUFFICIENT")
        self.assertEqual(d["top_risk_hypotheses"][0]["status"], "RISK_HYPOTHESIS")
        self.assertEqual(d["top_risk_hypotheses"][0]["signal_kind"], "observed_signal")

    def test_follow_up_has_timing_message_window_stop(self):
        r = {"working_days": 4, "communication": {"stage": "final", "tone": "neutral", "last_event": "last Tuesday's final interview", "source_ids": ["synthetic:user"]}}
        d = decide(situation("recruiting", recruiting=r))
        self.assertEqual(d["follow_up"]["action"], "send_now")
        self.assertIn("last Tuesday", d["draft"])
        self.assertIn("follow-up-draft.md", artifact_contents(d))
        self.assertTrue(d["follow_up"]["window"] and d["stop_condition"])
        validate_actions(d["actions"])
        self.assertEqual(d["application_status"], "waiting")

    def test_unknown_calendar_prepares_draft_but_does_not_invent_send_time(self):
        r = {"working_days": None, "communication": {"stage": "final", "tone": "formal", "last_event": "the final interview", "source_ids": ["synthetic:user"]}}
        d = decide(situation("recruiting", recruiting=r))
        self.assertEqual(d["follow_up"]["action"], "wait")
        self.assertTrue(d["draft"])
        self.assertIn("follow-up-draft.md", artifact_contents(d))

    def test_no_contact_still_suppresses_draft(self):
        r = {"no_contact": True, "communication": {"stage": "final", "tone": "neutral", "last_event": "final", "source_ids": ["synthetic:user"]}}
        d = decide(situation("recruiting", recruiting=r))
        self.assertEqual(d["follow_up"]["action"], "do_not_contact")
        self.assertIsNone(d["draft"])

    def test_ownership_defense_preserves_contribution_and_three_stages(self):
        value = situation("positioning")
        value["claims"][0]["ownership"]["contribution"] = "产品负责人，负责需求取舍与团队验收"
        cid = value["claims"][0]["id"]
        value["ownership"] = {"project_stage": "unknown", "contributions": [{"claim_id": cid, "claim_stage": "completed", "user_contribution_stage": "unknown"}]}
        d = decide(value)
        pack = d["ownership_defense"]
        self.assertIn("产品负责人", pack["safe_claim"])
        self.assertTrue(3 <= len(pack["defense_questions"]) <= 5)
        self.assertEqual(pack["project_stage"], "unknown")
        self.assertEqual(pack["contributions"][0]["claim_stage"], "completed")
        self.assertEqual(pack["contributions"][0]["user_contribution_stage"], "unknown")
        self.assertIn("ownership-defense.md", artifact_contents(d))

    def test_ownership_can_rewrite_now_without_new_receipts(self):
        d = decide(situation("positioning"))
        self.assertEqual(d["recommendation_type"], "CONDITIONAL")
        self.assertTrue(d["ownership_defense"]["safe_claim"])
        self.assertNotEqual(d["claims"][0]["confidence"], "VERIFIED")

    def test_explicit_history_stays_self_reported_fact_not_verified(self):
        raw = "我参加过研究比赛，排名尚未提供。"
        p = {"schema_version": "1", "sources": [{"source_id": "U", "source_type": "user_report", "text": raw}], "statements": [{"id": "F", "text": "用户自述参加过研究比赛", "source_id": "U", "source_type": "user_report", "source_span": "我参加过研究比赛", "epistemic": "FACT", "confidence": "self_reported", "kind": "claim", "modality": "observed"}, {"id": "X", "text": "排名未知", "source_id": "U", "source_type": "user_report", "source_span": "排名尚未提供", "epistemic": "UNKNOWN", "confidence": "unknown", "kind": "observation", "modality": "unknown"}], "situation": {"mode": "job", "summary": "决定投递方向", "claims": []}}
        n = extract(p)
        self.assertEqual(n["facts"][0]["confidence"], "self_reported")
        self.assertIn("排名未知", n["unknowns"])

    def test_bounded_new_decisions_can_enter_feedback_memory(self):
        from scripts.feedback_loop import decision_record
        from scripts.intelligence import memory_trace
        large = situation("positioning")
        large["claims"][0]["ownership"]["contribution"] = "x" * 390 + " not sole"
        interview = situation(interview={"signals": [{"topic": t, "basis": "b" * 160, "source_ids": ["synthetic:user"], "kind": "observed_signal"} for t in ["architecture", "ownership", "evaluation"]]})
        for value in [large, interview, direction([candidate(str(i) * 45, "ai-product") for i in range(6)])]:
            d = decide(value)
            record = decision_record(d, source="synthetic:bounded", expected_outcome="Observe, no causal claim")
            self.assertTrue(memory_trace(record["decision_trace"]))
        d = decide(large)
        self.assertIn("not sole", d["ownership_defense"]["reported_contributions"][0])
        self.assertIn("not sole", artifact_contents(d)["ownership-defense.md"])
