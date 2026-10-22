# Architecture

The product is a host-driven Skill with dependency-free local helpers. It is a
career decision agent, not a resume UI, job scraper, backend or LLM wrapper.
Python 3.10+ is needed only for helpers; the host provides model, tools and conversation.
The decision and memory CLIs emit UTF-8 and accept UTF-8 JSON with or without a BOM;
structured input is bounded to 256 KiB before decoding.

```text
user materials / consented task memory
  → host understands situation and deadline
  → claim audit + FACT / INFERENCE / UNKNOWN
  → 1–3 knowledge / practical references
  → one Decision + 1–3 actions
  → Codex local artifacts / human real-world actions
  → reported Outcome + limited learning
  → bounded memory for next situation
```

| Component | Responsibility | Boundary |
| --- | --- | --- |
| SKILL.md | Natural-language understanding and coherent judgment | Instructions to a capable host, not a standalone model |
| references | Career knowledge and action playbooks | No real-time company database |
| models.py | Conservative structured claim normalization | Does not authenticate operator receipts or fetch URLs |
| router.py | Five explicit situation routes | Host selects mode from natural language |
| decision.py | Reproducible conservative structured support | No semantic extraction from resumes or hiring prediction |
| method_adapter.py | Internal methodology plan and comparable feedback review | No dependency on another installed Skill |
| actions.py | Action ownership and actual Markdown artifact generation | Does not send messages, apply or decide for the user |
| resume_export.py | Sourced resume data to escaped fixed-template LaTeX and plain text; optional local XeLaTeX | Does not verify claim truth, upload data or certify ATS compatibility |
| memory_store.py | Consent-gated SQLite and immutable decision history | Local compact memory, no cloud sync |
| feedback_loop.py | Decision snapshot / sourced status-context hint | No causal proof from success |
| journey.py | Explicit event replay, version links, execution receipts and continuation card | No database, discovery, sending or automatic persistence |
| install_skill.py | Validated whitelist runtime copy | No overwrite, auto-enable memory or environment setup |
| validate_skill.py | Inventory, links, syntax, routing and context budget | No assertion of model behavior |
| context.py | Session spans, extraction types and freshness | No arbitrary NLP or source authentication |
| intelligence.py | Counterarguments, rationale summaries and finite tags | Conservative mode defaults require host adaptation |
| calibration.py | Comparable memory, topic calibration and preparation signals | No probability, causal inference or capability label |
| hypothesis.py | KEEP / REFINE / guarded PIVOT review | No automatic direction switch or statistical effect estimate |
| role_story.py | Existing claim → evidence → story → role questions | Never adds accomplishments; prose remains host-dependent |
| benchmark.py | Repeatable structured checks and blinded host packets | Does not grade natural-language decision quality |
| source_catalog.py | Validated distinct source records, computed counts and bounded topic/ID discovery | Offline metadata, not live source authentication or legal advice |

SQLite was chosen over rewriting whole JSON files: standard-library transactions,
bounded reads, foreign keys and concurrent updates reduce corruption risk without
adding a service. No vector database, graph database, authentication or API key is used.
Memory stays outside both checkout and installed Skill. Runtime package contains
the kernel, metadata, reference library, helpers, core contracts and license notices.

Behavioral responsibility remains with the host: verify sources, extract faithful
structured context, ask decisive questions, and execute authorized local tasks. The
CLI is a guardrail / reproducible demonstration, not a substitute for that reasoning.
Only synthetic materials are distributed. Optional integration is described in
[INTEGRATION.md](INTEGRATION.md); evidence and memory rules are in
[EVIDENCE.md](EVIDENCE.md) and [MEMORY.md](MEMORY.md).
v0.2 contracts are in [CONTEXT_EXTRACTION.md](CONTEXT_EXTRACTION.md) and
[DECISION_INTELLIGENCE.md](DECISION_INTELLIGENCE.md). Golden cases and development
evaluation reports stay in the checkout; runtime-only benchmark use needs an explicit
`--cases` path. Installation still has no development or private-memory dependency.

## Host-led experiences

Core playbooks and focused branches layer on the existing situation modes: resume
defense, role translation, evidence sprint, decision review, wording audit,
outcome-blind review, resume export, job-search experiments, action-start cards,
AI development recap and targeted interview retries.
The host selects the
experience from the request, reads its relevant references and conducts the work.
`junshi.py route --mode interview --experience defense` only selects references
and suggests an artifact filename; it does not run a session or generate a report.
Legacy route and decide contracts are unchanged. Runtime installation includes the
playbooks, and validation checks their presence. Public walkthroughs are synthetic
illustrations; they do not establish behavioral quality or hiring outcomes.

Resume export uses a bundled single-column template. The standard-library helper
has no mandatory TeX dependency: source export remains available without XeLaTeX.
Requested compilation, page-budget checks, text-layer checks and host visual
inspection are reported separately. Private outputs must be new directories outside
Git checkouts and the installed Skill. Only synthetic examples ship in the source.

The optional research index separates publication design and findings from product
adaptations. It is loaded for a relevant question rather than every request.
Application experiments and start cards remain host-led: routing cannot run an
experiment, authenticate a study or establish a causal hiring effect.

Source cards live in three runtime JSON catalogs. Identity, type, reading depth,
version, jurisdiction and limits are required; duplicate IDs, canonical URLs and
identical normalized titles are rejected. Summary discovery is separate from
reading one detailed card. Counts are computed from distinct records; topics overlap.
JD analysis distinguishes expression, evidence, actual gaps and unknowns before
choosing an action. Development recap reuses the claim/source substrate and
distinguishes assistant completion statements from inspected execution records.
Interview retries reuse an actual answer/checkpoint and change the case while
holding the criterion stable; practice observations never upgrade career confidence.
These are host decisions, not keyword classifiers or automatic evidence certification.

Structured-interview coaching declares a practice criterion before the answer.
Offer checks prioritize actual decisive terms and risk signals; the user performs
external verification and decisions. Neither workflow inherits research validity.

## Portable job-search continuation

The optional `journey` CLI replays a bounded explicitly supplied journal. Claim
revisions, resume hashes, opportunity submissions, recruiting observations, action
receipts and host-authored reviews retain stable references. Corrections mark
referencing resumes stale without changing original application history. File
verification is opt-in. A requested checkpoint creates a new private directory;
it does not activate the separate consent-gated memory store. No schema migration
of existing memory or behavioral change to its legacy compact application records
is implied. [Contract and host workflow](../references/practical/job-search-journey.md).

Resume export keeps its existing default and adds an editorial template with an
optional blank photo area. Both use escaped content, actual file receipts and the
same compilation/text/page checks. Visual/content review remain host responsibilities.


## Delivery boundaries

Snapshot packets, decision preparation, resumes and journey checkpoints share a
private destination guard in io_utils. It rejects the Skill installation, Git
checkouts (including worktree .git files), symlinks and Windows reparse points
before writing. Each caller retains its documented overwrite behavior.
Installation checks linked package entries before catalog reads or recursion;
junctions cannot expand the runtime copy beyond its reviewed source tree.

A resume attachment's latest version follows actual sent_at, while recruiting and
execution status follow recorded observation at. Backfilled older records remain
in the history without replacing a newer state. Attachment conflicts at one actual
instant require clarification. This validates supplied chronology, not external
delivery, employer adoption or the truth of a career claim.
