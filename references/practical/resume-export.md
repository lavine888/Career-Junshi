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

Show the usable draft and the material omissions or unresolved gaps. Prefer a
Chinese single-column layout when requested. A one-page preference is a target:
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
input, source map, generated files and review report private. Resume export is not
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
Only `target_role` and `contacts` are optional. Each source has `id` and `description`;
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

Render user content as escaped text, including LaTeX characters such as `%`, `&`
and `_`; never treat supplied experience or JD text as executable LaTeX. Preserve
the exported plain text alongside editable source so missing glyphs or truncated
sentences can be compared against a known draft.

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
   compare text coverage and reading order with the draft. Explain normalization
   differences. Missing extraction tooling means this check is unperformed.
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

For research support about writing assistance, use R3 in
[research and application](../knowledge/08-research-and-application.md) within the
same reference budget. That online-market experiment does not test this Skill,
LaTeX, page count, keyword stuffing or achievement inflation.
