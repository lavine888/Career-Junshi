# Career Junshi MVP Report

Date: 2026-10-03. Version: v0.1 MVP.

Status vocabulary: IMPLEMENTED = executable capability / completed Skill instructions;
TESTED = checks actually run; DOCUMENTED = contract only; PLANNED = future work.
Synthetic fixture success does not establish a career outcome or model reliability.

## Product

IMPLEMENTED: independent career decision Skill, focused on “我现在到底该怎么办？”
Five modes, one recommendation, 1–3 actions, observation and stop / pivot conditions.
No UI, SaaS backend, auth, payments, job scraper or mandatory external service.

## What was learned from Goutoujunshi

Audited upstream commit `6db7354a4002dc7c448a9c87ffdad8132570c9d3`: lightweight kernel,
Knowledge / Practical split, progressive loading, first-use extraction, bounded
consent-gated memory, action-first answers and observation / stop windows.
These patterns inform structure; no relationship content or script code was copied.

## What was reused conceptually from Career Alpha

Audited local commit `c51661432fd54a0b3d4e10a5bfc4f409ef0210e1`: Claim–Evidence Ledger,
confidence, ownership, interview ladders, opportunity costs and market feedback.
The local untracked work was preserved and not imported. KEEP / REFINE / PIVOT is
a bounded hypothesis-review vocabulary here; it is not claimed as copied code.

## What is original

Newly written career-specific claim guards, Career Situation Model, unified decisions,
Decision / Outcome local records, human action ownership, runtime installer, material
generation and ten executable scenario checks. “Original” describes this implementation,
not a claim that each underlying idea has never been explored elsewhere.

## License / Attribution

IMPLEMENTED: MIT (2026 Lavine), full upstream MIT notice (2026 powerycy) and Career
Alpha notice preserved, including in installed copies. Inspired by / adapted from
Goutoujunshi, with conceptual vs implemented reuse separated in
[ATTRIBUTION.md](ATTRIBUTION.md). No private vault content is included.

## Architecture

IMPLEMENTED: host-driven [SKILL.md](../SKILL.md), 20 references, Python 3.10+ standard
library, local SQLite, explicit structured CLI. The host performs natural-language
understanding and real source verification. Scripts normalize and guard structured
context, create artifacts and persist approved compressed records.
[Architecture details](ARCHITECTURE.md).

## SKILL behavior

IMPLEMENTED instructions: retrieve supplied material before asking; handle deadlines;
identify the actual Direction / Evidence / Positioning / Interview / Market / Timing
bottleneck; return one answer; keep internal labels behind the product; record outcomes.
TESTED: native Skill frontmatter validation and current build-session demonstrations
of the three synthetic requests. Those demonstrations are authored by the build Agent,
not an independent agent or repeated model evaluation. No actual interviews occurred.

## Reference routing

IMPLEMENTED / TESTED: five deterministic structured routes select 2–3 references;
rejection replaces follow-up. The host routes natural language by situation and
urgency, reading only 1–3 task-relevant resources. Tests verify paths and route budget,
not the host's ability to classify every paraphrase.

## Evidence model

IMPLEMENTED / TESTED: claim, confidence, evidence, ownership, stage, risk and safe wording.
Plans stay PLANNED; weak requested VERIFIED is capped. Checks cover ownership,
leadership, authorship, production, real-world results, metrics and awards. Text guards
are intentionally incomplete; operator receipts are not authenticated by the script.
[Evidence contract](EVIDENCE.md).

## Situation model

IMPLEMENTED / TESTED: situation, timezone-aware urgency, sourced facts, inferences,
unknowns, goal, bottleneck, options, recommendation, reasons, actions, observation,
stop and pivot. Offers use user-supplied weights and explicit constraints; unknown
ratings are not imputed. HR day counts are supplied, not holiday-calendar calculations.

## Memory model

IMPLEMENTED / TESTED: profile, target roles, projects, claims, companies, applications,
interview events, feedback, decisions and outcomes. Default off; explicit consent,
recall / update / view / pause / revoke / delete. Bounded fields, 200-record total,
per-kind limits, transactions, version gate and no silent history eviction.
TESTED on a real SQLite file with concurrent writes and a fresh store instance;
no mock persistence. Logical deletion retains revocation metadata and does not
promise to erase backups. [Memory contract](MEMORY.md).

## Decision loop

IMPLEMENTED / TESTED: compact Situation / Decision / Why / Expected Outcome / windows
saved with stable IDs; immutable history; outcomes require the same subject and an
existing decision. Updates do not silently replace prior decisions.

## Outcome loop

IMPLEMENTED / TESTED: hard outcome, sourced observations, user interpretation, agent
interpretation, unknowns and limited learning. Passing is never causal proof; waiting
cannot be changed by a user interpretation of rejection. No automatic profile upgrade.
Deleting a Decision removes linked Outcomes as documented.

## Career Alpha adapter

IMPLEMENTED / TESTED: internal plans using radar / wedge / proof / position / interview /
offer; build / contributor only for nonurgent job evidence gaps. No Career Alpha
installation or mechanical concatenation. Comparable gap review deduplicates sources;
five repeated cohort observations can suggest REFINE, never automatic PIVOT.

## LavineOS optional integration

DOCUMENTED: explicit compact context snapshot, stable IDs, source fingerprint,
timestamps and trust boundaries. Only local architectural docs / schema definitions
were audited. No private candidate data was read or copied. No sync, import,
writeback or hardcoded private path is implemented. [Contract](INTEGRATION.md).

## Codex execution

IMPLEMENTED / TESTED: proposed human / codex actions validated by kind; genuine local
Markdown materials created; existing outputs preserved. No sending, applications,
negotiation or Offer acceptance. Question ladders use real contribution slots;
the helper cannot invent technical answers. [Action contract](ACTIONS.md).

## Regression tests

TESTED: 61 unittest checks on Windows, Python 3.11.0. Ten product scenarios cover:
resume + JD + tomorrow's interview; three-day silence; unsupported production;
unclear team ownership; two Offers; rejection without feedback; rejection with depth
feedback; SWE → AI PM; hackathon claim; unknown direction. Additional checks cover
all requested integrity regressions, claim status ceilings, promise dates, no-contact,
weights / constraints, immutable history, capacity, consent and installed CLI failure paths.

## Demo results

TESTED: three structured CLI runs at fixed scenario time `2026-10-03T12:00:00+08:00`:

- [Interview](../cases/interview/output.md): evidence bottleneck, riskiest claim,
  lower wording, five-layer defense, three actions and observation / stop / pivot.
- [Follow-up](../cases/follow-up/output.md): one draft, waiting remains waiting,
  human sends, adjustable working-day observation and investment stop line.
- [Offer](../cases/offer/output.md): supplied goal and constraints select synthetic A;
  changing the user's priority to compensation selects B (scenario test).

Actual generated files are under each case's `artifacts/`. Separate `host-output.md`
files demonstrate unified natural-language answers in this build session. Both sets
are labeled synthetic; neither proves a real job result or independent model quality.

## Validation

TESTED commands: unittest discovery; full package validator; runtime-only validator;
bundled skill-creator quick validator; installation into an isolated temporary Skill
directory; subprocess CLI from a different working directory; consent → update → recall
→ revoke → view → delete against actual SQLite; all three demo artifact paths.

Phase checkpoints: source audit / bootstrap; Skill format; references; 11 claim checks;
25 route / decision checks; 34 memory checks; 39 loop checks; 42 adapter checks;
44 action checks; 54 scenario checks; 55 including leadership; 61 including installation.
Before executable tests existed, checks were limited to audit / format; no zero-test
run is presented as behavioral validation. Required-file failures were resolved by
completing the contracts and demo outputs, not bypassing the validator.

Python 3.10+ compatibility is intended by syntax / standard library usage. Only
Windows / Python 3.11 was executed locally; other OS / Python combinations are unverified.

## GitHub commit

Delivery target: [lavine888/Career-Junshi](https://github.com/lavine888/Career-Junshi),
branch `main`. See [commit history](https://github.com/lavine888/Career-Junshi/commits/main).
The final delivery message records the actual commit SHA and remote verification.
Local tests or a local commit alone do not establish remote publication.

## Known limitations

No independent repeated model evaluation or real career outcome study. Host reasoning
may vary; deterministic decisions are conservative structured support. Receipt trust
is operator-based, not cryptographic source authentication. Strong-word regex guards
can miss paraphrases or overflag negation. No live market feed / public holiday
calendar. Offer ratings are subjective. No encrypted memory, correction history for
ordinary profile updates, secure erasure or automatic full-document storage. The
optional adapter is documentation only. Artifacts with missing sources are clearly
marked incomplete, not evidence verification completed.

## What should NOT be built next

Avoid SaaS backend, login, payments, scrapers, email / LinkedIn automation, extensions,
vector / graph databases, cloud sync, mobile / voice apps, swarms and a large workbench.
These add surface area before the core decision behavior is independently evaluated.

## Recommended v0.2

PLANNED: blinded host evaluations with synthetic paraphrases / adversarial documents;
explicit source-check receipt review; compact memory correction / export UX; stronger
offer sensitivity explanations; narrow optional snapshot schema validation. Admit
real cases only with explicit permission and anonymization. Do not equate conversion
rate changes with strategy causality.
