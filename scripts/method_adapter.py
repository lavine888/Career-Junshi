"""Career Alpha methods as internal plans; no external Skill dependency."""
from scripts.models import ContractError, choices, items, obj, text

METHODS = {
    "job": ["radar", "wedge", "proof", "offer"],
    "positioning": ["proof", "position", "interview"],
    "interview": ["proof", "position", "interview", "offer"],
    "recruiting": ["offer", "proof", "interview"],
    "offer": ["wedge", "offer"],
}


def method_plan(mode: str, *, evidence_gap=False, urgent=False) -> list[str]:
    mode = choices(mode, set(METHODS), "mode")
    plan = list(METHODS[mode])
    if evidence_gap and mode == "job" and not urgent:
        plan.extend(["build", "contributor"])
    return list(dict.fromkeys(plan))


def review_pattern(feedback: list[dict]) -> dict:
    """Only a cohort with comparable metadata can suggest a direction review."""
    entries = items(feedback, "feedback", 50)
    normalized = []
    for raw in entries:
        r = obj(raw, "feedback")
        if set(r) != {"role_family", "gap", "source", "comparable"} or not isinstance(r["comparable"], bool):
            raise ContractError("feedback needs role_family, gap, source, and comparable boolean")
        normalized.append({"role_family": text(r["role_family"], "role_family", 100),
                           "gap": text(r["gap"], "gap", 240, empty=True),
                           "source": text(r["source"], "source", 240), "comparable": r["comparable"]})
    # Do not double count one source across claims or repeated imports.
    unique = {(r["source"], r["role_family"]): r for r in normalized if r["comparable"]}
    groups = {}
    for r in unique.values():
        if r["gap"]:
            key = (r["role_family"], r["gap"])
            groups[key] = groups.get(key, 0) + 1
    repeated = [{"role_family": k[0], "gap": k[1], "count": n} for k, n in groups.items() if n >= 5]
    return {"move": "REFINE" if repeated else "KEEP", "repeated_gaps": repeated,
            "pivot": "Consider PIVOT only after checking constraints, gap-closing cost and market confounders.",
            "boundary": "KEEP means insufficient evidence to change the hypothesis, not proof that it is correct."}
