# Evaluation

Evidence status as of 2026-10-03: IMPLEMENTED / TESTED and MODEL-EVALUATED for the
limited frozen synthetic host comparison below. REAL-WORLD-OBSERVED: NO.
Private real-context dry-run remains a builder review, not a recruiting outcome study.

v0.2.1 has 123 tests and a [completed 15-pair model comparison](MODEL_EVAL_REPORT.md):
30/30 valid generations on gpt-5.6-sol/high and 15/15 version-hidden reviews by the
different model gpt-6-astra/high, tools disabled. v0.2.1 wins 2, v0.1 wins 0, ties 13;
one hard-failure label per version, with no reduction. The exact scope is Skill
instructions plus the same routed reference paths/count budget, not runtime helper
execution or installed-Skill discovery. Cross-opportunity identity and deduplication
are not assessable from these inputs. [Raw evidence and protocol](../benchmark/model-eval/README.md).

The original gpt-6.1-sol model-access rejection remains in the manifest as a zero-output
historical attempt. Replacement was explicitly authorized and actually probed before
generation; it stayed fixed for both snapshots. No private context was evaluated.
See [V021_REPORT.md](V021_REPORT.md) for corrected runtime boundaries.

## What is tested

Level 1 checks extraction spans and provenance, explicit epistemic errors, claim
boundaries, action ownership, consent, immutability, duplicate events, recency and
installed-runtime behavior. Level 2 tests fixed structured decisions, counterarguments,
reconsideration conditions, bounded relevant recall, prediction states, recurrent
preparation priority, hypothesis gates, freshness and role translation.

Original 61 v0.1 tests remain intact. Added extraction and v0.2 tests use synthetic
fixtures. Some memory fixtures deliberately declare real_world to exercise gates;
they are test data and supply **zero real-world evaluation observations**.
No failure is ignored to obtain a passing result.

## Golden cases and dimensions

[13 fixed synthetic cases](../benchmark/cases.json) cover unknown direction, SWE to
AI product, JD evaluation, prototype/production conflict, team leadership, tomorrow's
interview, technical rejection, recruiter silence with calendar ambiguity, offer
tradeoffs, negotiation without written terms, direction/constraints conflict,
positioning despite strong project evidence, and weak defense despite a strong resume.
Each case has source-labeled material excerpts, notices, forbidden assumptions,
tradeoffs, multiple acceptable recommendations, bad recommendations, required actions,
stopping conditions and all ten dimensions. No single golden sentence is required.

| Diagnostic dimension | Reviewer checks |
| --- | --- |
| Situation Understanding | Correct urgency, stage and context; decisive questions only |
| Evidence Discipline | Sources and personal scope; no invented achievements or status |
| Bottleneck Identification | Evidence versus expression, direction, timing or market |
| Recommendation Clarity | A clear conditional first choice, without overclaiming |
| Actionability | One to three feasible actions with owner and concrete artifact |
| Opportunity Cost Awareness | Time budget, competing options, stopping investment |
| Uncertainty Calibration | Alternatives and decisive unknowns; no hiring probabilities |
| Stop / Pivot Quality | Observable review triggers, stopping lines and guarded pivot |
| Personal Context Usage | Relevant source context without unrelated or stale contamination |
| Outcome Learnability | Topic predictions and observations; no success-causes-strategy claim |

Ratings are PASS / PARTIAL / FAIL / UNASSESSABLE, each with response excerpt,
source reference and diagnostic. Do not combine them into a Career Score.
[Benchmark protocol](DECISION_BENCHMARK.md) explains lower levels and host packets.

## Reproduce

```sh
python -m unittest discover -v
python scripts/validate_skill.py
python scripts/benchmark.py run --now 2026-10-03T12:00:00+08:00
python scripts/benchmark.py packet --output /new/private/eval-packet
python scripts/benchmark.py validate-host --input /private/reviewed-run.json
```

[Structured report](../benchmark/structured-report.json) records coverage, hard rules,
field properties and regressions. Repeats use the same clock, cases, Skill revision
and interpreter. The structured report retains its historical Level 3/4 NOT_RUN markers; the completed
instruction/reference model diagnostic is recorded separately in benchmark/model-eval.
Installed runtime excludes development cases; provide `--cases /checkout/benchmark/cases.json`.

For Level 3, run each host-input independently with the installed Skill, with rubric
hidden. Record model/version/settings, Skill commit, run ID, clock, tools and missing
context. Save complete outputs. A separate reviewer reads the held rubric and raw
materials, quotes the responses and records failures. validate-host checks structure
and excerpts; it cannot authenticate model execution or reviewer independence.

## What is not tested and current failures

- One separate-model blind comparison is complete, with twelve diagnostic dimensions;
  no independent human certification or repeated-sample reliability claim. Most pairs
  tied and hard-failure labels did not decline. Cross-opportunity/history cases remain
  missing from host coverage; exact quote validation does not certify reviewer judgment.
- Local counterarguments are mode defaults, not a guarantee of situation-specific
  competing options. The host must replace generic wording when context warrants it.
- The structured planner alone did not select a personalized role order in a private
  multi-project dry-run. Source-faithful main/secondary ordering depended on host review.
- Span checks catch explicit errors but cannot validate every paraphrase, personal
  decision, comparable-event key, observation label or source receipt.
- Old untagged memory is not automatically migrated. Three-event windows can miss
  longer patterns. Reported real-world flags are attestations, not authenticated events.
- No real action acceptance, execution or recruiting outcome was available in the
  selected private context. No live result calibration or causal benefit is claimed.

## Private real-world protocol

Keep raw and identifying material outside any public checkout, with explicit memory
consent separate from session use. Public output contains anonymous conclusions only.
Do not publish a synthetic replacement as an observed real case.

Before: case ID, date, current situation, goal, constraints, source/evidence references
and unknowns. Decision: chosen move, strongest alternative and counterargument,
actions with owner, expected topic predictions, observation window, stop conditions
and reconsider_if. After: linked decision ID, dated reported hard outcome, source
observations, actual execution (done / partial / not done / unknown), user explanation,
agent explanation, unknowns, prediction calibration and what_changed.

Ask which effect the user observed, allowing more than one: A decided faster; B
avoided wasted preparation; C noticed an overlooked risk; D no help. Ask separately
whether the actions were executed. A favorable rating or passing interview does not
prove the advice caused an outcome. Missing follow-up remains missing / unknown.

| Metric | Numerator / denominator and missingness |
| --- | --- |
| Recommendation accepted | Explicit user acceptance / reviewed recommendations with an explicit response; report no-response count separately |
| Action executed | Reported completed agreed actions / agreed actions whose window elapsed and execution was assessed; partial and unknown separate |
| Reconsidered | Decisions actually revised after new evidence / elapsed-window decisions with follow-up; record trigger, exclude mere wording edits |
| Repeated risk | Comparable reviewed windows with recurrent signal / reviewed windows meeting at least three independent real outcomes; counts below gate separate |
| Outcome returned | Decisions with sourced linked outcomes / consented feedback decisions whose observation window elapsed; report overdue missing outcomes |

All rates require explicit counts, dates, denominators and uncertainty; do not invent
percentages before collecting observations. Offer-success rate is not the primary
metric. Delays, role mix, market, candidate experience and action execution confound
outcomes. Collect useful decision evidence before making any effectiveness claim.
