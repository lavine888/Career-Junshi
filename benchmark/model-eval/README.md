# Frozen synthetic host-model comparison

Read `RUN_MANIFEST.json` for snapshots, actual model access probes, settings,
timestamps, attempt statuses and output hashes. `MODEL_EVAL_RESULT.json` contains
unblinded counts and per-case diagnostics, not an intelligence score.

`raw/` preserves final model answers byte-for-byte. `reviews/` preserves final
blind-review judgments byte-for-byte. CLI transport logs are intentionally excluded:
they can contain local paths and account/runtime metadata. Failed attempts remain
in the manifest; no responses or judgments are rewritten for grading. The local
.gitattributes disables Git newline conversion throughout this evidence directory,
so committed and cloned bytes retain the recorded hashes.

`blind/review-packet.json` contains only case, rubric, Response A and Response B.
The randomly assigned mapping was stored separately during review and its hash
committed to the local manifest before reviews began. `UNBLIND_MAP.json` is released
only after all review attempts were frozen. This timestamp/hash chain is a local
audit trail, not an independently witnessed preregistration or reviewer attestation.

For a fresh human blind review, share only the review packet; do not share the
manifest, aggregate results or released mapping until the human judgments are frozen.

The fixed set is 13 existing synthetic cases plus 2 prepared holdouts. It contains
no claim-reference history or duplicate historical observations. Those two v0.2.1
runtime corrections are outside this model comparison's coverage. No tools,
Python guards, installed-skill discovery or real recruiting outcomes are tested.

## Audit the saved run

```sh
python verify_artifacts.py
```

This checks hashes, pair invariants, blind packet fields, exact reviewer excerpts,
and counts. It does not authenticate the model's semantic judgment or establish
career effectiveness. The generating CLI was 0.153.0; exact reproducibility of
response text is not expected because remote models and sampling can change.

## Repeat in a new directory

Use Python 3.11+ and an authenticated Codex CLI. The evaluator reads the current
authentication, ignores user model/MCP configuration, and never changes persistent
configuration. Verify that the two saved model identifiers are actually accessible
in your account before starting. Do not substitute models midway.

```sh
python new_run.py --target /new/empty/evaluation-directory
cd /new/empty/evaluation-directory
python run_eval.py probe --model gpt-5.6-sol
python run_eval.py probe --model gpt-6-astra --reviewer
# Continue only when both probes report AVAILABLE.
python run_eval.py generate
python blind_eval.py prepare
python blind_eval.py review
python finalize_eval.py
python verify_artifacts.py
```

Use a new local directory, outside public user-data storage. This preserves the
published run and makes new contexts, outputs, hashes and a new random mapping.
No blind packet or mapping from this published run is copied into the repeat.
If a model is unavailable, keep the probe failure and stop; choose a different
fully documented protocol before generating, rather than mixing hosts in one run.

Generation uses `gpt-5.6-sol/high`, timeout 240 seconds, three independent concurrent
requests. Review uses `gpt-6-astra/high`, timeout 300 seconds, three independent
concurrent requests. Every invocation is ephemeral, read-only, ignores user config,
sets project document budget to zero, disables web search and the shell/apps/
multi-agent/remote-plugin/hooks/memories feature flags. Prompts forbid all tool use;
the JSONL audit rejects observed command/MCP/web/file tool calls. No such calls
occurred. Only the frozen case, Skill and the same 1-3 reference paths/count budget
vary by snapshot content. Their character lengths need not match.

The shared generation instruction already asks for recommendations, 1-3 actions,
uncertainty and stop/review conditions, which can reduce measured Skill differences.
Prepared routing is preserved: denial/rejection cases use the follow-up reference,
and the negotiation case uses the offer reference. This is not a test of automatic
reference selection. The review rubric is unavailable in generation prompts.

The reviewer sees no Skill text, commit, version, path, mapping, build report or
expected winner. Twelve dimensions use A_BETTER / B_BETTER / TIE / NOT_ASSESSABLE;
material hard failures are reported separately. A verdict is a model diagnostic,
not a certified human judgment. Missing behaviors can use an empty excerpt; all
nonempty excerpts must be contiguous substrings of the actual response.

REAL-WORLD-OBSERVED: NO. Neither model wins nor synthetic failure counts establish
better hiring outcomes, general career-advice quality, or causal benefits.
