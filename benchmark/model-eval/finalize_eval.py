"""Verify frozen evidence, then unblind and count diagnostics without a score."""
import json
from collections import Counter
from run_eval import ROOT, DIMENSIONS, HARD_FAILURES, dump, now, sha


def finalize():
    manifest = json.loads((ROOT / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "REVIEWS_FROZEN", "Freeze all reviews before unblinding"
    assert sha(ROOT / "blind" / "review-packet.json") == manifest["blind_packet_sha256"]
    assert sha(ROOT / "RUBRIC.json") == manifest["rubric_sha256"]
    mapping_path = ROOT / "private" / "UNBLIND_MAP.json"
    assert sha(mapping_path) == manifest["mapping_commitment_sha256"]
    for record in manifest["generation_attempts"] + manifest["review_attempts"]:
        if record.get("raw_sha256"):
            assert sha(ROOT / record["raw_output_path"]) == record["raw_sha256"], "Changed immutable output"
        if record["status"] == "VALID":
            assert record["tool_calls_observed"] == 0
    for prompt in manifest["prompts"]:
        assert sha(ROOT / prompt["path"]) == prompt["sha256"]
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    attempts = {(r["case_id"], r["skill_version"]): r for r in manifest["generation_attempts"]}
    reviews = {r["case_id"]: r for r in manifest["review_attempts"]}
    counts = Counter({"v01": 0, "v021": 0, "TIE": 0, "UNASSESSABLE": 0})
    dimensions = {dim: Counter({"v01": 0, "v021": 0, "TIE": 0, "NOT_ASSESSABLE": 0}) for dim in DIMENSIONS}
    failures = {v: Counter({label: 0 for label in HARD_FAILURES}) for v in ["v01", "v021"]}
    responses_with_failure = Counter({"v01": 0, "v021": 0})
    valid_pairs = 0
    cases = []
    for cid in sorted(mapping):
        record = {"case_id": cid, "generation_statuses": {v: attempts[(cid, v)]["status"] for v in ["v01", "v021"]}, "review_status": reviews[cid]["status"]}
        if all(attempts[(cid, v)]["status"] == "VALID" for v in ["v01", "v021"]):
            valid_pairs += 1
        if reviews[cid]["status"] != "VALID" or not all(s == "VALID" for s in record["generation_statuses"].values()):
            record["winner"] = "UNASSESSABLE"
            counts["UNASSESSABLE"] += 1
            cases.append(record)
            continue
        review = json.loads((ROOT / reviews[cid]["raw_output_path"]).read_text(encoding="utf-8"))
        winner = mapping[cid].get(review["winner"], review["winner"])
        record.update({"blind_winner": review["winner"], "winner": winner, "review_reason": review["review_reason"], "decisive_excerpts": {mapping[cid][side.upper()]: review["decisive_excerpt_" + side] for side in ["a", "b"]}, "dimension_results": [], "hard_failures": {}})
        counts[winner] += 1
        for d in review["dimension_results"]:
            verdict = mapping[cid][d["comparison"][0]] if d["comparison"] in {"A_BETTER", "B_BETTER"} else d["comparison"]
            dimensions[d["dimension"]][verdict] += 1
            record["dimension_results"].append({"dimension": d["dimension"], "winner": verdict, "reason": d["reason"], "excerpts": {mapping[cid][side.upper()]: d["excerpt_" + side] for side in ["a", "b"]}})
        for side in ["a", "b"]:
            version = mapping[cid][side.upper()]
            entries = review["hard_failures_" + side]
            record["hard_failures"][version] = entries
            failures[version].update(e["label"] for e in entries)
            responses_with_failure[version] += bool(entries)
        cases.append(record)
    result = {"status": "MODEL-EVALUATED", "scope": "15 fixed synthetic same-host-model pairs, separate-model version-hidden review; not real recruiting outcomes", "generation_model": manifest["generation_model"], "review_model": manifest["reviewer_model"], "valid_generations": manifest["valid_generations"], "planned_generations": 30, "valid_pairs": valid_pairs, "valid_reviews": sum(r["status"] == "VALID" for r in manifest["review_attempts"]), "generation_status_counts": dict(Counter(r["status"] for r in manifest["generation_attempts"])), "review_status_counts": dict(Counter(r["status"] for r in manifest["review_attempts"])), "pair_counts": dict(counts), "dimension_counts": {dim: dict(counter) for dim, counter in dimensions.items()}, "hard_failure_counts": {v: dict(counter) for v, counter in failures.items()}, "responses_with_hard_failure": dict(responses_with_failure), "case_results": cases, "coverage_gaps": manifest["coverage_gaps"], "REAL-WORLD-OBSERVED": "NO", "limitations": ["One sample per case and version; no variance estimate or causal isolation of individual rules.", "The shared generation prompt asks for actions and stop/review conditions, so baseline may already perform well.", "Same reference paths/count budget, with naturally different snapshot document lengths; no token matching.", "Different reviewer model and fresh contexts reduce version leakage but do not establish reviewer correctness or independent human confirmation.", "No baseline without a Skill; cannot isolate benefit relative to a bare host model.", "Prepared references were preserved: rejection cases use follow-up, negotiation case uses offer reference; installed routing is not tested.", "Cross-opportunity corrections, historical deduplication, real outcome causation and success calibration are not exercised by these supplied case inputs."]}
    dump(ROOT / "UNBLIND_MAP.json", mapping)
    dump(ROOT / "MODEL_EVAL_RESULT.json", result)
    manifest["unblinded_at"] = now()
    manifest["status"] = "MODEL-EVALUATED"
    manifest["result_sha256"] = sha(ROOT / "MODEL_EVAL_RESULT.json")
    dump(ROOT / "RUN_MANIFEST.json", manifest)
    print(json.dumps({k: result[k] for k in ["valid_generations", "valid_pairs", "valid_reviews", "pair_counts", "hard_failure_counts"]}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    finalize()
