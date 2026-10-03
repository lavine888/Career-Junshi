# Holdout execution audit

The original run used fresh ephemeral `gpt-5.6-sol` contexts, high reasoning,
CONTROLLED_PRELOAD, disabled shell/web/apps/memory and separate L1/L3 calls.
No outcomes were supplied. The synthetic clock is not live recruiting evidence.

`first-pass-prompts/` contains the exact messages reconstructed from input, installed
Skill, allowed references and extraction contracts. Every UTF-8 prompt digest
matches its actual invocation record in `first-pass-prompt-manifest.json`.
Rubrics, expected recommendations and outputs were never included in generation.
The generic extraction contract is serialization guidance, not a case answer.

For a new response, use a fresh workspace containing the installed Skill and a new
output path. Match the historical Skill/reference bytes; SKILL.md and the allowed
reference files did not change in this iteration. Install with the existing
`scripts/install_skill.py --target WORKSPACE/.agents/skills/career-junshi` helper.
The run also preloads the exact historical content.

```text
python benchmark/holdout-v023-runner/generate_response.py PROMPT.txt NEW_OUTPUT.md --workspace FRESH_INSTALLED_WORKSPACE
```

Add `--extraction` for an L1 wrapper. For Node-based Codex, supply `--node` and
`--codex-js`. The runtime/schema/tool restrictions match the recorded runs.
Provider/model access and authentication must already work; this script never
installs dependencies or reads credentials. Prompt files preload the historical
Skill/reference content, so baseline regeneration does not silently load a new
product revision. New generations are nondeterministic, never overwrite evidence.

```text
python benchmark/holdout_tools.py verify
python benchmark/holdout_tools.py replay
python benchmark/holdout_tools.py replay --dataset holdout-v023-after
python benchmark/holdout_tools.py replay --dataset holdout-v023-mutations
```

Replay checks source identity and current compilation. It does not regrade semantics.
The Codex AI evaluator authored and reviewed the cases; no independent rater agreement is
claimed. Inspect retained excerpts and failure classifications before relying on
aggregate judgments.

`after-prompts/` and `mutations-prompts/` likewise reproduce all 26 actual messages
with matching hashes. All ten original/after host messages are hash-identical:
L3 changes cannot be attributed to compiler changes. Forty-six actual model calls
were made (20 baseline, 20 after, 6 mutations); no semantic-review model call is
claimed. The reviewer is the same Codex AI operator.

The frozen reviewer metadata contains an incorrect human label. See
[the identity erratum](../../documentation/V023_EVALUATOR_PROVENANCE.json); no
independent human review took place. Hashes and scores remain unchanged.

Git attributes preserve frozen corpus and runner bytes instead of normalizing
line endings. Prompt manifests distinguish serialized-file hashes from the
UTF-8 message hash (Python universal-newline decoding reproduces the sent
message). Product execution hashes record the working bytes actually executed;
ordinary source files retain the repository Git normalization policy.
