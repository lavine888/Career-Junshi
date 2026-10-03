# Architecture

The product is a host-driven Skill with dependency-free local helpers. It is a
career decision agent, not a resume UI, job scraper, backend or LLM wrapper.
Python 3.10+ is needed only for helpers; the host provides model, tools and conversation.

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
| memory_store.py | Consent-gated SQLite and immutable decision history | Local compact memory, no cloud sync |
| feedback_loop.py | Decision snapshot / next-move handoff | No causal proof from success |
| install_skill.py | Validated whitelist runtime copy | No overwrite, auto-enable memory or environment setup |
| validate_skill.py | Inventory, links, syntax, routing and context budget | No assertion of model behavior |
| context.py | Session spans, extraction types and freshness | No arbitrary NLP or source authentication |
| intelligence.py | Counterarguments, rationale summaries and finite tags | Conservative mode defaults require host adaptation |
| calibration.py | Comparable memory, topic calibration and preparation signals | No probability, causal inference or capability label |
| hypothesis.py | KEEP / REFINE / guarded PIVOT review | No automatic direction switch or statistical effect estimate |
| role_story.py | Existing claim → evidence → story → role questions | Never adds accomplishments; prose remains host-dependent |
| benchmark.py | Repeatable structured checks and blinded host packets | Does not grade natural-language decision quality |

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
