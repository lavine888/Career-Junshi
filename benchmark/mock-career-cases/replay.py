"""Replay frozen model extractions; semantic review stays a separate artifact."""
from __future__ import annotations
import json
import sys
from datetime import datetime
from pathlib import Path

DATASET = Path(__file__).resolve().parent
sys.path.insert(0, str(DATASET.parents[1]))
from scripts.actions import validate_actions
from scripts.benchmark import property_check
from scripts.context import extract
from scripts.decision import decide


def run_case(golden: dict) -> dict:
    case = DATASET / golden["case_id"]
    inp = json.loads((case / "input.json").read_text(encoding="utf-8"))
    packet = json.loads((DATASET / "debug-results/final" / case.name / "extraction-packet.json").read_text(encoding="utf-8"))
    expected = [{k: source[k] for k in ("source_id", "source_type", "text")} for source in inp["materials"]]
    source_identity = {s["source_id"]: s for s in expected} == {s["source_id"]: s for s in packet["sources"]}
    if not source_identity:
        raise ValueError("Frozen extraction changed original sources")
    now = datetime.fromisoformat(inp["as_of"])
    situation = extract(packet, now=now)
    decision = decide(situation, now=now)
    validate_actions(decision["actions"])
    checks = [property_check(decision, rule) for rule in golden["decision_properties"]]
    checks += [len(decision["references"]) <= 3,
               all(c["confidence"] != "VERIFIED" for c in decision["claims"]),
               all(a["status"] == "PROPOSED" for a in decision["actions"])]
    for rule in golden.get("extraction_properties", []):
        checks.append(property_check(situation, rule))
    return {"case_id": case.name, "source_identity": source_identity, "property_pass": all(checks),
            "checks": checks, "semantic_scope": "No automatic semantic PASS; read evaluation.json and report."}


def run() -> dict:
    goldens = json.loads((DATASET / "golden-properties.json").read_text(encoding="utf-8"))
    cases = [run_case(golden) for golden in goldens]
    return {"cases": cases, "regressions": [c["case_id"] for c in cases if not c["property_pass"]],
            "boundary": "Frozen extraction integrity/properties, not a fresh host/model evaluation or hiring outcome."}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result["regressions"]))
