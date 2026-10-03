"""Small structured router. Natural-language situation routing belongs to the host."""
from scripts.models import choices
from scripts.method_adapter import method_plan

ROUTES = {
    "job": ["references/knowledge/02-career-decision.md", "references/practical/jd-analysis.md"],
    "positioning": ["references/knowledge/01-evidence-and-claims.md", "references/practical/resume.md"],
    "interview": ["references/knowledge/01-evidence-and-claims.md", "references/practical/interview.md", "references/practical/project-defense.md"],
    "recruiting": ["references/knowledge/03-recruiting-process.md", "references/practical/follow-up.md"],
    "offer": ["references/knowledge/02-career-decision.md", "references/knowledge/06-offer-evaluation.md", "references/practical/offer.md"],
}


def route(mode: str, *, rejected: bool = False) -> dict:
    choices(mode, set(ROUTES), "situation mode")
    refs = list(ROUTES[mode])
    if mode == "recruiting" and rejected:
        refs[-1] = "references/practical/rejection.md"
    return {"mode": mode, "references": refs, "method_plan": method_plan(mode)}
