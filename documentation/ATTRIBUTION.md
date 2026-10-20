# Attribution and source audit

Initial audit: 2026-10-03; resume-workflow source added 2026-10-20.
This project is independent of the sources below.

## Goutoujunshi

[Repository](https://github.com/shengjidaguai-china/goutoujunshi), audited commit
`6db7354a4002dc7c448a9c87ffdad8132570c9d3`.
Inspected SKILL.md, README, reference hierarchy, LICENSE, and the memory / validator
implementations. MIT copyright: 2026 powerycy.

Inspired by / adapted from Goutoujunshi: lightweight skill kernel, Knowledge /
Practical routing, first-use extraction, consent-gated bounded local memory,
action-first interaction, observation windows and stop conditions. The directory
organization is adapted; the Python implementations and career references are
newly written, not copies of its scripts. The full upstream MIT notice is retained
in [licenses/Goutoujunshi.txt](licenses/Goutoujunshi.txt), including in installations.
No relationship content, dating scripts or PUA material is reused.

On 2026-10-20, also inspected the supplied knowledge/19 bibliography
(file blob `5bf54af364fe02c9170d55b23795feba565660ee`). Its separation of
research, theory and practice informed the optional career research index.
The relationship bibliography was not imported; career sources were checked
individually, with reading depth and transfer limits recorded in that index.

## Career Alpha

[Repository](https://github.com/lavine888/career-alpha), audited local commit
`c51661432fd54a0b3d4e10a5bfc4f409ef0210e1`.
Inspected the shared Claim–Evidence Ledger, interview / offer workflows and the
eight method entrypoints. Local untracked work was not imported.
Reused conceptually: evidence before wording, four confidence levels, ownership
boundaries, question ladders, career hypotheses and market feedback. Career Junshi
offers one situation decision, not concatenated Career Alpha outputs. Methods are
internal labels; Career Alpha need not be installed. Its MIT notice is retained in
[licenses/Career-Alpha.txt](licenses/Career-Alpha.txt).

## LavineOS

Only architectural documentation and object-schema definitions were inspected
locally. No personal profiles, decisions, events, resumes, vault contents or source
code were copied. No public revision could be established for that local source.
Conceptual influence: bounded task retrieval; separate Situation, Decision and
Outcome; original-source provenance; retrieval does not upgrade evidence.
The optional integration is a documented explicit snapshot contract, not sync.

## AI Job Search

[Repository](https://github.com/MadsLorentzen/ai-job-search), inspected commit
`84808eebc13fa7b781b2ede034120c092776668d` on 2026-10-20.
Inspected the README, MIT license, apply workflow, application-reviewer instructions,
example CV, PDF text verifier and layout verifier. The draft / independent-review /
compile / inspect loop and checking the PDF text layer informed the resume-export
workflow. The exporter and template are independently written; no upstream scripts,
candidate profiles or moderncv template code were copied.

Career Junshi retains its own evidence levels, consent boundaries, qualitative
decisions and configurable page budget. It does not import automatic profile writes,
a fixed two-page requirement, fit scores, job scraping or account integrations.
The full MIT notice (2026 Mads Lorentzen) is retained in
[licenses/ai-job-search.txt](licenses/ai-job-search.txt), including installations.

## Career Junshi additions

Career Situation Model; executable career claim guards; five situation playbooks;
unified decision output; Decision → Outcome memory with causal uncertainty;
human / Codex action contract; three synthetic demos and integrity regressions.
These are newly implemented here. Passing tests establishes software behavior,
not successful job applications or superiority to the reference projects.
