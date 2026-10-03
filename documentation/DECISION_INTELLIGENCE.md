# Decision intelligence v0.2 contracts

These additions extend v0.1 JSON records without changing SQLite tables or consent
policy version 1. Existing records remain readable; missing tags are not invented.
The natural-language host extracts and reviews context. Python validates boundaries
and prepares a reversible decision, not a personalized prediction of employment.

## Counterfactual and trace

Every decision includes recommendation.move, supporting_evidence,
strongest_counterargument, reconsider_if and confidence_basis. decision_trace exposes
situation, evidence_used, bottleneck, options_considered, chosen, rejected_options,
why and reconsider_if. This is a reviewable decision summary, not private chain of
thought. Mode-specific alternatives are defaults that the host must adapt to source
material; a schema passing does not demonstrate good judgment.
The consented decision handoff retains the trace and counterargument. Its compact
evidence_used contains at most six source references, rather than source text; field
budgets and the 6000-character record limit fail explicitly when exceeded. Compress
oversized summaries for review rather than silently storing raw material.

Stale / undated current information is excluded from supporting_evidence. A job
recommendation that would rely on current market fit first requests refreshed JD / HC.
Personal historical facts remain usable and correctable. Source dates are not proof
that a position remains open. The host checks current authoritative sources when
available and explains remaining uncertainty.

## Tags and similar memory

Optional input metadata has exactly mode, role_family, stage, situation_type,
risk_tags and situation_tags. Enumerations live in scripts/intelligence.py. Role
families are ai-product, agent-product, technical-product, ai-solutions and quant-ai;
unknown is allowed but never used to match history. Stages distinguish exploration,
application, preparation, post-interview, negotiation and decision. Tags describe a
situation or preparation risk, not a person or capability.

`decide --input situation.json --use-similar --memory-directory PRIVATE_DIR` reads
only an already active store. No consent or database is created implicitly. Matching
requires the same mode, role family and stage, plus shared tags and a decision no
older than 180 days. Rank by tag overlap, situation type, recency and stable ID.
Only the latest outcome per decision counts; at most three pairs enter the decision.
v0.2.1 filters comparable, recent candidates, then deduplicates reported real event
IDs and outcome sources **before** applying the three-pair limit. Eligible real events
take priority over synthetic/unknown records; the remaining slots may show other
comparable records but those do not count toward recurrent signals. Duplicate A,A,B
must not crowd out independent C. Original observation sources are still deduplicated
when counting a specific risk.
Correction-affected decisions are excluded. Unrelated Quant history cannot change an
AI Product follow-up. Old untagged records remain visible through administrative view.
Only history that changes the action enters supporting_evidence and similar_memory.used.

## Prediction and observation

Optional predictions (max five) each have topic (finite tag), expectation
(high_attention / risk_visible), and basis (source-based text). These concern topics,
never probability of passing. Outcome observations (max five) have topic, attention
(high / medium / low / not_asked / unknown), risk_observed (true / false / null), text
and source. False means explicitly assessed absence; null means not established.
not_asked requires null. Prediction calibration yields:

- SUPPORTED_THIS_CASE: matching high attention or explicitly observed predicted risk.
- CONTRADICTED_THIS_CASE: reported lower attention, or explicit assessment contrary
  to predicted visible risk. This concerns that prediction in that event only.
- NOT_OBSERVED: topic was not asked; neither support nor disproof of the concern.
- UNASSESSABLE: observation missing or ambiguous.

Outcome retains hard_outcome, observed_facts, user_interpretation,
agent_interpretation, unknowns, source and decision_id. Metadata is inherited from
the parent decision; mismatches fail. Optional origin is unknown / synthetic /
real_world; real_world requires event_id. These are operator attestations, not an
authenticated real-event detector. Outcome success never upgrades claim confidence.

## Recurrent signal

At least three comparable reported real-world outcomes with distinct event IDs and
distinct sources are needed. At least two explicitly observed occurrences of the
same topic risk yield RECURRENT_SIGNAL. Synthetic / unknown outcomes and duplicate
events do not count. A signal raises the next interview question-ladder priority,
with historical sources exposed. It cannot label someone's capability, infer hiring
causes or change direction automatically. Three is a conservative gate, not a
statistical significance claim. The current window is small and can miss longer
patterns; inspect source recaps before trusting a signal.

## Career hypothesis

Input has hypothesis, supporting_evidence, counterevidence, review_after and
alternative. Evidence has source, event_id, comparison_key, scope (core / local),
gap, text and origin. Comparison keys group the same role/stage/constraint context;
host correctness of that key requires review. Deduplicate sources and events.
One rejection keeps KEEP. Three comparable reported counterexamples concerning a
gap suggest REFINE. PIVOT requires five core counterexamples on the same gap plus a
sourced qualitative higher-value alternative, checked constraints and checked
confounders. Alternative contains hypothesis, expected_value (higher / unknown /
lower), basis, constraints_checked, confounders_checked. PIVOT is a user review
recommendation, never an executed career switch. Supporting evidence is displayed
for review; these conservative gates do not statistically weigh contradictions.

## Role and story mapping

The five compact role packs in references/role-packs.json contain role_family,
typical_signals, common_claim_risks, evidence_patterns, interview_dimensions and
common_gaps. They supply interview emphasis, not market claims or new achievements.
Optional project_story has project_id, source, claim_ids and story. Six story fields:
tension, personal_decision, ownership, tradeoff, result_evidence, learning.
result_evidence references an existing claim evidence source. Unknown personal
contribution, missing personal decision, incomplete dimensions or risky claims cannot
produce a defensible draft. Story prose is host-authored and must be source-checked;
nonempty text alone is not evidence. Mapping returns project → existing claims →
evidence → story → likely questions. Role translation preserves claim wording and scope.

## Correction

`memory_store.py --directory PRIVATE_DIR correct --subject SUBJECT --claim-id ID
--source SOURCE --input replacement-claim.json` accepts the existing raw claim model.
The command appends a compressed correction and updates matching current claim
records atomically, only with active consent. v0.2.1 input and decision records may
include claim_refs: `[{"project_id":"project-A","claim_id":"C1"}]`. The correction
subject is that stable project ID, while decisions may belong to different interview
or application subjects. Scoped references identify affected decisions across all
opportunities without confusing another project's C1. Their content is untouched
and they are excluded from similar recall.

For legacy claim_ids, cross-subject attribution is allowed only when the stored
claim ID belongs uniquely to the corrected project; same-subject references preserve
the prior behavior. Ambiguous legacy references are returned as unresolved_decisions
and excluded from routine recall pending review, not relabeled as confirmed impacts.
Historical v0.1 records without claim IDs cannot be automatically attributed to a
correction. Review those manually. Claim refs must refer to actual decision claims
and cannot assign one claim ID to two projects in a single situation. New decisions
should use explicit project refs rather than inferring identity from prose.
A narrated correction
caps the current claim at SELF_REPORTED (or PLANNED). Keep the new source and weaker wording; request independent
evidence if upgrading later. If no current claim record exists, the correction holds
the new claim for review; it does not silently create a new profile record.
