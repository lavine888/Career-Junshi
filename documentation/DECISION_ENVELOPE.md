# Decision Envelope v2

The host owns the recommendation. Python validates source bindings and explicit
integrity boundaries, compiles host materials, and hands compressed decisions to
the existing consented store. Legacy `decide` remains available for comparison.

## Core contract

```json
{
  "schema_version": "2",
  "situation": {"summary": "Should I apply?", "mode": "job", "goal": "Test current fit"},
  "facts": [{"id": "F1", "statement": "Candidate reports three projects",
    "source_ids": ["S1"], "source_spans": [{"source_id": "S1", "quote": "three projects"}],
    "epistemic": "FACT", "confidence": "self_reported"}],
  "inferences": [{"id": "I1", "statement": "A bounded application can provide feedback", "basis": ["F1"]}],
  "unknowns": [{"id": "U1", "statement": "Employer's current headcount", "decision_relevance": "reversal"}],
  "bottleneck": {"type": "Market", "explanation": "No applications yet"},
  "recommendation": {"type": "CONDITIONAL", "move": "Apply honestly after checking the vacancy",
    "why": ["Test the existing evidence"], "avoided_action": ["Do not start a fourth project"],
    "basis_ids": ["F1", "I1"]},
  "alternatives": [{"option": "Another project", "why_not_now": "Delays market feedback"}],
  "actions": [{"description": "Check the vacancy and submit an honest application", "execution_mode": "human", "priority": 1}],
  "reconsider_if": ["Employer confirms a mandatory requirement that cannot be substituted"],
  "observation_window": "After the first applications",
  "stop_condition": "Stop this vacancy if a hard constraint fails",
  "claims_used": [], "evidence_used": ["S1"], "extensions": {}
}
```

Modes retain job / offer / recruiting / positioning / interview. No fixed role
family or fit enum is required for judgment. Facts require IDs, statements, source
IDs, exact quote anchors and confidence direct / self_reported / interpretation /
unknown. Facts cannot have interpretation/unknown confidence. Personal narration
and resumes remain self_reported; quoting them does not authenticate achievements.
Inferences have source/statement IDs in basis. Unknowns have relevance blocking /
reversal / confidence_only. Their presence alone never blocks a recommendation.
The host distinguishes a blocked binding acceptance from feasible verification
actions. `basis_ids` makes the stated rationale reviewable; it does not prove
semantic entailment. Use source IDs directly where appropriate.

Factual percentages must occur in the linked quote anchors; changing a number
behind a valid quote is blocked. Derived arithmetic belongs in an explicitly
labeled inference rather than being promoted to a reported fact. This narrow
numeric check does not authenticate every metric, denominator or causal effect.

Optional deadline with deadline_source_ids is a timezone-aware ISO timestamp.
Python computes remaining hours against an explicit clock, and never invents an
employer calendar, promise or career choice. Explicit dates still need host review
against the source quote; this is not an arbitrary natural-language date parser.

## Progressive extensions

`extensions` may carry host-authored `{content: "Markdown"}` for direction (job),
offer, recruiting, ownership (positioning) or interview. Only the current mode's
extension is compiled into its fixed filename. Invalid optional metadata or an
inapplicable extension produces WARNING and is excluded from compilation/memory;
it does not destroy the core judgment. Missing optional content never triggers a
generic strategy. The host should supply a specific material when it is useful.
Extra statement kind/fit/stage annotations do not control judgment.

`claims` optionally uses the unchanged audited Claim model, with evidence.source
bound to session source IDs. `claims_used` identifies those claims; `claim_refs`
preserves project-scoped identities for cross-opportunity corrections. The code
does not silently upgrade or downgrade host Claim confidence: a mismatch requires
host correction. A Claim record is needed when claim tracking/persistence is used,
not for every mundane fact. Existing VERIFIED/SUPPORTED/SELF_REPORTED/PLANNED
checks continue unchanged. Hiring facts additionally reuse the existing polarity,
conditional/pending and hearsay checks when the source or mode is recruiting.
This does not require a statement-kind enum for unrelated facts. Optional legacy
metadata is only for comparable recall.
Optional `predictions` retains the existing topic/expectation/basis contract when
the host needs deterministic prediction/observation calibration. Invalid optional
prediction metadata is isolated with WARNING; it does not replace the move.
Similar memory is evidence supplied to the host before judgment, never passed to
the legacy risk-priority modifier in the host-first flow.

## Validation and repair

`validate_decision_envelope(envelope, context, now=...)` returns status, issues
(code, severity, field, explanation), safe_fields and the normalized envelope.
WARNING isolates optional annotations. REPAIR_REQUIRED requires wording/boundary
or core serialization correction. BLOCK prohibits executing a judgment based on
invalid support. The move is never recomputed. A positive integrity assertion in
the recommendation is treated as essential and BLOCKed; an artifact wording issue
requires repair. Unknown-as-fact and unbound factual support BLOCK. This is a
conservative field-based dependency approximation; it cannot understand all
implicit causal dependencies.

`review_with_repair()` permits one host callback with the original envelope and
only relevant issues. The caller retains original input/Skill/references; it never
includes a rubric. Rejected and repaired candidates remain in attempts. A failed
repair is returned explicitly; it cannot compile or save. Python does not call
an API or force a model/configuration. A host can supply one corrected envelope
through `--repair-input` after reading the issues. Preserve debug results in a
private session directory when real materials are used.

```text
python scripts/junshi.py host-decide --input envelope.json --context context.json
python scripts/junshi.py host-decide --input envelope.json --context context.json --debug-decision
python scripts/junshi.py host-decide --input envelope.json --context context.json --repair-input repaired.json --artifacts-dir NEW_DIR
```

Default output prioritizes judgment/actions/why/avoided effort/reconsideration;
it hides schema/status/repair counts. Debug output shows raw attempts and issues.
`--save-subject` writes only to an already active explicitly consented private
store (`--memory-directory`). It neither grants consent nor stores raw material.
An over-budget memory handoff fails explicitly without erasing a valid judgment.
Existing outcomes, append-only history, correction invalidation, deduplication and
calibration remain unchanged. Record actual feedback only; no fabricated outcome.

## Limits

Exact spans authenticate an anchor, not a paraphrase, author or factual truth.
Explicit bilingual pattern guards catch common verbal-contract, metric-credit,
silence-result, causal, authorship, stage and unsupported-certainty violations.
They are deliberately finite and can miss indirect wording or overflag mixed
sources/negation. ACCEPT is not semantic certification. Host review and excerpt-
backed evaluation remain necessary. The action-owner guard catches explicit
execution verbs; permission to send messages must still be enforced by the host.
No pattern selects a role, employer, salary preference or training investment.
