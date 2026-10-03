"""Case-level predictions, matching and preparation signals, never hiring odds."""
from datetime import datetime, timezone
from scripts.models import ContractError, choices, items, obj, text, timestamp
from scripts.intelligence import metadata, TAGS


def predictions(value):
    result = []
    for raw in items(value, "predictions", 5):
        p = obj(raw, "prediction")
        if set(p) != {"topic", "expectation", "basis"}:
            raise ContractError("prediction requires topic, expectation and source-based basis")
        result.append({"topic": choices(p["topic"], TAGS, "topic"),
                       "expectation": choices(p["expectation"], {"high_attention", "risk_visible"}, "expectation"),
                       "basis": text(p["basis"], "basis", 240)})
    if len({p["topic"] for p in result}) != len(result):
        raise ContractError("duplicate prediction topics")
    return result


def observations(value):
    result = []
    for raw in items(value, "observations", 5):
        o = obj(raw, "observation")
        if set(o) != {"topic", "attention", "risk_observed", "text", "source"}:
            raise ContractError("observation requires topic, attention, risk_observed, text and source")
        risk = o["risk_observed"]
        if risk is not None and not isinstance(risk, bool):
            raise ContractError("risk_observed must be true, false (explicitly assessed) or null")
        attention = choices(o["attention"], {"high", "medium", "low", "not_asked", "unknown"}, "attention")
        if attention == "not_asked" and risk is not None:
            raise ContractError("not asked cannot establish absence or presence of a risk")
        result.append({"topic": choices(o["topic"], TAGS, "topic"), "attention": attention,
                       "risk_observed": risk, "text": text(o["text"], "observation text", 240),
                       "source": text(o["source"], "observation source", 240)})
    if len({o["topic"] for o in result}) != len(result):
        raise ContractError("duplicate observation topics")
    return result


def calibrate(expected, observed):
    expected, observed = predictions(expected), observations(observed)
    by_topic = {o["topic"]: o for o in observed}
    result = []
    for p in expected:
        o = by_topic.get(p["topic"])
        state = "UNASSESSABLE"
        if o and o["attention"] == "not_asked":
            state = "NOT_OBSERVED"
        elif o and p["expectation"] == "high_attention" and o["attention"] in {"high", "medium", "low"}:
            state = "SUPPORTED_THIS_CASE" if o["attention"] == "high" else "CONTRADICTED_THIS_CASE"
        elif o and p["expectation"] == "risk_visible" and o["risk_observed"] is not None:
            state = "SUPPORTED_THIS_CASE" if o["risk_observed"] else "CONTRADICTED_THIS_CASE"
        result.append({"topic": p["topic"], "status": state, "source": o["source"] if o else None,
                       "boundary": "Topic observation in this case; not proof of ability, strategy effect or hiring probability."})
    return result


def match_score(current, previous):
    a, b = metadata(current), metadata(previous)
    if a["role_family"] == "unknown" or a["stage"] == "unknown":
        return None
    if any(a[k] != b[k] for k in ("mode", "role_family", "stage")):
        return None
    overlap = (set(a["risk_tags"] + a["situation_tags"]) & set(b["risk_tags"] + b["situation_tags"]))
    if not overlap:
        return None
    return len(overlap) + int(a["situation_type"] == b["situation_type"])


def select_similar(current, pairs, *, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ContractError("similar recall time requires timezone")
    ranked = []
    for p in items(pairs, "history candidates", 30):
        decision = p["decision"]
        m = decision["data"].get("metadata")
        if not m or not p.get("outcome"):
            continue
        age = (now - datetime.fromisoformat(timestamp(decision["created_at"], "created_at").replace("Z", "+00:00"))).total_seconds() / 86400
        if not 0 <= age <= 180:
            continue
        score = match_score(current, m)
        if score is not None:
            ranked.append((score, decision["created_at"], decision["id"], p))
    return [p for _, _, _, p in sorted(ranked, key=lambda row: row[:3], reverse=True)[:3]]


def recurrent_signal(pairs):
    eligible = []
    seen_events, seen_sources = set(), set()
    for pair in items(pairs, "similar history", 3):
        d, o = pair["decision"]["data"], pair["outcome"]["data"]
        event, source = o.get("event_id"), o.get("source")
        if o.get("origin") != "real_world" or not event or not source or event in seen_events or source in seen_sources:
            continue
        seen_events.add(event); seen_sources.add(source)
        eligible.append(o)
    if len(eligible) < 3:
        return {"status": "INSUFFICIENT_OBSERVATIONS", "comparable_outcomes": len(eligible), "risk_tags": []}
    counts = {topic: len({x["source"] for o in eligible for x in observations(o.get("observations", []))
                          if x["topic"] == topic and x["risk_observed"] is True}) for topic in TAGS}
    tags = sorted(topic for topic, count in counts.items() if count >= 2)
    return {"status": "RECURRENT_SIGNAL" if tags else "NO_RECURRENT_SIGNAL", "comparable_outcomes": len(eligible),
            "risk_tags": tags, "boundary": "Reported real events; only raises preparation priority. No automatic ability or causal label."}


def apply_history(d, pairs, *, now=None):
    # Recheck matching even when a library caller bypasses MemoryStore.
    relevant = select_similar(d["metadata"], items(pairs, "similar history", 3), now=now)
    signal = recurrent_signal(relevant)
    d["recurring_risk"] = signal
    d["similar_memory"] = {"considered": len(relevant), "used": [], "changed": False}
    if signal["status"] != "RECURRENT_SIGNAL" or d["mode"] != "interview":
        return
    target = " / ".join(signal["risk_tags"])
    for a in d["actions"]:
        if a["kind"] == "question_ladder":
            a["description"] = f"优先练 {target}：用个人决策、贡献边界和证据守住五层追问；依据三个可比复盘。"
    d["recommended_move"] += f" 可比复盘反复出现 {target} 风险，本轮优先防守该项。"
    sources = [{"decision_id": p["decision"]["id"], "outcome_id": p["outcome"]["id"], "source": p["outcome"]["data"]["source"]} for p in relevant]
    d["similar_memory"] = {"considered": len(relevant), "used": sources, "changed": True}
    d["recommendation"]["move"] = d["recommended_move"]
    d["why"].append("三个可比结果中至少两次有明确同类风险，优先补防守证据；不据此判断整体能力。")
    d["recommendation"]["supporting_evidence"].extend(sources)
    d["recommendation"]["reconsider_if"].append("新可比复盘或贡献纠正不再支持该风险时，降低此项准备优先级。")
    d["decision_trace"]["chosen"] = d["recommended_move"]
    d["decision_trace"]["options_considered"][0] = d["recommended_move"]
    d["decision_trace"]["evidence_used"] = d["recommendation"]["supporting_evidence"]
    d["decision_trace"]["reconsider_if"] = d["recommendation"]["reconsider_if"]
