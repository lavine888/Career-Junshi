"""Prepare version-hidden packets; review them without passing the mapping."""
import concurrent.futures
import json
import secrets
from pathlib import Path
from run_eval import ROOT, DIMENSIONS, HARD_FAILURES, attempt, dump, now, sha

DESCRIPTIONS = {
    "Situation Understanding": "Recognize the actual stage, urgency and problem; do not ask again for supplied facts.",
    "Evidence Discipline": "Attribute source statements, preserve personal ownership and evidence strength; receipts do not prove extra claims.",
    "Fact / Inference / Unknown separation": "Keep sourced reports distinct from inference and unknowns, including denial, condition and hearsay.",
    "Bottleneck Identification": "Identify the consequential bottleneck instead of treating every case as resume wording.",
    "Recommendation Clarity": "Give a clear first move with appropriate conditionality; do not postpone everything to unspecified research.",
    "Actionability": "Give feasible, bounded concrete actions and outputs consistent with the supplied budget; no execution claims.",
    "Opportunity Cost Awareness": "Account for time, competing opportunities and unnecessary investment; avoid opening large projects under urgency.",
    "Counterfactual Quality": "Consider a meaningful competing explanation or strongest alternative, when assessable from the case.",
    "Reconsider Condition": "Name new observable information that would reverse or materially change the recommendation.",
    "Stop / Pivot Quality": "Give a bounded review/stopping trigger; do not pivot from a single rejection or infer an outcome from silence.",
    "Personal-context usage": "Use the relevant supplied constraints and evidence, without inventing missing personal details or history.",
    "Unsupported-claim avoidance": "Avoid invented facts, achievement metrics, scope, status, production deployment and success-causes-strategy claims."
}

FAILURE_DEFINITIONS = {
    "FABRICATED_FACT": "Asserts a material factual detail absent from or contradicted by supplied sources; explicitly hypothetical suggestions are not facts.",
    "NEGATION_FLIP": "Turns a denied assertion into an affirmed assertion or reverses a terminal recruiting result.",
    "CONDITIONAL_AS_FACT": "Treats a conditional or pending outcome as confirmed.",
    "HEARSAY_AS_FACT": "Treats second-hand reported status as confirmed without attribution or verification.",
    "TEAM_TO_SOLE": "Claims sole individual ownership of work supplied as team work.",
    "DEMO_TO_PRODUCTION": "Treats a local prototype or demo as deployed production experience.",
    "NO_REPLY_TO_REJECTION": "Treats missing recruiter reply as an established rejection.",
    "SUCCESS_TO_CAUSATION": "Treats observed success as proof that a preparation strategy caused it.",
    "UNSUPPORTED_METRIC": "States or preserves an achievement metric without a measurement source; clearly hypothetical planning budgets and user-supplied preference arithmetic are not achievements.",
    "IGNORED_CONSTRAINT": "A recommendation materially violates an explicit supplied hard constraint or urgent time budget.",
    "NO_RECOMMENDATION": "No identifiable next recommendation, even conditional, is given.",
    "NO_ACTION": "No concrete feasible next action is given.",
    "NO_STOP_CONDITION": "No observable bounded stopping, review or reconsideration condition is given."
}


def schema():
    string = {"type": "string"}
    def obj(properties):
        return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}
    failure = obj({"label": {"type": "string", "enum": HARD_FAILURES}, "excerpt": string, "reason": string})
    dim = obj({"dimension": {"type": "string", "enum": DIMENSIONS}, "comparison": {"type": "string", "enum": ["A_BETTER", "B_BETTER", "TIE", "NOT_ASSESSABLE"]}, "excerpt_a": string, "excerpt_b": string, "reason": string})
    return obj({"case_id": string, "winner": {"type": "string", "enum": ["A", "B", "TIE", "UNASSESSABLE"]}, "dimension_results": {"type": "array", "items": dim}, "hard_failures_a": {"type": "array", "items": failure}, "hard_failures_b": {"type": "array", "items": failure}, "decisive_excerpt_a": string, "decisive_excerpt_b": string, "review_reason": string})


def prepare():
    manifest = json.loads((ROOT / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "GENERATIONS_FROZEN"
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    # Copied from the fixed public benchmark before outputs were inspected.
    checks = json.loads((ROOT / "review-case-checks.json").read_text(encoding="utf-8"))
    rubric = {"dimensions": DESCRIPTIONS, "hard_failure_definitions": FAILURE_DEFINITIONS, "judgment_policy": "Use A_BETTER, B_BETTER, TIE, NOT_ASSESSABLE per dimension. Do not make an overall numerical score. Material evidence/constraint hard failures outweigh stylistic preference. A tie is appropriate when substantively equivalent. Do not reward extra labels, verbosity or a preferred writing style. Assess feasibility, not checkbox vocabulary. Missing case information is not a license to invent it. Conditional example wording and future planned actions are not claims of completed work. Only use excerpts that are exact contiguous substrings of the actual response (no ellipsis, no rewrites). Empty excerpt is permitted only to explain an absent behavior. Quote short excerpts and give brief evidence-backed reasons. Return all twelve dimensions once each. Winner must be justified by material differences; not simply by counting dimensions. No tools or external knowledge."}
    dump(ROOT / "RUBRIC.json", rubric)
    dump(ROOT / "schemas" / "review-schema.json", schema())
    mapping = {}
    packets = []
    attempts = {(r["case_id"], r["skill_version"]): r for r in manifest["generation_attempts"]}
    for case in cases:
        cid = case["case_id"]
        order = ["v01", "v021"]
        secrets.SystemRandom().shuffle(order)
        mapping[cid] = {"A": order[0], "B": order[1]}
        responses = {}
        for label, version in mapping[cid].items():
            record = attempts[(cid, version)]
            if record["status"] == "VALID":
                path = ROOT / record["raw_output_path"]
                assert sha(path) == record["raw_sha256"]
                responses[label] = json.loads(path.read_text(encoding="utf-8"))["response"]
            else:
                responses[label] = "[NO VALID RESPONSE]"
        packet = {"case": {"case_id": cid, "request": case["situation"], "context": case["available_context"]}, "rubric": {**rubric, "case_checks": checks[cid]}, "Response A": responses["A"], "Response B": responses["B"]}
        if any(token in responses[label] for token in ["v0.1", "v0.2", "96174ae", "b30e82c"] for label in responses):
            raise RuntimeError("Version identity leaked in immutable response; prepare human review rather than edit it")
        path = ROOT / "blind" / (cid + ".json")
        assert not path.exists()
        dump(path, packet)
        packets.append(packet)
    dump(ROOT / "blind" / "review-packet.json", packets)
    dump(ROOT / "private" / "UNBLIND_MAP.json", mapping)
    manifest["blind_packet_sha256"] = sha(ROOT / "blind" / "review-packet.json")
    manifest["mapping_commitment_sha256"] = sha(ROOT / "private" / "UNBLIND_MAP.json")
    manifest["rubric_sha256"] = sha(ROOT / "RUBRIC.json")
    manifest["blinded_at"] = now()
    manifest["status"] = "BLIND_PACKETS_FROZEN"
    dump(ROOT / "RUN_MANIFEST.json", manifest)
    print("Frozen 15 version-hidden packets; mapping stored separately", flush=True)


def validate_review(record):
    if record["status"] != "VALID":
        return
    try:
        review = json.loads((ROOT / record["raw_output_path"]).read_text(encoding="utf-8"))
        packet = json.loads((ROOT / "blind" / (record["case_id"] + ".json")).read_text(encoding="utf-8"))
        assert review["case_id"] == record["case_id"], "Mismatched case"
        assert len(review["dimension_results"]) == 12 and {d["dimension"] for d in review["dimension_results"]} == set(DIMENSIONS), "Missing/duplicate dimensions"
        for side in ["a", "b"]:
            response = packet["Response " + side.upper()]
            excerpts = [review["decisive_excerpt_" + side]] + [d["excerpt_" + side] for d in review["dimension_results"]] + [f["excerpt"] for f in review["hard_failures_" + side]]
            assert all(isinstance(e, str) and (not e or e in response) for e in excerpts), "Nonverbatim excerpt"
            labels = [f["label"] for f in review["hard_failures_" + side]]
            assert len(labels) == len(set(labels)), "Repeated failure label"
    except (AssertionError, KeyError, TypeError) as exc:
        record.update(status="INVALID_OUTPUT", error="Review validation: " + str(exc))


def review_all():
    manifest = json.loads((ROOT / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "BLIND_PACKETS_FROZEN"
    probe = json.loads((ROOT / "reviewer-probe.json").read_text(encoding="utf-8"))
    assert probe["status"] == "AVAILABLE", "Do not assume reviewer access"
    model, effort = probe["model"], probe["reasoning_effort"]
    manifest["reviewer_model"] = model
    manifest["reviewer_reasoning_effort"] = effort
    manifest["reviewer_access_probe"] = probe
    manifest["review_method"] = "Different model, fresh ephemeral context for every pair; reviewer sees only case, rubric, A and B. No mapping, snapshots, reports or implementation history."
    manifest["review_started_at"] = now()
    manifest["review_attempts"] = []
    manifest["status"] = "BLIND_REVIEWING"
    dump(ROOT / "RUN_MANIFEST.json", manifest)
    # Review prompts contain only the four permitted packet fields.
    jobs = []
    for packet_path in sorted((ROOT / "blind").glob("[GH][0-9][0-9].json")):
        cid = packet_path.stem
        prompt = ROOT / "blind" / (cid + ".txt")
        prompt.write_text(packet_path.read_text(encoding="utf-8"), encoding="utf-8")
        jobs.append((cid, prompt))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(attempt, "review-" + cid, prompt, "reviews", ROOT / "schemas" / "review-schema.json", model, effort, 300): cid for cid, prompt in jobs}
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            record["case_id"] = futures[future]
            validate_review(record)
            manifest["review_attempts"].append(record)
            dump(ROOT / "RUN_MANIFEST.json", manifest)
            print(json.dumps({"reviewed": len(manifest["review_attempts"]), "total": 15, "case": record["case_id"], "status": record["status"], "error": record["error"], "seconds": record["seconds"]}), flush=True)
    manifest["reviews_frozen_at"] = now()
    manifest["status"] = "REVIEWS_FROZEN"
    dump(ROOT / "RUN_MANIFEST.json", manifest)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "review"])
    args = parser.parse_args()
    prepare() if args.mode == "prepare" else review_all()
