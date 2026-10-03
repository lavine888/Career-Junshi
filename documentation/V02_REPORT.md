# Career Junshi v0.2 — Decision Intelligence

Local validation date: 2026-10-03. v0.1 baseline: main at
96174ae688071501b219b0343b557299f8d4a9a9. Additive changes; existing Skill, consent,
SQLite schema, five modes and all 61 original tests are preserved.

## What changed

IMPLEMENTED / TESTED: source-located context extraction, reviewable counterarguments
and reconsideration conditions, finite situation tags, bounded similar memory,
topic prediction calibration, guarded recurrent preparation signals, career hypothesis
review, five role packs and project–claim–evidence–story–question mapping. Added
fixed benchmark packets, a reproducible structured report and evaluation protocol.
The first Markdown view gives recommendation and actions before reasons; detailed
facts and inferences are available through --details or JSON.

## Why v0.2 exists

v0.1 safely gave next actions, but source strings lacked a formal raw-context bridge,
saved outcomes did not affect the next comparable decision, and deterministic tests
could be mistaken for a decision-quality evaluation. v0.2 makes those boundaries
explicit and introduces a small inspectable feedback path without adding a service.

## Context extraction

IMPLEMENTED / TESTED: session sources, exact spans or Unicode locators, source IDs
and types, epistemic labels, self-report confidence, preferred/required distinction
and freshness. Seven dedicated extraction tests plus integrated v0.2 coverage check
team leadership versus sole contribution, process update versus pass, feeling versus
fact, source mismatch, forged excerpt and stale context. Raw source documents are
not saved by the extractor or decision-memory handoff. Semantic faithfulness still
requires the host. See [contract](CONTEXT_EXTRACTION.md).

## Decision benchmark

IMPLEMENTED / TESTED: [13 fixed synthetic cases](../benchmark/cases.json), each with
source-labeled materials, context notices, prohibited assumptions, tradeoffs, multiple
acceptable choices, bad choices, actions, stop conditions and ten dimensions.
[Structured report](../benchmark/structured-report.json): 13/13 covered, deterministic
hard rules pass, structured properties pass, regressions none. Counterarguments,
reconsideration and rejected-option reasons are included in the checks.

Independent host-input and reviewer-rubric packets can be generated repeatedly.
Host submission validation requires actual response excerpts and explicit metadata;
it does not grade or authenticate those annotations. [Protocol](DECISION_BENCHMARK.md).

## Counterfactual reasoning

IMPLEMENTED / TESTED: recommendation exposes supporting_evidence,
strongest_counterargument, reconsider_if and confidence_basis. decision_trace records
the inspectable situation, sources, bottleneck, options, chosen move, rejected options,
reasons and reconsideration conditions. Recruiter delay considers holidays, batch
recruitment and approval as alternatives; offer comparison acknowledges subjective
weights and uncertain team conditions. These are mode defaults requiring host
adaptation, not hidden model reasoning or a guarantee of personalized judgment.

## Similar memory

IMPLEMENTED / TESTED: active-consent-only recall selects at most three recent pairs
with matching mode, role family, stage and overlapping finite tags; ranks by overlap,
situation type and recency. Latest outcome per decision only. Old, untagged,
unrelated and correction-affected decisions are excluded. Only materially used
history enters the recommendation evidence. Quant history cannot alter an AI Product
decision. No vector index, automatic profile scan, implicit consent or raw persistence.

## Outcome calibration

IMPLEMENTED / TESTED: expectations concern high attention or visible topic risk.
Observations yield SUPPORTED_THIS_CASE, CONTRADICTED_THIS_CASE, NOT_OBSERVED or
UNASSESSABLE. A metric not asked is not disproved; missing observations stay
unassessable. Passing and user explanations remain separate from causal claims.
Outcome metadata must match its parent decision. No hiring probability is generated.

## Recurrent signals

IMPLEMENTED / TESTED: three distinct comparable reported real-world events and
sources are needed; at least two explicit same-topic risks raise preparation priority.
The next question ladder actually changes and exposes the historical basis. One or
two outcomes, duplicate recaps and synthetic events cannot form RECURRENT_SIGNAL.
Public tests declaring real_world are **synthetic gate fixtures**, not observed real
events. Capability labels, confidence upgrades and causal hiring conclusions are absent.

## Career hypothesis

IMPLEMENTED / TESTED: source-linked supporting and counterevidence, review window,
KEEP / REFINE / PIVOT. One rejection stays KEEP; repeated comparable local gaps
suggest REFINE. PIVOT review requires five comparable core counterexamples and a
sourced higher-value alternative with checked constraints and confounders. Duplicate
or incomparable feedback cannot cross the gate. This is a conservative review rule,
not a statistical estimate or automatically executed career switch.

## Role packs

IMPLEMENTED / TESTED: five compact packs for AI Product, Agent Product, Technical
Product / Technical PM, AI Application / Solutions and Quant / AI × Quant. Each has
exactly six specified fields. The same project's claim scope and evidence stay
unchanged while role emphasis differs. Story quality checks tension, personal
decision, ownership, tradeoff, result-source reference and learning; team-only
material cannot produce a defensible personal draft. Source truth and prose quality
remain host responsibilities.

## Decision quality eval

TESTED: Level 1 contracts and Level 2 structured properties.
MODEL-EVALUATED: not claimed; independent Level 3 blind evaluation NOT_RUN.
REAL-WORLD-OBSERVED: no recruiting outcome observed; Level 4 outcome evaluation NOT_RUN.
An informal builder-authored private-context response exists locally, but is not an
independent benchmark run. No diagnostic Career Score or fabricated model rating.
[EVAL.md](EVAL.md) records coverage, limitations and a repeatable next evaluation.

## Tests

108 tests passed: 61 unchanged original tests, seven extraction tests and 40 v0.2
tests. Installed-runtime tests run the actual CLI and memory lifecycle. New A–J
coverage includes extraction, counterfactuals, similar and irrelevant memory,
prediction support and non-observation, recurrence gate, correction, freshness and
role translation. The structured benchmark uses an explicit fixed clock; no fixtures
or skipped checks are presented as live integration success.

Commands: `python -m unittest discover -v`, `python scripts/validate_skill.py`,
`python scripts/benchmark.py run --now 2026-10-03T12:00:00+08:00`.

## Private real-case findings

A bounded local dry-run used three selected private documents. Session packet,
source map, structured decision and builder review stay outside the repository.
No raw/private input, original locator, personal identifier or project history is
published. Anonymous findings: the source/self-report boundaries survived extraction;
current role eligibility and engineering contribution remained unknown; role ordering
and two-week prioritization required host judgment beyond the structured planner.
No recruiting outcome, action acceptance or execution was available in the selected
context. Preparation artifacts are not hiring success. No private data became a
public golden case or a real outcome fixture.

## Regressions

Original baseline: 61/61 passed before changes. Current: those 61/61 remain intact
and passed. Default memory stays off; pause/revoke gates and append-only history
remain. Corrections atomically append the new source and weaker current claim,
identify linked decisions and exclude them from recall without editing history.
Runtime installation preserves no-overwrite behavior and includes new helpers and
role data, while excluding cases, tests, databases and private input.

## Known limitations

Context guards are not a general semantic extractor or receipt verifier. Recurrent
real_world flags and observation classes are operator attestations. Recency and
three-event windows are conservative defaults. Older untagged records need manual
review; old decisions without claim IDs cannot be attributed to corrections. A
comparison key or expected-value assessment can be wrong. Supporting evidence in
career hypotheses remains reviewer-visible rather than statistically weighted.
No independent semantic evaluation or real-world effectiveness has been demonstrated.

## What remains host-model dependent

Faithful paraphrases, material conflicts, role order, decisive questions, personalized
competing options, matching comparability keys, narrative stories, current-source
checks and observed-risk interpretation. A source span or nonempty personal-decision
field does not establish truth. Templates should be replaced when the sources support
a different bottleneck or option. See the current failures in [EVAL.md](EVAL.md).

## What should NOT be built next

No backend, user account, payment, dashboard, large ontology, job crawler, vector /
graph database, agent swarm, hiring probability, automatic career pivot or polished
resume claims unsupported by evidence. More modules do not establish decision quality.

## Recommended v0.3

PLANNED: independent blind host evaluation against held rubrics, with source-backed
failure analysis; then a small consented real-world cohort measuring explicit acceptance,
action execution, reconsideration, repeated-risk windows and outcome return with
counts and denominators. Improve generic alternatives and role prioritization only
where observed failures justify it. Collect actual feedback before claiming benefit.
