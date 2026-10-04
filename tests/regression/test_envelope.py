"""Truth boundaries and execution contracts, not expected career rankings."""
import copy
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from scripts.envelope import (validate_decision_envelope, review_with_repair, compile_artifacts,
                              memory_handoff, render_envelope)
from scripts.memory_store import MemoryStore
from scripts.models import ContractError


def context(text="Candidate prefers manager quality over salary."):
    return {"materials": [{"source_id": "S1", "source_type": "document", "text": text}]}


def envelope(c, move="Choose the lower-paying team because manager quality is the stated priority."):
    return {"schema_version": "2", "situation": {"summary": "Choose a role", "mode": "job"},
            "facts": [{"id": "F1", "statement": c["materials"][0]["text"], "source_ids": ["S1"],
                       "source_spans": [{"source_id": "S1", "quote": c["materials"][0]["text"]}],
                       "epistemic": "FACT", "confidence": "direct"}],
            "inferences": [], "unknowns": [], "bottleneck": {"type": "Goals", "explanation": "Compare supplied priorities"},
            "recommendation": {"type": "CONDITIONAL", "move": move, "why": ["Use the stated goal"], "basis_ids": ["F1"],
                               "avoided_action": ["Do not choose by salary alone"]},
            "alternatives": [], "actions": [{"description": "Confirm the manager's working expectations", "execution_mode": "human", "priority": 1}],
            "reconsider_if": ["New information changes the manager assessment"],
            "observation_window": "Before the actual offer deadline", "stop_condition": "Stop if a hard constraint fails",
            "claims_used": [], "evidence_used": ["S1"], "extensions": {}}


class EnvelopeTests(unittest.TestCase):
    def test_unusual_preferences_survive_without_rank_algorithm(self):
        for company, months in [("Zephyr", 6), ("Fir", 8)]:
            c = context(f"User prioritizes Quant at {company} and accepts {months} months retraining despite weaker current proof.")
            e = envelope(c, f"Keep Quant primary and invest the accepted {months} months.")
            self.assertEqual(validate_decision_envelope(e, c)["status"], "ACCEPT")
            self.assertIn(e["recommendation"]["move"], compile_artifacts(e, c)["next-actions.md"])
        c = context()
        self.assertEqual(validate_decision_envelope(envelope(c), c)["status"], "ACCEPT")

    def test_five_adversarial_essential_assertions_block(self):
        examples = [
            ("Founder verbally promised equity later; no written agreement.", "Choose this because equity is guaranteed.", "VERBAL_PROMISE_PROMOTED"),
            ("Team conversion increased 35%; several changes launched simultaneously.", "I improved conversion 35%.", "METRIC_ATTRIBUTION"),
            ("No HR response; listing removed.", "You are rejected.", "SILENCE_TO_REJECTION"),
            ("Three interview rejections; only two explicit local technical signals.", "This role is fundamentally unsuitable.", "UNSUPPORTED_PIVOT_CERTAINTY"),
            ("Candidate did not implement the storage subsystem.", "I architected the entire system.", "UNSUPPORTED_AUTHORSHIP")]
        for source, move, code in examples:
            with self.subTest(code=code):
                c = context(source)
                e = envelope(c, move)
                v = validate_decision_envelope(e, c)
                self.assertEqual(v["status"], "BLOCK")
                self.assertIn(code, [x["code"] for x in v["issues"]])
                with self.assertRaises(ContractError):
                    compile_artifacts(e, c)

    def test_negated_boundaries_and_valid_move_are_not_rejected(self):
        c = context("Founder verbally promised equity later; no written agreement.")
        e = envelope(c, "Do not treat equity as guaranteed; verify written equity first.")
        self.assertEqual(validate_decision_envelope(e, c)["status"], "ACCEPT")

    def test_internal_negation_and_clause_scopes_preserve_truth_boundaries(self):
        c = context("Team project; candidate did not implement storage.")
        for prose in ["我没有独立开发存储，系统实现由工程同事负责。",
                      "本人未独立实现全部模块。",
                      "I did not implement the entire system.",
                      "I have not architected the entire system.",
                      "I have not solely implemented the module."]:
            with self.subTest(prose=prose):
                self.assertEqual(validate_decision_envelope(envelope(c, prose), c)["status"], "ACCEPT")
        for prose in ["我不只是参与，而是独立完成全部代码。",
                      "I was not merely coordinating, I alone implemented the system."]:
            with self.subTest(prose=prose):
                self.assertEqual(validate_decision_envelope(envelope(c, prose), c)["status"], "BLOCK")

    def test_artifact_wording_repair_preserves_move(self):
        c = context("Team conversion increased 35%; several changes launched simultaneously.")
        e = envelope(c, "Retain the team result and clearly separate personal contribution.")
        e["situation"]["mode"] = "positioning"
        e["extensions"] = {"ownership": {"content": "I improved conversion 35%."}}
        v = validate_decision_envelope(e, c)
        self.assertEqual(v["status"], "REPAIR_REQUIRED")
        calls = []
        def repair(raw, request):
            calls.append(request)
            raw["extensions"]["ownership"]["content"] = "Team conversion increased 35%; individual causal impact remains unknown."
            return raw
        result = review_with_repair(e, c, repair)
        self.assertEqual(result["status"], "ACCEPT")
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["envelope"]["recommendation"]["move"], e["recommendation"]["move"])
        self.assertEqual(result["attempts"][0]["raw_envelope"], e)
        self.assertNotIn("rubric", str(calls))

    def test_failed_repair_is_bounded_and_retained(self):
        c = context("No HR response.")
        e = envelope(c, "You are rejected.")
        calls = []
        result = review_with_repair(e, c, lambda raw, issues: calls.append(issues) or raw)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(result["attempts"]), 2)
        self.assertIsNone(result["envelope"])
        self.assertEqual(result["status"], "BLOCK")

    def test_sources_and_quotes_cannot_be_forged(self):
        c = context()
        for field, replacement in [("source_ids", ["NO-SOURCE"]), ("source_spans", [{"source_id": "S1", "quote": "invented manager endorsement"}])]:
            e = envelope(c)
            e["facts"][0][field] = replacement
            self.assertEqual(validate_decision_envelope(e, c)["status"], "BLOCK")
        c["materials"].append(copy.deepcopy(c["materials"][0]))
        self.assertEqual(validate_decision_envelope(envelope(c), c)["status"], "REPAIR_REQUIRED")

    def test_epistemic_and_confidence_boundaries(self):
        c = context()
        for conf in ["interpretation", "unknown"]:
            e = envelope(c)
            e["facts"][0]["confidence"] = conf
            self.assertEqual(validate_decision_envelope(e, c)["status"], "BLOCK")
        c["materials"][0]["source_type"] = "resume"
        self.assertEqual(validate_decision_envelope(envelope(c), c)["status"], "REPAIR_REQUIRED")
        e = envelope(c)
        e["facts"][0]["confidence"] = "self_reported"
        self.assertEqual(validate_decision_envelope(e, c)["status"], "ACCEPT")

    def test_factual_metric_cannot_change_behind_a_valid_quote(self):
        for company, observed, invented in [("Juniper", 12, 65), ("Cedar", 41.5, 88.2), ("Hazel", -18, 18)]:
            c = context(f"{company} reports conversion {observed}%.")
            e = envelope(c)
            e["facts"][0]["statement"] = f"{company} reports conversion {invented}%."
            v = validate_decision_envelope(e, c)
            self.assertEqual(v["status"], "BLOCK")
            self.assertIn("UNSUPPORTED_METRIC", [i["code"] for i in v["issues"]])
            e["facts"][0]["statement"] = f"{company} reports conversion {observed}％."
            self.assertEqual(validate_decision_envelope(e, c)["status"], "ACCEPT")

    def test_existing_recruiting_polarity_and_qualifiers_are_preserved(self):
        for source, false_fact in [("You did not pass.", "You passed."),
                                   ("If approved, an offer may be issued.", "An offer was issued."),
                                   ("Someone said the candidate passed.", "The candidate passed.")]:
            c = context(source)
            c["materials"][0]["source_type"] = "hr_chat"
            e = envelope(c)
            e["facts"][0]["statement"] = false_fact
            self.assertEqual(validate_decision_envelope(e, c)["status"], "BLOCK")
            e["facts"][0]["statement"] = source
            self.assertEqual(validate_decision_envelope(e, c)["status"], "ACCEPT")

    def test_optional_labels_do_not_override_valid_judgment(self):
        c = context()
        e = envelope(c)
        e["metadata"] = {"role_family": "surgeon", "fit": "strong"}
        e["facts"][0].update(kind="weird", fit="strong")
        e["extensions"] = {"offer": {"content": "Wrong-mode artifact"}, "direction": {"content": 123}}
        v = validate_decision_envelope(e, c)
        self.assertEqual(v["status"], "ACCEPT")
        self.assertNotIn("metadata", v["envelope"])
        self.assertEqual(list(compile_artifacts(e, c)), ["next-actions.md"])
        self.assertEqual(v["envelope"]["recommendation"]["move"], e["recommendation"]["move"])

    def test_unknowns_do_not_automatically_block_verification(self):
        c = context()
        e = envelope(c)
        e["unknowns"] = [{"id": "U1", "statement": "Manager working hours", "decision_relevance": "blocking"}]
        e["recommendation"].update(type="BLOCKED", move="Do not sign yet; verify hours before the binding decision.", basis_ids=["F1", "U1"])
        self.assertEqual(validate_decision_envelope(e, c)["status"], "ACCEPT")
        e["recommendation"]["type"] = "SUFFICIENT"
        self.assertEqual(validate_decision_envelope(e, c)["status"], "BLOCK")

    def test_action_budget_and_human_ownership(self):
        c = context()
        e = envelope(c)
        e["actions"] *= 4
        self.assertEqual(validate_decision_envelope(e, c)["status"], "REPAIR_REQUIRED")
        for desc in ["发送 HR 消息", "Send recruiter message", "Apply to employer"]:
            e = envelope(c)
            e["actions"][0].update(description=desc, execution_mode="codex")
            self.assertEqual(validate_decision_envelope(e, c)["status"], "BLOCK")
        e["actions"][0]["description"] = "Draft an HR message for user review"
        self.assertEqual(validate_decision_envelope(e, c)["status"], "ACCEPT")
        e["actions"][0]["status"] = "COMPLETED"
        self.assertEqual(validate_decision_envelope(e, c)["status"], "BLOCK")

    def test_reconsideration_and_core_failures_require_host_repair(self):
        c = context()
        e = envelope(c)
        e["reconsider_if"] = []
        self.assertEqual(validate_decision_envelope(e, c)["status"], "REPAIR_REQUIRED")
        e["recommendation"]["type"] = "possibly"
        self.assertEqual(validate_decision_envelope(e, c)["status"], "REPAIR_REQUIRED")

    def test_explicit_deadline_calculation_never_rechooses_move(self):
        c = context("Deadline 2026-10-06T16:00:00+08:00")
        e = envelope(c)
        e["situation"].update(deadline="2026-10-06T16:00:00+08:00", deadline_source_ids=["S1"])
        v = validate_decision_envelope(e, c, now=datetime.fromisoformat("2026-10-04T10:00:00+08:00"))
        self.assertEqual(v["envelope"]["urgency"]["hours_remaining"], 54)
        self.assertEqual(v["envelope"]["recommendation"]["move"], e["recommendation"]["move"])

    def test_artifacts_preserve_host_content_and_existing_files(self):
        c = context()
        e = envelope(c)
        e["extensions"] = {"direction": {"content": "# Deliberate comparison\n\nLower pay fits the user's priority."}}
        with tempfile.TemporaryDirectory() as tmp:
            paths = compile_artifacts(e, c, tmp)
            self.assertTrue(Path(paths[1]).read_text(encoding="utf-8").startswith("# Deliberate comparison"))
            with self.assertRaises(ContractError):
                compile_artifacts(e, c, tmp)
        rendered = render_envelope(validate_decision_envelope(e, c)["envelope"])
        self.assertTrue(rendered.startswith("我的判断：" + e["recommendation"]["move"]))
        self.assertNotIn("ACCEPT", rendered)

    def test_memory_consent_append_only_outcome_and_raw_source_boundary(self):
        c = context()
        e = envelope(c)
        handoff = memory_handoff(e, c)
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp)/"private")
            with self.assertRaises(ContractError):
                store.record_decision("opportunity", handoff)
            self.assertFalse(store.path.exists())
            store.consent(confirmed=True)
            saved = store.record_decision("opportunity", handoff)
            d = store.read(kind="decision", subject="opportunity")[0]
            self.assertEqual(d["data"]["decision"], e["recommendation"]["move"])
            self.assertEqual(d["data"]["decision_trace"]["evidence_used"], ["S1"])
            self.assertNotIn("source_spans", str(d))
            with self.assertRaises(ContractError):
                store._put("decision", "opportunity", handoff, record_id=saved["id"])
            store.record_outcome("opportunity", {"decision_id": saved["id"], "hard_outcome": "unknown", "observed_facts": [], "user_interpretation": "", "agent_interpretation": "", "unknowns": [], "source": "actual-user-recap"})
            self.assertIn("结果的因果原因与策略效果仍未知", store.read(kind="outcome", subject="opportunity")[0]["data"]["unknowns"])
            store.set_state("paused")
            with self.assertRaises(ContractError):
                store.record_decision("opportunity", handoff)

    def test_claim_identity_cannot_escape_audit(self):
        c = context()
        e = envelope(c)
        e["claims_used"] = ["missing"]
        self.assertEqual(validate_decision_envelope(e, c)["status"], "BLOCK")
        e["claims_used"] = []
        e["claim_refs"] = [{"project_id": "P", "claim_id": "missing"}]
        self.assertEqual(validate_decision_envelope(e, c)["status"], "REPAIR_REQUIRED")

    def test_causation_stage_and_sole_boundaries(self):
        examples = [("Team outcome with several changes simultaneously", "I alone built the system.", "TEAM_TO_SOLE"),
                    ("团队同时推出多项变化，无法单独归因", "多项措施共同推动增长。", "UNSUPPORTED_CAUSATION"),
                    ("项目仅是原型 demo", "已经生产上线。", "STAGE_PROMOTED"),
                    ("Only a backtest", "achieved live profit.", "STAGE_PROMOTED")]
        for source, move, code in examples:
            c = context(source)
            v = validate_decision_envelope(envelope(c, move), c)
            self.assertIn(code, [i["code"] for i in v["issues"]])
            self.assertEqual(v["status"], "BLOCK")

    def test_memory_budget_failure_does_not_invalidate_judgment(self):
        c = context()
        e = envelope(c)
        e["recommendation"]["why"] = ["Reason " + "x"*350]*3
        self.assertEqual(validate_decision_envelope(e, c)["status"], "ACCEPT")
        with self.assertRaises(ContractError):
            memory_handoff(e, c)

    def test_optional_prediction_handoff_reuses_existing_calibration(self):
        c = context("Interview includes architecture discussion.")
        e = envelope(c)
        e["predictions"] = [{"topic": "architecture", "expectation": "high_attention", "basis": "S1 explicitly includes architecture"}]
        handoff = memory_handoff(e, c)
        self.assertEqual(handoff["predictions"], e["predictions"])
        with tempfile.TemporaryDirectory() as tmp:
            store = MemoryStore(Path(tmp)/"private")
            store.consent(confirmed=True)
            parent = store.record_decision("opportunity", handoff)
            store.record_outcome("opportunity", {"decision_id": parent["id"], "hard_outcome": "unknown", "observed_facts": [], "user_interpretation": "", "agent_interpretation": "", "unknowns": [], "source": "synthetic-recap", "origin": "synthetic", "observations": [{"topic": "architecture", "attention": "not_asked", "risk_observed": None, "text": "Topic was not asked in this synthetic event", "source": "synthetic-recap"}]})
            outcome = store.read(kind="outcome", subject="opportunity")[0]["data"]
            self.assertIn("NOT_OBSERVED", str(outcome["calibration"]))
            self.assertEqual(outcome["hard_outcome"], "unknown")
        e["predictions"] = [{"topic": "custom unsupported tag"}]
        v = validate_decision_envelope(e, c)
        self.assertEqual(v["status"], "ACCEPT")
        self.assertNotIn("predictions", v["envelope"])

    def test_installed_host_cli_clean_debug_and_failure_paths(self):
        from scripts.install_skill import install
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = install(base / "skills" / "career-junshi")
            c = context()
            e = envelope(c)
            (base/"context.json").write_text(json.dumps(c), encoding="utf-8")
            (base/"envelope.json").write_text(json.dumps(e), encoding="utf-8")
            cmd = [sys.executable, str(target/"scripts/junshi.py"), "host-decide", "--input", str(base/"envelope.json"), "--context", str(base/"context.json")]
            env = {**os.environ, "PYTHONUTF8": "1"}
            run = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env, timeout=20)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(run.stdout.startswith("我的判断："))
            self.assertNotIn("ACCEPT", run.stdout)
            run = subprocess.run(cmd+["--debug-decision"], capture_output=True, text=True, encoding="utf-8", env=env, timeout=20)
            self.assertEqual(json.loads(run.stdout)["status"], "ACCEPT")
            e["recommendation"]["basis_ids"] = ["INVENTED"]
            (base/"envelope.json").write_text(json.dumps(e), encoding="utf-8")
            run = subprocess.run(cmd+["--artifacts-dir", str(base/"blocked-output")], capture_output=True, text=True, encoding="utf-8", env=env, timeout=20)
            self.assertEqual(run.returncode, 2)
            self.assertFalse((base/"blocked-output").exists())


if __name__ == "__main__":
    unittest.main()
