# v0.3 experiment freeze and resume evaluation

- STATUS: **EXPERIMENTAL**
- EVALUATION: **INCOMPLETE**
- A/B COVERAGE: **1 / 10 completed**
- CONCLUSION: **MIXED / INSUFFICIENT EVIDENCE**
- REAL USER PILOT: **NOT STARTED**
- MAIN ARCHITECTURE: **v0.2.3 until evaluation completes**

The specified gpt-5.6-sol service hit its usage limit after nine successful model
calls and nine explicit quota errors. The error's “5:32 AM” has no verified date or
timezone; do not assume a reset time. This task freezes the experiment and prepares
resumption; it makes **zero new model calls** and changes no product behavior.

## Frozen revisions and coverage

- Stable baseline/main: `acf2a34363bda9f67a47f3645fbd772b16f94508` (v0.2.3).
- Product experiment snapshot: `355cc1f2ece441c67e74529a232e073152217a76`.
- Experimental branch: `experiment/v0.3-host-first`; never merge it into main before
  completing this comparison and deciding YES / MIXED / NO. No release tag exists.
- `RESUME_EVAL.json.experiment_commit` identifies the actual product/evidence
  snapshot above. The later tooling/documentation commit contains that manifest;
  it cannot truthfully contain its own Git hash. Use the branch tip for the runner.
- Historical generations used an earlier validator epoch. `FINAL_FREEZE.json`
  pins the already disclosed final runtime used for resumption. Preserve original
  results and report initial versus final-runtime outcomes separately; do not
  relabel a deterministic replay as another fresh model sample.

| Case | Completed model calls | Remaining base calls |
| --- | --- | --- |
| H01 years gate | A extraction; B envelope | A host presentation |
| H02 title/scope | A extraction/host; B envelope/sole repair | None: complete pair |
| H03 recurring feedback | A extraction; B envelope/sole repair | A host presentation |
| H04–H10 | None successful | A extraction/host and B envelope for each |

There are **23 pending base calls**, not 23 guaranteed total calls. H04–H10 may
each require at most one additional host repair, giving 23–30 model calls if all
base transports succeed. Invalid content is still a completed sample: preserve it,
never regenerate to improve its quality. Two historical repairs have already used
their entire budgets. H02's existing complete pair is read-only.

## Manifests

All paths in new manifests are repository-relative; no private runtime log,
credential, real Career memory, account ID or private career material is included.
Historical exact prompt/runtime evidence retains inert artifact path strings where
removing them would change a frozen hash or the actual model input. They are
provenance, not runnable dependencies. No new command hardcodes those old paths.

- [Resume contract](../benchmark/host-first-v030/RESUME_EVAL.json): actual commits,
  model, configuration, raw inputs, reference hashes, immutable file hashes and gates.
- [Completed calls](../benchmark/host-first-v030/COMPLETED_CALLS.json): nine model
  outputs, architecture/stage, exact prompt/input/output hashes, timestamps and paths.
- [Remaining calls](../benchmark/host-first-v030/REMAINING_CALLS.json): only the 23
  unfinished base calls, deterministic case order. Conditional repairs enter the
  external checkpoint only after this frozen validator requests one.
- [Repair accounting](../benchmark/host-first-v030/REPAIR_ACCOUNTING.json): initial
  validation, sole repair and original final result; final-runtime replay separately.
- [Freeze verification](../benchmark/host-first-v030/FREEZE_VALIDATION.json): branch,
  HEAD/status before changes, actual required validation results and hash checks.
- `RESUME_TOOLING_FREEZE.json`: hashes of these additions, wrapper and offline tests.
  Earlier `FINAL_FREEZE.json` remains valid for its original 154-file snapshot; new
  files are additions, not replacements. Every original file remains byte-identical.

## Configuration and invariants

The fixed model is **gpt-5.6-sol**, reasoning **high**, reference mode
**CONTROLLED_PRELOAD**, sandbox **read-only**, maximum repair **one per B case**.
Web search and all listed runner tools/features remain disabled; successful
historical calls invoked zero tools. No fallback model or reduced reasoning exists.
Autonomous reference reads remain a separate BLOCKED_BY_HOST issue.

Use the same raw input, frozen baseline, final frozen experiment/validator/Skill,
allowed reference preload, repair prompt/budget, rubric and AI operator review
protocol. No product rule, evidence rule, memory policy, action compiler, Skill,
reference, input, rubric or previous model output may change during resumption.
The previous AI reviewer is also the implementation author, not an independent
human or second-model judge. These v023 cases are now known development cases;
this experiment does not create a new blind distribution.

> Do not inspect future rubrics while generating missing responses beyond what the frozen runner already permits.
>
> Do not use previous evaluation outcomes to improve pending responses.
>
> Do not modify Skill, validator, repair rules or references before all frozen calls finish.

Hash verification may read rubric bytes as opaque files. Rubric contents must never
enter generation/repair prompts; only review after the new outputs are frozen.

## Resume procedure

Use an isolated checkout of baseline `acf2a34363bda9f67a47f3645fbd772b16f94508`
for A, and this experiment branch for B. For example create a separate checkout
with `git clone --no-hardlinks` and `git checkout` the exact baseline; do not switch
the experiment working tree back and forth. Baseline runtime and all frozen inputs
are hash-verified, so a directory claiming to be the baseline is insufficient.

The existing `resume.py` and `run.py` stay byte-identical. A manifest-gated wrapper
adds checkpointing and permission/order enforcement around that existing runner.
First run this **zero-model** verification from the experiment repository:

```powershell
python benchmark/host-first-v030/resume_manifest.py --baseline C:/temp/junshi-v023-baseline --state-dir C:/temp/junshi-v030-eval --plan-only
```

Replace paths for your machine. The state directory and private runtime must be
outside both repositories and separate from each other. On the configured Windows
machine, when model quota/access is available, resume with:

```powershell
python benchmark/host-first-v030/resume_manifest.py --baseline C:/temp/junshi-v023-baseline --state-dir C:/temp/junshi-v030-eval --private-runtime C:/temp/junshi-v030-private --node D:/Nodejs/node.exe --codex-js D:/Nodejs/node_global/node_modules/@openai/codex/bin/codex.js
```

Use the **same state directory** on every continuation. Never initialize a second
checkpoint for the same live experiment, which would permit duplicate sampling.
The wrapper verifies the fixed contract, baseline, original outputs and every
prior resumed cohort before execution. Completed call hashes/prompt hashes are
checked and those calls are skipped. It permits only PENDING calls, in H01→H10
order, then A extraction→A presentation→B generation→conditional sole repair.
It never overwrites a valid output. Each attempt writes to a new numbered cohort;
the external `state.json` is updated by atomic same-directory replacement after
each completed call. Newly requested repairs are added exactly once.

The external checkpoint is derived mutable progress; tracked RESUME_EVAL and
REMAINING_CALLS are the immutable starting contract. Do not edit them to mark a
call complete. Output files and recorded hashes are the completion evidence.
Keep checkpoint/cohorts together and back them up. Do not commit private event logs.

On quota/access failure, record **BLOCKED_MODEL_ACCESS** and stop after that first
failed call, retaining all attempts. Run no model fallback and no retry loop. A
later explicit invocation may retry that failed PENDING transport after access is
restored. A timeout or crash with uncertain completion records BLOCKED_RECOVERY:
inspect the retained response/private execution log before any retry, because the
service may already have generated a sample. A stale RUNNING.lock or state.json.new
also requires inspection; do not blindly delete it or overwrite evidence.

If any baseline, input, output, prompt, runtime, reference or tooling hash differs,
**STOP**. Do not regenerate/overwrite frozen files to repair the mismatch. Report
the exact path and restore verified bytes from the frozen commit if appropriate.

## Final review and decision

After all missing generations and necessary sole repairs finish, freeze each new
cohort before opening its rubric. Produce a separate combined-output index and
review; leave earlier failures, partial grades and original manifests untouched.
Transport completion is not semantic PASS; rejected/invalid cases remain failures
to evaluate. No fresh synthetic outcome or real hiring result may be fabricated.

Review the frozen fifteen semantic dimensions with PASS / PARTIAL / FAIL /
NOT_APPLICABLE and exact excerpts. Count semantic results, integrity hard failures
(fabrication, team-to-sole, metric credit, verbal-contract, silence-rejection,
success-causation, premature certainty), and pipeline failures (schema/extraction,
generic fallback, missing prioritization, artifacts). Classify validator behavior:
correct rejection, repaired wording/preserved move, false rejection, missed integrity.

For B report initial ACCEPT / REPAIR_REQUIRED / BLOCK over all observed initial
envelopes; repair success over attempted repairs; false-block/rejection candidates;
and recommendation.move changes over repairs. Keep initial and final validator
epochs separate. Currently initial acceptance=1/3, repair-required=2/3, BLOCK=0/3,
original repair success=1/2, unchanged moves=2/2. H03 is one false-rejection candidate;
the final-runtime retained-envelope replay accepts 3/3 without additional model calls.
Neither denominator is ten; no missing sample enters a numerator.

Apply the pre-existing gates without relaxing them: no increase in integrity hard
failures; at least 7/10 PASS or strong PARTIAL; at most one primarily schema/pipeline
failure; most valid recommendations survive; repairs preserve valid judgment; low
false rejection. Determine whether stronger semantic judgment survives with fewer
integrity and pipeline failures, not merely whether wording looks better.

YES adopts only after complete evidence; MIXED keeps experimental; NO rejects the
replacement. Until then the status is **MIXED / INCOMPLETE**. Main remains v0.2.3,
and no real-user pilot, release tag or merge is authorized by this freeze.
