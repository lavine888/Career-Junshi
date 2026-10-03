# Decision Quality v0.2.2 contracts

These are optional additions to the five existing modes, not new modes or a
scoring service. Narrative extraction/qualitative interpretation belongs to the
host; scripts validate bindings and compile bounded outputs. Legacy inputs remain
valid. The normal packet still has schema_version, sources, statements, situation.

## Common output and source binding

`recommendation_type`: SUFFICIENT / CONDITIONAL / BLOCKED.
`decision_sufficiency`: state (DECISION_ prefix), basis, blocking_unknowns,
reversal_unknowns (at most three each). It describes a move's sufficiency, not
the truth of a Claim. A conditional recommendation can be acted on reversibly;
commitment still respects hard constraints and human approval.

Every new assessment requiring source_ids must bind a nonempty list of up to
eight existing session IDs. `extract` derives an ID/type-only context_sources
registry, including sources whose only statement is UNKNOWN. Raw source text
remains session-only. Do not put context_sources, facts, inferences or unknowns
inside the host-supplied packet situation. Direct structured inputs can provide
the validated registry as an operator handoff; this is an attestation, not proof
that an interpretation follows from the referenced text.

## Job direction input

`situation.direction = {"candidates": [...]}`; at most six. Each candidate:

| Field | Contract |
| --- | --- |
| name | Supplied contemplated role label, unique, ≤45 characters |
| role_family | ai-product, agent-product, technical-product, ai-solutions, quant-ai |
| source_ids | Existing session IDs supporting the host assessment |
| assessment | Eight keys below, each unknown / low / medium / high |
| strongest_proof, largest_gap, resume_case, market_test | Text ≤400 each; absent evidence may stay empty |
| constraint_status | pass / fail / unknown |

Criteria are evidence_strength, continuity, defensibility, role_relevance,
goal_fit, gap_cost, optionality, market_testability. The compiler compares ordinal
assessments in this disclosed order, reversing known gap cost; unknown cost is
not treated as cheap. A failed constraint or low goal fit deprioritizes; weak
evidence with high gap cost stays exploratory. Exact top ties remain joint primary
choices, not alphabetical winners. No usable comparison produces BLOCKED.

Output has `direction` with primary / secondary / exploratory / deprioritized,
comparison and one-resume tie_break; primary_choice, secondary_choice and
exploratory_choice mirror categories. The artifact names proof, gap, cost,
resume case and market test. All levels are host interpretations, not verified
ability or market demand. Role packs supply family context, not a universal order.

## Offer input

Existing options/constraints/weights remain valid. Qualitative preferences use
`offer.priorities` mapping existing dimensions to high / medium / low and
`offer.source_ids` pointing to the stated goals. Do not convert “high” to a
numeric weight. Ratings must already be supplied 0–5 values. Missing dimensions
are not filled; unsupported currencies, stability mappings and thresholds are
not invented.

Optional `critical_unknowns` (≤8) each contains unknown, option (existing exact
name or empty for shared), priority (decisive / important / confidence_only),
why_it_matters, how_to_verify, reversal_condition and source_ids. Texts are ≤400;
reversal_condition is ≤240. The host chooses priority and explains it; the code
does not claim to estimate objective value of information.

With stated goals, the first informative priority tier compares common supplied
ratings. A dominant option can become a conditional current_preference. A real
higher-tier tradeoff cannot be overturned by lower-tier brand. An explicit failed
hard constraint excludes the option; unknown constraints remain conditional.
Absent goals or meaningful distinguishing dimensions can produce BLOCKED.
Output contains offer_priorities, current_preference, reversal_conditions and
top 1–3 decision_unknowns. None scores remain None; no composite score is created.
The comparison artifact carries why/how/reversal, with the full evidence detail
remaining in structured output.

## Interview input

Optional `interview` has available_hours (provided number 0–72) and signals (≤5).
Each signal has topic (existing finite tag), basis (≤160), source_ids and kind
(observed_signal / risk_hypothesis). The observed signal is attention or explicit
feedback, not automatically a weakness. Output top_risk_hypotheses (≤3) retains
signal_kind and RISK_HYPOTHESIS status. Primary actions stay ≤3; substeps belong
under them. Keep the deadline and actual budget from source material.

## Recruiting input

Optional `recruiting.communication` has stage (application / interview / final /
unknown), tone (formal / neutral / warm), last_event (source-based ≤120) and
source_ids. Existing working_days and promised-date checks govern sending;
communication adapts the draft instead of changing status. Unknown calendars
can produce a prepared draft with conditional wait. no_contact means an explicit
contact prohibition, not no reply.

`follow_up` has action (send_now / wait / do_not_contact), timing, window, draft;
draft also appears at the top level when available. Artifact generation never
sends a message. Existing follow-up/terminal guards remain active.

## Positioning ownership input

Optional `ownership` has project_stage and contributions (≤20). Each contribution
has an existing unique claim_id, claim_stage and user_contribution_stage. Each
stage uses unknown / planned / demo / backtest / completed / production, default
unknown. Distinguish completion of reported product work from overall project
completion and personal engineering implementation. These declarations do not
upgrade core Claim confidence or replace audit evidence requirements.

`ownership_defense` includes safe_claim, complete reported_contributions, boundary,
independent stage fields and 3–5 defense_questions. Long contributions stay complete
in the pack instead of cutting a negative qualifier; the short claim uses a bounded
description. Documents existing are not checked receipts. The host reviews wording
for usability and fidelity before the person uses it.

## Evaluation and feedback limits

The nineteen new tests assert behavioral properties, including changed labels and
evidence, not exact Chinese answers. A source ID, output schema or passing property
test cannot certify judgment. Existing consent, append-only decision history,
feedback budgets and success-versus-causation rules still apply. New outputs fit
the compact handoff on the tested boundary cases; this does not authorize saving
raw context. Retained semantic failures and the separate blocked retrieval experiment
are documented in the repository reports; packaged contracts cover runtime fields.
