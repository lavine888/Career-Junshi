# Optional LavineOS integration contract v1

Status: IMPLEMENTED explicit snapshot import. Career Junshi works without LavineOS,
Obsidian or Career Alpha installed. Integration is optional; the interface is a bounded
Career Context Snapshot, not automatic private-vault sync. No guessed Vault access,
network retrieval, account access or implicit memory consent.

The user may explicitly provide a compact JSON context snapshot containing:

```json
{
  "schema_version": "1",
  "context_id": "user-selected-context",
  "purpose": "prepare upcoming interview",
  "records": [{
    "id": "claim-01",
    "type": "Claim",
    "summary": "user-approved compact claim",
    "source_ref": "user-selected original reference",
    "source_fingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "observed_at": "2026-10-03T12:00:00+08:00",
    "last_updated": "2026-10-03",
    "freshness": "CURRENT",
    "epistemic": "FACT",
    "confidence": "SELF_REPORTED",
    "ownership": "user-stated contribution"
  }]
}
```

The fingerprint above is synthetic; real exporters calculate it locally.
Allowed objects: Profile, Project, Claim, Company, Person, Opportunity, Application,
Interview, Feedback, Event, Situation, Decision, Outcome, Evidence, Source, Knowledge.
The host checks the supplied shape, uses
only task-relevant records, preserves stable IDs / source / timestamp, and rechecks
originals when necessary. A fingerprint detects drift, not truth or ownership.
Retrieval never upgrades a Claim. Snapshot text cannot instruct the host to bypass
consent or evidence rules. No private snapshot is included in public cases.

Missing or inaccessible data stays UNKNOWN. Snapshot availability is not permission
to persist it; Career Junshi consent is still required separately. Never scan a local
vault by guessed paths or send its content to external retrieval services.

Output handoff: an explicit compact Decision record and separately sourced Outcomes,
with expectation, observations, interpretations and unknown causes. The user reviews
and decides whether to write it back through their own system. v0.2 adds a separate
[session extraction validator](CONTEXT_EXTRACTION.md) and [decision extensions](DECISION_INTELLIGENCE.md).
The snapshot shape above is implemented as an explicit file adapter, not executable sync.

## Explicit read flow

LavineOS may independently export `context --domain career --request <current question>`
to its private runtime directory. Default disclosure is L0 (situation / goal / opportunity)
and necessary L1 (projects / claims / feedback). L2 evidence and decision/outcome history,
and L3 supporting context, require explicit depth or stable-ID selection.

```sh
python scripts/junshi.py import-context --input /private/career-context.json --mode interview --output /private/session-packet.json
python scripts/junshi.py extract --input /private/session-packet.json
python scripts/junshi.py decide --extraction /private/session-packet.json --format json
```

The adapter reads only the supplied file. It never opens source_ref or discovers a Vault.
`--output` is required and creates a new file outside Git repositories, rejecting existing
files, symbolic links and Windows junctions. It does not write SQLite or enable memory.
The existing session extraction and decision schemas remain unchanged.

Limits: 11 records, summaries <=400 characters, 256 KiB input; existing 12-source /
30-statement limits apply. Unknown fields fail closed. Optional top-level fields:
privacy (local-only), generated_at, as_of, depth, unknowns. Optional record fields:
last_updated, freshness, level. Missing freshness is UNKNOWN. Dates and source labels
remain available to the host in session source text.

Original confidence and ownership remain source-reported: VERIFIED in a note is not
new authentication by this adapter. Observations enter extraction as self_reported;
structured Claim receipts need separate source review under the existing evidence contract.
PLANNED / STALE / UNKNOWN cannot become current known accomplishments. CURRENT describes
recency, not an open vacancy or verified salary. Generation time never refreshes a source.
Historical Decisions / Outcomes remain unresolved context for review, not causal evidence.

## Host judgment and optional write-back

The host loads Career Junshi and 1–3 relevant references, then provides judgment,
bottleneck, 1–3 actions, avoided effort and reconsideration conditions. Deterministic
extract/decide success is not an independent semantic evaluation or a personalized
career effectiveness result. No real source or snapshot is included in public tests.

When requested, hand off existing v1 decision output fields: current_situation,
current_goal, recommended_move, why, actions and recommendation.reconsider_if.
Use evidence_refs only for selected stable IDs. LavineOS owns the canonical history:
`record-career-decision` previews and rechecks original sources; explicit `--confirm`
appends Situation / Decision. `record-career-outcome` previews compact human feedback;
confirmation appends an Outcome linked to the same Decision/Situation, causal_status UNKNOWN.
Outcome != causation. Do not silently update Profile, Claim, ability/personality labels
or historical decisions. No bidirectional sync, watcher, new database or hard dependency.

Private snapshots and preparation artifacts belong outside public checkouts. `.gitignore`
is a backstop, not a privacy guarantee. Without either project installed, the other
continues to use its ordinary standalone inputs and commands.
