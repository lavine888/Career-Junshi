"""Reviewable rationale and finite situation metadata; no hidden model reasoning."""
from scripts.models import ContractError, choices, items, obj, text
from scripts.context import freshness

FAMILIES = {"ai-product", "agent-product", "technical-product", "ai-solutions", "quant-ai", "unknown"}
STAGES = {"exploration", "application", "preparation", "post-interview", "negotiation", "decision", "unknown"}
TYPES = {"direction-choice", "gap-check", "claim-defense", "positioning", "follow-up", "offer-choice"}
TAGS = {"ownership", "architecture", "metrics", "production", "product-judgment", "evaluation",
        "salary", "manager", "timing", "constraints", "feedback", "market", "evidence", "direction"}


def memory_trace(value):
    """Validate compressed review summary. Evidence entries are source references only."""
    v = obj(value, "memory decision trace")
    required = {"situation", "evidence_used", "bottleneck", "options_considered", "chosen", "rejected_options", "why", "reconsider_if"}
    if set(v) != required:
        raise ContractError("memory trace requires the complete review summary")
    result = {k: text(v[k], k, 600 if k == "chosen" else 400) for k in ("situation", "bottleneck", "chosen")}
    for key, limit, width in (("evidence_used", 6, 240), ("options_considered", 3, 400), ("why", 4, 240), ("reconsider_if", 3, 240)):
        result[key] = [text(s, key, width) for s in items(v[key], key, limit)]
    result["rejected_options"] = []
    for raw in items(v["rejected_options"], "rejected_options", 2):
        if set(obj(raw, "rejected option")) != {"option", "why"}:
            raise ContractError("rejected option requires option and why")
        result["rejected_options"].append({"option": text(raw["option"], "option", 400), "why": text(raw["why"], "why", 400)})
    return result


def metadata(value):
    v = obj(value, "metadata")
    required = {"mode", "role_family", "stage", "situation_type", "risk_tags", "situation_tags"}
    if set(v) != required:
        raise ContractError("metadata requires mode, role_family, stage, situation_type, risk_tags, situation_tags")
    result = {"mode": choices(v["mode"], {"job", "positioning", "interview", "recruiting", "offer"}, "mode"),
              "role_family": choices(v["role_family"], FAMILIES, "role_family"),
              "stage": choices(v["stage"], STAGES, "stage"),
              "situation_type": choices(v["situation_type"], TYPES, "situation_type")}
    for key in ("risk_tags", "situation_tags"):
        result[key] = list(dict.fromkeys(choices(t, TAGS, key) for t in items(v[key], key, 8)))
    return result


def situation_metadata(value, decision):
    if "metadata" in value:
        m = metadata(value["metadata"])
        if m["mode"] != decision["mode"]:
            raise ContractError("metadata mode differs from current decision")
        return m
    mode = decision["mode"]
    kind = {"job": "direction-choice", "positioning": "positioning", "interview": "claim-defense",
            "recruiting": "follow-up", "offer": "offer-choice"}[mode]
    return metadata({"mode": mode, "role_family": "unknown", "stage": "unknown", "situation_type": kind,
                     "risk_tags": ["evidence"] if decision["bottleneck"] == "Evidence" else [],
                     "situation_tags": []})


def enrich(d, value, *, now=None):
    mode = d["mode"]
    counter, alternative, reconsider = {
        "job": ("缺口可能来自岗位职责差异，现有项目也可能已能支持更窄的岗位。", "先主投已有证据更强的相邻岗位，保留小规模目标岗位试验。", "新鲜 JD 显示该项只是优先项，或补证成本、硬约束与可比反馈改变时重新判断。"),
        "positioning": ("表达问题可能只是没有突出已有贡献，继续补项目未必有用。", "先核对个人决策与证据，再只改写一条经历。", "个人贡献、项目阶段或结果来源被纠正时重新审计措辞。"),
        "interview": ("面试可能更重产品判断或沟通；最强 Claim 不一定会被追问。", "保留一条真实产品取舍故事，同时优先防守证据薄弱处。", "JD、面试安排或可比复盘显示不同考察重点时调整准备优先级。"),
        "recruiting": ("假期、批量招聘、排期或审批也能解释延迟；无法从沉默辨认原因。", "继续其他机会，按承诺日期和实际工作日只跟进一次。", "收到明确结果、联系边界、承诺日期变化或竞争 Offer 截止时间时立即重评。"),
        "offer": ("高分来自当前主观权重；团队和经理信息误差可能使低分选项更合适。", "先核实最能改变排序的书面条款、经理与个人负责范围。", "关键条款、硬约束或权重变化导致首选改变时重新比较；接近评分不能当确定优势。"),
    }[mode]
    counter = d.pop("quality_counterargument", counter)
    alternative = d.pop("quality_alternative", alternative)
    reconsider_if = d.pop("quality_reconsider_if", [reconsider])
    decision_sources = d.pop("decision_source_ids", [])
    usable = []
    for fact in d["facts"]:
        if "freshness" in fact:
            state = freshness(fact["freshness"], now=now)
            fact["freshness_assessment"] = state
            if state["status"] not in {"CURRENT_SOURCE", "STABLE_HISTORY"}:
                d["unknowns"].append({"label": "UNKNOWN", "text": f"来源 {fact['source']} 的当前有效性需复核（{state['status']}）"})
                continue
        if decision_sources and fact.get("source_id", fact["source"]) not in decision_sources:
            continue
        usable.append({"source": fact["source"], "text": fact["text"],
                       "source_locator": fact.get("source_locator", "legacy:unlocated")})
    stale = [f for f in d["facts"] if f.get("freshness_assessment", {}).get("status") in {"STALE", "CHECK_REQUIRED"}]
    for c in d["claims"]:
        if c["confidence"] in {"SUPPORTED", "VERIFIED"}:
            usable.extend({"source": e["source"], "text": c["safe_wording"], "claim_id": c["id"],
                           "source_locator": "operator-attested-evidence"} for e in c["evidence"]
                          if e["kind"] != "self_report" and "claim" in e["supports"])
    if stale and mode == "job" and d["bottleneck"] == "Market":
        d["recommended_move"] = "先复核当前 JD / 招聘名额；个人项目证据仍可使用，投递判断需要当前岗位依据。"
        d["bottleneck"] = "Market"
        for a in d["actions"]:
            if a["kind"] == "apply":
                a["description"] = "确认当前 JD / 名额有效后，再选择一小批岗位验证反馈"
    d["metadata"] = situation_metadata(value, d)
    d["recommendation"] = {"move": d["recommended_move"], "supporting_evidence": usable,
                           "strongest_counterargument": counter, "reconsider_if": reconsider_if,
                           "confidence_basis": "有界规则建议，依据上述来源报告与未确认条件；不提供录用概率。"}
    d["decision_trace"] = {"situation": d["current_situation"], "evidence_used": usable,
                           "bottleneck": d["bottleneck"], "options_considered": [d["recommended_move"], alternative],
                           "chosen": d["recommended_move"],
                           "rejected_options": [{"option": alternative, "why": "可保留作备选；当前目标、风险和停止线优先支持首选的可逆动作。"}],
                           "why": d["why"], "reconsider_if": reconsider_if}
    d["schema_version"] = "2"
    return d
