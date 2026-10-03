# Decision Quality Benchmark

Golden cases are fixed, sourced by origin, and contain raw available context plus
must_notice, must_not_assume, tradeoffs, multiple acceptable recommendations,
bad recommendations, required actions, stop condition and ten diagnostic dimensions.
There is no single ideal sentence or composite Career Score.

Levels:

1. Deterministic contract / integrity checks. Unit tests and output invariants.
2. Structured decision regression. Repeated fixed inputs and semantic **properties
   of explicit structured fields**, not natural-language wisdom.
3. Host model decision evaluation. Blind host-input packet, separately held rubric,
   real model outputs and excerpt-backed reviewer diagnostics on each dimension.
4. Real-world outcome evaluation. Consented private before / decision / after records,
   actual action execution and observations. No Offer-success causality metric.

`python scripts/benchmark.py run` reports case coverage, hard-rule pass, decision
properties and regressions. Level 3 / 4 remain NOT_RUN in that report. It does not
infer model quality from the lower levels.

`packet --output /new/private/directory` exports host-inputs.json and evaluator-rubric.json
separately. The host must not see the rubric or structured canonical answers. Use
the same inputs, Skill revision and model settings for repeats; note time, model,
run ID, tools, unavailable context and reviewer. A builder evaluating its own outputs
is not independent. Failed / partial answers remain in reports, not edited away.

`validate-host --input reviewed-run.json` checks externally supplied model metadata,
unique case IDs, all ten dimension annotations, and exact response excerpts. A
rating needs diagnostic and source_reference. UNASSESSABLE can lack an excerpt.
This command accepts annotations; it does not judge their semantic correctness or
verify that the claimed model ran. Missing cases stay visible. Do not manufacture
host evaluations to claim MODEL-EVALUATED.

Dimensions: Situation Understanding; Evidence Discipline; Bottleneck Identification;
Recommendation Clarity; Actionability; Opportunity Cost Awareness; Uncertainty
Calibration; Stop / Pivot Quality; Personal Context Usage; Outcome Learnability.
Use PASS / PARTIAL / FAIL / UNASSESSABLE with reasons. For example, a useful answer
can choose follow-up or conditional waiting, but must preserve result uncertainty,
promised dates, calendar ambiguity, other opportunities and a stopping line.

Public golden inputs are synthetic until a genuinely consented anonymous real case
can be safely published. A private real-context evaluation does not make a synthetic
case real; only an anonymous conclusion may leave that private workspace. Evaluation
protocol and observed coverage are recorded in [EVAL.md](EVAL.md).
