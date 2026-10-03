# Autonomous reference retrieval — v0.2.2

The five-case semantic review was completed and hash-frozen before this separate
experiment. Each run used a new temporary runtime install and fresh gpt-5.6-sol/high
context. SKILL.md and references were not preloaded. The prompt requested the
installed Skill, its router and 1–3 relevant references, and required an immediate
stop on permission denial. No alternative tools, paths or bypass were attempted.

| Task | Initial request | Reference requests | Successfully read refs | Count | Irrelevant loaded | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Interview | SKILL.md | None | None | 0 | No | BLOCKED_BY_HOST |
| HR | SKILL.md | None | None | 0 | No | BLOCKED_BY_HOST |
| Offer | SKILL.md | None | None | 0 | No | BLOCKED_BY_HOST |
| Direction | SKILL.md | None | None | 0 | No | BLOCKED_BY_HOST |
| Ownership | SKILL.md | None | None | 0 | No | BLOCKED_BY_HOST |

Each stderr contains exactly one rejected Get-Content request against that
installation's SKILL.md: `exec_command failed: CreateProcess … rejected: blocked
by policy`. No process began, so completed command-event count is zero despite an
actual denied request. Both runtime stderr and host response confirm the stop.
The HR response lists two planned references, explicitly not requested or read;
plans are not successful retrieval evidence.

[Machine records](../benchmark/decision-quality-v022/reference-retrieval.json)
contain timestamps, model settings, prompt/raw hashes, requested/read arrays,
counts and errors. Per-case redacted responses and blocked-read stderr excerpts
are under [retrieval artifacts](../benchmark/decision-quality-v022/retrieval).
An initial five-run experiment is retained under retrieval-initial. After an
Offer action-length boundary fix, all five decisions were confirmed identical,
refrozen and the same experiment repeated. This table describes the final five;
both sets were blocked on the first read, without a workaround. Host Skill and
reference text did not change.

Only local installation/runtime path prefixes are redacted; original hashes and
unredacted logs remain in the private temporary evaluation workspace.

All five runs are BLOCKED_BY_HOST; autonomous Skill → router → relevant-reference
retrieval is **unverified**. Zero irrelevant files means none could be read, not
proof of good routing. The inner runtime policy rejection is separate from outer
task approval. These results do not change the frozen semantic grades obtained
with explicit installed-Skill/reference preload.
