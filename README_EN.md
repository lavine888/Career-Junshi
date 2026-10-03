# Career Junshi · 求职军师

Not just a better resume: understand the opportunity, defend your claims, interpret
feedback, and decide what to do next.

“My interview is tomorrow. What should I prepare tonight?”

“HR hasn't replied for three days. Should I follow up?”

“Which offer should I choose?”

“Can I honestly say I led this project?”

“I don't know which jobs to apply for.”

Career Junshi asks what is limiting your progress, then recommends one move,
1–3 actions, an observation window and stop / pivot conditions. It is a stateful
career decision Skill for a capable host, with standard-library local helpers.

[中文](README.md) · [Synthetic cases](cases) · [v0.2 report](documentation/V02_REPORT.md) · [Evaluation](documentation/EVAL.md)

v0.2.1 preserves recruiting denial/conditions/hearsay, traces scoped claim corrections
across opportunities and deduplicates history before the three-pair cap. All 123
tests pass; the prior 108 remain unchanged. Fifteen synthetic comparison pairs are
prepared, but the configured model was rejected by the CLI login endpoint; zero
valid responses and no model-comparison claims. See the [patch report](documentation/V021_REPORT.md).

## v0.2 · Decision Intelligence

v0.1 established evidence-safe career decisions. v0.2 adds source-located context,
counterarguments and reconsideration conditions, at most three comparable memory
pairs, topic prediction calibration, guarded recurring preparation signals, lightweight
career hypotheses and five role packs. Role translation preserves achievements and
personal ownership. A correction updates current claims while preserving history.

This is bounded feedback calibration, not a self-learning AI. The [13 fixed synthetic
cases](benchmark/cases.json) test contracts and structured decisions. Independent host
model evaluation and real-world effects are not established. Private context dry-run
findings are anonymous and do not constitute recruiting outcomes.

```sh
python -m unittest discover -v
python scripts/benchmark.py run
python scripts/benchmark.py packet --output /new/private/eval-packet
python scripts/junshi.py decide --extraction /private/session-packet.json --format json
```

See [extraction](documentation/CONTEXT_EXTRACTION.md) and [decision contracts](documentation/DECISION_INTELLIGENCE.md).
Memory remains off unless explicitly consented. `decide --input /private/situation.json
--use-similar --memory-directory /private/memory` requires an already active store;
it cannot initialize consent. Narrative judgment and factual source review remain
host responsibilities; local tests cannot evaluate natural-language wisdom.

## Install and ask

Python 3.10+ for helpers. No dependencies, API key, backend or private vault required.

```sh
git clone https://github.com/lavine888/Career-Junshi.git
cd Career-Junshi
python scripts/validate_skill.py
python scripts/install_skill.py --target "$HOME/.agents/skills/career-junshi"
python "$HOME/.agents/skills/career-junshi/scripts/validate_skill.py" --runtime-only
```

For PowerShell use `"$env:USERPROFILE\.agents\skills\career-junshi"` as the target.
Choose the directory your host discovers; current Codex locations are in the
[official OpenAI docs](https://learn.chatgpt.com/docs/build-skills).
The installer copies runtime files and license notices, preserves an existing target,
and never enables memory. Start a new chat and ask:

```text
Use $career-junshi. Here are my resume and JD. My interview is tomorrow afternoon.
What should I do tonight?
```

The host supplies natural-language understanding and tools. Already supplied context
is extracted first; only decision-changing gaps are queried. Five modes: job decision,
positioning / resume, interview defense, recruiting, offers. Internal methods stay
behind one coherent user-facing decision.

## Evidence, memory and action

Claims: VERIFIED / SUPPORTED / SELF_REPORTED / PLANNED. Situation:
FACT / INFERENCE / UNKNOWN with provenance. A URL is not verification; code is not
proof of authorship. Plans, team work, demos, backtests and participation cannot
become completed, solo, production, live profit or awards. Weak claims are narrowed.

Opt-in SQLite remembers compact profiles, targets, projects, claims, companies,
applications, interviews, feedback, decisions and outcomes. View / pause / revoke /
delete are supported. Raw resumes, JDs, mail and chats are excluded by default.
Decision history is append-only; observations and interpretations stay separate.
Passing an interview never proves the preparation caused success.
See [memory commands and limits](documentation/MEMORY.md).

Codex can inspect supplied evidence and generate risk maps, question ladders, drafts
and offer comparisons. The human applies, messages recruiters, interviews, negotiates
and accepts or rejects. These scripts never send messages.

## Reproducible helpers

```sh
python scripts/junshi.py route --mode interview
python scripts/junshi.py audit --input cases/interview/input.json
python scripts/junshi.py decide --input cases/interview/input.json --now 2026-10-03T12:00:00+08:00
python scripts/junshi.py decide --input cases/follow-up/input.json --now 2026-10-03T12:00:00+08:00
python scripts/junshi.py decide --input cases/offer/input.json --now 2026-10-03T12:00:00+08:00
python -m unittest discover -s tests -v
python scripts/validate_skill.py
```

`--format json` shows internals; `--artifacts-dir <new-private-directory>` creates
Markdown materials without overwriting. CLI inputs are structured operator context,
not arbitrary resumes or chat text. It does not fetch jobs or authenticate receipts.
All cases are synthetic; passing tests is not career outcome validation. Current
company / market claims require fresh host checks. Memory is unencrypted and logical
deletion does not erase external backups.

## Design and attribution

Inspired by / adapted from [Goutoujunshi](https://github.com/shengjidaguai-china/goutoujunshi):
lightweight kernel, reference routing, local memory philosophy and action-first
interaction. Conceptually informed by [Career Alpha](https://github.com/lavine888/career-alpha):
Evidence First, claim ledger, interview defense and market feedback.

Career Junshi adds career situations, evidence guards, decision / outcome history
and material generation. No relationship content or private vault data was copied.
LavineOS is an optional [documented snapshot contract](documentation/INTEGRATION.md),
not implemented sync. [MIT](LICENSE); upstream notices are retained. See
[attribution](documentation/ATTRIBUTION.md) and [architecture](documentation/ARCHITECTURE.md).
