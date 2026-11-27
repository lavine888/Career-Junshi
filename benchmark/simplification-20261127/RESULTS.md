# Simplification ablation results

On 2026-11-27, an authenticated ChatGPT account returned `READY` using Codex CLI
`0.171.0-alpha.13.2`, `gpt-6.2-sol`, and `medium` reasoning effort. All three arms
used this configuration. Each generation and each case review had its own
ephemeral session. Across the probe, 27 generations and nine reviews, 37 distinct
session IDs were observed. Memory, user configuration, shell, apps, agent tools
and web search were disabled. No model tool calls were observed.

| Arm | Valid / attempted | Frozen checks passed | Facts | Follow-up | Burden | Immediate value | Preferred, including ties |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A · Generic prompt | 9 / 9 | 25 / 26 | 18 / 18 | 3 / 4 | 17 / 18 | 17 / 18 | 4 |
| B · Short Skill | 9 / 9 | 25 / 26 | 18 / 18 | 1 / 2 | 17 / 18 | 18 / 18 | 4 |
| C · Original Skill | 9 / 9 | 25 / 26 | 18 / 18 | 2 / 2 | 17 / 18 | 18 / 18 | 5 |

Scores are the independent model reviewer's judgments. Follow-up applicability
varied across answers, so compare that dimension per case. An answer can pass its
frozen checks while still having a gap the reviewer records as an issue.

| Arm | Input Tokens | Cached input Tokens¹ | Output Tokens | Median wall time | Failures / tool calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 191,585 | 152,832 | 1,223 | 9.64 s | 0 / 0 |
| B | 219,340 | 145,664 | 1,212 | 10.17 s | 0 / 0 |
| C | 225,272 | 115,968 | 1,280 | 10.42 s | 0 / 0 |

¹ Cached input is included in total input. These are CLI-reported totals across
nine calls per arm and include the common host prompt. The access probe alone
reported 21,238 input Tokens. B used 2.63% fewer total input Tokens than C. The
wall times include CLI startup and network latency. Cache and startup varied
across calls, and neither billing cost nor a reliable speed improvement was measured.

## Where the answers differed

- **S01, first use.** B delivered usable wording but asked both “能举一个你维护的测试用例吗？”
  and “它检查的是什么排课冲突？”. C asked a single question anchored to testing.
  A asked one question but assumed the demo had actually detected a conflict,
  which the input had left unknown. Both Skill kernels and their shared reference
  already require one question at a time. This trace shows a concrete ambiguity
  in how a question is counted. It does not isolate an omitted C-only rule.
- **S04, 90 minutes before an interview.** C filled all 90 minutes with three actions
  and added a review outside that budget. B met the time constraint. A's prep
  plan was preferred because it included wording and a concrete design drill.
- **S06, recruiter silence.** A supplied a message and a conditional send time
  but omitted a post-send observation window and stopping rule. B and C
  supplied both. Retain the recruiter follow-up contract.
- **S07 and S08, offers and continuation.** C was preferred in S07 because it
  verified ongoing engineering scope and expected time commitment. A was
  preferred in S08 because it retained both the revision and submission state
  of R2. Equal checklist totals hide these differences.

## What to keep and what to cut

Keep the shorter B kernel as the comparison base. The experiment gives no
reason to restore C's extra entry-point tables and repeated workflow steps as a
bundle. Preserve the obligations that mattered in the reviews: factual scope,
one answerable follow-up, the user's actual time budget, the HR observation and
stop window, decision reversal conditions, and the original submission record.

B and C used the same task references. This design cannot establish which task
reference is safe to delete. The full router is a candidate for a later
single-variable test on the five indexed scenarios. Today it adds 4,379 source
characters per indexed case. Since B showed a first-use regression, the replay
tested only one clarification in the first-use reference under the frozen B
loading policy. Router and reference deletions remain unvalidated.

## Candidate replay and release decision

D clarified what counts as one answerable follow-up in
[a three-line reference patch](results/candidate.patch). The nine frozen cases
were generated again with the same model and effort. S01 and S02 added 145
characters each. The other seven prompts were byte-for-byte equal after LF
normalization. All nine generations and nine new pairwise reviews completed
without tool calls. Each reviewer saw the retained B answer and the new D
answer in randomly labeled order.

| Arm in the pairwise review | Frozen checks passed | Facts | Follow-up | Burden | Immediate value | Preferred, including ties |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B · Original answer retained | 25 / 26 | 17 / 18 | 1 / 2 | 17 / 18 | 18 / 18 | 5 |
| D · Clarified reference | 25 / 26 | 17 / 18 | 2 / 2 | 17 / 18 | 17 / 18 | 7 |

D fixed the two-question behavior in S01 in this sample. In S02 it split the
requested replacement sentence into two sentences, moving the checklist
failure rather than removing it. The seven identical prompts also produced
different answers, including the unconfirmed “one-way” commute detail in
S07. Those differences demonstrate sample variability. The change has not
earned promotion to the shipped reference. The PR keeps B's reference
and stores D as a reproducible patch.

[Replay responses](results/replay-packet.json), [replay blind reviews](results/replay-reviews.json),
[replay mapping](results/replay-mapping.json), [replay telemetry](results/replay-generation.json)
and [aggregate scores](results/replay-summary.json) record the full replay.
Apply the candidate patch on a disposable checkout before running
`run.py --candidate` to reconstruct D's prompts.

## Deterministic checks

The Python suite ran 286 tests with 285 passed and one Windows symlink test
skipped. Package validation passed. The 13 structured benchmark cases showed
zero regressions. A separate legacy Holdout runtime replay still reports its
documented H03 extraction failure. The nine frozen prompts above evaluate
generated answers, while these checks cover distinct deterministic paths.

## Evidence and limits

- [Original responses](results/blind-packet.json), [frozen reviews](results/blind-reviews.json),
  [mapping opened after review](results/mapping.json), [generation telemetry and prompt hashes](results/generation.json),
  [aggregate counts](results/summary.json).
- Reviews were generated by the same model family in separate, identity-hidden
  sessions. The reviewer did not receive prompts, arm labels, session IDs or
  telemetry. A single sample per case and one model reviewer leave uncertainty
  from generation and judgment variability. No users or hiring outcomes were measured.
- References were supplied before generation. Zero tool calls reflects the
  experiment design. Real installed routing, reference retrieval, multi-turn
  follow-up quality and real-user value remain unmeasured.
