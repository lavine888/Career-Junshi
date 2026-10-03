"""Synthetic fixtures only. real_world flags exercise gates, not real-event evaluation."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.context import extract, freshness
from scripts.decision import decide, render
from scripts.calibration import calibrate, predictions, observations, select_similar
from scripts.feedback_loop import decision_record
from scripts.memory_store import MemoryStore
from scripts.models import ContractError
from scripts.hypothesis import review_hypothesis
from scripts.role_story import map_story, role_packs
from scripts.benchmark import load_cases, run, packet, validate_host_submission, DIMENSIONS

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 10, 3, 12, tzinfo=timezone(timedelta(hours=8)))


def meta(family="ai-product", mode="interview", stage="preparation"):
    return {"mode": mode, "role_family": family, "stage": stage, "situation_type": "claim-defense",
            "risk_tags": ["ownership"], "situation_tags": ["evidence"]}


def claim():
    return {"id": "C1", "claim": "Built an evaluation prototype", "confidence": "SUPPORTED",
            "ownership": {"scope": "team", "contribution": "Designed the evaluation cases"}, "stage": "demo",
            "evidence": [{"source": "fixture://evaluation", "kind": "supporting", "supports": ["claim"], "summary": "Evaluation cases exist"}], "risk": []}


def scenario():
    return {"mode": "interview", "summary": "A team prototype will be discussed tomorrow", "goal": "Defend true contribution",
            "facts": [{"text": "Interview tomorrow", "source": "fixture://calendar", "source_type": "user_report"}],
            "unknowns": ["Actual questions"], "claims": [claim()], "metadata": meta(),
            "predictions": [{"topic": "ownership", "expectation": "risk_visible", "basis": "fixture://contribution"},
                            {"topic": "architecture", "expectation": "high_attention", "basis": "fixture://jd"}]}


def observation(topic="ownership", attention="high", risk=True, source="fixture://recap"):
    return {"topic": topic, "attention": attention, "risk_observed": risk, "text": "Asked to distinguish personal and team decisions", "source": source}


def extracted_packet():
    return {"schema_version": "1", "sources": [{"source_id": "JD1", "source_type": "jd", "text": "Evaluation preferred"}],
            "statements": [{"id": "F1", "text": "Evaluation preferred", "source_id": "JD1", "source_type": "jd",
                            "source_span": "Evaluation preferred", "epistemic": "FACT", "confidence": "direct",
                            "kind": "requirement", "modality": "preferred"}],
            "situation": {"mode": "job", "summary": "Assess fit", "goal": "Choose bounded application"}}


class DecisionIntelligenceTests(unittest.TestCase):
    def test_A_extraction_reaches_decision_without_raw_document(self):
        d = decide(extract(extracted_packet()), now=NOW)
        self.assertEqual(d["facts"][0]["source_id"], "JD1")
        self.assertEqual(d["facts"][0]["source_span"], "Evaluation preferred")
        self.assertNotIn("sources", d)
        self.assertNotIn("sources", decision_record(d, source="fixture://session", expected_outcome="Get fit evidence"))

    def test_B_every_mode_has_counterargument_competing_option_and_reconsider(self):
        for case in load_cases():
            d = decide(case["input"], now=NOW)
            self.assertTrue(d["recommendation"]["strongest_counterargument"])
            self.assertTrue(d["recommendation"]["reconsider_if"])
            self.assertEqual(d["decision_trace"]["chosen"], d["recommended_move"])
            self.assertGreaterEqual(len(d["decision_trace"]["options_considered"]), 2)
            self.assertTrue(d["decision_trace"]["rejected_options"][0]["why"])

    def test_B_silence_has_holiday_and_batch_alternatives(self):
        d = decide({"mode": "recruiting", "summary": "Five calendar days of silence", "recruiting": {"status": "waiting"}}, now=NOW)
        self.assertIn("假期", d["recommendation"]["strongest_counterargument"])
        self.assertIn("批量", d["recommendation"]["strongest_counterargument"])
        self.assertEqual(d["application_status"], "waiting")

    def test_first_screen_recommendation_actions_then_why(self):
        d = decide(scenario(), now=NOW)
        output = render(d)
        self.assertLess(output.index("现在最值得做"), output.index("为什么"))
        self.assertNotIn("decision_trace", output)

    def test_interpretation_cannot_bypass_extraction_into_facts(self):
        s = scenario(); s["facts"][0]["kind"] = "feeling"
        with self.assertRaises(ContractError): decide(s, now=NOW)

    def test_I_stale_market_not_used_as_current_evidence(self):
        s = scenario(); s["mode"] = "job"; s.pop("metadata"); s["job"] = {"fit": "supported"}
        s["facts"][0]["freshness"] = {"category": "market", "observed_at": "2024-01-01T00:00:00Z"}
        d = decide(s, now=NOW)
        self.assertEqual(d["facts"][0]["freshness_assessment"]["status"], "STALE")
        self.assertFalse(any(x.get("source") == "fixture://calendar" for x in d["recommendation"]["supporting_evidence"]))
        self.assertIn("复核", d["recommended_move"])

    def test_I_personal_history_not_invalidated_by_market_age(self):
        s = scenario(); s["facts"][0]["freshness"] = {"category": "personal_history", "observed_at": "2024-01-01T00:00:00Z"}
        d = decide(s, now=NOW)
        self.assertEqual(d["facts"][0]["freshness_assessment"]["status"], "STABLE_HISTORY")
        self.assertTrue(d["recommendation"]["supporting_evidence"])

    def test_I_undated_headcount_and_salary_without_region_need_check(self):
        self.assertEqual(freshness({"category": "headcount"}, now=NOW)["status"], "CHECK_REQUIRED")
        self.assertEqual(freshness({"category": "salary", "observed_at": NOW.isoformat()}, now=NOW)["status"], "CHECK_REQUIRED")


class CalibrationTests(unittest.TestCase):
    def test_E_architecture_high_attention_supported(self):
        p = [{"topic": "architecture", "expectation": "high_attention", "basis": "fixture://jd"}]
        self.assertEqual(calibrate(p, [observation("architecture")])[0]["status"], "SUPPORTED_THIS_CASE")

    def test_F_metric_not_asked_is_not_disproved(self):
        p = [{"topic": "metrics", "expectation": "risk_visible", "basis": "fixture://claim"}]
        self.assertEqual(calibrate(p, [observation("metrics", "not_asked", None)])[0]["status"], "NOT_OBSERVED")

    def test_explicit_contradiction_is_local(self):
        p = [{"topic": "ownership", "expectation": "risk_visible", "basis": "fixture://claim"}]
        d = calibrate(p, [observation(risk=False)])[0]
        self.assertEqual(d["status"], "CONTRADICTED_THIS_CASE")
        self.assertIn("not proof of ability", d["boundary"])

    def test_missing_observation_unassessable(self):
        self.assertEqual(calibrate(scenario()["predictions"], [])[0]["status"], "UNASSESSABLE")

    def test_not_asked_cannot_assert_risk_absent(self):
        with self.assertRaises(ContractError): observations([observation(attention="not_asked", risk=False)])

    def test_predictions_cannot_include_hiring_probability(self):
        with self.assertRaises(ContractError): predictions([{"topic": "ownership", "expectation": "90% pass", "basis": "guess"}])


class SimilarMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.store = MemoryStore(self.tmp.name); self.store.consent(confirmed=True)

    def save_event(self, index, *, family="ai-product", origin="real_world", risk=True, event=None, source=None):
        s = scenario(); s["metadata"] = meta(family)
        d = decide(s)
        subject = f"fixture-interview-{index}"
        saved = self.store.record_decision(subject, decision_record(d, source=f"fixture://decision-{index}", expected_outcome="Contribution could be tested"))
        outcome = {"decision_id": saved["id"], "hard_outcome": "passed", "observed_facts": [],
                   "user_interpretation": "Preparation helped", "agent_interpretation": "Cannot know cause", "unknowns": ["Cause"],
                   "source": source or f"fixture://recap-{index}", "event_id": event or f"fixture-event-{index}", "origin": origin,
                   "observations": [observation(risk=risk, source=f"fixture://recap-{index}")]}
        self.store.record_outcome(subject, outcome)
        return saved, subject

    def current(self):
        return datetime.now(timezone.utc) + timedelta(seconds=2)

    def test_C_three_comparable_outcomes_change_next_defense(self):
        for i in range(3): self.save_event(i, risk=i < 2)
        pairs = self.store.similar(meta(), now=self.current())
        baseline = decide(scenario(), now=self.current())
        d = decide(scenario(), now=self.current(), history=pairs)
        self.assertEqual(d["recurring_risk"]["status"], "RECURRENT_SIGNAL")
        self.assertTrue(d["similar_memory"]["changed"])
        self.assertNotEqual(d["actions"][1]["description"], baseline["actions"][1]["description"])
        self.assertEqual(d["claims"], baseline["claims"])
        self.assertEqual(len(d["similar_memory"]["used"]), 3)
        self.assertIn(d["decision_trace"]["chosen"], d["decision_trace"]["options_considered"])

    def test_D_quant_history_does_not_pollute_ai_product(self):
        for i in range(3): self.save_event(i, family="quant-ai")
        pairs = self.store.similar(meta(), now=self.current())
        self.assertEqual(pairs, [])
        self.assertFalse(decide(scenario(), history=pairs)["similar_memory"]["changed"])

    def test_G_one_or_two_outcomes_do_not_form_recurrent_signal(self):
        for i in range(2):
            self.save_event(i)
            d = decide(scenario(), now=self.current(), history=self.store.similar(meta(), now=self.current()))
            self.assertEqual(d["recurring_risk"]["status"], "INSUFFICIENT_OBSERVATIONS")
            self.assertFalse(d["similar_memory"]["changed"])

    def test_G_synthetic_events_never_count_as_real(self):
        for i in range(3): self.save_event(i, origin="synthetic")
        d = decide(scenario(), now=self.current(), history=self.store.similar(meta(), now=self.current()))
        self.assertEqual(d["recurring_risk"]["comparable_outcomes"], 0)

    def test_G_duplicate_events_and_sources_do_not_create_pattern(self):
        for i in range(3): self.save_event(i, event="same-event", source="fixture://same-recap")
        d = decide(scenario(), now=self.current(), history=self.store.similar(meta(), now=self.current()))
        self.assertEqual(d["recurring_risk"]["comparable_outcomes"], 1)
        for i in range(3, 6): self.save_event(i)
        pairs = self.store.similar(meta(), now=self.current())
        for p in pairs:
            p["outcome"]["data"]["observations"][0]["source"] = "fixture://same-original-observation"
        d = decide(scenario(), now=self.current(), history=pairs)
        self.assertFalse(d["similar_memory"]["changed"])

    def test_recall_at_most_three_and_wrong_stage_ignored(self):
        for i in range(4): self.save_event(i)
        self.assertEqual(len(self.store.similar(meta(), now=self.current())), 3)
        self.assertEqual(self.store.similar(meta(stage="post-interview"), now=self.current()), [])

    def test_recent_and_tags_required(self):
        self.save_event(1)
        pairs = self.store.similar(meta(), now=self.current())
        pairs[0]["decision"]["created_at"] = "2020-01-01T00:00:00Z"
        self.assertEqual(select_similar(meta(), pairs, now=self.current()), [])
        self.assertFalse(decide(scenario(), now=self.current(), history=pairs)["similar_memory"]["changed"])
        m = meta(); m["risk_tags"] = ["salary"]; m["situation_tags"] = []
        self.assertEqual(self.store.similar(m, now=self.current()), [])

    def test_pause_revoke_block_similar_and_corrections(self):
        self.save_event(1)
        for state in ("paused", "revoked"):
            self.store.set_state(state)
            with self.assertRaises(ContractError): self.store.similar(meta())
            with self.assertRaises(ContractError): self.store.correct_claim("fixture-interview-1", "C1", claim(), source="fixture://correction")
        self.assertTrue(self.store.read(administrative=True))

    def test_H_correction_downgrades_current_claim_preserves_history(self):
        saved, subject = self.save_event(1)
        self.store.put("claim", subject, {"summary": "claim", "source": "fixture://resume", "epistemic": "UNKNOWN", "claim": claim()})
        before = self.store.read(kind="decision", subject=subject)[0]
        self.assertTrue(before["data"]["decision_trace"]["reconsider_if"])
        self.assertTrue(before["data"]["strongest_counterargument"])
        replacement = claim(); replacement["confidence"] = "SELF_REPORTED"; replacement["ownership"]["contribution"] = "Only wrote evaluation examples, not architecture"
        corrected = self.store.correct_claim(subject, "C1", replacement, source="fixture://user-correction")
        self.assertIn(saved["id"], corrected["affected_decisions"])
        self.assertEqual(self.store.read(kind="decision", subject=subject)[0], before)
        self.assertEqual(self.store.similar(meta(), now=self.current()), [])
        current = self.store.read(kind="claim", subject=subject)[0]["data"]["claim"]
        self.assertEqual(current["confidence"], "SELF_REPORTED")
        self.assertIn("not architecture", current["ownership"]["contribution"])

    def test_outcome_calibrates_parent_predictions_not_pass_cause(self):
        self.save_event(1)
        data = self.store.read(kind="outcome")[0]["data"]
        self.assertEqual(data["calibration"][0]["status"], "SUPPORTED_THIS_CASE")
        self.assertEqual(data["calibration"][1]["status"], "UNASSESSABLE")
        self.assertIn("不证明", data["learning"])

    def test_H_correction_caps_old_supported_receipt_without_new_verification(self):
        saved, subject = self.save_event(1)
        result = self.store.correct_claim(subject, "C1", claim(), source="fixture://narrated-correction")
        self.assertEqual(result["current_claim"]["confidence"], "SELF_REPORTED")
        self.assertFalse(result["history_rewritten"])

    def test_outcome_cannot_change_parent_role_to_create_comparability(self):
        saved, subject = self.save_event(1, family="quant-ai")
        bad = {"decision_id": saved["id"], "hard_outcome": "passed", "observed_facts": [], "source": "fixture://recap",
               "user_interpretation": "", "agent_interpretation": "", "unknowns": [], "metadata": meta()}
        with self.assertRaises(ContractError): self.store.record_outcome(subject, bad)

    def test_legacy_untagged_history_remains_readable_not_matched(self):
        d = decision_record(decide(scenario()), source="fixture://old", expected_outcome="unknown")
        for key in ("metadata", "predictions", "claim_ids", "decision_trace", "strongest_counterargument"): d.pop(key)
        self.store.record_decision("legacy", d)
        self.assertEqual(len(self.store.read(kind="decision")), 1)
        self.assertEqual(self.store.similar(meta()), [])


def hypothesis(count=1, scope="local"):
    return {"hypothesis": "AI product roles fit current evidence", "supporting_evidence": [],
            "counterevidence": [{"source": f"fixture://feedback-{i}", "event_id": f"event-{i}", "comparison_key": "same-role-stage-budget",
                                 "scope": scope, "gap": "product-judgment", "text": "Explicit scoped gap", "origin": "real_world"} for i in range(count)],
            "review_after": "Next five comparable applications or one week", "alternative": {"hypothesis": "Solutions with existing evidence",
                "expected_value": "higher", "basis": "fixture://alternative-comparison", "constraints_checked": True, "confounders_checked": True}}


class HypothesisAndRoleTests(unittest.TestCase):
    def test_single_rejection_keeps_direction(self):
        self.assertEqual(review_hypothesis(hypothesis())["status"], "KEEP")

    def test_comparable_local_gaps_refine(self):
        self.assertEqual(review_hypothesis(hypothesis(3))["status"], "REFINE")

    def test_pivot_requires_core_counterevidence_and_value_constraints(self):
        h = hypothesis(5, "core")
        self.assertEqual(review_hypothesis(h)["status"], "PIVOT")
        for key, val in (("expected_value", "unknown"), ("basis", ""), ("constraints_checked", False), ("confounders_checked", False)):
            v = copy.deepcopy(h); v["alternative"][key] = val
            self.assertEqual(review_hypothesis(v)["status"], "REFINE")

    def test_duplicate_or_noncomparable_feedback_cannot_pivot(self):
        h = hypothesis(5, "core")
        for e in h["counterevidence"]: e["event_id"] = "same-event"
        self.assertEqual(review_hypothesis(h)["status"], "KEEP")
        h = hypothesis(5, "core")
        for i, e in enumerate(h["counterevidence"]): e["comparison_key"] = f"different-role-{i}"
        self.assertEqual(review_hypothesis(h)["status"], "KEEP")

    def test_synthetic_feedback_does_not_establish_career_pattern(self):
        h = hypothesis(5, "core")
        for e in h["counterevidence"]: e["origin"] = "synthetic"
        self.assertEqual(review_hypothesis(h)["status"], "KEEP")

    def story(self):
        return {"project_id": "P1", "source": "fixture://project", "claim_ids": ["C1"],
                "story": {"tension": "Evaluation unclear", "personal_decision": "Chose evaluation cases", "ownership": "Team; evaluation cases mine",
                          "tradeoff": "Coverage versus cost", "result_evidence": "fixture://evaluation", "learning": "Need failure examples"}}

    def test_J_same_project_different_role_focus_no_new_achievement(self):
        from scripts.models import audit_claim
        audited = [audit_claim(claim())]
        a, b = map_story(self.story(), audited, "ai-product"), map_story(self.story(), audited, "technical-product")
        self.assertNotEqual(a["role_emphasis"], b["role_emphasis"])
        self.assertEqual(a["claim_wording"], b["claim_wording"])
        self.assertEqual(a["evidence"], b["evidence"])
        self.assertEqual(len(role_packs()), 5)

    def test_team_only_material_not_a_strong_personal_story(self):
        from scripts.models import audit_claim
        c = claim(); c["ownership"]["contribution"] = ""
        story = self.story(); story["story"]["personal_decision"] = ""
        m = map_story(story, [audit_claim(c)], "ai-product")
        self.assertEqual(m["story_quality"], "NEEDS_EVIDENCE_OR_PERSONAL_DECISION")
        self.assertIn("personal_decision", m["gaps"])

    def test_story_cannot_invent_new_result_evidence(self):
        from scripts.models import audit_claim
        story = self.story(); story["story"]["result_evidence"] = "invented 40% improvement"
        with self.assertRaises(ContractError): map_story(story, [audit_claim(claim())], "ai-product")


class BenchmarkAndCliTests(unittest.TestCase):
    def test_fixed_benchmark_is_reproducible_and_does_not_claim_model_eval(self):
        cases = load_cases(); a, b = run(cases, now=NOW), run(cases, now=NOW)
        self.assertEqual(a, b)
        self.assertEqual(len(cases), 13)
        self.assertEqual(a["regressions"], [])
        self.assertEqual(a["levels"]["3"]["status"], "NOT_RUN")

    def test_host_packet_blinds_inputs_from_rubric(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "packet"; packet(load_cases(), output)
            content = (output / "host-inputs.json").read_text(encoding="utf-8")
            self.assertNotIn("bad_recommendations", content)
            self.assertNotIn("acceptable_recommendations", content)
            with self.assertRaises(ContractError): packet(load_cases(), output)

    def test_host_evaluation_requires_actual_response_excerpt(self):
        cases = load_cases()
        submission = {"run_id": "fixture-only", "model": "not-an-execution", "settings": "test", "evaluated_at": NOW.isoformat(),
                      "reviewer": "synthetic-validator-fixture", "results": [{"case_id": cases[0]["case_id"], "response": "Wait for real evidence",
                      "dimensions": {d: {"rating": "PASS", "response_span": "not in response", "diagnostic": "fixture", "source_reference": "fixture"} for d in DIMENSIONS}}]}
        with self.assertRaises(ContractError): validate_host_submission(submission, cases)

    def test_installed_runtime_role_and_extraction_paths_work(self):
        from scripts.install_skill import install
        with tempfile.TemporaryDirectory() as tmp:
            target = install(Path(tmp) / "career-junshi")
            inp = Path(tmp) / "packet.json"; inp.write_text(json.dumps(extracted_packet()), encoding="utf-8")
            result = subprocess.run([sys.executable, str(target / "scripts/junshi.py"), "decide", "--extraction", str(inp), "--format", "json"], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["facts"][0]["source_id"], "JD1")
            self.assertTrue((target / "references/role-packs.json").exists())

    def test_cli_similar_does_not_implicitly_initialize_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp = Path(tmp) / "situation.json"; inp.write_text(json.dumps(scenario()), encoding="utf-8")
            directory = Path(tmp) / "absent-memory"
            result = subprocess.run([sys.executable, str(ROOT / "scripts/junshi.py"), "decide", "--input", str(inp), "--use-similar", "--memory-directory", str(directory)], capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(directory.exists())


if __name__ == "__main__":
    unittest.main()
