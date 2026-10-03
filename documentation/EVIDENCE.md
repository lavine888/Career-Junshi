# Evidence contract

## Claim input

```json
{
  "id": "C1",
  "claim": "Implemented an evaluation prototype",
  "confidence": "SELF_REPORTED",
  "stage": "demo",
  "ownership": {"scope": "team", "contribution": "candidate says: evaluation script"},
  "evidence": [],
  "risk": []
}
```

`stage`: planned / demo / backtest / completed / production.
`ownership.scope`: sole / team / unclear. “sole” is an assertion requiring proof.
`confidence`: VERIFIED / SUPPORTED / SELF_REPORTED / PLANNED.

Evidence records contain source, kind (direct / supporting / self_report), supports,
optional summary, and optionally both checked_by and checked_at (timezone-aware ISO).
Support aspects: claim / authorship / sole_ownership / leadership / production / real_world /
award / metric. Records are operator attestations about exact inspected artifacts,
not declarations to invent. Examples under tests are explicitly synthetic.

## Normalization

The requested level is a ceiling, never an instruction to upgrade. Planned stage
always remains PLANNED. A direct artifact must cover the exact assertion plus each
strong dimension to permit VERIFIED. It must have an operator and checking time.
Missing authorship, sole ownership, production, award, metric or real-world evidence
adds risk. Conflicting project stage or team scope also blocks VERIFIED. The helper
produces safe wording separate from the original sentence and retains sources.
Claim memory stores this normalization and a safe summary, not the requested label.

Text triggers catch common strong expressions; they do not constitute a complete
semantic check. False positives (for example a negated production sentence) and
missed paraphrases require host inspection. The helper cannot prove ownership just
because a JSON receipt says it was checked. No sandboxed script can authenticate
an invented operator record without real source work. Never present a fixture or
typed URL as real verification.

Unsupported technology, titles, employers, revenue, users and rankings must also be
checked by the host. Do not add details from similar resumes. A source artifact's
existence and a candidate's personal authorship are different claims.

## Situation input

`mode`, `summary`, optional `goal`, `deadline`, `facts`, `inferences`, `unknowns`,
`claims`, and a matching `job` / `recruiting` / `offer` object. Unknown top-level fields
fail. Facts have text, source and source_type (user_report / document / tool). Their
label FACT means a sourced observation or report, not independent truth. Inferences
and unknowns stay separate. Dates need a timezone; workday counts must be supplied
or actually checked by the host. The helper has no public-holiday calendar.

Offer ratings are 0–5 subjective candidate inputs. Named weights are nonnegative;
unknown dimensions remain unknown. Hard constraints must be explicitly stated
(an empty list is an explicit absence), and an option's constraint_status must be
pass / fail / unknown. No brand ranking is built in. `downside` is scored as downside
protection: higher means safer / more acceptable to this user, like all other ratings.

See [knowledge evidence guide](../references/knowledge/01-evidence-and-claims.md)
and the executable scenarios in the full source repository. CLI inputs are structured
operator context, not arbitrary resume or chat text.
