#!/usr/bin/env python3
"""Repeatable structured checks and blinded host packets; never grades wisdom locally."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.actions import validate_actions
from scripts.decision import decide
from scripts.models import ContractError, choices, items, obj, text, timestamp

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = ["Situation Understanding", "Evidence Discipline", "Bottleneck Identification", "Recommendation Clarity",
              "Actionability", "Opportunity Cost Awareness", "Uncertainty Calibration", "Stop / Pivot Quality",
              "Personal Context Usage", "Outcome Learnability"]
FIELDS = {"case_id", "origin", "situation", "available_context", "must_notice", "must_not_assume", "important_tradeoffs",
          "acceptable_recommendations", "bad_recommendations", "required_actions", "required_stop_condition", "evaluation_dimensions",
          "input", "decision_properties"}


def load_cases(path: Path | None = None) -> list:
    cases = json.loads((path or ROOT / "benchmark/cases.json").read_text(encoding="utf-8"))
    items(cases, "golden cases", 15)
    if not 10 <= len(cases) <= 15:
        raise ContractError("golden set must contain 10–15 cases")
    seen = set()
    for c in cases:
        obj(c, "case")
        if set(c) != FIELDS or c["case_id"] in seen:
            raise ContractError("golden case fields missing / duplicate ID")
        text(c["case_id"], "case id", 80); seen.add(c["case_id"])
        choices(c["origin"], {"synthetic", "anonymized_real"}, "origin")
        if c["evaluation_dimensions"] != DIMENSIONS:
            raise ContractError("case must cover all diagnostic dimensions")
        for field in ("must_notice", "must_not_assume", "important_tradeoffs", "acceptable_recommendations", "bad_recommendations", "required_actions"):
            if not items(c[field], field, 12):
                raise ContractError(f"empty rubric field:{field}")
        text(c["required_stop_condition"], "stop rubric", 400)
        obj(c["input"], "structured context")
    return cases


def property_check(d: dict, rule: dict) -> bool:
    r = obj(rule, "property rule")
    if set(r) != {"path", "op", "value"}:
        raise ContractError("invalid benchmark rule")
    current = d
    for segment in r["path"].split("."):
        if not isinstance(current, dict) or segment not in current:
            return False
        current = current[segment]
    op = choices(r["op"], {"in", "nonempty", "includes_action", "equals", "contains"}, "property operation")
    if op == "in": return current in r["value"]
    if op == "equals": return current == r["value"]
    if op == "nonempty": return bool(current)
    if op == "includes_action": return any(a["kind"] in r["value"] for a in current)
    return r["value"] in current


def run(cases: list, *, now: datetime) -> dict:
    results = []
    for c in cases:
        d = decide(c["input"], now=now)
        checks = [property_check(d, r) for r in c["decision_properties"]]
        validate_actions(d["actions"])
        hard = [all(cl["confidence"] == "PLANNED" for cl in d["claims"] if cl["stage"] == "planned"),
                all(cl["confidence"] != "VERIFIED" for cl in d["claims"] if cl["risk"]),
                len(d["references"]) <= 3, bool(d["unknowns"]), bool(d["stop_condition"])]
        if c["input"]["mode"] == "recruiting" and c["input"].get("recruiting", {}).get("status", "waiting") == "waiting":
            hard.append(d["application_status"] == "waiting")
        results.append({"case_id": c["case_id"], "origin": c["origin"], "hard_rule_pass": all(hard),
                        "decision_properties": [{"rule": r, "pass": p} for r, p in zip(c["decision_properties"], checks)],
                        "property_pass": all(checks), "bottleneck": d["bottleneck"]})
    return {"schema_version": "1", "case_coverage": len(results), "levels": {
        "1": {"scope": "deterministic output integrity rules", "pass": all(r["hard_rule_pass"] for r in results)},
        "2": {"scope": "structured decision regression, not semantic quality", "pass": all(r["property_pass"] for r in results)},
        "3": {"status": "NOT_RUN", "scope": "host model evaluation requires separate outputs and reviewers"},
        "4": {"status": "NOT_RUN", "scope": "real-world outcome protocol; no hiring causality claim"}},
        "regressions": [r["case_id"] for r in results if not r["hard_rule_pass"] or not r["property_pass"]],
        "cases": results, "boundary": "No composite Career Score. Fixture checks cannot grade natural-language decision quality."}


def packet(cases: list, output: Path) -> list[str]:
    output = output.expanduser().resolve()
    if output.exists():
        raise ContractError("Packet destination exists; use a new private directory")
    output.mkdir(parents=True)
    # Host sees only raw context; the evaluation rubric remains separate.
    inputs = [{"case_id": c["case_id"], "origin": c["origin"], "request": c["situation"], "available_context": c["available_context"]} for c in cases]
    rubrics = [{k: v for k, v in c.items() if k not in {"input", "decision_properties"}} for c in cases]
    values = {"host-inputs.json": {"schema_version": "1", "instructions": "Use career-junshi. Do not read the evaluator rubric. Record model, version/settings, time and run_id separately.", "cases": inputs},
              "evaluator-rubric.json": {"dimensions": DIMENSIONS, "cases": rubrics,
                                       "ratings": ["PASS", "PARTIAL", "FAIL", "UNASSESSABLE"], "requirement": "Cite exact response excerpts and relevant source; do not assign an aggregate score."}}
    for name, value in values.items():
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [str(output / n) for n in values]


def validate_host_submission(value: dict, cases: list) -> dict:
    v = obj(value, "host evaluation")
    if set(v) != {"run_id", "model", "settings", "evaluated_at", "reviewer", "results"}:
        raise ContractError("host submission requires explicit run/model/settings/time/reviewer/results")
    for name in ("run_id", "model", "settings", "evaluated_at", "reviewer"):
        text(v[name], name, 200)
    timestamp(v["evaluated_at"], "evaluated_at")
    ids = {c["case_id"] for c in cases}
    seen = set()
    for raw in items(v["results"], "results", 15):
        r = obj(raw, "host result")
        if set(r) != {"case_id", "response", "dimensions"} or r["case_id"] not in ids or r["case_id"] in seen:
            raise ContractError("unknown / duplicate host case or result fields")
        seen.add(r["case_id"])
        response = text(r["response"], "response", 16000)
        annotations = obj(r["dimensions"], "dimensions")
        if set(annotations) != set(DIMENSIONS):
            raise ContractError("all dimensions need a diagnostic")
        for dimension, annotation in annotations.items():
            a = obj(annotation, dimension)
            if set(a) != {"rating", "response_span", "diagnostic", "source_reference"}:
                raise ContractError("diagnostic requires response and source evidence")
            choices(a["rating"], {"PASS", "PARTIAL", "FAIL", "UNASSESSABLE"}, "rating")
            span = text(a["response_span"], "response_span", 600, empty=a["rating"] == "UNASSESSABLE")
            if span and span not in response:
                raise ContractError("evaluation excerpt is absent from response")
            text(a["diagnostic"], "diagnostic", 600)
            text(a["source_reference"], "source_reference", 240)
    return {"accepted_cases": sorted(seen), "missing_cases": sorted(ids - seen), "composite_score": None,
            "boundary": "This validates externally supplied annotations, not their semantic correctness, independence or actual model execution."}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cases", type=Path, help="Explicit golden set (required in runtime-only installations)")
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run"); r.add_argument("--now", default="2026-10-03T12:00:00+08:00"); r.add_argument("--output", type=Path)
    s = sub.add_parser("packet"); s.add_argument("--output", type=Path, required=True)
    h = sub.add_parser("validate-host"); h.add_argument("--input", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        cases = load_cases(args.cases)
        if args.command == "run":
            result = run(cases, now=datetime.fromisoformat(timestamp(args.now, "now").replace("Z", "+00:00")))
            if args.output:
                with args.output.open("x", encoding="utf-8") as out:
                    out.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            code = 1 if result["regressions"] else 0
        elif args.command == "packet":
            result = {"files": packet(cases, args.output), "host_eval_status": "NOT_RUN"}; code = 0
        else:
            result = validate_host_submission(json.loads(args.input.read_text(encoding="utf-8")), cases); code = 0
        print(json.dumps(result, ensure_ascii=False, indent=2)); return code
    except (ContractError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
