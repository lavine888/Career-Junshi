# Continue one traceable job-search journey

Use when a user wants to continue a search, connect a resume to an application,
return feedback, record actual execution or update affected materials. This replaces
an unrelated practical reference within the 1–3 reference budget. The journal is
an optional working artifact, not a new decision engine or a mandatory sequence.

## Host behavior

- Reuse this chat, a user-pasted continuation card or an explicitly supplied journal.
  Do not search private folders, create memory or ask the user to fill a database.
- State the current opportunity, the actual material version and the one useful next
  action. If a card lacks original sources, keep that boundary; never reconstruct
  supposed exact old advice, submissions or results from its summary.
- Resume preparation, actual submission, recruiting progress, action execution and
  review are separate observations. A draft, an instruction to apply or a completed
  practice session is not a reported submission. An early reply is not an Offer.
- For a reported submission, capture company/role identity, resume version, actual
  time and source. Deduplicate the same hiring process, preserving the version
  originally sent. A later revision does not silently replace that history.
- Classify a feedback category only from the supplied observation. `skill_gap`
  concerns an explicitly discussed gap, `role_cancelled` an explicitly reported
  cancellation, `process` scheduling/process observations; otherwise use `unknown`.
  Preserve source and origin. A question alone is not proof of weakness or rejection.
- After review, choose a concrete linked next action and explain why: practice,
  rewrite, refresh role information, stop this opportunity, verify, or continue.
  A cancellation should not downgrade claims. One rejection cannot establish a
  general career pattern. Use the existing decision-review and hypothesis rules.
- Keep action plans intact. Append a sourced execution receipt for DONE / PARTIAL /
  BLOCKED / UNKNOWN, explaining what was actually done and what remains unchecked.
  `apply`, messages and major decisions retain human ownership. The helper records
  reports; it never performs those external actions.
- When a fact changes, append a new claim revision naming the old revision. List
  affected resume versions, keep their original artifacts and submissions, and
  produce a new resume ID with the former ID as parent. Do not upgrade confidence
  from an interview result or automatically resend a corrected resume.
- End a meaningful work session with a short continuation card: current goal,
  opportunity/status/version, remaining next action, known evidence gap and review
  trigger/date. Omit irrelevant fields. Date windows are observations, not scheduled
  reminders; never invent dates or holiday calculations.

## Persistence and helpers

Default: card in chat, no files. A user request for a private checkpoint authorizes
that selected working artifact only. It does not enable durable memory, automatic
reads, folder discovery, cloud sync or publishing. Memory still requires its own
explicit consent. Only synthetic data belongs in the public repository.

```sh
python scripts/junshi.py journey --input /private/journey.json
python scripts/junshi.py journey --input /private/journey.json --event /private/event.json --verify-files --output-dir /private/new-checkpoint
```

The first command only reads the supplied journal and prints a card. Without
`--verify-files`, listed resume files are not opened. `--event` appends in memory;
the input is never overwritten. `--output-dir` creates `journey.json`, `review.json`
and `continue.md` in a new directory outside Git and the Skill. Bring the full
journal back for exact replay; a summary alone carries only the facts it contains.
Missing/changed files prevent READY. Merely printing the card does not save it.

## Bounded packet and events

Top-level fields are exactly `schema_version: "1"`, `case_id`, `goal`,
`next_review_at` (timezone-aware ISO time or empty text), and `events` (at most 100).
Input is limited to 256 KiB. Archive explicitly when full; do not silently evict.
Every event has exactly `id`, `type`, `at`, `source`, `origin`, `payload`.
IDs are unique; `at` is a timezone-aware recorded observation time, not future work;
`origin` is `synthetic`, `real_world` or `unknown`. These are operator reports,
not authentication. Dependencies must precede their references in append order.

| type | Exact payload fields |
| --- | --- |
| claim | `project_id`, `claim` (existing raw audit model), `supersedes` (previous revision event ID or empty for first) |
| opportunity | `opportunity_id`, `company`, `role` |
| resume | `lineage`, `artifacts`, `checks` copied from actual export and review records |
| submission | `opportunity_id`, `resume_id`, `submitted_at` |
| material_update | `opportunity_id`, `resume_id`, `sent_at`, `summary`; a reported attachment update in the same hiring process, not a second initial application |
| recruiting | `opportunity_id`, `status`, `summary` |
| action | `kind` (existing action kinds), `description`, `opportunity_id` (empty for a cross-opportunity action) |
| execution | `action_id` (action event ID), `status`, `summary` |
| feedback | `opportunity_id`, `category`, `summary`, `claim_refs` |
| review | `feedback_id`, `conclusion`, `reason`, `next_action_id` |

A claim revision reference is exactly `{project_id, claim_id, revision_id}`; it
must identify the same recorded project and claim. Resume lineage is exactly
`{resume_id, parent_resume_id, opportunity_id, claim_refs}`. Empty parent/opportunity
IDs mean none; a tracked resume requires at least one explicit claim revision.
The parent and any target opportunity must already exist. Unlinked source exports
remain supported; they cannot establish claim-to-application traceability.

Each artifact is `{kind, path, sha256}` with kind `tex` / `text` / `data` / `pdf`,
an absolute path and lowercase SHA-256. Copy actual exporter receipts, not guessed
paths. `--verify-files` checks only those files (each at most 30 MiB). File hashes
identify versions; they do not verify career claims or replace PDF inspection.

READY requires an actual hash-matched PDF and all of `content_check: PASSED`,
`compilation: COMPILED`, `page_check: PASSED`, `text_check: PASSED`, `log_check: PASSED`,
`visual_review: PASSED`. The host can report the content/visual checks only after
performing them, with the event source pointing to that review. The other checks
come from the actual export. No new check is manufactured by the journal.
A source-only export remains SOURCE_ONLY. Changing a referenced claim revision
marks the old resume STALE; modifying an artifact is FILES_CHANGED. Record a later
reported corrected attachment as material_update, preserving the original submission
and its version. Sending does not prove the employer adopted or reviewed it.

Recruiting statuses are waiting / interview / offer / rejected / withdrawn / freeze.
Except withdrawing/freezing an unsubmitted opportunity, progress requires an
actual reported submission. Silence remains waiting. Explicitly reported new facts
may update status; conflicting records need host review rather than invented truth.
The latest review prioritizes its linked unfinished action, without discarding
other pending work. Original events and claim revisions stay intact on export.

Legacy `feedback` accepts optional `feedback_context: {category, text, source}`
using the categories above. Without it, the command keeps its conservative status
hint; it does not infer a cause from free text. This command does not replace the
host's comparison with the original recommendation.
