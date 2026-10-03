"""Read-only evidence audit: hashes, pair invariants, blindness and citations."""
import json
from collections import Counter
from run_eval import ROOT, DIMENSIONS, sha
from blind_eval import validate_review

m = json.loads((ROOT / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
assert m["status"] == "MODEL-EVALUATED"
assert sha(ROOT / "cases.json") == m["case_sha256"]
assert sha(ROOT / "blind" / "review-packet.json") == m["blind_packet_sha256"]
assert sha(ROOT / "UNBLIND_MAP.json") == m["mapping_commitment_sha256"]
assert sha(ROOT / "RUBRIC.json") == m["rubric_sha256"]
assert sha(ROOT / "MODEL_EVAL_RESULT.json") == m["result_sha256"]
assert m["reviews_frozen_at"] <= m["unblinded_at"]
assert m["blinded_at"] <= m["review_started_at"]
assert len(m["generation_attempts"]) == 30
assert len({(r["case_id"], r["skill_version"]) for r in m["generation_attempts"]}) == 30
for p in m["prompts"]:
    assert sha(ROOT / p["path"]) == p["sha256"]
    assert 1 <= p["reference_count"] <= 3
for r in m["generation_attempts"] + m["review_attempts"]:
    if r.get("raw_sha256"):
        assert sha(ROOT / r["raw_output_path"]) == r["raw_sha256"]
    if r["status"] == "VALID":
        assert r["tool_calls_observed"] == 0
for r in m["generation_attempts"]:
    assert r["model"] == m["generation_model"] and r["settings"]["reasoning_effort"] == m["reasoning_effort"]
    assert r["settings"]["timeout_seconds"] == m["timeout_seconds"]
for cid in {r["case_id"] for r in m["generation_attempts"]}:
    prompts = [p for p in m["prompts"] if p["case_id"] == cid]
    assert len(prompts) == 2 and prompts[0]["reference_paths"] == prompts[1]["reference_paths"]
    packets = []
    for p in prompts:
        header, payload = (ROOT / p["path"]).read_text(encoding="utf-8").split("\n", 1)
        packet = json.loads(payload)
        packets.append((header, {k: v for k, v in packet.items() if k != "skill_documents"}))
    assert packets[0] == packets[1], "Unintended pair input difference"
    blind = json.loads((ROOT / "blind" / (cid + ".json")).read_text(encoding="utf-8"))
    assert set(blind) == {"case", "rubric", "Response A", "Response B"}
    assert not any(t in json.dumps(blind, ensure_ascii=False) for t in ["v0.1", "v0.2", "96174ae", "b30e82c"])
for r in m["review_attempts"]:
    assert r["model"] == m["reviewer_model"] and r["settings"]["reasoning_effort"] == m["reviewer_reasoning_effort"]
    assert sha(ROOT / "blind" / (r["case_id"] + ".txt")) == r["prompt_sha256"]
    old_status = r["status"]
    validate_review(r)
    assert r["status"] == old_status
result = json.loads((ROOT / "MODEL_EVAL_RESULT.json").read_text(encoding="utf-8"))
assert sum(result["pair_counts"].values()) == 15
assert all(sum(counts.values()) == result["valid_reviews"] for counts in result["dimension_counts"].values())
assert set(result["dimension_counts"]) == set(DIMENSIONS)
assert result["REAL-WORLD-OBSERVED"] == "NO"
print(json.dumps({"audit": "PASS", "immutable_generation_hashes": len(m["generation_attempts"]), "review_hashes": len(m["review_attempts"]), "pair_invariants": 15, "blind_packets": 15, "valid_reviews": result["valid_reviews"], "tool_calls_observed": 0}, ensure_ascii=False))
