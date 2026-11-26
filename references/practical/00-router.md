# Practical router

This is the host's detailed routing index. Choose one primary task by the user's
intent, deadline and bottleneck, then load only 1–3 task references in total.
For a simple request, answer directly. The four capabilities below organize the
experience; they do not introduce new CLI modes. Users can speak naturally.

## 1. Experience and evidence

| Intent | Existing CLI mode | References / playbook |
| --- | --- | --- |
| First use, project contribution or claim defense | positioning / interview | [resume-defense](resume-defense.md) |
| GitHub-only start | positioning | [public-projects](public-projects.md) |
| Resume positioning, wording or personal scope | positioning | [evidence](../knowledge/01-evidence-and-claims.md) + [resume](resume.md) |
| Audit a specific claim | positioning | [wording-audit](wording-audit.md) |
| Reconstruct AI-assisted development | positioning / interview | [development-recap](development-recap.md) |
| Adapt a project to supplied roles | positioning | [role-translation](role-translation.md) + relevant [role pack](../role-packs.json) |
| Export reviewed resume | positioning | [resume-export](resume-export.md) |

## 2. Roles and applications

| Intent | Existing CLI mode | References / playbook |
| --- | --- | --- |
| Role worth applying / transition / unknown direction | job | [career-decision](../knowledge/02-career-decision.md) + [jd-analysis](jd-analysis.md) |
| Close one evidence gap | job / positioning | [evidence-sprint](evidence-sprint.md) |
| Start a stuck task | job / positioning / interview | [action-start](action-start.md) |
| Test one application hypothesis | job / positioning / recruiting | [job-search-experiment](job-search-experiment.md) |
| HR silence or process | recruiting | [recruiting-process](../knowledge/03-recruiting-process.md) + [follow-up](follow-up.md) |
| Explicit rejection | recruiting | recruiting-process + [rejection](rejection.md) |
| Draft a recruiting message | recruiting | [hr-chat](hr-chat.md) |
| Application form / browser records | positioning / recruiting | [application-autofill](application-autofill.md) |

## 3. Interview coaching

| Intent | Existing CLI mode | References / playbook |
| --- | --- | --- |
| Upcoming interview or risky project claim | interview | evidence + [interview](interview.md) + [project-defense](project-defense.md) |
| Adaptive drill, whole mock, story retrieval, debrief | interview | [interview-coaching](interview-coaching.md) |
| Practice a recorded gap with a variant | interview | [interview-retry](interview-retry.md) |
| Practice one declared JD criterion | interview | [structured-interview](structured-interview.md) |
| True behavioral story | interview | [behavioral](behavioral.md) |

## 4. Feedback and decisions

| Intent | Existing CLI mode | References / playbook |
| --- | --- | --- |
| Reconsider earlier advice with new observations | current mode | [decision-review](decision-review.md) |
| Explicit review before outcome reveal | current mode | [outcome-blind-review](outcome-blind-review.md) |
| Compare offers | offer | career-decision + [offer-evaluation](../knowledge/06-offer-evaluation.md) + [offer](offer.md) |
| Verify decisive or suspicious offer terms | offer / recruiting | [offer-check](offer-check.md) |
| Compensation alignment, negotiation or rehearsal | offer / recruiting | [negotiation](negotiation.md) |
| Continue a tracked opportunity | current mode | [job-search-journey](job-search-journey.md) |
| Authorized memory / outcomes | current mode | [career-memory](career-memory.md) |

Use optional knowledge only when it changes the answer: [role positioning](../knowledge/04-role-positioning.md),
[interview evaluation](../knowledge/05-interview-evaluation.md), [market boundaries](../knowledge/07-career-market-boundaries.md),
[research and application](../knowledge/08-research-and-application.md). Replace a less relevant reference;
research supports only its studied population, intervention and outcome, not a demonstrated hiring effect.

The host handles free-text routing and interaction. The existing structured helper
`python scripts/junshi.py route --mode interview --experience defense` selects references
and suggests an artifact name; it does not run a conversation, create a report or save memory.
The CLI's five situation modes and experience identifiers remain compatible.
