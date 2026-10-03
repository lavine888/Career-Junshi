"""Frozen source/property checks, not fresh semantic grading or model execution."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from scripts.context import extract
from scripts.decision import decide
from scripts.actions import validate_actions
from scripts.feedback_loop import decision_record


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run():
    freeze = read(HERE / "SEMANTIC_FREEZE.json")
    integrity = all(hashlib.sha256((HERE / path).read_bytes()).hexdigest() == digest
                    for path, digest in freeze["sha256"].items())
    rows = []
    for case in sorted((HERE / "final").iterdir()):
        original = read(REPO / "benchmark/mock-career-cases" / case.name / "input.json")
        packet = read(case / "extraction-packet.json")
        sources = [{k: s[k] for k in ("source_id", "source_type", "text")} for s in original["materials"]]
        identity = {s["source_id"]: s for s in sources} == {s["source_id"]: s for s in packet["sources"]}
        now = datetime.fromisoformat(original["as_of"])
        d = decide(extract(packet, now=now), now=now)
        validate_actions(d["actions"])
        decision_record(d, source="synthetic:replay", expected_outcome="Observe only; no success causation")
        checks = [identity, len(d["actions"]) <= 3, bool(d["decision_sufficiency"]),
                  all(c["confidence"] != "VERIFIED" for c in d["claims"])]
        if d["mode"] == "job":
            checks += [bool(d["direction"][k]) for k in ("primary", "secondary", "exploratory")]
        elif d["mode"] == "interview":
            checks += [all(s["status"] == "RISK_HYPOTHESIS" for s in d["top_risk_hypotheses"])]
        elif d["mode"] == "offer":
            checks += [bool(d["current_preference"]), d["recommendation_type"] == "CONDITIONAL",
                       1 <= len(d["decision_unknowns"]) <= 3, bool(d["reversal_conditions"])]
        elif d["mode"] == "recruiting":
            checks += [d["application_status"] == "waiting", bool(d["draft"]),
                       (case / "artifacts/follow-up-draft.md").is_file()]
        elif d["mode"] == "positioning":
            p = d["ownership_defense"]
            checks += [p["project_stage"] == "unknown", 3 <= len(p["defense_questions"]) <= 5,
                       all(set(c) == {"claim_id", "claim_stage", "user_contribution_stage"} for c in p["contributions"])]
        for outcome in case.glob("outcome-*.json"):
            o = read(outcome)
            checks += [o["origin"] == "synthetic", o["decision_preserved"],
                       o["temporary_store_deleted"], not o["memory_changed_preparation"],
                       o["feedback"]["causal_status"] == "UNKNOWN"]
        review = read(case / "evaluation.json")
        response = (case / "host-after.md").read_text(encoding="utf-8")
        checks += [all(q in response for q in review["host_exact_quotes"])]
        rows.append({"case_id": case.name, "source_identity": identity, "property_pass": all(checks),
                     "frozen_operator_grade": review["after"]})
    return {"frozen_semantic_integrity": integrity, "cases": rows,
            "regressions": [r["case_id"] for r in rows if not r["property_pass"]],
            "boundary": "Properties and retained quote integrity only; semantic grades are frozen operator judgments, not automatically reassigned."}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["regressions"]) or not result["frozen_semantic_integrity"])
