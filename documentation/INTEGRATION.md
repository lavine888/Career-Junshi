# Optional LavineOS integration contract v1

Status: DOCUMENTED. No automatic vault access, parser, import, writeback or sync is
implemented. Career Junshi works without LavineOS, Obsidian or Career Alpha installed.

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
    "source_fingerprint": "sha256 of original source, calculated locally",
    "observed_at": "2026-10-03T12:00:00+08:00",
    "epistemic": "FACT",
    "confidence": "SELF_REPORTED",
    "ownership": "user-stated contribution"
  }]
}
```

Allowed conceptual objects: Profile, Project, Claim, Company, Application, Interview,
Feedback, Situation, Decision, Outcome. The host checks the supplied shape, uses
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
The LavineOS snapshot shape above remains a documented interface, not executable sync.
