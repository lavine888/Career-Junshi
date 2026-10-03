# Five core mock career decision cases

All materials and outcomes are **synthetic** and supplied for public debugging.
`input.md` contains the supplied visible case section; `input.json` preserves every
source block verbatim and discloses a fixed scenario clock. `rubric.json` and
`mock-outcome.json` are evaluator-only, withheld from generation.

The five properties are interview bottleneck identification, recruiting uncertainty,
offer decisions under uncertainty, career direction prioritization, and ownership
discipline. `golden-properties.json` defines machine integrity guards and links each
semantic rubric. It never requires an exact offer winner or role ranking.

Run the frozen extraction regression from the repository root:

```sh
python benchmark/mock-career-cases/replay.py
```

This replays the final real-model extractions through current helpers, without a
new model call or persistent memory. It cannot grade career judgment. Read the
[debug report](../../documentation/MOCK_CASE_DEBUG_REPORT.md) and per-case
`debug-results/<case>/evaluation.json` for semantic results and remaining failures.

Artifacts retain all four extraction attempts, three host attempts, initial failure
clusters, raw independent model reviews, actual CLI decisions/artifacts, and mock
outcome calibration. `before` and `after` use identical lossy repaired packets and
isolate code changes. `complete` and `final` additionally repair measurement assembly;
they are not evidence of code-only gains. The first harness attempt is preserved
as `before-harness-attempt1` and is not counted as a completed run.

Host generation used native temporary runtime installs. Initial reference reads
were rejected by nested exec policy; qualified baseline/after runs preload allowed
reference contents, with tools disabled. Autonomous retrieval remains unverified.
Generation and reviewer contexts are fresh, using gpt-5.6-sol/high. Reviews use the
same model family and are independently checked by the operator; no blinded or
independent-family quality claim is made. Full logs containing local runtime/account
details remain private; public transport metadata records times, usage and hashes.

Only isolated temporary stores receive mock Decision/Outcome records. Synthetic
outcomes never create a recurring real-world risk, ability label, or success cause.
Case 2 A/B are independent compatible outcomes, not result forecasts. Missing
observations stay unassessable; the explicit not-asked probe is separately labeled.
No real candidate memory, private vault or external career action is used.
