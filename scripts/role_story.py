"""Translate existing evidence into role emphasis and defensible stories."""
import json
from pathlib import Path
from scripts.models import ContractError, items, obj, text
from scripts.intelligence import FAMILIES


def role_packs():
    value = json.loads((Path(__file__).resolve().parents[1] / "references" / "role-packs.json").read_text(encoding="utf-8"))
    keys = {"role_family", "typical_signals", "common_claim_risks", "evidence_patterns", "interview_dimensions", "common_gaps"}
    if len(value) != 5 or {p["role_family"] for p in value} != FAMILIES - {"unknown"}:
        raise ContractError("exactly five role packs required")
    for p in value:
        if set(p) != keys or any(not items(p[k], k, 5) for k in keys - {"role_family"}):
            raise ContractError("invalid role pack")
        for k in keys - {"role_family"}:
            for v in p[k]:
                text(v, k, 240)
    return value


def map_story(value, claims, family):
    p = obj(value, "project story")
    required = {"project_id", "source", "claim_ids", "story"}
    if set(p) != required:
        raise ContractError("project story requires project_id, source, claim_ids and story")
    ids = [text(c, "claim_id", 80) for c in items(p["claim_ids"], "story claims", 5)]
    by_id = {c["id"]: c for c in claims}
    if not ids or set(ids) - set(by_id) or len(ids) != len(set(ids)):
        raise ContractError("story must map to unique existing claims")
    story = obj(p["story"], "story")
    fields = {"tension", "personal_decision", "ownership", "tradeoff", "result_evidence", "learning"}
    if set(story) != fields:
        raise ContractError("story requires six quality dimensions")
    clean = {k: text(story[k], k, 400, empty=True) for k in fields}
    selected = [by_id[c] for c in ids]
    evidence = [{"claim_id": c["id"], "source": e["source"], "supports": e["supports"]} for c in selected for e in c["evidence"]]
    sources = {e["source"] for e in evidence}
    if clean["result_evidence"] and clean["result_evidence"] not in sources:
        raise ContractError("result_evidence must identify an existing claim evidence source, not a new accomplishment")
    gaps = [k for k, v in clean.items() if not v]
    if any(not c["ownership"]["contribution"] or c["ownership"]["scope"] == "unclear" for c in selected):
        gaps.append("personal_contribution")
    if any(c["risk"] or c["confidence"] not in {"SUPPORTED", "VERIFIED"} for c in selected):
        gaps.append("claim_evidence")
    pack = next((p for p in role_packs() if p["role_family"] == family), None)
    questions = ["你具体决定了什么？团队和你的贡献如何划分？", "为什么采用这个方案，最强备选是什么？", "结果证据支持多大范围，失败与学习是什么？"]
    return {"project_id": text(p["project_id"], "project_id", 80), "source": text(p["source"], "project source", 240),
            "claim_ids": ids, "claim_wording": [c["safe_wording"] for c in selected], "evidence": evidence,
            "story": clean, "story_quality": "DEFENSIBLE_DRAFT" if not gaps else "NEEDS_EVIDENCE_OR_PERSONAL_DECISION",
            "gaps": sorted(set(gaps)), "role_family": family,
            "role_emphasis": pack["interview_dimensions"] if pack else [], "likely_questions": questions,
            "boundary": "Role emphasis changes questions, not claim scope or achievements. Story prose remains host-authored and source-checked."}
