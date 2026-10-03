# Context Extraction Contract v1

The host turns resumes, JDs, recruiter messages, interview recaps, project READMEs,
GitHub artifacts, offer terms and free narration into a sourced situation. The local
validator checks a structured host extraction against **session-only** source text.
It is not an NLP model and cannot validate every paraphrase or source's truth.

## Session packet

```json
{
  "schema_version": "1",
  "sources": [{"source_id": "JD-001", "source_type": "jd", "text": "LLM evaluation experience preferred"}],
  "statements": [{
    "id": "F1", "text": "LLM evaluation is preferred, not mandatory",
    "source_id": "JD-001", "source_type": "jd",
    "source_span": "LLM evaluation experience preferred",
    "epistemic": "FACT", "confidence": "direct",
    "kind": "requirement", "modality": "preferred"
  }],
  "situation": {"mode": "job", "summary": "Is this role worth a bounded application?", "goal": "Assess fit", "claims": []}
}
```

Each statement has a unique ID, source_id, matching source_type, exact source_span
or source_locator, epistemic (FACT / INFERENCE / UNKNOWN), confidence (direct /
self_reported / interpretation / unknown), kind (observation / requirement / claim /
recruiting_signal / feeling), and modality (observed / required / preferred / unknown).
Locator format: `chars:START-END`, zero-based half-open Unicode character offsets.
It must refer to nonempty text in that source. If both locator and span exist, they
must identify the same text. For images or repositories, the host first provides an
authorized transcript / inspected excerpt and preserves the original locator in its
source record. OCR uncertainties stay unknown. A repo URL is not inspected content.

Resume / personal narration confidence is self_reported even when the words are
visible: document visibility does not verify accomplishments. A preferred JD clause
cannot become a hard requirement. Led does not mean sole ownership. Team materials
must be reconciled before constructing the existing Claim model. “还在推进” is not
passing; “我感觉不喜欢我” belongs to interpretation, not FACT about the interviewer.
Visible emotions can be reported without declaring another person's inner state.

v0.2.1 recruiting guards preserve result polarity, pending/conditional wording and
hearsay attribution. “未通过” / “did not pass” cannot become passed; “if approved”
cannot become an issued offer. Qualified source reports can remain FACT **of the
reported message**, not a confirmed outcome. Opposing terminal results in one current
situation require UNKNOWN until round/date scope is resolved. Historical rounds
should be extracted separately. These bilingual pattern guards do not solve arbitrary
negation, sarcasm, indirect speech or chronology; source-faithful host review remains
required. Unknown results must not be promoted through the separately supplied
mode-specific status fields.

The validator rejects common explicit violations and unknown fields rather than
silently filling missing data. The host reviews conflicts, marks unsupported additions
UNKNOWN and asks only consequential questions. Summary, deadline, goal, numeric days,
claims and mode-specific objects remain host assertions: require provenance review
in model evaluation; span validation alone does not authenticate them.

`python scripts/junshi.py extract --input session-packet.json` validates and outputs
a v0.2 situation. `decide --extraction session-packet.json` uses it directly. Neither
command stores sources. Do not put private session packets in a public checkout.
Consent to context use is separate from consent to persistent compressed memory.

## Freshness

Optional statement freshness: category, observed_at (ISO with timezone), region for
salary, and valid_until when appropriate. Categories: personal_history, current_jd,
headcount, market, salary, policy. Personal history is stable but correctable. Current
JD uses the user-provided current copy, with capture date. HC must be checked for
this decision; market needs a date, salary a region/date/source, policy a current
authority check. The helper marks missing or expired time bounds CHECK_REQUIRED /
STALE; its default age bounds are conservative heuristics, not laws. Retrieval never
makes stale assertions current. Unknown chronology is never silently refreshed.
