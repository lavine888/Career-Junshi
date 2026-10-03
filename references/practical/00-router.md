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
