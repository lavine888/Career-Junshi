# Practical router

The host reads only 1–3 relevant references, including knowledge documents. A mixed
situation has one primary mode selected by deadline and bottleneck; secondary work
supports one decision. No slash commands are required from the user.

| User situation | Primary mode | Default resources |
| --- | --- | --- |
| Role worth applying / transition / unknown direction | job | knowledge/02 + jd-analysis |
| Resume or ownership wording | positioning | knowledge/01 + resume |
| Upcoming interview or risky project claim | interview | knowledge/01 + interview + project-defense |
| Silence or process | recruiting | knowledge/03 + follow-up |
| Explicit rejection | recruiting | knowledge/03 + rejection (replace follow-up) |
| Offer comparison | offer | knowledge/02 + knowledge/06 + offer |

Optional replacements: [hr-chat](hr-chat.md) for draft messages;
[behavioral](behavioral.md) for true stories;
[negotiation](negotiation.md) for a proposal;
[career-memory](career-memory.md) for recall and outcomes;
[knowledge/04](../knowledge/04-role-positioning.md) for translation;
[knowledge/05](../knowledge/05-interview-evaluation.md) for feedback interpretation;
[knowledge/07](../knowledge/07-career-market-boundaries.md) for current market claims.
Replace a less relevant document instead of loading the entire library.

Structured helper: `python scripts/junshi.py route --mode interview` returns references
and an internal method plan. Free-text routing is done by the host Skill, not keywords.

## Host-led experiences

Natural-language experience names select a task playbook, replacing the normal
practical reference within the same 1–3-resource budget:

| Request | Mode | Playbook |
| --- | --- | --- |
| 简历守城 / defend one resume claim | interview or positioning | [resume-defense](resume-defense.md) |
| 岗位表达 / adapt one project to supplied roles | positioning | [role-translation](role-translation.md) |
| 补证冲刺 / fill one evidence gap within a budget | job or positioning | [evidence-sprint](evidence-sprint.md) |
| 决策复盘 / compare a prior judgment with new observations | current situation mode | [decision-review](decision-review.md) |
| 措辞核对 / check ownership, stage and causal wording | positioning | [wording-audit](wording-audit.md) |
| 隐藏结果复盘 / observations before the result is revealed | current situation mode | [outcome-blind-review](outcome-blind-review.md) |

Defense can pause with a copyable checkpoint and resume one question from the
supplied record. Outcome-blind review requires a context that has not received the
result; known results use ordinary review instead. Neither branch saves memory.

For example, `python scripts/junshi.py route --mode interview --experience defense`
selects the playbook and suggests a report filename. It does not conduct an interview,
generate a report or save a session. File creation and compact memory remain separately
authorized operations; ordinary routes keep their existing contract.
