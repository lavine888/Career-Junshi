<div align="center">

![Career Junshi — Make every claim defensible](assets/readme-hero-fancy.png)

# Career Junshi · 求职军师

### Turn real experience into a resume you can defend.

Start with one project claim. Clarify ownership, build the missing evidence, choose your next move.

[![MIT](https://img.shields.io/badge/License-MIT-D8B466?style=flat-square)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-627EAA?style=flat-square)
[![Memory opt-in](https://img.shields.io/badge/Memory-opt--in-83D5BA?style=flat-square)](documentation/MEMORY.md)

[See it in action](#demo) · [Get started](#start) · [Four experiences](#experiences) · [Evaluation](#evaluation) · [中文](README.md)

</div>

Career Junshi is a career workflow for Codex and other hosts that support local Skills.
For candidates explaining real projects, changing roles, preparing for an interview,
or deciding where to focus their job search.

**Bring real context. Leave with an evidence-grounded judgment and 1–3 useful next actions.**

<a id="demo"></a>

## Can you defend the next question?

> **Resume claim:** “Independently built a production RAG platform, improving accuracy by 30%.”
>
> **Actual account:** A team course prototype. You wrote evaluation scripts and classified
> failures; a teammate built the service. Ten internal questions, no baseline, no production users.

Junshi narrows unsupported wording and starts with the work you actually did:

```text
Junshi: For the ten questions you ran, what made an answer count as a failure?

You: My teammate and I agreed on three checks: missing document citations,
     incorrect cited passages, or an answer contradicting the document.
     I put those checks in the script and recorded the results.

Junshi: That contribution is clearer. It remains your account;
        the code and evaluation records have not been checked.
```

You leave with a sentence you can use now:

> Contributed to a team RAG course prototype, owning evaluation scripts and failure
> classification; evaluated ten internal questions against team-agreed criteria and
> recorded missing citations, incorrect passages, and contradictions with source documents.

**Keep the contribution. Remove the unsupported independence, production claim, and 30% improvement.**
Know exactly what evidence to bring back next.

<sub>Translated and condensed from an actual host trial with anonymous synthetic material, not a real candidate or hiring outcome. See the [trial record](documentation/EVOLUTION_EVAL.md). The [full walkthrough](cases/experiences/defense/example.md) is a separately authored illustration.</sub>

<a id="start"></a>

## Start with one sentence

### 1 · Install

Send this to a host that supports local Skills:

```text
Install career-junshi from the main branch of
https://github.com/lavine888/Career-Junshi using the repository installer.
Check for an existing installation first; do not overwrite it.
Validate the installed runtime files. Do not enable persistent memory.
```

### 2 · Bring one real experience

```text
Use $career-junshi for a resume defense session.

My resume says: ...
What I actually did: ...
Target role / JD: ...
Next interview or deadline: ...

Ask one question at a time and follow my actual answers.
Finish with safe wording, evidence gaps, and the most useful next step.
```

A complete resume is optional. You can also ask to rewrite a paragraph or prioritize
tonight's preparation. Supplied materials come first; questions fill only consequential
gaps. Persistent memory can stay off.

<a id="experiences"></a>

## Four experiences, one evidence loop

| Where you are stuck | Ask this | What you get |
| --- | --- | --- |
| **🛡 Resume defense** · A project might unravel under questions | “Challenge this claim, one question at a time.” | Clarified points, missing evidence, safe wording, next step |
| **🎯 Role translation** · One project, different target jobs | “Adapt this project to these two JDs and explain each version.” | Shared fact sheet, role versions, rationale and gaps |
| **🧩 Evidence sprint** · A gap needs a bounded task | “I have four hours this week. Close one important evidence gap.” | Deliverable, acceptance criteria, time budget and stopping point |
| **🔄 Decision review** · New feedback changes the picture | “Compare the earlier recommendation with this feedback.” | Prior judgment versus observations, revisions and next action |

Stop a defense session whenever you need. Role versions keep the same facts.
Sprints fit your actual time. Reviews preserve what was unknown rather than
inventing predictions after the event.

**Explore the authored synthetic walkthroughs:** [defense](cases/experiences/defense/example.md) ·
[role translation](cases/experiences/role-translation/example.md) ·
[evidence sprint](cases/experiences/proof-sprint/example.md) ·
[decision review](cases/experiences/decision-review/example.md). Walkthroughs are in Chinese.

```mermaid
flowchart LR
    A["One real experience"] --> B["Questions and evidence"]
    B --> C["Role-specific wording"]
    C --> D["Build one missing proof"]
    D --> E["Return with feedback"]
    E --> B
```

## Bring the rest of your job search, too

| Your question | Junshi's task |
| --- | --- |
| “Which roles should I prioritize?” | Use goals, experience and current JDs to separate primary, secondary and exploratory targets |
| “Interview tomorrow. Only 90 minutes tonight.” | Narrow preparation to the highest risks and 1–3 actions; identify effort to stop |
| “Five days without an HR reply. Follow up?” | Check the conversation, promised dates and workdays; provide timing, a draft and a stop rule |
| “Which offer should I choose?” | Compare personal goals and written terms; identify the preference and unknowns that could reverse it |

## The real contribution stays intact

Team outcomes are not sole implementation. Prototypes are not production. Plans are
not completed accomplishments. A repository or link alone does not prove authorship,
users, or impact.

Junshi preserves sources, contribution and stage, separating **observations, inference,
and unknowns**. Weak evidence leads to narrower wording and a useful evidence task,
not a candidate score or hiring probability. See the [evidence contract](documentation/EVIDENCE.md).

**You control the actions.** Reports can stay in chat; specify a destination when requesting
files. You apply, send messages, negotiate and choose offers. Shareable drafts use only
selected content and are never posted automatically.

**Memory is optional.** Explicit consent enables compact local decision and feedback
records; full resumes, JDs and conversations are excluded by default. View, pause,
revoke and delete are available. The database is unencrypted; deletion cannot guarantee
erasure of external backups. Local storage does not mean offline model inference;
conversation materials remain subject to the host's data policies. See [memory](documentation/MEMORY.md).

<a id="evaluation"></a>

## What has been checked

The current implementation has **204 automated tests**, **13 structured synthetic
benchmark cases**, and limited independent host trials of the four experiences.
These check software behavior and evidence boundaries; they do not establish improved
interview or offer rates.

Known weaknesses remain in existing holdouts. Extraction and handoffs can fail, and
advice can be generic or too cautious. This iteration does not rerun every frozen
evaluation or claim that the earlier real-user pilot gates have been met. Current
hiring information still needs fresh sources.

[Evolution plan](documentation/EVOLUTION_PLAN.md) · [Iteration evaluation](documentation/EVOLUTION_EVAL.md) ·
[Evaluation protocol](documentation/EVAL.md) · [Frozen holdouts](documentation/V023_HOLDOUT_EVAL.md)

<details>
<summary><b>Manual installation</b></summary>

A host with local Skill support and Python 3.10+ are required. Helpers use only the
standard library; the project does not run its own model service.

```sh
git clone --branch main https://github.com/lavine888/Career-Junshi.git
cd Career-Junshi
python scripts/validate_skill.py
python scripts/install_skill.py --target /path/to/your/skills/career-junshi
python /path/to/your/skills/career-junshi/scripts/validate_skill.py --runtime-only
```

Replace `/path/to/your/skills` with a directory your host discovers, including on Windows.
The target folder must be named `career-junshi`; existing targets are refused and preserved.
Installation copies runtime files and license notices, not examples, tests, `.git` or
databases. It does not enable memory.

</details>

<details>
<summary><b>Development, architecture and structured CLI</b></summary>

The host understands context and conducts conversations. Python supplies bounded
structured support, evidence checks, artifacts and optional memory. `route --experience`
selects references; it does not run a conversation or generate a report.

```sh
python -m unittest discover -s tests -v
python scripts/benchmark.py run
python scripts/validate_skill.py
python scripts/junshi.py route --mode interview --experience defense
```

The entrypoint is [SKILL.md](SKILL.md), playbooks are in [references](references), synthetic
materials in [cases](cases), and checks and reports in [tests](tests) and [documentation](documentation).

[Architecture](documentation/ARCHITECTURE.md) · [Extraction](documentation/CONTEXT_EXTRACTION.md) ·
[Decision contracts](documentation/DECISION_INTELLIGENCE.md) · [Optional snapshot import](documentation/INTEGRATION.md) ·
[Issues and ideas](https://github.com/lavine888/Career-Junshi/issues)

The separate [v0.3 Host-First experiment](https://github.com/lavine888/Career-Junshi/tree/experiment/v0.3-host-first)
is incomplete and is not evidence of architectural superiority for this iteration.

</details>

---

[MIT](LICENSE) · [Attribution and reuse scope](documentation/ATTRIBUTION.md).
The lightweight kernel and reference routing draw from [Goutoujunshi](https://github.com/shengjidaguai-china/goutoujunshi);
evidence and career feedback methods draw from [Career Alpha](https://github.com/lavine888/career-alpha).
Upstream license notices are retained.
