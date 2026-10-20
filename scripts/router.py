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

EXPERIENCES = {
    "job-search-experiment": {"modes": {"job", "positioning", "recruiting"},
                              "references": ["references/knowledge/08-research-and-application.md", "references/practical/job-search-experiment.md"],
                              "artifact": "job-search-experiment.md"},
    "action-start": {"modes": {"job", "positioning", "interview"},
                     "references": ["references/knowledge/01-evidence-and-claims.md", "references/practical/action-start.md"],
                     "artifact": "action-start.md"},
    "resume-export": {"modes": {"positioning"},
                      "references": ["references/knowledge/01-evidence-and-claims.md", "references/practical/resume-export.md"],
                      "artifact": "resume.tex"},
    "wording-audit": {"modes": {"positioning"},
                      "references": ["references/knowledge/01-evidence-and-claims.md", "references/practical/wording-audit.md"],
                      "artifact": "wording-audit.md"},
    "defense": {"modes": {"positioning", "interview"},
                "references": ["references/knowledge/01-evidence-and-claims.md", "references/practical/resume-defense.md"],
                "artifact": "resume-defense.md"},
    "role-translation": {"modes": {"positioning"},
                         "references": ["references/knowledge/01-evidence-and-claims.md", "references/practical/role-translation.md", "references/role-packs.json"],
                         "artifact": "role-translation.md"},
    "proof-sprint": {"modes": {"job", "positioning"},
                     "references": ["references/knowledge/01-evidence-and-claims.md", "references/practical/evidence-sprint.md"],
                     "artifact": "evidence-sprint.md"},
    "decision-review": {"modes": set(ROUTES),
                        "references": ["references/knowledge/02-career-decision.md", "references/practical/decision-review.md"],
                        "artifact": "decision-review.md"},
    "outcome-blind-review": {"modes": set(ROUTES),
                             "references": ["references/knowledge/02-career-decision.md", "references/practical/outcome-blind-review.md"],
                             "artifact": "outcome-blind-review.md"},
}


def route(mode: str, *, rejected: bool = False, experience: str | None = None) -> dict:
    choices(mode, set(ROUTES), "situation mode")
    if experience is not None:
        choices(experience, set(EXPERIENCES), "experience")
        profile = EXPERIENCES[experience]
        choices(mode, profile["modes"], "experience mode")
        return {"mode": mode, "references": list(profile["references"]), "method_plan": method_plan(mode),
                "experience": experience, "suggested_artifact": profile["artifact"],
                "execution": "host-led", "boundary": "Routing selects references only; the host conducts the conversation and produces requested materials."}
    refs = list(ROUTES[mode])
    if mode == "recruiting" and rejected:
        refs[-1] = "references/practical/rejection.md"
    return {"mode": mode, "references": refs, "method_plan": method_plan(mode)}
