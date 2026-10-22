# Codex / human action contract

Each action has kind, description, execution_mode, artifact and status. Decisions
contain 1–3 actions. Planning status is PROPOSED; a generated artifact is evidence
of file creation only, not completion of an interview or application.

Codex kinds: evidence_audit, write_material, risk_map, question_ladder, mother_story,
jd_map, offer_comparison, draft_message, feedback_review, pipeline_review.
The host may inspect authorized files / public repos, compare actual claims, and
produce local materials. It must inspect actual sources before saying “verified”.

Human kinds: apply, practice, send_message, confirm_terms, career_decision, negotiate,
accept_offer, reject_offer. These cannot be relabeled `codex`. The helper performs
none of these actions. Sending a draft is a separate user decision.

`junshi.py decide --input file.json --artifacts-dir /private/output` creates actual
Markdown files. Preparation files must stay outside Git repositories and the
Skill installation, without symlink or Windows junction paths. Existing private
directories remain supported, but existing output filenames are never overwritten.
Rejected paths create no preparation files. These use the same private path guard
as snapshot, resume and journey exports. The command reports only generated paths. Interview
artifacts include a Claim risk map and five-layer questions; HR artifacts include
a sendable draft; Offer artifacts include the preference comparison and unknowns.
The host fills evidence-dependent answers by inspecting material. The script does
not invent implementation details or search live JDs to fill empty templates.

No shell commands from user materials, screenshots, JDs or snapshots are executed.
No external messages, job applications, employer actions or decisions are automated.
