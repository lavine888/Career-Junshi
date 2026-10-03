"""Compact Decision/Outcome handoff; learning never establishes causal success."""
from scripts.models import choices, obj, text


def decision_record(decision: dict, *, source: str, expected_outcome: str) -> dict:
    d = obj(decision, "decision")
    result = {"situation": text(d.get("current_situation"), "situation", 400),
            "decision": text(d.get("recommended_move"), "decision", 600),
            "why": text("；".join(d.get("why", [])), "why", 600),
            "expected_outcome": text(expected_outcome, "expected_outcome", 400),
            "source": text(source, "source", 240),
            "observation_window": text(d.get("observation_window"), "observation_window", 400),
            "stop_condition": text(d.get("stop_condition"), "stop_condition", 400),
            "pivot_condition": text(d.get("pivot_condition"), "pivot_condition", 400)}
    if "metadata" in d:
        result.update(metadata=d["metadata"], predictions=d.get("predictions", []), claim_ids=[c["id"] for c in d.get("claims", [])])
    if d.get("claim_refs"):
        result["claim_refs"] = d["claim_refs"]
    if "decision_trace" in d:
        from scripts.intelligence import memory_trace
        trace = dict(d["decision_trace"])
        trace["evidence_used"] = list(dict.fromkeys(e["source"] for e in trace["evidence_used"]))[:6]
        result["decision_trace"] = memory_trace(trace)
        result["strongest_counterargument"] = text(d["recommendation"]["strongest_counterargument"], "counterargument", 400)
    return result


def feedback_next_move(outcome: dict) -> dict:
    o = obj(outcome, "outcome")
    status = choices(o.get("hard_outcome"), {"passed", "rejected", "offer", "waiting", "withdrawn", "freeze", "unknown"}, "hard_outcome")
    messages = {
        "passed": "推进下一阶段；保留本次具体追问，不能据通过证明策略因果。",
        "offer": "先核对目标、约束和书面条款，再比较选择。",
        "rejected": "结束此机会；只按明确反馈修正一处，用下一批可比机会验证。",
        "waiting": "保持等待状态；依据承诺日期与一次跟进窗口观察。",
        "freeze": "降低此机会投入；不因此降级个人能力判断。",
        "withdrawn": "记录退出理由与约束，投入下一项可逆行动。",
        "unknown": "先确认可观察结果和来源，不改写招聘状态。",
    }
    return {"recommended_move": messages[status], "learning_scope": "this opportunity only",
            "causal_status": "UNKNOWN", "profile_auto_updates": [], "review": "REFINE only a supported specific gap; do not PIVOT from one observation."}
