# Simplification ablation — 2026-11-27

Status: **27 independent generations and nine blind case reviews completed**. See the [results and decision](RESULTS.md).

Frozen source commits: B `dd5ea0330c3b1c1c5a3e83fa643fc0ea5f7ff8f0`, C `0b9d091b95bf540e28d25111d222d3bb9096b2c8`. A is a strong generic career-coach prompt in cases.json. Nine synthetic scenarios, not real candidate data.

## Actual source character measurements

| Case | A prompt | B direct | B selected | C direct | B with index | C with index |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S01 项目首用 | 217 | 9879 | 9879 | 12639 | 14258 | 17389 |
| S02 答后改写 | 217 | 9879 | 9879 | 12639 | 14258 | 17389 |
| S03 JD 硬门槛 | 217 | 9415 | 13794 | 12175 | 13794 | 16925 |
| S04 紧急面试 | 217 | 8231 | 12610 | 10991 | 12610 | 15741 |
| S05 整场模拟 | 217 | 12140 | 16519 | 14900 | 16519 | 19650 |
| S06 HR 沉默 | 217 | 5232 | 9611 | 7992 | 9611 | 12742 |
| S07 Offer 比较 | 217 | 7757 | 12136 | 10517 | 12136 | 15267 |
| S08 旧版本接续 | 217 | 12283 | 12283 | 15043 | 16662 | 19793 |
| S09 明确停止 | 217 | 2738 | 2738 | 5498 | 7117 | 10248 |
| Total | 1953 | 77554 | 99449 | 102394 | 116965 | 145144 |

Measured LF-normalized source characters (not tokens). Same task input and framing excluded from all arms. Selected references held constant across B/C. B selected includes the full routing index for five scenarios, and uses the explicit direct route or simple reply for four. C direct assumes the original entry can route each case directly. Both are modeled policies; no tool trace observed. If both read the index, compare the last two columns instead. A lacks the task reference material by design.

Finding: B kernel saves 2,760 characters, but an additional B router read costs 4,379. B selected is -2.88% versus C direct across this sample, rather than the ~50% kernel-only reduction. For an individual indexed route B can cost 1,619 more characters than C direct. Do not claim measured latency, token cost or quality gains.

## Independent test protocol

`python benchmark/simplification-20261127/run.py --model <accessible-model> --output /private/new/run-dir`

Requires authenticated Codex CLI, both frozen commits available via Git, and an accessible model. The runner probes model access, saves the exact prompts, then starts a fresh ephemeral invocation for each answer. It records the CLI's token counts, wall time, unique tool items and failures. The review packet excludes arm mapping, prompts and telemetry.

```sh
python benchmark/simplification-20261127/run.py --model gpt-6.2-sol --effort medium --output /private/new/generation
python benchmark/simplification-20261127/review.py --model gpt-6.2-sol --effort medium --packet /private/new/generation/blind-packet.json --output /private/new/review
```

The reviewer receives one synthetic input, its frozen checks and its anonymized answers per fresh session. Review each check as pass, fail or unknown with evidence from the response. Score factual accuracy, follow-up quality, burden and immediate value separately. Freeze these records before opening the mapping. Transport logs, prompts and session identifiers stay in the private run directory.

This protocol compares **preloaded prompts**. S02 and S08 replay frozen prior state. Installed-Skill routing, adaptive multi-turn behavior and real-user outcomes require separate observations.

For a follow-up replay, add `--candidate` to the generation command and choose a new
output directory. This runs the nine cases using the current checkout and B's
reference-loading policy. To compare with B, pair each replay answer with the
original B answer under fresh random labels in the same packet format. Keep
the new mapping separate and use `review.py --responses 2`. Treat this as a
separate round and retain the original 27 generations.
