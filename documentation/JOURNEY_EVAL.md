# Job-search journey and reusable layouts

Date: 2026-10-21. Baseline: `b8fd603e93a20a180fe8cca8d0a4bd015eccf204`.
All distributed material and observed trial requests are synthetic. No real candidate
files, long-term memory, recruiting actions or hiring outcomes were used.

## Implemented scope

- Explicit journal replay links project/claim revisions, resume versions and hashes,
  opportunity identity, actual reported submissions, later attachment updates,
  recruiting observations, actions, execution receipts and linked review actions.
- Corrections flag stale resume versions without rewriting prior submissions.
  Updated attachments in the same process do not add initial applications.
- No default persistence or file discovery. File verification is explicit; requested
  checkpoints are new private directories outside Git and the installed Skill.
- Existing compact memory behavior and consent rules remain unchanged. The optional
  journal is a user-requested working artifact, not an automatically activated store.
- Resume export preserves standard behavior and adds an editorial template and blank
  photo area. Actual artifact hashes and optional lineage are included in verification.
- Explicit sourced feedback context can distinguish a reported gap from cancellation;
  unstructured guesses do not replace host review or prove causality.

## Automated verification

`python -B -m unittest discover -s tests -v`: 262 tests passed in the full run.
This final run includes attachment-update handling and installed-runtime continuation.
`python -B scripts/validate_skill.py`: valid, no errors.
The generic skill-creator validator also passed using Python UTF-8 mode on Windows.

`python -B scripts/benchmark.py run`: 13 frozen cases, no regressions using the
protocol clock (2026-10-03 12:00 +08:00). A preliminary run using the current date
instead failed G06's `urgency.within_72h` expectation because that fixed interview
was no longer imminent; no planner or expectation was changed to hide the result.
[Both clock results](../benchmark/journey-20261021/benchmark-clock-check.json).

The two continuous journey regressions cover:

1. Audited synthetic claim → actual source export R1 → reported application →
   interview feedback → linked practice and partial execution → claim correction →
   new editorial source version R2 → reported material update → private checkpoint →
   restored identical state. R1 remains the original submission and becomes stale;
   R2 is a child version, one opportunity remains one opportunity, and source-only
   does not become a checked PDF. Claim confidence remains self-reported.
2. Reported cancellation → stop local investment → cross-opportunity next action.
   Other opportunities remain planned and the claim is not downgraded from the outcome.

Other boundaries cover duplicate IDs, wrong project/revision links, missing execution
parents, future reports, mixed claim revisions, file hash changes, installation,
private output/no overwrite and incompatible layout/photo options. Source-only tests
use real local source exports; they do not pretend to compile or inspect a PDF.

## Actual PDF compilation and inspection

Three actual XeLaTeX compilations (two passes each), using MiKTeX-XeTeX and independent
Poppler 26.09.0, produced three one-page synthetic PDFs:

- Chinese editorial layout, blank 28 × 38 mm photo area, two internships and projects.
- English editorial layout, links and an education entry with no bullets.
- Chinese standard layout, preserving the existing source-only input contract.

All three passed compilation, page, log, text coverage, reading order and occurrence
checks. Every rendered page was inspected at 1500 px; no clipping, missing glyphs,
overlapping text or isolated headings were observed. Actual assets and hashes are in
[the verification record](../benchmark/journey-20261021/verification.json).

A journal using the actual compiled English PDF and its hash receipts was also run:
missing host visual review → REVIEW_PENDING; no explicit file verification →
REVIEW_PENDING; matched files plus actual content/visual reviews → READY; later
sourced claim revision → STALE. This is mechanical readiness and operator review,
not authentication of the supplied claims or a universal ATS certification.
The machine exporter itself still does not mark content/visual review passed.

## Fresh-context host trial

One fresh-context subagent used SKILL.md and three relevant resources. It received
no tests, cases, implementation findings or expected answer. Two sequential synthetic
user turns covered a corrected team contribution, already-submitted R1, reported R2
attachment update and a reported recruiting freeze without ability feedback.

Observed outputs preserved self-report, original submission history, draft versus
actual reported artifacts, no default persistence and local rather than directional
adjustment. [Requests and response excerpts](../benchmark/journey-20261021/forward-trial.md).
This is one same-host-model trial, not an independent human study, different-model
review or evidence of outcome improvement. Tool side effects were agent-reported;
there was no independently authenticated full trace of hidden tool behavior.

## Remaining limits

- No real-user completion time, adoption, retention, interview or Offer effect measured.
- Existing frozen behavioral benchmarks were not all rerun.
- A supplied journal is an operator account, not authenticated evidence. The helper
  validates identity and checks receipts; the host must verify semantic mapping,
  feedback classification, sources and decisive career judgments.
- A summary-only card cannot restore missing raw facts or exact earlier advice.
- Real portrait insertion, cross-machine font substitution and arbitrary custom TeX
  are outside the actual layout test. Reinspect after adding a photo.
- No existing installed copy is silently overwritten or updated.
