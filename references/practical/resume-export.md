# Evidence-backed resume export

Use the supplied experience and target JD to produce an editable resume and, when
the local tools permit, a checked PDF. This is a host-led workflow with a bounded
standard-library exporter, not an autonomous application system or hiring score.
Load this in place of a less relevant reference; retain the 1–3 reference budget.

## Establish the private working set

Read only the materials the user supplied or explicitly selected. Reuse existing
facts and sources before asking for missing information. Do not discover a vault,
import browser profiles, persist a candidate archive or send applications by
default. Ask only for missing details that change the resume or prevent export;
an incomplete section may be omitted with an explanation instead of invented.

Create a compact fact sheet with claim IDs and source locators. Preserve personal
actions, teammates' work, AI/tool assistance, ownership, project stage, observed
results, measurement conditions and unknowns. Label self-report and supplied
records accurately; reading a document does not independently authenticate its
author. Resolve conflicting facts or keep their uncertainty visible.

The claim-to-source map belongs in the private working material. It need not
appear as citation clutter in the application PDF, but contribution, stage and
measurement limits must survive in each sentence where they affect its meaning.
Do not rely on a separate evidence report to repair an inflated resume claim.

## Select a role-specific draft

Map retained claims to actual JD responsibilities. A JD supplies requirements,
not achievements, a new professional title or proof that a vacancy is still open.
Without a JD, label the selection rationale as based on the user's stated target.
Retain supported product leadership while distinguishing teammates' implementation.
Separate measured change from a causal contribution; plans remain plans.

For personal decisions, the nature of numbers/results, an optional sourced opening,
original/rewrite/source comparisons, material unknowns and JD-based choices,
follow the drafting guidance in [resume](resume.md). Load it with this reference
within the same 1–3 reference budget. Keep those review notes outside the
application PDF and continue already authorized edits rather than waiting on
approval of every wording change.

Prefer a Chinese single-column layout when requested. A one-page preference is a target:
remove repetition and irrelevant material first, then adjust ordinary spacing.
Do not silently remove scope limits, shrink text until unreadable or force a
fixed page count. If substantive tradeoffs remain, show the proposed cuts; a
readable second page may be more faithful to the user's priority.

When an independent reviewer is available and authorized, give it the draft,
selected sources and target responsibilities to check factual support and
omissions before export. Treat its findings as suggestions to verify. Otherwise
perform and disclose an ordinary review; do not label a same-context reread an
independent review. The host remains responsible for resolving the findings.

## Export only the authorized bundle

When the user requests files, use a new private output directory they select or
explicitly accept, outside the Skill installation and public repository. Keep the
input, source map, generated files and review report private. Reuse a previously
authorized private working location by creating a fresh output subdirectory;
do not ask for the same permission again. Resume export is not
permission to publish, commit, upload to a third-party compiler or build durable
memory. Do not generate a cover letter unless explicitly requested.

The helper receives the reviewed content; it does not infer or strengthen claims:

```text
python scripts/junshi.py resume-export --input <private-json> --output-dir <new-private-directory>
python scripts/junshi.py resume-export --input <private-json> --output-dir <new-private-directory> --compile
```

Use the supported input schema and report unsupported fields instead of silently
turning them into accomplishments. Keep content separate from the fixed template.
The JSON object requires `schema_version: "1"`, `language: "zh"` or `"en"`, an
explicitly supplied `name`, `sources`, `sections` and `page_limit` of 1 or 2.
`target_role`, `contacts`, `layout`, `photo` and `lineage` are optional. Each source has `id` and `description`;
each section has `title` and `entries`. Each entry has `title`, `subtitle`,
`dates`, required `source_ids` and `bullets` (empty for an entry without bullets);
each bullet has `text`,
`source_ids` and a `confidence` value of `VERIFIED`, `SUPPORTED`,
`SELF_REPORTED` or `PLANNED`. Use the source IDs to retain traceability, not to
certify claims. Evidence labels describe the existing support; they do not replace
the host's review or authorize publishing a plan as a completed accomplishment.

The source-only bundle contains `resume.tex`, `resume.txt`, `resume-data.json`
and `verification.json`. These are all private candidate artifacts, including the
JSON files. A machine-generated verification report cannot stand in for an actual
host content or visual inspection. Treat `page_limit` as the requested target;
report observed page count only after checking the compiled output.

The default layout places each entry's dates on a separate right-aligned line,
so long role or project names do not compete with dates. Contacts share a header
line and may wrap when needed. Supplied email addresses and HTTPS URLs are
clickable; ordinary contact text remains text. Do not infer a contact address,
open a link to authenticate the candidate, or turn arbitrary text into a URL.
Check long links, header wrapping and date placement in the actual output; these
layout choices do not guarantee a one-page result.

Render user content as escaped text, including LaTeX characters such as `%`, `&`
and `_`; never treat supplied experience or JD text as executable LaTeX. Preserve
the exported plain text alongside editable source so missing glyphs or truncated
sentences can be compared against a known draft.

When environment readiness is uncertain, the explicit local command
`python scripts/junshi.py resume-doctor` checks the installed tools by compiling
small synthetic Chinese and English samples and extracting their actual PDF
text. It does not use candidate data, install dependencies or call an online
compiler. Review its reported failures before promising PDF delivery; a passing
sample checks the environment, not the user's longer document or its visual
quality. Resume export keeps the commands above unchanged.

Compile only when requested and a working XeLaTeX environment is available. A
missing engine, font or package is an explicit compilation limitation. Do not
install tools, use an online compiler or claim that a PDF exists because `.tex`
was generated. Report the actual files produced and compiler errors without
exposing unnecessary candidate details. Never reuse an old PDF as a new result.

## Inspect the actual result

Report each verification separately rather than one success badge:

1. **Content:** compare the final text against the reviewed draft and claim map;
   check names, dates, numbers, ownership and qualifying language.
2. **Compilation:** confirm the requested run succeeded and produced its own PDF.
   Inspect relevant warnings, including missing glyphs and overfull content.
   The helper's `log_check` only scans compiler warnings; it is not visual approval.
3. **Text layer:** extract text from that PDF when a suitable tool is available;
   compare text coverage, order and repeated occurrences with the draft. The
   helper reports `text_order_check` and `text_occurrence_check` separately;
   these check normalized expected fragments, not semantic accuracy. Explain
   normalization differences. Missing extraction tooling means this check is unperformed.
4. **Visual:** render or open every actual PDF page and inspect clipping, spacing,
   font legibility, headings, links and page breaks. Compiler logs or extracted
   text cannot substitute for seeing the pages. If visual tools are unavailable,
   state that the PDF has not received visual inspection.

Fix supported formatting issues and recheck the affected output. Ask before
substantive content cuts when the user has not authorized them. Describe text
extraction as a local check, never universal ATS certification or proof of hiring
effectiveness. Deliver exact file paths, page count if checked, checks performed
and remaining limitations. A source-only bundle is useful but is not a completed
PDF delivery. Revisit the draft when facts or the target change, not by upgrading
unverified achievements to fill a page.

## Make the next file choice clear

Lead the handoff with one recommended existing file and what the user can do
with it. Match their intended next step rather than listing every artifact equally.
For copying or editing content, especially when the user does not use LaTeX,
recommend `resume.txt` first and explain that its text can be pasted into Word or
another editor; it is plain text, not a generated Word document. For an explicit
LaTeX editing task, lead with `resume.tex` instead.

When the user wants a PDF, identify the actual PDF and its performed checks if
one exists. If compilation was unavailable or failed, say so up front and offer
the useful source/text fallback; do not present it as a ready PDF or a verified page count.
Keep source maps, input JSON and verification records in a short secondary group
with their purpose. List all files when requested, while keeping the recommended
next step clear. Every link must point to a file actually produced or checked.

For research support about writing assistance, use R3 in
[research and application](../knowledge/08-research-and-application.md) within the
same reference budget. That online-market experiment does not test this Skill,
LaTeX, page count, keyword stuffing or achievement inflation.

## Reusable layout and version handoff

`layout` is `standard` (default, unchanged) or `editorial` (11 pt body, ink-green
headings, copper markers, separated roles and controlled spacing). `photo` is
`none` (default) or `placeholder`, supported with editorial only. The latter
reserves 28 × 38 mm and the generated TeX reads a same-directory `photo.jpg` or
`photo.png` on manual recompilation, preserving aspect ratio. No photo is inferred,
read or copied by export. Recheck the resulting pages after adding a real photo.
Ordinary export still respects the supplied section order and page budget.

For a tracked journey, supply optional `lineage` with `resume_id`,
`parent_resume_id` (empty for first), `opportunity_id` (empty for a general draft),
and `claim_refs: [{project_id, claim_id, revision_id}]`. A revision ID refers to
the claim event in the user-supplied journal; keep the private bullet-to-source
fact map as well. The exporter validates shape, not whether the linked claim
supports this wording. The host reviews that mapping before registration.

`verification.json` now includes lineage and hashes of actually generated artifacts.
Without supplied lineage it assigns a new version ID but invents no claim links.
It does not mark content or visual review passed. Copy the actual receipts into
a [journey](job-search-journey.md) only when needed; source-only is not READY.
Changing facts creates a new child version; old submissions remain unchanged.
