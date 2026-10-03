"""Bounded qualitative decision compilation, not NLP or an objective career score."""
from __future__ import annotations
import re
from scripts.models import ContractError, choices, items, obj, text, number
from scripts.intelligence import FAMILIES, TAGS

LEVELS = ("unknown", "low", "medium", "high")
CRITERIA = ("evidence_strength", "continuity", "defensibility", "role_relevance", "goal_fit", "gap_cost", "optionality", "market_testability")
STAGES = {"unknown", "planned", "demo", "backtest", "completed", "production"}


def fields(value, allowed, label):
    result = obj(value, label)
    if set(result) - set(allowed):
        raise ContractError(f"unknown {label} fields")
    return result


def source_ids(value, n):
    ids = list(dict.fromkeys(text(s, "decision source_id", 240) for s in items(value, "decision sources", 8)))
    if not ids or set(ids) - n["_source_ids"]:
        raise ContractError("decision assessment requires existing session source IDs")
    return ids


def decision_state(plan, state, basis, *, blocking=None, reversing=None):
    plan["recommendation_type"] = state
    plan["decision_sufficiency"] = {"state": "DECISION_" + state, "basis": basis,
                                    "blocking_unknowns": (blocking or [])[:3], "reversal_unknowns": (reversing or [])[:3]}
    return plan


def direction_plan(value, n, action):
    raw = fields(value, {"candidates"}, "direction")
    candidates = []
    for value in items(raw.get("candidates", []), "direction candidates", 6):
        c = fields(value, {"name", "role_family", "source_ids", "assessment", "strongest_proof", "largest_gap", "resume_case", "market_test", "constraint_status"}, "direction candidate")
        assessment = fields(c.get("assessment", {}), CRITERIA, "direction assessment")
        levels = {k: choices(assessment.get(k, "unknown"), {"unknown", "low", "medium", "high"}, k) for k in CRITERIA}
        candidates.append({"name": text(c.get("name"), "direction name", 45),
                           "role_family": choices(c.get("role_family"), FAMILIES - {"unknown"}, "direction role family"),
                           "source_ids": source_ids(c.get("source_ids", []), n), "assessment": levels,
                           "constraint_status": choices(c.get("constraint_status", "unknown"), {"pass", "fail", "unknown"}, "direction constraints"),
                           **{k: text(c.get(k, ""), k, 400, empty=True) for k in ("strongest_proof", "largest_gap", "resume_case", "market_test")}})
    if len({c["name"] for c in candidates}) != len(candidates):
        raise ContractError("direction names must be unique")
    # Ordinal comparison of disclosed host assessments, not invented numeric scores.
    # Existing, defensible, continuous evidence breaks ties before rebuilding work.
    def order(c):
        a = c["assessment"]
        return tuple((0 if a[k] == "unknown" else 4 - LEVELS.index(a[k])) if k == "gap_cost" else LEVELS.index(a[k]) for k in CRITERIA)
    tiers = {k: [] for k in ("primary", "secondary", "exploratory", "deprioritized")}
    eligible = []
    for c in candidates:
        a = c["assessment"]
        if c["constraint_status"] == "fail" or a["goal_fit"] == "low":
            tiers["deprioritized"].append(c["name"])
        elif a["evidence_strength"] == "low" and a["gap_cost"] == "high":
            tiers["exploratory"].append(c["name"])
        elif c["strongest_proof"] and any(a[k] != "unknown" for k in ("evidence_strength", "role_relevance", "goal_fit")):
            eligible.append(c)
        else:
            tiers["exploratory"].append(c["name"])
    ranked = sorted(eligible, key=order, reverse=True)
    if ranked:
        best = order(ranked[0])
        tiers["primary"] = [c["name"] for c in ranked if order(c) == best]
        rest = [c for c in ranked if order(c) != best]
        if rest:
            next_key = order(rest[0])
            tiers["secondary"] = [c["name"] for c in rest if order(c) == next_key]
            tiers["exploratory"].extend(c["name"] for c in rest if order(c) != next_key)
        move = "主投：" + " / ".join(tiers["primary"])
        if tiers["secondary"]: move += "；副投：" + " / ".join(tiers["secondary"])
        if tiers["exploratory"]: move += "；仅保留探索，不作为当前主线：" + " / ".join(tiers["exploratory"])
        if tiers["deprioritized"]: move += "；当前降低投入：" + " / ".join(tiers["deprioritized"])
        why = ["优先保留已有、连续且可防守的证据，用一份简历即可验证；不为职位名重建经历",
               "比较来自有来源的定性判断；未独立核实的经历保持自述，不变成已认证成果"]
        state = "CONDITIONAL" if len(tiers["primary"]) > 1 or any(c["constraint_status"] == "unknown" or c["largest_gap"] for c in ranked if c["name"] in tiers["primary"]) else "SUFFICIENT"
        refs = list(dict.fromkeys(s for c in ranked if c["name"] in tiers["primary"] for s in c["source_ids"]))
    else:
        move = "先确认一项能改变排序的目标或可防守经历；目前没有足够依据指定主投方向。"
        why, state, refs = ["缺少可比较的岗位证据或所有选项违反硬约束；不按名称任意排名"], "BLOCKED", []
    plan = {"bottleneck": "Direction", "recommended_move": move, "why": why,
            "direction": {**tiers, "comparison": candidates, "tie_break": "明天只发一版简历：保留最多可防守的现有证据，最少重建或编造。实质同等时保留并列，不凭名称打破。"},
            "primary_choice": tiers["primary"], "secondary_choice": tiers["secondary"], "exploratory_choice": tiers["exploratory"],
            "actions": [action("write_material", "按当前主线整理一版真实简历，只突出已有个人决策与贡献", "codex", "主线经历表述"),
                        action("jd_map", "核对当前职责与比较中的最大缺口；给副线和探索线设置小规模验证", "codex", "岗位方向对照"),
                        action("apply", "优先验证主线；副线限量，探索线不分散当前主投", "human")],
            "observation_window": "一周或首批五个可比岗位；这是可调整的验证窗口，非市场承诺",
            "stop_condition": "硬约束不满足、缺口超出预算或无法诚实防守时停止该方向的主投",
            "pivot_condition": "可比 JD / 面试证据反复支持另一方向且更符合目标时重排；单次拒绝不足以转向",
            "quality_counterargument": "更弱的方向可能已有尚未提供的强证据；当前排序也可能不符合实际岗位职责。",
            "quality_alternative": " / ".join(tiers["secondary"] + tiers["exploratory"]) or "补充会改变排序的证据后重新比较",
            "quality_reconsider_if": ["新证据改变个人贡献、核心目标、硬约束或缺口成本时重新排序"],
            "decision_source_ids": refs}
    return decision_state(plan, state, "有来源的定性比较足以形成可逆的投递主线" if ranked else "缺少可比较证据", blocking=[] if ranked else ["决定排序的目标或强证据"], reversing=[c["largest_gap"] for c in ranked if c["name"] in tiers["primary"] and c["largest_gap"]])


def conditional_offer(value, n, comparison, dimensions):
    priorities = fields(value.get("priorities", {}), dimensions, "offer priorities")
    priorities = {k: choices(v, {"high", "medium", "low"}, "offer priority") for k, v in priorities.items()}
    refs = source_ids(value.get("source_ids", []), n) if priorities else []
    unknowns = []
    names = {c["name"] for c in comparison}
    for value in items(value.get("critical_unknowns", []), "critical offer unknowns", 8):
        u = fields(value, {"unknown", "option", "priority", "why_it_matters", "how_to_verify", "reversal_condition", "source_ids"}, "offer unknown")
        option = text(u.get("option", ""), "unknown option", 120, empty=True)
        if option and option not in names: raise ContractError("offer unknown refers to absent option")
        unknowns.append({"option": option, "priority": choices(u.get("priority", "important"), {"decisive", "important", "confidence_only"}, "information priority"),
                         "source_ids": source_ids(u.get("source_ids", []), n),
                         **{k: text(u.get(k), k, 240 if k == "reversal_condition" else 400) for k in ("unknown", "why_it_matters", "how_to_verify", "reversal_condition")}})
    if not priorities: return None
    available = [c for c in comparison if c.get("eligible") is not False]
    winner = None
    if n["goal"] and len(available) >= 2:
        for level in ("high", "medium", "low"):
            common = [k for k, v in priorities.items() if v == level and all(k in c.get("ratings", {}) for c in available)]
            if not common: continue
            dominant = [c for c in available if all(all(c["ratings"][k] >= other["ratings"][k] for k in common) and any(c["ratings"][k] > other["ratings"][k] for k in common) for other in available if other is not c)]
            if len(dominant) == 1:
                winner = dominant[0]
            # An actual tradeoff at a higher priority cannot be overridden by brand
            # or another lower tier. Identical higher tiers permit the next tier.
            if winner or any(len({c["ratings"][k] for c in available}) > 1 for k in common): break
    elif n["goal"] and len(available) == 1:
        winner = available[0]
    preference = winner["name"] if winner else None
    relevant = [u for u in unknowns if not u["option"] or u["option"] == preference]
    relevant.sort(key=lambda u: ("decisive", "important", "confidence_only").index(u["priority"]))
    top = relevant[:3]
    reversals = [u["reversal_condition"] for u in top]
    if winner and not reversals:
        reversals = ["书面职责不支持偏好的交付范围，或任一用户硬约束不满足时重新选择"]
    return {"current_preference": preference, "offer_priorities": priorities, "decision_unknowns": top, "reversal_conditions": reversals,
            "recommendation_type": "CONDITIONAL" if winner else "BLOCKED",
            "recommended_move": f"当前条件性首选 {preference}；已提供维度更符合你的高优先级目标，关键未知确认前不承诺接受。" if winner else "先确认能打破取舍的目标或硬约束；现有维度尚不能给出有依据的首选。",
            "quality_counterargument": "当前优势来自已提供的偏好与维度；口头职责、经理或经营条件的不确定性可能使备选更合适。",
            "quality_reconsider_if": reversals or ["补充决定性目标、约束或缺失比较维度后重评"],
            "decision_source_ids": refs}


def interview_focus(value, n):
    raw = fields(value, {"available_hours", "signals"}, "interview")
    hours = number(raw["available_hours"], "preparation hours", 0, 72) if "available_hours" in raw else None
    signals = []
    for value in items(raw.get("signals", []), "interview signals", 5):
        s = fields(value, {"topic", "basis", "source_ids", "kind"}, "interview signal")
        signals.append({"topic": choices(s.get("topic"), TAGS, "signal topic"), "basis": text(s.get("basis"), "signal basis", 160),
                        "source_ids": source_ids(s.get("source_ids", []), n),
                        "signal_kind": choices(s.get("kind"), {"observed_signal", "risk_hypothesis"}, "signal kind"), "status": "RISK_HYPOTHESIS"})
    signals.sort(key=lambda s: s["signal_kind"] != "observed_signal")
    return {"available_hours": hours, "top_risk_hypotheses": signals[:3]}


def communication(value, n):
    c = fields(value, {"stage", "tone", "last_event", "source_ids"}, "recruiting communication")
    source_ids(c.get("source_ids", []), n)
    stage = choices(c.get("stage", "unknown"), {"application", "interview", "final", "unknown"}, "communication stage")
    tone = choices(c.get("tone", "neutral"), {"formal", "neutral", "warm"}, "communication tone")
    event = text(c.get("last_event", ""), "last event", 120, empty=True)
    event = event or {"application": "本次投递", "interview": "本次面试", "final": "本次终面", "unknown": "本次招聘流程"}[stage]
    greeting = {"formal": "您好", "neutral": "你好", "warm": "你好，感谢之前的沟通"}[tone]
    return f"{greeting}，想跟进一下{event}后的进展。如果目前仍在流程中也没关系，有后续安排或需要补充的材料，麻烦告知，谢谢。"


def ownership_pack(value, claims, facts):
    raw = fields(value, {"project_stage", "contributions"}, "ownership context")
    project = choices(raw.get("project_stage", "unknown"), STAGES, "project stage")
    ids = {c["id"] for c in claims}
    stages = {}
    for value in items(raw.get("contributions", []), "contribution stages", 20):
        c = fields(value, {"claim_id", "claim_stage", "user_contribution_stage"}, "contribution stage")
        cid = text(c.get("claim_id"), "stage claim ID", 80)
        if cid not in ids or cid in stages: raise ContractError("contribution stage requires unique existing Claim")
        stages[cid] = {"claim_id": cid, "claim_stage": choices(c.get("claim_stage", "unknown"), STAGES, "claim stage"), "user_contribution_stage": choices(c.get("user_contribution_stage", "unknown"), STAGES, "personal contribution stage")}
    bounded = list(dict.fromkeys(c["ownership"]["contribution"] for c in claims if c["ownership"]["contribution"]))
    contribution = "；".join(bounded)
    # Preserve complete contributions separately; never cut a qualifier mid-sentence.
    safe = "据本人描述，在团队项目中负责：" + contribution + "。个人工程作者范围按已核实部分说明。" if contribution and len(contribution) <= 300 else ("据本人描述，参与团队项目；个人贡献按下列自述逐项说明，工程作者范围按已核实部分说明。" if contribution else "个人贡献尚未明确，先限定为团队项目参与；具体负责部分待确认。")
    target = next((c for c in claims if any("authorship" in r or "sole_ownership" in r for r in c["risk"])), claims[0] if claims else None)
    label = target["claim"][:180] if target else "这条经历"
    questions = [f"在“{label}”中，你个人做了哪些动作，能展示哪些原始产物？",
                 "哪项需求、产品或架构决定由你作出？当时比较过哪些备选？",
                 "哪些实现由团队完成，哪些只是你的评审、集成或验收？"]
    if any(re.search(r"AI.*(?:编码|编程)|coding tools|AI coding", f["text"], re.I) for f in facts):
        questions.append("AI 编码工具生成了哪部分工作？你用什么检查和验收确认它正确？")
    elif project == "unknown":
        questions.append("整体项目、这条主张和你的个人贡献分别到了什么阶段？有什么证据？")
    if target and any("authorship" in r for r in target["risk"]):
        questions.append("哪项技术细节可以由你本人解释并举证，哪些需要注明实现者？")
    return {"safe_claim": safe, "reported_contributions": bounded, "boundary": "保留已陈述的产品或项目领导贡献；团队、AI 工具与个人工程实现分开归属，文档存在不等于已核查。",
            "project_stage": project, "contributions": [stages.get(c["id"], {"claim_id": c["id"], "claim_stage": "unknown", "user_contribution_stage": "unknown"}) for c in claims],
            "defense_questions": questions[:5], "stage_boundary": "旧 Claim.stage 不推导整体项目阶段或个人工程完成；缺少独立阶段证据时保持未知。"}
