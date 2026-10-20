<div align="center">

![Career Junshi — Evidence-backed experience, actionable next steps](assets/readme-hero-editorial.png)

# Career Junshi · 求职军师

### Turn real experience into a resume you can defend.

Rewrite a resume, rehearse an interview, build evidence or choose an offer. Start where you are stuck.

[![MIT](https://img.shields.io/badge/License-MIT-D8B466?style=flat-square)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-627EAA?style=flat-square)
[![Memory opt-in](https://img.shields.io/badge/Memory-opt--in-83D5BA?style=flat-square)](documentation/MEMORY.md)

[Get started](#start) · [Core experiences](#experiences) · [Resume export](#resume-export) · [Source library](#library) · [中文](README.md)

</div>

Career Junshi is a career workflow for Codex and other hosts that support local Skills.
Bring a real project, a JD or a decision. Leave with usable wording, an evidence-grounded judgment
and 1–3 useful next actions.

<a id="demo"></a>

## See one project claim improve

> **Resume claim:** “Independently built a production RAG platform, improving accuracy by 30%.”
>
> **Actual account:** A team course prototype. You wrote evaluation scripts and classified
> failures; a teammate built the service. Ten internal questions, no baseline, no production users.

Junshi starts with the actual work, one question at a time:

```text
Junshi: For those ten questions, what made an answer count as a failure?

You: My teammate and I agreed on three checks: missing citations,
     incorrect cited passages, or contradictions with the document.
     I put the checks in the script and recorded the results.

Junshi: Your contribution is clearer. It remains your account;
        the code and evaluation records still need checking.
```

**You leave with usable wording that keeps ownership clear:**

> Contributed to a team RAG course prototype, owning evaluation scripts and failure
> classification; evaluated ten internal questions against team-agreed criteria and
> recorded missing citations, incorrect passages, and contradictions with source documents.

<sub>Adapted from an actual host trial using anonymous synthetic material, not a real candidate or hiring outcome. [Trial record](documentation/EVOLUTION_EVAL.md) · [Separately authored walkthrough](cases/experiences/defense/example.md)</sub>

<a id="start"></a>

## Start in two steps

### 1. Install the Skill

Send this to a host that supports local Skills:

```text
Install career-junshi from the main branch of
https://github.com/lavine888/Career-Junshi using the repository installer.
Check for an existing installation first; do not overwrite it.
Validate the installed runtime files. Do not enable persistent memory.
```

<details>
<summary>Manual installation and requirements</summary>

Use a host with local Skill support. The installer and helpers use Python 3.10+
and its standard library.

```sh
git clone --branch main https://github.com/lavine888/Career-Junshi.git
cd Career-Junshi
python scripts/validate_skill.py
python scripts/install_skill.py --target /path/to/your/skills/career-junshi
python /path/to/your/skills/career-junshi/scripts/validate_skill.py --runtime-only
```

Replace `/path/to/your/skills` with a directory your host discovers, including on Windows.
The target folder must be named `career-junshi`; existing targets are preserved and refused.
Installation copies runtime files and license notices, excluding examples, tests, `.git`
and databases. It does not enable memory.

</details>

### 2. Bring one real experience

```text
Use $career-junshi for a resume defense session.

My resume says: ...
What I actually did: ...
Target role / JD: ...
Next interview or deadline: ...

Ask one question at a time and follow my actual answers.
Finish with usable resume wording, evidence gaps and the most useful next step.
```

A complete resume is optional. Ask to rewrite a paragraph or prioritize tonight's preparation.
Junshi uses supplied materials first and asks only for consequential missing information.
Persistent memory can stay off.

<a id="experiences"></a>

## Four core experiences

| Where you are stuck | Ask this | What you get |
| --- | --- | --- |
| **🛡 Resume defense** · A project might unravel under questions | “Challenge this claim, one question at a time.” | Clear ownership, evidence gaps and usable wording |
| **🎯 Role translation** · One project, different target jobs | “Adapt this project to these two JDs and explain each version.” | Shared facts, role versions and editing rationale |
| **🧩 Evidence sprint** · A gap needs a bounded task | “I have four hours this week. Close one important evidence gap.” | A deliverable, acceptance criteria, a budget and a stopping point |
| **🔄 Decision review** · New feedback changes the picture | “Compare the earlier recommendation with this feedback.” | Prior judgment versus observations and a revised next action |

Enter at any point and stop whenever you need. Role versions keep the same facts.

Authored synthetic walkthroughs, in Chinese: [defense](cases/experiences/defense/example.md) ·
[role translation](cases/experiences/role-translation/example.md) ·
[evidence sprint](cases/experiences/proof-sprint/example.md) · [decision review](cases/experiences/decision-review/example.md)

<a id="resume-export"></a>

## Settle the content, then export the resume

```text
Prepare a Chinese single-column resume for this JD, aiming for one page.
Preserve real contributions and explain material cuts. Export LaTeX and plain text
to a new private directory I specify. Compile a PDF if local XeLaTeX is available.
Report content, compilation, PDF text-layer and actual visual checks separately.
```

The export keeps **LaTeX source, plain text, sourced content data and a verification report**.
Drafting and review precede formatting; independent review depends on host capabilities.

<details>
<summary>PDF compilation, page budget and file location</summary>

Source export needs no LaTeX installation. PDF compilation requires local XeLaTeX,
template fonts and packages. Choose one or two pages; the helper never silently
cuts content or shrinks fonts. Missing compilation or visual review is reported;
text-layer checks do not certify compatibility with every ATS.
Private output goes to a new directory you specify outside Git and the installed Skill.

[Synthetic source-export example](cases/experiences/resume-export/example.md) ·
[Full export workflow](references/practical/resume-export.md)

</details>

## More situations: ask directly

| Ask this | Junshi helps you |
| --- | --- |
| “Which roles should I prioritize?” | Use goals, experience and current JDs to choose primary, secondary and exploratory targets |
| “Run a mock interview for this JD. State what this question observes.” | Choose a job criterion, ask one question and respond to the actual answer |
| “Second interview tomorrow. Only 90 minutes tonight.” | Prioritize the highest risks, 1–3 actions and a stopping point |
| “Five days without an HR reply. Follow up?” | Check the conversation, promised dates and workdays; draft a follow-up with timing and a stop rule |
| “Which offer should I choose? What needs checking first?” | Compare goals and written terms, verify decisive unknowns, and prioritize actual fee or identity risks |
| “Two resumes got different feedback. Design a trial within one hour this week.” | Define one question, comparable opportunities, one intended change and an observation window |
| “I have 15 minutes and keep changing templates. Help me start.” | Produce one inspectable result with a cue, a fallback and a firm stopping point |

<details>
<summary>Advanced use: wording checks, checkpoints and outcome-blind review</summary>

- **Wording audit:** “Check verbs, ownership and causality. Change only unsupported claims.”
  Keep supported leadership; separate before/after observations from personal attribution.
  [Illustration](cases/experiences/wording-audit/example.md)
- **Checkpoints:** “Pause and give me a copyable checkpoint.” Paste the record next time to
  resume; checkpoints stay in chat by default. [Illustration](cases/experiences/defense-resume/example.md)
- **Outcome-blind review:** In a fresh chat without the result, supply interview observations,
  freeze an initial judgment, then reveal the outcome. Removing text cannot make the same
  conversation forget; known results use ordinary review.
  [Illustration](cases/experiences/outcome-blind-review/example.md)

Application trials preserve versions, denominators and observation windows. Different roles
or channels do not establish a template effect; pending applications stay pending.
[Application trial](cases/experiences/job-search-experiment/example.md) ·
[Action-start card](cases/experiences/action-start/example.md)

</details>

<a id="library"></a>

## A source library with explicit limits

**18 distinct studies and official documents across eight topics:** job search, career choice,
resumes, interviews, negotiation, offers, workplace rights and hiring safety.
A work used for multiple topics is counted once.

Each card records source type, actual reading depth, scope, limits and version.
Ask **“What supports this advice, and where does it not apply?”** to retrieve relevant cards.

[Browse the index](references/knowledge/08-research-and-application.md).
Sources inform method choices; individual legal questions still need current applicable authority.

## Real contributions and user control

- **Preserve facts.** Keep sources, ownership and project stage clear; distinguish observations,
  inference and unknowns. Weak evidence leads to narrower wording and a useful evidence task.
  [Evidence contract](documentation/EVIDENCE.md)
- **You control actions.** Reports stay in chat unless you request files and specify a destination.
  You apply, send messages, negotiate, accept offers and publish material.
- **Memory is opt-in.** Explicit consent enables compact local records; full resumes, JDs and
  conversations are excluded by default. View, pause, revoke and delete are available.
  [Memory guide](documentation/MEMORY.md)

The local database is unencrypted; deletion cannot erase external backups.
Conversation materials remain subject to the host's data policies.

<a id="evaluation"></a>

## Verification progress

**237 automated tests, 13 structured synthetic benchmark cases** and limited independent
fresh-context trials cover installation, routing, evidence handling and interactions.
They do not establish improved interview or offer rates.

<details>
<summary>Evaluation records and known limits</summary>

| Scope | Record |
| --- | --- |
| Four core experiences | [Core evaluation](documentation/EVOLUTION_EVAL.md) |
| Wording, checkpoints and outcome-blind review | [Refinement evaluation](documentation/REFINEMENT_EVAL.md) |
| Resume source export and PDF verification limits | [Export evaluation](documentation/RESUME_EXPORT_EVAL.md) |
| Application trials, action starts and research transfer | [Research-workflow evaluation](documentation/RESEARCH_EVOLUTION_EVAL.md) |
| Sources, structured interviews and offer checks | [Career-library evaluation](documentation/CAREER_LIBRARY_EVAL.md) |

Existing frozen cases retain extraction, handoff and generalization weaknesses.
They have not all been rerun, and the earlier real-user pilot gates are not claimed as met.
Current hiring, salary and company facts need fresh sources. The Skill supplies neither
an overall candidate score nor a hiring probability.

[Evaluation protocol](documentation/EVAL.md) · [Frozen holdouts](documentation/V023_HOLDOUT_EVAL.md) ·
[Experience plan](documentation/EVOLUTION_PLAN.md)

</details>

<details>
<summary>Development, architecture and structured CLI</summary>

The host understands context and conducts conversations. Python supplies bounded structured
support, artifacts and optional memory. `route --experience` selects references;
it does not run a conversation or generate a report.

```sh
python -m unittest discover -s tests -v
python scripts/validate_skill.py
python scripts/benchmark.py run
python scripts/junshi.py route --mode interview --experience defense
python scripts/junshi.py sources --topic interview
python scripts/junshi.py sources --id R7
```

[Skill entrypoint](SKILL.md) · [Playbooks](references) · [Synthetic cases](cases) · [Tests](tests) ·
[Architecture](documentation/ARCHITECTURE.md) · [Extraction](documentation/CONTEXT_EXTRACTION.md) ·
[Decision contracts](documentation/DECISION_INTELLIGENCE.md) · [Optional snapshot import](documentation/INTEGRATION.md) ·
[Issues and ideas](https://github.com/lavine888/Career-Junshi/issues)

The separate [v0.3 Host-First experiment](https://github.com/lavine888/Career-Junshi/tree/experiment/v0.3-host-first)
is incomplete; its results do not establish an architectural conclusion for the current version.

</details>

---

[MIT](LICENSE)
