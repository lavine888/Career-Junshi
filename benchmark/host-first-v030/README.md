# v0.3 host-first experiment — incomplete

The original ten inputs/rubrics and all v023 freezes remain unchanged. `fresh/`
contains a real gpt-5.6-sol/high CONTROLLED_PRELOAD attempt: 18 service attempts,
9 completed generations, 9 explicit usage-limit failures, one complete A/B pair.
It is not a completed ten-case comparison. No failed call is replaced by a mock
or an old semantic response. `fresh/OUTPUT_FREEZE.json` precedes rubric-informed
review and preserves the raw responses, prompts, failures and CLI results.

`QUOTA_INTERRUPTION.json` retains the service failure evidence. Raw process logs
remain private; public records retain hashes/settings/timestamps/usage/tool counts.
No tools were invoked by successful model turns. The service's reset-time text is
not interpreted as a confirmed timezone-aware reset instant.

`post-run-correction/` replays exactly retained envelopes after the general internal-
negation guard fix. It makes zero model calls and is not an extra repair round.
`final-runtime/` uses the final validator, including factual percentage binding and
optional legacy prediction handoff. It is a separate deterministic replay, never a
fresh sample. Earlier rejected results remain intact. The AI operator review lives
outside `fresh/`; there is no independent human or second-model-rater claim.

## Initial run

Provide an isolated checkout of baseline commit acf2a34363bda9f67a47f3645fbd772b16f94508.
Do not run A against the new experimental checkout. `BASELINE_RUNTIME.json` records
canonical UTF-8/LF hashes of the original runtime. The runner installs each actual
runtime into a fresh temporary workspace. Both arms receive the same frozen raw
input and allowed reference payload. B receives the new Skill/envelope contract;
A receives the old extraction contract and actual baseline compiled decision.
Serialization and presentation prompts differ as required by the architecture.

```text
python benchmark/host-first-v030/run.py --baseline FROZEN_V023_CHECKOUT --output NEW_RESULTS --private-runtime NEW_PRIVATE_RUNTIME --node NODE_PATH --codex-js CODEX_JS_PATH
```

The installed model/runtime must have available gpt-5.6-sol quota. Do not switch
models to fill missing cells. Do not pass a rubric to generation. No pilot, memory
consent, employer message or application is performed by either runner.

## Resume missing calls

The resume helper verifies parent freezes and baseline runtime hashes. It reuses
only successful responses whose actual prompt/response hashes match, preserves the
one-repair budget, and stops at the first usage-limit rejection. Every new run
requires a fresh output/private directory. A previous failed/rejected response is
never deleted. Reuse several frozen cohorts by repeating `--previous` newest first.

```text
python benchmark/host-first-v030/resume.py --previous benchmark/host-first-v030/fresh --baseline FROZEN_V023_CHECKOUT --output NEW_RESUMED_RESULTS --private-runtime NEW_PRIVATE_RUNTIME --node NODE_PATH --codex-js CODEX_JS_PATH --plan-only
python benchmark/host-first-v030/resume.py --previous benchmark/host-first-v030/fresh --baseline FROZEN_V023_CHECKOUT --output DIFFERENT_NEW_RESULTS --private-runtime DIFFERENT_NEW_PRIVATE_RUNTIME --node NODE_PATH --codex-js CODEX_JS_PATH
```

`--plan-only` was actually verified: 23 missing base calls, zero model calls. New
B cases may need at most one repair each. Already completed repairs must be reused,
not regenerated. New cohorts disclose their runtime epoch and parent hashes; the
general guard correction must not be hidden as a code-identical first pass. A quota
error is an execution blocker, not evidence of career judgment failure or success.

After all ten pairs complete: freeze outputs, review against the original rubric,
compare original versus final-runtime failures separately, run regressions, and
apply the documented YES/MIXED/NO adoption gate. A future independent distribution
is needed to establish generalization beyond these now-known development cases.
