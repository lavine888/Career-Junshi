"""Structured, conservative claim normalization. Never verifies a URL by itself."""
from __future__ import annotations

import math
import re
from datetime import datetime
from typing import Any

CONFIDENCE = ("PLANNED", "SELF_REPORTED", "SUPPORTED", "VERIFIED")
STAGES = {"planned", "demo", "backtest", "completed", "production"}
SUPPORTS = {"claim", "authorship", "sole_ownership", "leadership", "production", "real_world", "award", "metric"}


class ContractError(ValueError):
    """Invalid structured input; callers must not silently continue."""


def obj(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def text(value: Any, label: str, maximum: int = 800, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()) or len(value) > maximum:
        raise ContractError(f"{label} must be {'optional' if empty else 'nonempty'} text <= {maximum} characters")
    return value.strip()


def choices(value: Any, allowed: set | tuple, label: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ContractError(f"invalid {label}: {value!r}")
    return value


def items(value: Any, label: str, maximum: int = 20) -> list:
    if not isinstance(value, list) or len(value) > maximum:
        raise ContractError(f"{label} must be a list of at most {maximum}")
    return value


def number(value: Any, label: str, low: float = 0, high: float = 100) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ContractError(f"{label} must be finite and in [{low}, {high}]")
    return float(value)


def timestamp(value: Any, label: str) -> str:
    value = text(value, label, 64)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{label} must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{label} must include a timezone")
    return value


def evidence_record(value: Any) -> dict:
    e = obj(value, "evidence")
    permitted = {"source", "kind", "supports", "checked_by", "checked_at", "summary"}
    if set(e) - permitted:
        raise ContractError("unknown evidence fields")
    supports = list(dict.fromkeys(choices(s, SUPPORTS, "support") for s in items(e.get("supports", []), "supports", 8)))
    result = {"source": text(e.get("source"), "source", 240),
              "kind": choices(e.get("kind"), {"direct", "supporting", "self_report"}, "evidence kind"),
              "supports": supports, "summary": text(e.get("summary", ""), "summary", 400, empty=True)}
    if e.get("checked_by") or e.get("checked_at"):
        result["checked_by"] = text(e.get("checked_by"), "checked_by", 80)
        result["checked_at"] = timestamp(e.get("checked_at"), "checked_at")
    return result


def audit_claim(value: Any) -> dict:
    c = obj(value, "claim")
    allowed = {"id", "claim", "confidence", "evidence", "ownership", "stage", "risk"}
    if set(c) - allowed:
        raise ContractError("unknown claim fields")
    claim_id = text(c.get("id"), "claim id", 80)
    claim = text(c.get("claim"), "claim", 600)
    stage = choices(c.get("stage"), STAGES, "stage")
    requested = choices(c.get("confidence", "SELF_REPORTED"), CONFIDENCE, "confidence")
    ownership = obj(c.get("ownership"), "ownership")
    if set(ownership) - {"scope", "contribution"}:
        raise ContractError("unknown ownership fields")
    scope = choices(ownership.get("scope"), {"sole", "team", "unclear"}, "ownership scope")
    contribution = text(ownership.get("contribution", ""), "contribution", 400, empty=True)
    evidence = [evidence_record(e) for e in items(c.get("evidence", []), "evidence")]
    relevant = [e for e in evidence if e["kind"] != "self_report" and "claim" in e["supports"]]
    covered = set().union(*(set(e["supports"]) for e in relevant)) if relevant else set()
    checked = [e for e in relevant if e["kind"] == "direct" and e.get("checked_by") and e.get("checked_at")]
    verified = set().union(*(set(e["supports"]) for e in checked)) if checked else set()
    required = {"claim"}
    risk = [text(r, "risk", 160) for r in items(c.get("risk", []), "risk", 12)]
    lower = claim.casefold()
    production = stage == "production" or bool(re.search(r"\bproduction\b|生产环境|生产级|线上用户", lower))
    sole = bool(re.search(r"\bsole\b|独立完成|全部.*(?:实现|编写)|所有代码", lower)) or scope == "sole"
    authorship = bool(re.search(r"\b(?:authored|implemented|wrote)\b|本人编写|本人实现", lower))
    award = bool(re.search(r"\b(?:won|winner|award|ranked)\b|获奖|冠军|第一名|排名", lower))
    real_world = bool(re.search(r"\breal.world\b|实盘|实际盈利", lower))
    metric = bool(re.search(r"\d+(?:\.\d+)?\s*[%％]|\d+\s*(?:用户|收入)|\brevenue\b", lower))
    leadership = bool(re.search(r"\bled\b|主导|负责人|从\s*0\s*到\s*1", lower))
    for flag, aspect in ((production, "production"), (sole, "sole_ownership"),
                         (authorship, "authorship"), (award, "award"),
                         (real_world, "real_world"), (metric, "metric"), (leadership, "leadership")):
        if flag:
            required.add(aspect)
            if aspect not in covered:
                risk.append(f"missing_evidence:{aspect}")
    if production and stage != "production":
        risk.append("stage_conflict:demo_or_other_is_not_production")
    if real_world and stage == "backtest":
        risk.append("stage_conflict:backtest_is_not_real_world")
    if sole and scope != "sole":
        risk.append("ownership_conflict:team_or_unclear_is_not_sole")
    if leadership and (scope == "unclear" or not contribution):
        risk.append("ownership_unclear:leadership_needs_personal_decisions")
    if not contribution:
        risk.append("personal_contribution_unknown")
    computed = "VERIFIED" if required <= verified and not risk else "SUPPORTED" if relevant else "SELF_REPORTED"
    confidence = CONFIDENCE[min(CONFIDENCE.index(requested), CONFIDENCE.index(computed))]
    if stage == "planned" or requested == "PLANNED":
        confidence = "PLANNED"
        risk.append("planned_work_is_not_completed")
    risk = list(dict.fromkeys(risk))
    stage_label = {"planned": "计划中", "demo": "原型", "backtest": "回测", "completed": "已完成（范围待核实）", "production": "生产使用待核实"}[stage]
    if confidence == "PLANNED":
        safe = "计划中的项目；尚不能作为已完成经历或结果。"
    elif risk:
        who = f"已陈述的个人贡献：{contribution}" if contribution else "个人贡献待确认"
        safe = f"项目阶段：{stage_label}；{who}。具体结果与强表述需补证。"
    else:
        safe = claim if confidence in {"SUPPORTED", "VERIFIED"} else f"据本人描述：{claim}"
    return {"id": claim_id, "claim": claim, "confidence": confidence, "evidence": evidence,
            "ownership": {"scope": scope, "contribution": contribution}, "stage": stage,
            "risk": risk, "safe_wording": safe,
            "verification_boundary": "Structured receipts are operator attestations, not authenticated verification by this script."}
