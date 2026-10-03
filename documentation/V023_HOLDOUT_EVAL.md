# Career Junshi v0.2.3 — Holdout Generalization Evaluation

## Scope and ordering

Baseline: [d6994a95](https://github.com/lavine888/Career-Junshi/commit/d6994a95d0d1ce2427a0f0f503e2c28a73cfb9b5), v0.2.2, 154 passing tests. Exactly ten new synthetic career cases were authored before generation. No private history or real hiring outcomes were supplied. Fictional scenarios use a disclosed clock of 2026-10-04 10:00 +08:00; it is not live market evidence.

The order was input/rubric design freeze → unmodified baseline L1/L2/L3 → output freeze → rubric-informed AI-operator L4 → FIRST_PASS_FREEZE → failure classification → three general fixes → paired runtime replay and fresh after-run → mutations and regression. Every pre-existing baseline file hash was checked before first-pass execution and before FIRST_PASS_FREEZE. Original cases, outputs, rubrics and grades are immutable.

REFERENCE_MODE = CONTROLLED_PRELOAD. Each generation received input, the installed Skill and two or three allowed references; extraction also received general serialization contracts. No rubric, expected recommendation, must_notice, failure list, future outcome or previous response entered generation. The twenty original prompt digests match the actual invocation records; the exact messages are retained in [runner packets](../benchmark/holdout-v023-runner/README.md). Autonomous reference access remains BLOCKED_BY_HOST, a separate compatibility issue, not a decision-quality failure.

Actual model: gpt-5.6-sol, high reasoning, fresh ephemeral contexts, disabled tools/web/apps/memory, separate extraction and host calls. L2 ran the real extraction and decision CLI/artifact generation. No simulated host response or outcome replay substitutes for a model turn.

## Holdout dataset

[Corpus](../benchmark/holdout-v023/) contains exactly ten input/ and rubric/ pairs: required years, scope versus salary, recurring technical feedback, unwritten equity, team metric attribution, ML versus customer deployment, delayed recruiting and removed listing, project avoidance, manager/care constraints, unknown systems interview. The set varies stage, location, industry, role, urgency, proof quality and personality.

The authored design has 8 cases with conflicting evidence, 9 tempting unsupported interpretations, 8 recommendations possible despite unknowns, and 2 genuinely blocked binding decisions (H04, H09). All required rubric fields are present. Acceptable recommendation ranges are used, not one winning sentence. The design metadata never entered generation.

## Frozen first-pass results

[FIRST_PASS_FREEZE.json](../benchmark/holdout-v023/FIRST_PASS_FREEZE.json) hashes 138 files covering inputs, rubrics, extraction packets/raw wrappers, decisions/artifacts/errors, host outputs/provenance, reviews and summary. It was created before any product edit. [Summary](../benchmark/holdout-v023/summary.json) retains the exact grades.

| Case | Mode | Extraction | Decision | Host | Overall | Main strength | Main failure |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H01-years-gate | job | PASS | PARTIAL | PASS | PARTIAL | Required years remain a gate; bounded honest application | L2 says verify a years gap rather than clearly apply |
| H02-title-scope | offer | PASS | PASS | PASS | PASS | Written role substance beats compensation and title | Generic L2 confirmation list rather than role-specific negotiation |
| H03-repeated-feedback | job | PARTIAL | FAIL | PASS | FAIL | Host distinguishes two explicit signals from three rejections | Structured layer reroutes a specific refinement question into generic discovery |
| H04-equity-gap | offer | PASS | FAIL | PASS | FAIL | Host blocks joining/resigning pending equity and cash feasibility | One unscored option becomes a superior current preference; binding blocker state lost |
| H05-metric-credit | positioning | PASS | PARTIAL | PARTIAL | FAIL | Separates team result, personal product leadership and engineering authorship | Short resume wording asserts joint causation without identification; L2 safe wording duplicated |
| H06-two-technical-paths | job | PARTIAL | FAIL | PARTIAL | FAIL | Host prioritizes customer-facing technical work for founder goal | No direction packet outside finite role families; travel question weakens hard cap to average |
| H07-delayed-listing | recruiting | PASS | FAIL | PASS | FAIL | Host protects the real October 6 alternative deadline; listing removal is not rejection | L2 has the deadline yet follows a three-working-day default |
| H08-building-avoidance | job | PARTIAL | FAIL | PASS | FAIL | Host says stop the fourth project and apply tonight | L2 asks another evidence/JD audit despite supplied defensible work and zero applications |
| H09-manager-care | offer | PARTIAL | FAIL | PASS | FAIL | Host distinguishes observed manager conduct from unproved toxicity/turnover | Hard care constraint unknown but unscored singleton is called superior preference |
| H10-unknown-systems | interview | PASS | PARTIAL | PASS | PARTIAL | Host supplies truthful bridge, hypothetical reasoning and bounded learning | L2 defense artifacts remain generic; no tailored spoken recovery bridge |

Overall: **1 PASS / 2 PARTIAL / 7 FAIL**. Host layer: **8 PASS / 2 PARTIAL**. These are different scopes. A fluent host cannot erase missing structured judgments, binding blockers or causal errors. A retained problematic alternative wording may leave the host layer PARTIAL while an integrity hard failure makes the end-to-end case FAIL.

Hard-failure instances: NO_PRIORITIZATION=3, OVER_CAUTION=4, GENERIC_ADVICE=3, PREMATURE_CERTAINTY=2, SUCCESS_TO_CAUSATION=1, NO_AVOIDED_ACTION=1.
Cases with decision-courage failures: 6 (OVER_CAUTION 4, PREMATURE_CERTAINTY 2). Separately, H05 has one unsupported joint-causation statement. No composite career-intelligence score is calculated.

Each case review uses all fifteen requested dimensions, PASS/PARTIAL/FAIL/NOT_APPLICABLE and verbatim excerpts. First-screen priority, calibrated commitment, information relevance and avoided actions are explicitly recorded. Relevant questions concern eligibility, written scope/equity, cash feasibility, travel limits, real deadlines or care schedule—not irrelevant interviewer titles.

The same Codex AI assistant authored and reviewed the corpus. There is no independent-rater reliability claim. Some dimensions share an excerpt and narrative judgment; fine distinctions between a partial wording defect and a hard failure deserve independent review before public performance claims. This is an evaluation, not an objective score engine.

### Reviewer-identity erratum

Frozen review metadata mistakenly says “Human operator” / “same human operator”. **The actual reviewer is the current Codex AI assistant**, which also authored the scenarios. There was no independent human or second-model review. The original files and scores are preserved to maintain the user-requested freeze; [explicit provenance correction](V023_EVALUATOR_PROVENANCE.json) overrides that mistaken identity label. Excerpt-backed grades are AI operator judgments, not independent validation.

### Assembly exceptions, preserved

- Before any generation, unsupported source-type aliases in an authoring draft were normalized to accepted document/hr_chat tags; source text was unchanged. No observed answer informed case changes.
- H01 originally failed an over-strict harness identity check because it also copied the permitted user question as REQ-001. S1–S3 are byte-identical and REQ-001 exactly equals the question. The original error remains; a separately marked supplemental baseline compilation uses the original packet, not a regenerated extraction.
- H05–H09 model turns completed, but the harness had not created output parent directories. Exact agent_message text was recovered from the completed event log, without regeneration or editing. Original writer errors, hashes and provenance remain. The after harness creates directories first and accepts only an exact additional request source.
- Output freeze preceded semantic review. H01 supplemental assembly correction was added before FIRST_PASS_FREEZE and is included there. The earlier OUTPUT_FREEZE is retained as a narrower event, not misrepresented as containing later reviews.

## Failure clusters

| Classification | Evidence | Disposition |
| --- | --- | --- |
| A — general product defect | H04/H09 unscored singleton promotion and lost hard blockers | Fix 1 |
| A — general product defect | H06 excludes out-of-catalog roles from direction comparison | Fix 2; representation capacity is distinct from extraction success |
| A — general product defect | H07 supplied deadline ignored by follow-up compiler | Fix 3 |
| A — usability defect | H05 ownership sentence duplication, recurring from prior distribution | Retain; not integrity inflation, no fourth fix |
| B — host variance | H03/H08 omit useful structured direction/readiness; H05 short variant asserts causation; H06 averages a hard travel cap | Retain; no case-specific rules or one-off Skill wording |
| C — evaluation ambiguity/assembly | H01 request-source identity; writer race; nonbinding draft does not establish legal effect | Correct assembly with full provenance; no product credit |
| D — missing fresh data | Live vacancies, local law/tax, employer calendar remain unverified | Not marked as a defect for failing to browse a synthetic tools-disabled run |
| E — platform limitation | Autonomous reference retrieval blocked independently | Excluded from this controlled-preload comparison |
| F — benchmark preference | Exact phrasing, proposed workload ratios, generic spoken bridge format | No patch for stylistic preference; actionable fallback weaknesses still disclosed |

## General fixes and overfitting safeguards

Exactly three behavioral fixes, recorded with failure_cluster, cases_affected, root_cause, general_rule, why_not_overfit and new_regression in [fixes.json](../benchmark/holdout-v023-after/fixes.json). Product changes are confined to the existing decision compiler, its contract documentation and ten meaningful regression tests. SKILL.md and practical guidance are unchanged; no version-only commit, new mode, scoring engine, taxonomy expansion, database, agent or frontend.

1. **Unsupported singleton Offer superiority / hard acceptance boundary**: No comparative superiority from an unscored singleton. Unknown explicit hard constraints block binding acceptance; preserve a sourced comparative tilt when it exists and allow nonbinding discussion.
   Generalization check: No company, compensation, equity or care-schedule string matching. Uses existing options, ratings, constraints and eligibility for any industry. Ordinary nonblocking unknowns still permit conditional comparison.
2. **Contemplated career outside the finite family catalog**: Allow existing role_family=unknown in direction candidates; keep supplied actual names and source-bound assessments.
   Generalization check: No new family or role packs. Arbitrary clinical, energy and supply-chain roles, reordered and renamed, remain comparable; unsupported assessments still block.
3. **Follow-up heuristic outranks supplied deadline**: A real deadline within 72h outranks heuristic waiting, with one truthful status request and bounded decision window. Explicit contact ban and prior follow-up still prevail; expired deadline triggers availability review, never invented extension.
   Generalization check: Uses timezone-aware existing urgency; tests vary hours, event labels, industries and contact boundaries. Draft never invents another Offer.

Regressions alter labels, role names, amounts/hours, ordering, industries, evidence/goal distribution and hard-constraint status. Unknown catalog membership never upgrades evidence. Known comparison can retain a tilt while binding acceptance is blocked; ordinary unknowns stay conditional. A request to stop contact or an already-sent follow-up still overrides urgency. These rules contain no holdout company names, metrics or special-case expected directions.

Old Offer/Ownership partials were not reused as new cases. The new Offer distribution does expose a general threshold/sufficiency weakness, so it qualifies for repair. Ownership wording still has a usability weakness; it is not falsely declared solved merely because evidence integrity tests pass.

## Before versus after

Paired runtime replay holds the original packets fixed. H04/H09 now block binding acceptance without inventing a winner; H07 gives a deadline-bounded status request. H06 remains generic on its original packet because the extractor omitted direction; allowing unknown roles does not retroactively create missing assessments. H03/H08 generic fallback and H05 awkward wording also remain.

Fresh after-run changes both extraction and model sample. The Skill and allowed host-reference bytes are unchanged; any L3 wording improvement or regression is model variance, not evidence of code causation. Both views must be reported separately. New outputs and all worse responses are retained outside the frozen corpus.

| Case | Before overall | Fresh after extraction | Decision | Host | Overall | Main remaining failure |
| --- | --- | --- | --- | --- | --- | --- |
| H01-years-gate | PARTIAL | PASS | FAIL | PASS | FAIL | Fresh extraction changes fit to unknown and L2 returns unrelated role-discovery work |
| H02-title-scope | PASS | PASS | PASS | PASS | PASS | No new material failure |
| H03-repeated-feedback | FAIL | FAIL | FAIL | PASS | FAIL | Extraction labels a friend causal opinion kind=claim with confidence=interpretation; contract rejects it |
| H04-equity-gap | FAIL | PARTIAL | PARTIAL | PASS | PARTIAL | Fresh packet omits qualitative priorities/critical_unknowns, so L2 verification stays generic |
| H05-metric-credit | FAIL | PASS | PARTIAL | PASS | PARTIAL | Structured ownership sentence remains duplicated and awkward |
| H06-two-technical-paths | FAIL | PASS | PASS | PASS | PASS | Ordinal judgments remain host interpretations, not verified abilities |
| H07-delayed-listing | FAIL | PASS | PASS | PARTIAL | FAIL | Host opens with definitive not-rejected status although current hidden result is unknown |
| H08-building-avoidance | FAIL | PARTIAL | FAIL | PASS | FAIL | Extractor uses undocumented fit=supported; compiler falls through to generic evidence/JD discovery |
| H09-manager-care | FAIL | PASS | PASS | PASS | PASS | Manager signals still require targeted human confirmation |
| H10-unknown-systems | PARTIAL | PASS | PARTIAL | PASS | PARTIAL | Structured artifact remains generic compared with tailored spoken host answer |

Fresh after totals: **3 PASS / 3 PARTIAL / 4 FAIL**; host layer **9 PASS / 1 PARTIAL**. After hard instances: NO_PRIORITIZATION=2, OVER_CAUTION=2, GENERIC_ADVICE=2, PREMATURE_CERTAINTY=1, NO_AVOIDED_ACTION=1. Courage failures occur in 3 cases (2 over-caution, 1 unsupported certainty). No integrity hard failure was observed in this after sample, but the original H05 causal slip was not structurally fixed.

All ten before/after host prompts are SHA-256 identical. L3 improvements and regressions are therefore sampling variance. In particular, H07 worsens from host PASS to PARTIAL: “你还没有被拒” overstates the unknown hidden result. A no-communicated-rejection reading is possible; the strict reading is retained explicitly rather than silently changing grading standards. Original and worse responses are kept.

H01 extraction changes gap to unknown and produces worse generic discovery. H03 emits an inferred friend opinion as kind=claim/confidence=interpretation; the contract correctly refuses that packet. H08 emits fit=supported instead of the documented fit vocabulary and gets the coarse fallback. These failures are not repaired by rewriting packets, weakening guards or simulating successful CLI calls.

Within fix 1, the first after compilation exposed a second consequence of removing an unsupported winner: option-specific decisive questions were filtered out when preference was None. The same cluster was corrected to retain those questions. Initial compilation is preserved under first-pass/; final-runtime/ contains the final actual CLI artifacts with product hashes. A dedicated regression checks the blocked-singleton questions and reversal conditions. This is not a fourth behavioral fix or a new model-generation attempt.

## Mutation tests

| Changed variable | Original decision | Mutated decision | Host | Structured | Limitation |
| --- | --- | --- | --- | --- | --- |
| priority | 我的判断：**不要只为了加薪接受。当前首选是留任，同时把曜原 Offer 当作一次限时谈判机会。** | **按你现在的目标，曜原集团更符合。** | PASS | FAIL | L2 rejects partial metadata; no structured acceptance decision produced. |
| goal | **主线：工业 AI Solutions / Forward Deployed，但限定为“亲自构建、参与交付、非重销售”的岗位。**   | **主线：ML Engineer，聚焦模型工程、数据质量、评估、漂移和可靠性。**   | PASS | PASS | Goal change reverses the primary role while preserving actual role labels and evidence boundaries. |
| deadline | **你还没有被拒。**职位页面消失只是弱信号，不能覆盖 HR 在 2026-10-02 明确给出的“流程仍在处理中”。但这家公司已经无法按原时间表给结果，因此也**不值得无限等待**。 | **不能据此认定被拒。现在先不催；从 10 月 2 日最新回复后，按该公司的实际工作日等待约 3 个工作日，再进行一次有限跟进。** | PASS | PARTIAL | Urgent send_now becomes wait, but extractor retains a superseded timeline inside promised_date; timing precision remains ambiguous. |

The three controlled mutations alter priorities/goal or remove the competing deadline; they are outside the ten-case corpus. Input wording was made coherent with that one change. The mutation rationale was never sent to generation. All three host recommendations change in the expected decision-relevant direction. Structured results are 1 PASS / 1 PARTIAL / 1 FAIL: the cash-priority packet has partial metadata and produces no valid decision; the no-deadline recruiting packet keeps a superseded promised timeline. Host sensitivity is not a perfect pipeline result. No real outcome is fabricated.

## Full regression

- 164/164 unit tests pass (154 baseline + 10 behavioral regressions). Name, role, ordinal/numeric value, ordering, industry, evidence distribution, eligibility and deadline mutations are included within the new tests.
- Skill packaging/link/routing/syntax validation passes.
- Original 13 structured benchmarks: no regression.
- Five previous frozen mock cases: source identity and properties pass; old frozen outputs unchanged.
- Five v0.2.2 frozen semantic artifacts: integrity/properties pass; retained grades remain 3 PASS / 2 PARTIAL. This is a frozen replay, not five fresh semantic generations.
- All ten new baseline/after host and extraction generations completed. Fresh after L1 rejects H03; its failure is retained. Green unit tests do not replace this failed integration.
- Three mutation host/extraction generations completed; one structured metadata failure and one timing ambiguity remain.
- First-pass, after and mutation manifests verify. Twenty baseline + twenty fresh after + six mutation model turns were real, with zero tool commands and no outcome writes.

[Machine-readable regression evidence](../benchmark/V023_REGRESSION.json), [read-only verification/replay](../benchmark/holdout_tools.py), [exact generation packets](../benchmark/holdout-v023-runner/README.md). These helpers do not compute a semantic score or reassign operator grades.

## Remaining weaknesses and overfitting assessment

The host displays general principles on these new situations: bounded applications despite tenure uncertainty, goal over title, local refinement over an unjustified pivot, promises versus contracts, honest attribution, conditional direction, deadline-aware follow-up, stopping project avoidance and truthful systems recovery. That is synthetic evidence of transferable behavior, not evidence that a model was trained or real careers improved.

The structured pipeline remains brittle. A narrow catalog blocked a legitimate career comparison; unscored singleton selection invented comparative support; time heuristics ignored a real deadline. Those are general defects discovered on a new distribution. They received general fixes. Generic job fallback, optional-field omissions, metadata/confidence variance, awkward ownership wording and unsupported natural-language certainty remain. The initial ownership causal slip can disappear with unchanged instructions, so it cannot be declared cured by code.

Some preferences are evaluation choices: exact first-screen length, a particular allocation ratio, or the best spoken bridge. They do not justify one-off patches. The corpus was never edited to improve scores; failed/worse outputs were not deleted; no case name/amount appears in product rules. Metamorphic properties and three decisive mutations reduce a named-scenario explanation, but ten authored synthetic cases with one AI operator are insufficient to establish broad generalization or human superiority.

Conclusion: **partial generalization, with incomplete pipeline generalization**. The test does not support “Career Junshi increases offer rate”, “improves job-search success” or “makes better decisions than humans”. Even a perfect retained set would only establish performance on that frozen synthetic set.

## Real-user readiness

**Not ready for a direct-to-user pilot under the requested gates.**

| Gate | Status | Evidence |
| --- | --- | --- |
| No integrity hard failures | NOT_ESTABLISHED | First-pass H05 asserts joint causation; after sample avoids it with identical instructions, so elimination is not proven |
| Direction can prioritize | PARTIAL | H06 and its goal mutation prioritize; H01/H08 structured routing still retreats |
| Conditional decisions work | PARTIAL | H02/H06 conditionally choose, H04/H09 binding blockers work; mutation metadata still fails |
| Unknowns do not automatically block advice | PARTIAL | Host generally acts; structured omissions cause generic discovery or a rejected packet |
| Ownership does not inflate | PASS_WITH_LIMIT | No personal engineering/sole-team upgrade; causal wording and readability risks remain |
| Actions stay bounded | PASS | Valid runtime plans and host responses use at most three main actions |
| Stop/reconsider conditions work | PARTIAL | Real deadline now protects L2; mutated superseded timeline and certainty wording remain |

A strong-result REAL_USER_PILOT.md is not produced because these criteria are not met. Do not expand another synthetic suite merely to accumulate green grades. First independently review the retained failures, verify the actual extraction/handoff and causal wording, and require human review of user-facing advice. Once those gates are evidenced, prefer a lightweight 5–10 anonymous-user pilot over another synthetic benchmark iteration. Its outcomes should be decision clarity, executed action, useful risk, avoided preparation and feedback that changes the next decision—not offer rate. No volunteers contacted and no unnecessary private data requested.

Frozen evidence and runner paths use Git byte-preservation attributes so commit/
checkout normalization cannot invalidate their manifest hashes. Prompt records
separate serialized-file hashes from normalized UTF-8 message hashes. Product
execution hashes describe working bytes at execution, while source code retains
normal repository line-ending normalization; no behavior or score is changed.

Whitespace attributes recognize preserved CRLF bytes and intentional Markdown
hard breaks in captured messages; JSON/code whitespace and semantic assertions
remain checked. Artifact content is not rewritten to satisfy formatting checks.
