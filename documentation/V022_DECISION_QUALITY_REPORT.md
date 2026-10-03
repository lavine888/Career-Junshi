# Career Junshi v0.2.2 — Decision Quality Patch

## Baseline

Baseline: [eea9f0a](https://github.com/lavine888/Career-Junshi/commit/eea9f0aca97b95e0fee06d7bbc0b761889c7dcb0),
135 tests, 13 original structured benchmarks and five frozen integrity/property replays.
Semantic results were Interview PARTIAL, HR PARTIAL, Offer PARTIAL, Direction FAIL,
Ownership PARTIAL. All original 21 synthetic source blocks, rubrics, outcomes,
tests and prior evaluation artifacts remain byte-identical.

The order was baseline freeze → implementation → tests → original 13 → fresh
five-case extraction/CLI/outcomes → fresh host outputs → operator review → semantic
freeze → separate retrieval experiment → delivery documentation. Runtime Skill and
practical-reference instructions are product changes made before generation;
reports, READMEs and contract documentation were updated after retrieval.

## Why this patch

The remaining problem was choosing and compiling useful actions, not relaxing
evidence guards. Missing verification can lower confidence without preventing a
reversible recommendation. Output now distinguishes a clear move, a conditional
move and a genuinely blocked comparison.

## Decision Sufficiency

`recommendation_type` is SUFFICIENT, CONDITIONAL or BLOCKED. The bounded
`decision_sufficiency` carries DECISION_SUFFICIENT / DECISION_CONDITIONAL /
DECISION_BLOCKED, a basis and at most three blocking/reversal unknowns.
Unknown interviewer identity does not block sourced project preparation; missing
Offer goals or meaningful comparison can block ranking. These states do not
authenticate facts, establish success probability or change Claim confidence.

## Career Direction

Optional job-mode `direction.candidates` uses actual contemplated labels and
existing role families, source IDs, strongest proof, largest gap, resume case,
market test and eight qualitative criteria. It outputs primary, secondary,
exploratory and deprioritized categories plus a comparison artifact.

Ordinal comparison considers evidence strength, continuity, defensibility,
role relevance, goal fit, gap cost, optionality and market testability, in that
disclosed order. Low goal fit or a failed constraint excludes the primary line;
weak evidence with high gap cost becomes exploration. The one-resume question
preserves existing defensible evidence. Exact qualitative ties remain ties.
Unknown assessments alone do not produce an arbitrary winner. There is no
universal family ordering, role-name branch or exposed objective fit score.

Rename/reorder and evidence-reversal tests demonstrate that a different family
can win. The fresh case produces Agent Product primary, AI PM secondary and
Technical PM / Quant exploration. The host puts a narrower Technical PM second;
both are admissible sourced hierarchies, not expected-answer matches.

## Offer Decisions

Qualitative priorities can yield `current_preference` without manufacturing
numeric weights. A candidate must dominate the supplied common dimensions at the
first informative priority tier; a real higher-tier tradeoff blocks a lower-tier
brand override. Unknown hard-constraint status permits only a provisional move;
an explicit failure always excludes the option. Existing supplied-weight arithmetic
remains available.

`decision_unknowns` contains the top 1–3 relevant checks, with why, verification
method and reversal condition. The compiler sorts disclosed decisive/important/
confidence-only priorities, not statistically estimated information value. The
Offer artifact now prioritizes these checks instead of dumping every missing field.
The fresh case conditionally prefers B and prioritizes written scope, runway and
manager quality. Other absent high-priority dimensions remain unknown; no universal
runway threshold, missing rating or FX conversion is invented.

## Interview Action Compression

The urgent plan retains at most three primary actions. Optional available-hours
and sourced topic signals improve the focus. Observed questioning is a signal
of attention, while a weakness remains a RISK_HYPOTHESIS. Subjective discomfort
does not become interviewer feedback. The fresh host uses 3 hours + 75 minutes +
45 minutes, retains product judgment and stops unrelated last-minute learning.

## Recruiting Actions

Optional communication stage, tone and known timeline produce a contextual
sendable draft. `follow_up` includes send_now / wait / do_not_contact, timing,
window and draft; its artifact includes the stop condition. With an unknown
calendar, the compiler prepares the message and conditions sending on actual
working days instead of inventing them. Silence remains waiting. Explicit
no-contact and terminal-status guards still suppress the draft. Nothing is sent.

## Ownership Defense

Positioning produces a safe rewritten claim, ownership boundary, 3–5 questions
and `ownership-defense.md`. Product leadership stays visible; team/AI implementation
is not assigned to the individual. Complete reported contributions are retained
separately so a length limit cannot cut a qualifier such as “not sole.”

Project stage, individual Claim stage and personal-contribution stage are separate
declared fields, defaulting to unknown. Legacy Claim.stage does not establish the
other two; supplied completion declarations remain self-report interpretations,
not verified engineering completion. Core audit confidence and stage contracts are
unchanged. The fresh case has project_stage unknown and an unknown personal stage
for the compound implementation claim.

## UNKNOWN Calibration

Explicit personal history remains FACT/self_reported of the account. Verification,
ranking, scope and professional depth may separately remain UNKNOWN. Fresh direction
extraction preserves reported competition participation as FACT/self_reported and
research depth as UNKNOWN. Feelings remain INFERENCE. The extractor-owned source-ID
registry allows profiles to reference supplied uncertainty without storing raw text
or letting the host inject facts/context_sources into the packet's situation.

## Five Mock Case Results

All five fresh model extractions preserve their original source blocks and pass
actual extraction, CLI and artifact generation. All five property checks pass;
that does not substitute for semantic review. [Frozen outputs and evaluations](../benchmark/decision-quality-v022/semantic-summary.json)
include raw before/after host responses, model extraction responses, exact quoted
evidence, structured output, artifacts and execution timestamps/hashes.

| Case | Extraction | Structured decision | Host | Overall |
| --- | --- | --- | --- | --- |
| Interview | PASS | PASS | PASS | PASS |
| HR Silence | PASS | PASS | PASS | PASS |
| Offer | PASS | PASS | PARTIAL | PARTIAL |
| Career Direction | PASS | PASS | PASS | PASS |
| Ownership | PASS | PARTIAL | PARTIAL | PARTIAL |

Supplied interview/ownership outcomes and HR branches A/B ran in explicitly
consented, isolated temporary stores that were deleted. Original decisions stayed
unchanged. Synthetic observations cannot create real-world recurrent risk or
change future preparation via similar memory. A business-round pass with pending
HC is not final hiring success; ownership questioning without a hiring result
remains unknown. No outcomes were invented for Offer or Direction.

Architecture high attention supports only that topic prediction in this case.
Ownership risk_visible remains UNASSESSABLE because questioning does not show an
observed weakness. The finite outcome adapter still maps only architecture and
ownership; the full supplied text retains model-failure questions but evaluation
coverage is incomplete. A separate synthetic not-asked guard probe yields
NOT_OBSERVED; it is not inserted into the supplied outcome. Success never proves
the preparation caused success.

## Before / After Semantic Comparison

| Case | Before | After | Main change | Remaining issue |
| --- | --- | --- | --- | --- |
| Interview | PARTIAL | PASS | Three primary actions; observed topics guide preparation without diagnosing weakness | Long substeps; compiler is less concrete than host |
| HR Silence | PARTIAL | PASS | Contextual draft, conditional timing, observation and stopping window | Employer calendar unknown; social reassurance is a general judgment |
| Offer | PARTIAL | PARTIAL | Compiler conditionally prefers and prioritizes three reversal checks | Host adds an unsupported “two unresolved checks → A” threshold |
| Career Direction | FAIL | PASS | Both paths name a hierarchy, cut options and explain evidence/gaps | Actual current JDs and research depth unverified |
| Ownership | PARTIAL | PARTIAL | Safe claim plus five defense questions and separate stage fields | CLI concatenation is clumsy; host omits explicit three-stage disclosure |

This is fresh synthetic operator review, not independent blind preference grading.
General extraction profiles and explicit installed-SKILL preload were added to the
harness; before/after differences are not isolated code-only causal effects.

## Autonomous Reference Retrieval

After [semantic freeze](../benchmark/decision-quality-v022/SEMANTIC_FREEZE.json), five
fresh installed-Skill runs attempted initial SKILL.md reads without preloading
Skill or references. All five were **BLOCKED_BY_HOST**, confirmed by runtime stderr
`rejected: blocked by policy`. No reference was requested/read; no alternative tool
or bypass was attempted. This is an inner process-policy rejection, not a GitHub
or outer task-approval rejection. [Retrieval report](REFERENCE_RETRIEVAL_EVAL.md)
records the separate evidence. Autonomous retrieval is not verified.

## Tests

154 tests pass: the existing 135 plus 19 new property regressions. Existing tests
were not modified. Checks cover hierarchy, changed labels/evidence, missing-evidence
blocking, failed constraints, sourced qualitative Offer reversal, focused actions,
conditional follow-up drafts, ownership defense/stages, explicit reported history
and compatibility with existing feedback field budgets and long Offer action text.

The original 13 benchmarks have no regression; the old five frozen packet replays
also have no regression. `validate_skill.py` passes, including installation with
the new decision_quality module. `benchmark/decision-quality-v022/replay.py` checks
the frozen new artifacts/properties and source identity without rerunning a model.
Full logs and verification metadata are packaged with the synthetic evaluation.

A preliminary harness rerun was correctly rejected because artifact files already
existed. It was rerun into a fresh final directory; no overwrite guard was weakened.
Final generation needed no extraction repair, rubric change or replacement input.
The final long-input check found that three complete Offer verification methods
could exceed the existing 1000-character action limit. Only that overflow branch
now points to the full comparison artifact. All five frozen decision objects were
recomputed exactly identical; host SKILL/reference inputs were unchanged, so their
fresh raw outputs were retained. Product/result hashes were refrozen, retrieval
was repeated after that freeze, and delivery documentation was finalized afterward.

## Regressions

No original deterministic, structured-benchmark or frozen-property regression was
observed. Old dataset and evaluation hashes remain unchanged. There are still two
overall semantic PARTIALs; passing 154 tests is not five perfect judgments or
evidence of improved real hiring outcomes.

## Known Host-model Limits

Actual fresh contexts use gpt-5.6-sol/high with tools disabled for semantic generation,
installed SKILL and 2–3 relevant references explicitly preloaded. Model execution
VALID means transport completed, not semantic PASS. Generation receives neither
rubrics nor future outcomes. Operator review consults them afterward; it is not an
independent model judge. Account/runtime logs stay private. Public retrieval
derivatives redact only local path prefixes and retain hashes of the originals.

The host can still invent an acceptance heuristic despite general instructions.
Qualitative assessments and source IDs are host declarations: the compiler checks
bindings and bounded contracts, not the truth of each interpretation. Unread
documents, current hiring conditions and autonomous reference loading remain
unverified.

## What was intentionally NOT changed

Five product modes, consent policy, SQLite schema, negative/conditional/hearsay
guards, Claim identity and correction handling, deduplication, stage/confidence
audit boundaries, frozen raw inputs/rubrics/outcomes, prior reports and results.
No Career Score, fixed role order, model configuration switch, private vault read,
real user-memory write, recruiter message or new project recommendation was added.

## Remaining Failures

Offer host fallback threshold is unsupported. Ownership compiler wording mixes
contributions with an audit explanation, and host stage disclosure is incomplete.
Outcome topic mapping is limited. Autonomous retrieval is blocked before routing.
These are retained failures, not silently relabeled as passing behavior.

## Recommended Next Step

Refine general host handling of unsupported acceptance heuristics and three-stage
ownership disclosure, then reevaluate with changed company/role labels and different
evidence distributions. Validate reference routing in a host that permits ordinary
installed-Skill reads. Keep that experiment separate from career judgment and
continue to avoid causal claims about hiring outcomes.
