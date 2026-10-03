"""Read-only frozen evidence verification and deterministic holdout replay.

This tool never grades semantic quality or gives the model access to rubrics.
Use separate fresh contexts for L1 and L3; original generations are retained.
"""
from pathlib import Path
from datetime import datetime
import argparse
import hashlib
import json
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from scripts.context import extract
from scripts.decision import decide
from scripts.actions import validate_actions


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def verify():
    root = REPO / "benchmark/holdout-v023"
    manifest = read(root / "FIRST_PASS_FREEZE.json")
    actual = {str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*")
              if p.is_file() and p.name != "FIRST_PASS_FREEZE.json"}
    expected = set(manifest["files"])
    errors = sorted(actual ^ expected)
    for name, digest in manifest["files"].items():
        path = root / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append(name)
    return {"frozen_integrity": not errors, "files": len(expected), "changed_missing_or_extra": sorted(set(errors)),
            "boundary": "Integrity of retained evidence only; not an automatic semantic PASS."}


def replay(dataset="holdout-v023", phase="first-pass"):
    root = REPO / "benchmark" / dataset
    rows = []
    for case in sorted(root.iterdir()):
        packet_path = case / phase / "extraction-packet.json"
        if not packet_path.is_file():
            continue
        original = read(case / "input/context.json")
        packet = read(packet_path)
        given = {s["source_id"]: {k: s[k] for k in ("source_id", "source_type", "text")} for s in original["materials"]}
        actual = {s["source_id"]: s for s in packet["sources"]}
        identity = all(actual.get(k) == v for k, v in given.items()) and all(
            s["source_type"] == "user_report" and s["text"] == original["request"]
            for k, s in actual.items() if k not in given)
        row = {"case_id": case.name, "source_identity": identity}
        try:
            if not identity:
                raise ValueError("Source identity does not match permitted input")
            now = datetime.fromisoformat(original["as_of"])
            d = decide(extract(packet, now=now), now=now)
            validate_actions(d["actions"])
            row.update(runtime="VALID", mode=d["mode"], recommendation_type=d["recommendation_type"],
                       recommended_move=d["recommended_move"], primary_choice=d.get("primary_choice"),
                       current_preference=d.get("current_preference"), action_count=len(d["actions"]))
        except ValueError as error:
            row.update(runtime="FAILED", error=str(error))
        rows.append(row)
    return {"cases": rows, "runtime_failures": [r["case_id"] for r in rows if r["runtime"] != "VALID"],
            "boundary": "Current runtime on retained packets; never reassigns frozen semantic grades or predicts user outcomes."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["verify", "replay"])
    parser.add_argument("--dataset", choices=["holdout-v023", "holdout-v023-after", "holdout-v023-mutations"], default="holdout-v023")
    args = parser.parse_args()
    result = verify() if args.command == "verify" else replay(args.dataset)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("frozen_integrity", not result.get("runtime_failures")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
