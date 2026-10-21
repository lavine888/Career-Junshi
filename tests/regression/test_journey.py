"""Synthetic multi-stage journeys. Source exports are real; no hiring outcomes claimed."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.feedback_loop import feedback_next_move
from scripts.install_skill import install
from scripts.journey import review_journey, render_handoff, write_checkpoint
from scripts.models import ContractError
from scripts.resume_export import export_resume
from tests.regression.test_resume_export import sample

NOW = "2026-10-21T16:00:00+08:00"


def journal():
    return {"schema_version": "1", "case_id": "synthetic-J1", "goal": "AI product internship",
            "next_review_at": "2026-10-22T16:00:00+08:00", "events": []}


def event(packet, kind, eid, payload):
    packet["events"].append({"id": eid, "type": kind, "at": "2026-10-21T12:00:00+08:00",
                            "source": "synthetic:user recap", "origin": "synthetic", "payload": payload})


def claim(packet, revision="C1-v1", supersedes="", wording="Participated in a team prototype"):
    event(packet, "claim", revision, {"project_id": "P1", "supersedes": supersedes,
          "claim": {"id": "C1", "claim": wording, "confidence": "SELF_REPORTED", "evidence": [],
                    "ownership": {"scope": "team", "contribution": "Designed a review checklist"},
                    "stage": "demo", "risk": []}})


def ref(revision="C1-v1"):
    return {"project_id": "P1", "claim_id": "C1", "revision_id": revision}


def opportunity(packet, oid="O1"):
    event(packet, "opportunity", "create-" + oid,
          {"opportunity_id": oid, "company": "Synthetic Company", "role": "AI product internship"})


def action(packet, aid="A1", kind="practice", oid="O1"):
    event(packet, "action", aid, {"kind": kind, "description": "Explain the actual evaluation criteria", "opportunity_id": oid})


def exported(packet, base, rid="R1", parent="", revision="C1-v1", layout="standard"):
    data = sample()
    data["layout"] = layout
    data["lineage"] = {"resume_id": rid, "parent_resume_id": parent, "opportunity_id": "O1", "claim_refs": [ref(revision)]}
    report = export_resume(data, base / rid)
    event(packet, "resume", "export-" + rid,
          {"lineage": report["lineage"], "artifacts": report["artifacts"], "checks": report["checks"]})
    return report


class JourneyTests(unittest.TestCase):
    def test_feedback_to_corrected_resume_preserves_submission_and_restarts_from_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); packet = journal(); claim(packet); opportunity(packet)
            first = exported(packet, base)
            event(packet, "submission", "sent", {"opportunity_id": "O1", "resume_id": "R1", "submitted_at": "2026-10-21T11:00:00+08:00"})
            event(packet, "recruiting", "interview", {"opportunity_id": "O1", "status": "interview", "summary": "Synthetic invitation"})
            event(packet, "feedback", "F1", {"opportunity_id": "O1", "category": "skill_gap", "summary": "Asked for actual evaluation criteria", "claim_refs": [ref()]})
            action(packet)
            event(packet, "review", "review", {"feedback_id": "F1", "conclusion": "practice", "reason": "Prepare the observed topic without upgrading the claim", "next_action_id": "A1"})
            event(packet, "execution", "receipt", {"action_id": "A1", "status": "PARTIAL", "summary": "Explained criteria; artifact not checked"})
            claim(packet, "C1-v2", "C1-v1", "Participated in a team prototype; service implemented by teammates")
            exported(packet, base, "R2", "R1", "C1-v2", "editorial")
            event(packet, "material_update", "resent", {"opportunity_id": "O1", "resume_id": "R2", "sent_at": "2026-10-21T11:45:00+08:00", "summary": "User reports sending corrected version through original channel"})
            before = copy.deepcopy(packet)
            result = review_journey(packet, verify_files=True, now=NOW)
            self.assertEqual(packet, before)
            self.assertEqual(result["handoff"]["stale_resume_ids"], ["R1"])
            self.assertEqual(result["state"]["opportunities"][0]["resume_id"], "R1")
            self.assertTrue(result["state"]["opportunities"][0]["submitted_resume_stale"])
            self.assertEqual(result["state"]["opportunities"][0]["latest_resume_id"], "R2")
            self.assertEqual(len(result["state"]["opportunities"]), 1)
            self.assertEqual(len(result["state"]["opportunities"][0]["material_updates"]), 1)
            self.assertEqual(result["state"]["actions"][0]["status"], "PARTIAL")
            self.assertEqual(result["state"]["resumes"][1]["parent_resume_id"], "R1")
            self.assertEqual(result["state"]["claims"][0]["claim"]["confidence"], "SELF_REPORTED")
            self.assertEqual(result["state"]["resumes"][1]["status"], "SOURCE_ONLY")
            output = Path(write_checkpoint(packet, result, base / "checkpoint"))
            restored = review_journey(json.loads((output / "journey.json").read_text(encoding="utf-8")), verify_files=True, now=NOW)
            self.assertEqual(restored, result)
            self.assertIn("R1", (output / "continue.md").read_text(encoding="utf-8"))
            self.assertFalse(result["memory_enabled"])
            self.assertFalse(result["external_actions_executed"])
            self.assertEqual(hashlib.sha256((base / "R1/resume.tex").read_bytes()).hexdigest(), first["artifacts"][0]["sha256"])

    def test_cancelled_role_stops_local_investment_without_changing_claim_or_other_opportunity(self):
        packet = journal(); claim(packet); opportunity(packet); opportunity(packet, "O2")
        event(packet, "recruiting", "cancel", {"opportunity_id": "O1", "status": "freeze", "summary": "Recruiter reports requisition cancelled"})
        event(packet, "feedback", "F1", {"opportunity_id": "O1", "category": "role_cancelled", "summary": "Requisition cancelled", "claim_refs": []})
        action(packet, "verify-other", "pipeline_review", "")
        event(packet, "review", "review", {"feedback_id": "F1", "conclusion": "stop", "reason": "Role status, not evidence of candidate weakness", "next_action_id": "verify-other"})
        result = review_journey(packet, now=NOW)
        self.assertEqual([o["status"] for o in result["state"]["opportunities"]], ["freeze", "planned"])
        self.assertEqual(result["state"]["claims"][0]["revision_id"], "C1-v1")
        self.assertEqual(result["handoff"]["next_actions"][0]["id"], "verify-other")
        self.assertEqual(result["state"]["reviews"][0]["conclusion"], "stop")
        self.assertEqual(result["state"]["actions"][0]["kind"], "pipeline_review")

    def test_proposed_apply_or_done_receipt_does_not_invent_submission(self):
        packet = journal(); opportunity(packet); action(packet, kind="apply")
        event(packet, "execution", "receipt", {"action_id": "A1", "status": "DONE", "summary": "User reports completing application; exact version is not supplied"})
        result = review_journey(packet, now=NOW)
        self.assertEqual(result["state"]["opportunities"][0]["status"], "planned")
        self.assertEqual(result["state"]["actions"][0]["owner"], "human")
        self.assertEqual(result["state"]["actions"][0]["receipts"][0]["origin"], "synthetic")

    def test_file_changes_and_no_implicit_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); packet = journal(); claim(packet); opportunity(packet); exported(packet, base)
            (base / "R1/resume.tex").write_text("modified", encoding="utf-8")
            self.assertEqual(review_journey(packet, now=NOW)["state"]["resumes"][0]["artifacts"][0]["file_check"], "NOT_CHECKED")
            self.assertEqual(review_journey(packet, verify_files=True, now=NOW)["state"]["resumes"][0]["status"], "FILES_CHANGED")

    def test_duplicate_cross_project_future_and_unlinked_records_rejected(self):
        packet = journal(); claim(packet); opportunity(packet)
        bad = []
        p = copy.deepcopy(packet); p["events"].append(copy.deepcopy(p["events"][0])); bad.append(p)
        p = copy.deepcopy(packet); claim(p, "C1-v2", "wrong"); bad.append(p)
        p = copy.deepcopy(packet); p["events"][0]["at"] = "2027-01-01T00:00:00+08:00"; bad.append(p)
        p = copy.deepcopy(packet); event(p, "execution", "receipt", {"action_id": "missing", "status": "DONE", "summary": "not linked"}); bad.append(p)
        p = copy.deepcopy(packet); event(p, "feedback", "F1", {"opportunity_id": "O1", "category": "skill_gap", "summary": "Wrong project", "claim_refs": [{**ref(), "project_id": "OTHER"}]}); bad.append(p)
        for p in bad:
            with self.subTest(p=p), self.assertRaises(ContractError): review_journey(p, now=NOW)

    def test_no_overwrite_public_output_or_mismatched_checkpoint(self):
        packet = journal(); opportunity(packet); result = review_journey(packet, now=NOW)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "checkpoint"; write_checkpoint(packet, result, target)
            with self.assertRaises(ContractError): write_checkpoint(packet, result, target)
            altered = copy.deepcopy(result); altered["handoff"]["goal"] = "tampered"
            with self.assertRaises(ContractError): write_checkpoint(packet, altered, Path(tmp) / "bad")
            self.assertFalse((Path(tmp) / "bad").exists())
            repo = Path(tmp) / "repo"; repo.mkdir(); (repo / ".git").mkdir()
            with self.assertRaises(ContractError): write_checkpoint(packet, result, repo / "out")

    def test_distinct_reported_context_changes_feedback_but_unattributed_cause_does_not(self):
        base = {"hard_outcome": "rejected"}
        gap = feedback_next_move({**base, "feedback_context": {"category": "skill_gap", "text": "Asked about eval", "source": "synthetic:interview recap"}})
        cancelled = feedback_next_move({**base, "feedback_context": {"category": "role_cancelled", "text": "Role cancelled", "source": "synthetic:HR recap"}})
        self.assertNotEqual(gap["recommended_move"], cancelled["recommended_move"])
        self.assertEqual(gap["causal_status"], "UNKNOWN")
        self.assertEqual(feedback_next_move({**base, "guess": "weakness"}), feedback_next_move(base))
        with self.assertRaises(ContractError): feedback_next_move({**base, "feedback_context": {"category": "skill_gap", "text": "guess", "source": ""}})

    def test_installed_cli_checkpoint_continuation_is_explicit_and_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); installed = install(base / "career-junshi")
            packet = journal(); opportunity(packet); source = base / "input.json"
            source.write_text(json.dumps(packet), encoding="utf-8")
            command = [sys.executable, "-B", str(installed / "scripts/junshi.py"), "journey", "--input", str(source), "--now", NOW, "--format", "json"]
            result = subprocess.run(command, cwd=base, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
            self.assertEqual({p.name for p in base.iterdir()}, {"career-junshi", "input.json"})
            out = base / "private-checkpoint"
            result = subprocess.run(command + ["--output-dir", str(out)], cwd=base, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
            restored = json.loads((out / "journey.json").read_text(encoding="utf-8"))
            self.assertEqual(restored, packet)
            self.assertFalse(json.loads(result.stdout)["memory_enabled"])
