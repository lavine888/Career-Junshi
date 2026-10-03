"""Small, auditable career hypotheses; one rejection never forces a pivot."""
from scripts.models import ContractError, choices, items, obj, text


def review_hypothesis(value):
    h = obj(value, "career hypothesis")
    required = {"hypothesis", "supporting_evidence", "counterevidence", "review_after", "alternative"}
    if set(h) != required:
        raise ContractError("hypothesis requires hypothesis, supporting_evidence, counterevidence, review_after, alternative")
    clean = {"hypothesis": text(h["hypothesis"], "hypothesis", 400),
             "review_after": text(h["review_after"], "review_after", 240)}
    for key in ("supporting_evidence", "counterevidence"):
        clean[key] = []
        for raw in items(h[key], key, 10):
            e = obj(raw, "hypothesis evidence")
            if set(e) != {"source", "event_id", "comparison_key", "scope", "gap", "text", "origin"}:
                raise ContractError("hypothesis evidence needs sourced distinct comparable events, scope, gap, text and origin")
            clean[key].append({k: text(e[k], k, 240 if k == "text" else 100) for k in ("source", "event_id", "comparison_key", "gap", "text")})
            clean[key][-1].update(scope=choices(e["scope"], {"core", "local"}, "scope"),
                                 origin=choices(e["origin"], {"synthetic", "real_world", "unknown"}, "origin"))
    a = obj(h["alternative"], "alternative")
    if set(a) != {"hypothesis", "expected_value", "basis", "constraints_checked", "confounders_checked"}:
        raise ContractError("alternative requires value basis, checked constraints and confounders")
    for key in ("constraints_checked", "confounders_checked"):
        if not isinstance(a[key], bool):
            raise ContractError(f"{key} must be boolean")
    clean["alternative"] = {**a, "hypothesis": text(a["hypothesis"], "alternative hypothesis", 400, empty=True),
                            "basis": text(a["basis"], "value basis", 400, empty=True),
                            "expected_value": choices(a["expected_value"], {"higher", "unknown", "lower"}, "expected_value")}
    seen_events, seen_sources, groups = set(), set(), {}
    for e in clean["counterevidence"]:
        if e["origin"] != "real_world" or e["event_id"] in seen_events or e["source"] in seen_sources:
            continue
        seen_events.add(e["event_id"]); seen_sources.add(e["source"])
        groups.setdefault((e["comparison_key"], e["scope"], e["gap"]), []).append(e)
    core = max((len(v) for k, v in groups.items() if k[1] == "core"), default=0)
    local = max((len(v) for k, v in groups.items() if k[1] == "local"), default=0)
    qualifies = core >= 5 and a["expected_value"] == "higher" and a["basis"].strip() and a["hypothesis"].strip() and a["constraints_checked"] and a["confounders_checked"]
    clean["status"] = "PIVOT" if qualifies else "REFINE" if max(core, local) >= 3 else "KEEP"
    clean["reason"] = "多次可比核心反证与更高价值替代均有来源，建议由用户复核转向。" if qualifies else "重复局部 / 核心缺口先缩小或补证；替代价值或混杂因素未满足转向条件。" if clean["status"] == "REFINE" else "证据不足以改变方向；继续有界试验，不从单次拒绝推断普遍结论。"
    clean["boundary"] = "Conservative review gate; reports are not authenticated, expected value is qualitative and user supplied, no automatic career switch."
    return clean
