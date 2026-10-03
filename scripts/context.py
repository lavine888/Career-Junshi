"""Validate host extraction and session provenance; no NLP or persistence."""
from __future__ import annotations

import re
from datetime import datetime, timezone

from scripts.models import ContractError, choices, items, obj, text, timestamp

SOURCE_TYPES = {"resume", "jd", "hr_chat", "interview_recap", "project_readme", "github", "offer", "user_report", "document", "tool"}
EPISTEMIC = {"FACT", "INFERENCE", "UNKNOWN"}


def freshness(value: dict, *, now: datetime | None = None) -> dict:
    f = obj(value, "freshness")
    if set(f) - {"category", "observed_at", "valid_until", "region"}:
        raise ContractError("unknown freshness fields")
    category = choices(f.get("category"), {"personal_history", "current_jd", "headcount", "market", "salary", "policy"}, "freshness category")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ContractError("freshness now requires timezone")
    checked = timestamp(f["observed_at"], "observed_at") if f.get("observed_at") else None
    until = timestamp(f["valid_until"], "valid_until") if f.get("valid_until") else None
    region = text(f.get("region", ""), "region", 120, empty=True)
    state = "STABLE_HISTORY" if category == "personal_history" else "CHECK_REQUIRED"
    if checked:
        age = (now - datetime.fromisoformat(checked.replace("Z", "+00:00"))).total_seconds() / 86400
        max_age = {"headcount": 1, "current_jd": 7, "market": 30, "salary": 30, "policy": 1}.get(category)
        if age < 0:
            state = "CHECK_REQUIRED"
        elif max_age is not None:
            state = "CURRENT_SOURCE" if age <= max_age else "STALE"
    if until and now > datetime.fromisoformat(until.replace("Z", "+00:00")):
        state = "STALE"
    if category == "salary" and not region:
        state = "CHECK_REQUIRED" if state != "STALE" else state
    return {"category": category, "observed_at": checked, "valid_until": until, "region": region,
            "freshness_required": category != "personal_history", "status": state,
            "boundary": "Age rules are heuristics; dates do not authenticate source truth or current HC."}


def statement(value: dict, sources: dict) -> dict:
    s = obj(value, "statement")
    allowed = {"id", "text", "source_id", "source_type", "source_span", "source_locator", "epistemic", "confidence", "kind", "modality", "freshness"}
    if set(s) - allowed:
        raise ContractError("unknown extracted statement fields")
    sid = text(s.get("source_id"), "source_id", 80)
    if sid not in sources:
        raise ContractError("statement source_id not in session sources")
    source = sources[sid]
    source_type = choices(s.get("source_type"), SOURCE_TYPES, "source_type")
    if source_type != source["source_type"]:
        raise ContractError("source_type mismatch")
    span = text(s.get("source_span", ""), "source_span", 600, empty=True)
    locator = text(s.get("source_locator", ""), "source_locator", 100, empty=True)
    excerpt = span
    if locator:
        m = re.fullmatch(r"chars:(\d+)-(\d+)", locator)
        if not m or not 0 <= int(m[1]) < int(m[2]) <= len(source["text"]):
            raise ContractError("invalid session source_locator")
        excerpt = source["text"][int(m[1]):int(m[2])]
        if len(excerpt) > 600 or (span and span != excerpt):
            raise ContractError("locator and source_span differ or excerpt exceeds budget")
    if not excerpt or excerpt not in source["text"]:
        raise ContractError("source_span is missing or absent from session source")
    epistemic = choices(s.get("epistemic"), EPISTEMIC, "epistemic")
    confidence = choices(s.get("confidence"), {"direct", "self_reported", "interpretation", "unknown"}, "extraction confidence")
    kind = choices(s.get("kind"), {"observation", "requirement", "claim", "recruiting_signal", "feeling"}, "statement kind")
    modality = choices(s.get("modality"), {"observed", "required", "preferred", "unknown"}, "modality")
    content = text(s.get("text"), "statement text", 400)
    if kind == "feeling" and epistemic != "INFERENCE":
        raise ContractError("user interpretation belongs to INFERENCE")
    if epistemic == "FACT" and confidence in {"interpretation", "unknown"}:
        raise ContractError("interpretation / unknown cannot be FACT")
    if source_type in {"resume", "user_report"} and kind == "claim" and confidence != "self_reported":
        raise ContractError("resume / narration accomplishment is self_reported")
    if kind == "requirement" and modality == "required" and re.search(r"preferred|nice.to.have|优先|加分|优选", excerpt, re.I):
        raise ContractError("preferred clause cannot become hard requirement")
    if kind == "claim" and re.search(r"sole|独立完成|所有代码", content, re.I) and not re.search(r"sole|独立完成|所有代码", excerpt, re.I):
        raise ContractError("leadership or source existence cannot imply sole ownership")
    if kind == "recruiting_signal" and re.search(r"passed|通过|已录用", content, re.I) and not re.search(r"passed|通过|录用", excerpt, re.I):
        raise ContractError("process update cannot imply passed")
    result = {"id": text(s.get("id"), "statement id", 80), "text": content, "source": sid,
              "source_id": sid, "source_type": source_type, "source_span": excerpt,
              "source_locator": locator, "epistemic": epistemic, "confidence": confidence,
              "kind": kind, "modality": modality}
    if "freshness" in s:
        result["freshness"] = dict(s["freshness"])
    return result


def extract(packet: dict, *, now: datetime | None = None) -> dict:
    p = obj(packet, "extraction packet")
    if set(p) != {"schema_version", "sources", "statements", "situation"} or p["schema_version"] != "1":
        raise ContractError("extraction packet requires v1 sources, statements and situation")
    sources = {}
    for raw in items(p["sources"], "sources", 12):
        raw = obj(raw, "source")
        if set(raw) != {"source_id", "source_type", "text"}:
            raise ContractError("source requires id, type and session text")
        sid = text(raw["source_id"], "source_id", 80)
        if sid in sources:
            raise ContractError("duplicate source_id")
        sources[sid] = {"source_type": choices(raw["source_type"], SOURCE_TYPES, "source_type"),
                        "text": text(raw["text"], "source text", 16000)}
    statements = [statement(s, sources) for s in items(p["statements"], "statements", 30)]
    if len({s["id"] for s in statements}) != len(statements):
        raise ContractError("duplicate statement id")
    result = dict(obj(p["situation"], "situation"))
    if any(k in result for k in ("facts", "inferences", "unknowns", "sources")):
        raise ContractError("facts / inferences / unknowns must derive from sourced statements")
    result["facts"] = [s for s in statements if s["epistemic"] == "FACT"]
    result["inferences"] = [s for s in statements if s["epistemic"] == "INFERENCE"]
    result["unknowns"] = [s["text"] for s in statements if s["epistemic"] == "UNKNOWN"]
    for s in statements:
        if s.get("freshness"):
            check = freshness(s["freshness"], now=now)
            if check["status"] in {"STALE", "CHECK_REQUIRED"}:
                result["unknowns"].append(f"{s['source_id']}：{check['category']} {check['status']}，需核对当前来源")
    return result
