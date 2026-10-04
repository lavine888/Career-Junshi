# Local memory and consent

Host-first decisions use [Envelope v2](DECISION_ENVELOPE.md)'s validated compact
handoff and the same active-consent/append-only store. `host-decide --save-subject`
does not grant consent; source transcripts and artifacts are not persisted.
Comparable recall may inform the host before judgment, but does not invoke the
legacy automatic risk-priority modifier. Outcomes and unknown causes retain the
existing contracts below.

Default: no database and no persistent memory. `status` is read-only and does not
initialize a store. Ask explicit permission for compact local records; declining
does not reduce the rest of the Skill's functionality. `--yes` represents an already
obtained user instruction, not permission to infer consent.

Default private locations:

- Windows: `%LOCALAPPDATA%/career-junshi`
- macOS: `~/Library/Application Support/career-junshi`
- Linux: `$XDG_DATA_HOME/career-junshi` or `~/.local/share/career-junshi`

Override with `CAREER_JUNSHI_MEMORY_DIR` or `--directory` before the subcommand.
The directory must be outside the installed Skill. Do not select a public repository.
No external requests occur. SQLite is unencrypted; protect local account access.
On POSIX, newly created directories use mode 0700; existing directory permissions
and Windows ACLs are not rewritten.

## Commands

```sh
python scripts/memory_store.py status
# Only after explicit agreement to compact local memory:
python scripts/memory_store.py consent --yes
python scripts/memory_store.py update --kind profile --subject candidate --input /private/profile.json
python scripts/memory_store.py recall --subject candidate --limit 5
python scripts/memory_store.py view --limit 20
python scripts/memory_store.py pause
# Renew explicit consent to resume:
python scripts/memory_store.py consent --yes
python scripts/memory_store.py revoke
# Only when the user requests deletion:
python scripts/memory_store.py delete --yes
```

Update a known record using `--id`. All ordinary records use exactly:

```json
{"summary": "候选人希望在当前城市求职", "source": "user statement, session date", "epistemic": "FACT"}
```

Kinds: profile, target_role, project, claim, company, application, interview_event,
feedback, decision, outcome, hypothesis, correction. Hypotheses use their dedicated
review contract; corrections use the `correct` command. Claims add a `claim` field using [EVIDENCE.md](EVIDENCE.md).
Do not feed normalized output back as a raw claim (safe_wording is output-only).
Only allowlisted fields are accepted. Summary is capped at 400 characters; source
at 240; total record at 6000. At most 200 records and per-kind limits apply. No silent
eviction of decision history; ask the user to review obsolete records when full.
Limits reduce accidental full-document storage; short pasted text could still be
sensitive, so the host must compress rather than store raw source content.

## State transitions

| State | Automatic recall | Writes | User view | User deletion |
| --- | --- | --- | --- | --- |
| uninitialized | no | no | no records | no records |
| active | bounded by kind / subject | yes | yes | yes |
| paused | no | no | yes | yes |
| revoked | no | no | yes | yes |

`consent --yes` enables or resumes with renewed explicit agreement. A paused state
cannot override revocation. Policy-version mismatch fails closed. View is an explicit
administrative inspection; it is not permission for routine recalled decision context.

## Decision → Outcome

Use `decision --subject opportunity-id --input /private/decision.json` with required:
situation, decision, why, expected_outcome, source, observation_window, stop_condition,
pivot_condition. `feedback_loop.decision_record` creates this compact shape from a
decision output with an explicitly supplied expectation. Returned stable ID links
future outcomes. Decision and outcome records are append-only; new recommendations
create new records. Ordinary updates cannot alter their history.

v0.2 allows optional metadata, predictions, claim_ids, decision_trace and
strongest_counterargument; the handoff includes them
when present. Tagged decisions can use limited similar recall; untagged historical
records remain readable without automatic inferred tags. No table migration or
consent-policy change is required. Optional outcome fields are metadata (must match
parent), observations, event_id and origin. Their detailed contracts, case calibration,
correction and hypothesis commands are in [DECISION_INTELLIGENCE.md](DECISION_INTELLIGENCE.md).
v0.2.1 adds optional claim_refs with stable project_id / claim_id pairs. They let a
project correction find dependent decisions across different opportunity subjects.
No database migration, implicit consent or historical record rewrite occurs.

`outcome --subject opportunity-id --input /private/outcome.json` requires these v0.1 fields:

```json
{
  "decision_id": "returned-decision-id",
  "hard_outcome": "passed",
  "observed_facts": [{"text": "用户说 architecture 被追问 12 分钟", "source": "user interview recap"}],
  "user_interpretation": "用户认为准备有帮助",
  "agent_interpretation": "本次话题相关，但因果效果未知",
  "unknowns": ["面试官评分"],
  "source": "user outcome report"
}
```

hard_outcome: passed / rejected / offer / waiting / withdrawn / freeze / unknown.
The record FACT label applies to the sourced outcome report; interpretations have
separate fields and are never proof. The helper adds limited learning and causal
uncertainty. It does not automatically change the candidate profile or strength.
Results must reference an existing Decision for the same subject.

`delete --id ID --yes` removes that record; deleting a Decision also deletes its
linked Outcomes. Whole-store delete removes all records, compacts the database and
sets consent to revoked. It retains policy / revocation metadata. This is logical
deletion, not secure forensic erasure; external exports, backups and SSD remnants
are outside this command. Successful writes are reported only after commit.
