# v0.3 host-first report — evaluation incomplete

**Gate: MIXED / pending evidence. Keep the host-first path experimental; do not
replace the legacy flow.** The specified model service exhausted its usage quota
after nine successful generations. Only one of ten fresh A/B pairs completed.
This operational gate is not a completed scientific finding of mixed superiority.
We cannot answer YES or NO to architectural outperformance from the missing data.

No pilot, release/version bump, real outcome or hiring-effect claim is made.

## Why architecture changed

The frozen v023 baseline is acf2a34363bda9f67a47f3645fbd772b16f94508, 164 passing
tests. Historical fresh-after four-layer grades were 3 PASS / 3 PARTIAL / 4 FAIL,
while the separate host layer had 9 PASS / 1 PARTIAL. This motivated moving semantic
judgment to the host and keeping deterministic support focused on boundaries and
execution. These historical grades are not substituted for missing fresh A calls.

## Structured-first failure evidence

The [v023 report](V023_HOLDOUT_EVAL.md) records H03's rejected interpretation/profile,
H06's catalog/representation boundary, H08's generic discovery despite supplied
readiness, and H10's generic spoken defense. In this new partial run H03 again
fails actual A compilation: `interview is only valid in interview mode`.
A selects job for a direction question but rejects the supplied optional interview
profile. This is a serialization/representation failure, not proof that the
candidate should change careers.

H01's fresh A recommendation begins “先补或验证这个具体缺口” and still compiles
“比较两个岗位假设与五份新鲜 JD”. B instead says “值得投” and caps the existing
application at one hour without treating three years as waived. A's host turn is
missing because of quota, so this is a partial comparison of available layers.

## Host-first architecture

**LLM decides. Code verifies. Memory remembers. Reality calibrates.**

The host interprets goals, evidence, tradeoffs, bottlenecks and next actions. The
new `host-decide` command validates an envelope and faithfully compiles its material.
It does not call the legacy `decide`, rank roles, choose a company, introduce salary
preferences, or turn history into an automatic current bottleneck. The old engine
is unchanged and remains available. See [architecture and diagram](V030_ARCHITECTURE.md).

## Decision Envelope v2

The [contract](DECISION_ENVELOPE.md) has core situation, sourced facts, inferences,
decision-relevant unknowns, bottleneck, recommendation, alternatives, 1–3 actions,
reconsideration, observation and stopping conditions. Exact source quotes and IDs
anchor facts. Personal accounts retain self_reported confidence. No role catalog,
fit/rating table or statement-kind taxonomy is required for career judgment.

Optional mode-specific Markdown extensions compile only for the applicable mode.
Invalid optional metadata is isolated rather than destroying the judgment. Optional
audited Claims/project refs preserve identity and correction; optional prediction
metadata reuses existing outcome calibration. Strict memory budgets apply only
when that separate operation is requested, not to an ordinary answer.

## Validator

`validate_decision_envelope()` returns ACCEPT / REPAIR_REQUIRED / BLOCK, field-level
issues and safe field names. It checks source/quote binding, epistemic confidence,
factual percentage consistency, existing Claim audit, bounded actions, explicit
execution ownership, observable reconsideration and common bilingual integrity
violations. A saved status is not a token to bypass revalidation before compilation.

The five requested adversarial scenarios are rejected or flagged in actual tests:
verbal equity promoted to guarantee, team percentage claimed individually, silence
promoted to rejection, unsupported fundamental-role certainty, and whole-system
authorship despite non-authorship. Legitimate lower-pay/manager-priority and Quant-
with-accepted-training choices pass, including changed labels and amounts.

Finite patterns and anchors do not authenticate sources or prove arbitrary prose
entailment, causality, mixed-source scope or hidden premise dependencies. Positive
claims in recommendation fields BLOCK; artifact boundary problems require repair.
This field-based dependency approximation can miss or overflag semantic errors.

## Repair Loop

Maximum one host repair. Original and repaired candidates/validation are retained.
Two cases actually invoked repair: H02 had a date-only deadline serialized without
a timezone; H03 supplied four reconsideration entries against the three-entry
contract. Both corrected envelopes preserved their recommendation.move **exactly**.

The first validator then falsely rejected H03's repaired sentence:

> 我没有独立开发分布式存储，系统实现由工程同事负责

Its pattern matched the subject through a negated ownership phrase and the following
implementation clause. This was a genuine general guard defect. A focused test went
red on three Chinese/English negation variants; the fix scopes prefix checks and
recognizes internal negative ownership predicates. Positive sole-authorship controls
remain rejected. There is no company, role or benchmark-number branch.

Original failed H03 compilation remains in `fresh/`. A separate replay of its
unchanged already-repaired envelope passes after the fix: zero model calls, no
second host repair, no grade rewrite. A factual-percentage anchor check and optional
prediction handoff and reused legacy hiring-result guards were also completed and tested after the interrupted run; these
are disclosed as a final runtime epoch, not hidden in the initial protocol.

## Frozen Holdout Comparison

REFERENCE_MODE = CONTROLLED_PRELOAD. Actual model = gpt-5.6-sol, high reasoning.
Both arms use identical raw inputs and reference payloads; Skill/serialization
instructions differ according to the architecture. A uses fresh extraction → actual
baseline CLI → host presentation; B uses fresh host envelope → validator → at most
one repair → compiler. Successful turns invoked zero tools and received no rubrics,
future outcomes or opposite-arm responses.

The initial [output freeze](../benchmark/host-first-v030/fresh/OUTPUT_FREEZE.json)
preceded rubric-informed review. All original v023 cases/rubrics/outputs/freezes
are byte-preserved. New generations remain in a separate namespace.

| Case | Fresh A available | Initial B pipeline | Final B retained-envelope replay | Coverage |
| --- | --- | --- | --- | --- |
| H01 years gate | Structured PARTIAL; host quota failure | ACCEPT; semantic PASS | ACCEPT, same move | Pair incomplete |
| H02 title/scope | Structured usable; host PARTIAL | One repair → ACCEPT; semantic PASS | ACCEPT, same move | Only complete pair |
| H03 repeated feedback | Structured schema failure; host quota failure | One repair → false guard rejection | ACCEPT after general guard correction | Pair incomplete |
| H04 equity | Extraction quota failure | NOT_RUN | NOT_RUN | Missing |
| H05 metric credit | NOT_RUN | Envelope quota failure | NOT_RUN | Missing |
| H06 technical paths | Extraction quota failure | NOT_RUN | NOT_RUN | Missing |
| H07 recruiter signals | NOT_RUN | Envelope quota failure | NOT_RUN | Missing |
| H08 project avoidance | Extraction quota failure | NOT_RUN | NOT_RUN | Missing |
| H09 manager/care | NOT_RUN | Envelope quota failure | NOT_RUN | Missing |
| H10 unknown systems | Extraction quota failure | NOT_RUN | NOT_RUN | Missing |

No ten-case PASS/PARTIAL/FAIL total or win rate is computed. Three passing final
replays cannot fill the seven absent B generations or the absent A presentations.

## Integrity Failures

The AI operator found no integrity hard failure in the three available B judgments.
That is a limited observation, not 0/10 or proof of noninferior integrity. The most
important unexecuted probes include unwritten equity, metric attribution, manager
constraints and interview fabrication. Adversarial unit success does not substitute
for those real host/model integrations. Existing evidence/Claim tests remain green.

## Pipeline Failures

There were 18 service attempts: 9 completed generations, 9 explicit usage-limit
rejections. These are service execution failures, not project judgments. The first
runner advanced other cases after quota exhaustion; all attempts remain recorded.
The resume helper now stops on the first such rejection and never retries in a loop.
No model, effort, guard, expected answer or rubric was switched to fill missing cells.

[Quota evidence](../benchmark/host-first-v030/QUOTA_INTERRUPTION.json) contains the
actual error and provenance. The reported “5:32 AM” is not assigned a date/timezone.
At least 23 base calls remain, plus at most one repair for each newly run B case.

## Schema Rejections

A H03 rejects the optional interview profile in job mode. Initial B H02 rejects
an explicit deadline without timezone; its single repair removes the unsupported
precision while retaining the October 9 date in actions. Initial B H03 requires
compression of four reconsideration entries; its repair succeeds semantically but
is falsely rejected by the original negation guard. The original final B count is
2 ACCEPT / 1 unresolved among only three available cases. Final-runtime replay is
3 ACCEPT / 0 unresolved on the same retained envelopes. These different epochs
are not pooled into a fresh ten-case result. The observed repair rate warrants
attention; schema rarity is not established.

## Semantic Results

The [partial excerpt-backed review](../benchmark/host-first-v030/partial-review.json)
is authored by the current Codex AI assistant, which also implemented the experiment.
There is no independent human or second-model judge. H01 B gives a clear recommendation/action cap and explicitly returns to comparable
opportunities after the bounded application.
H02 B gives a goal-aligned decision, written negotiation and usable decline draft.
H03 B makes a narrow KEEP/REFINE move and preserves the third rejection's unknown
cause; its original end-to-end pipeline nevertheless failed. The final replay fixes
execution, not the model's judgment.

H02 A presents a sensible preference but calls the nullable exact deadline an
“明显的管线／证据错误” even while acknowledging no cutoff time was supplied.
That diagnostic overstates what the timestamp contract permits. Its structured
verification also focuses on the current job's longer path rather than the decisive
new role negotiation. Only this pair has both fresh host outputs; it cannot
establish the full architecture comparison.

## Existing Regressions

186 tests pass: all original 164 unchanged plus 22 envelope regressions. No old
test was deleted or weakened; no authority-assumption migration was needed because
the legacy engine remains intact. Coverage includes adversarial/unusual choices,
source binding, confidence, action bounds/ownership, one-round repair, optional
metadata/extensions, actual installed CLI, artifacts, consented memory, append-only
outcomes and calibration compatibility.

Original 13 structured benchmarks and five frozen semantic/property replays pass.
Their retained grades remain 3 PASS / 2 PARTIAL; they are not fresh generations.
Skill packaging/routing/link/syntax checks pass. v023 first-pass 138, after 206 and
mutation 50 manifest entries remain unchanged. Full evidence is in
[regression metadata](../benchmark/host-first-v030/REGRESSION.json).

## Limitations

- The required ten-pair experiment is incomplete due to external model quota.
- Three B judgments are too few to establish integrity, schema reliability or
  calibrated commitment across all modes. Initial repair/false-rejection rate is high.
- Source anchors and patterns cannot prove arbitrary natural-language truth or
  authorize external actions; host review/permission remains necessary.
- Previously frozen v023 cases were unseen to v022, but their failures are now known
  development evidence. This v03 reevaluation is not a newly blind unseen distribution.
- Reviewer/author overlap, one model sample per call and unequal pipeline call counts
  preclude independent reliability or code-only causal claims.
- Autonomous reference loading remains BLOCKED_BY_HOST and is excluded; no fresh
  real hiring/market/legal evidence or real-user outcome was supplied.

## Real-user Readiness

Not established. The minimum of seven end-to-end PASS/strong PARTIAL, integrity
noninferiority, at most one pure schema/transport failure, and broad survival of
host judgment cannot be assessed. The quota failures are external; excluding them
does not create successful missing observations. No REAL_USER_PILOT.md or pilot
activity is created. Existing consent and execution boundaries remain active.

## Recommended Next Step

Restore access to the specified model, then use the [verified resume plan](../benchmark/host-first-v030/pending-plan/PENDING_CALLS.json)
and [runner instructions](../benchmark/host-first-v030/README.md) to generate only
the missing calls in a fresh directory. Reuse completed responses/repairs with
prompt/hash verification, disclose runtime epochs, freeze and review all ten pairs,
then apply YES/MIXED/NO and the pilot gate. Until then the host-first path remains
experimental, with no claim that it outperformed structured-first on unseen cases.
