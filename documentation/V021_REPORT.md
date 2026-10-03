# Career Junshi v0.2.1 — reliability corrections

Baseline: v0.2 at d7a257bb415e414437632c350ee54c6922ebe5c2. This patch keeps the
five modes, standard-library runtime, consent policy and existing memory tables.
No real candidate material or recruiting outcomes are included in public tests.

## Corrected boundaries

1. Recruiting extraction preserves denial, conditions and hearsay. Prior span
   validation accepted a positive paraphrase of a negative message. The new guard
   rejects that change and keeps unresolved conflicting reports UNKNOWN.
2. Claim corrections follow stable project_id / claim_id references across different
   opportunity subjects. Explicit references protect unrelated projects with the
   same short claim ID. Unique legacy IDs can be matched; ambiguous ones need review.
   Current claims update atomically and historical decisions remain unchanged.
3. Comparable historical candidates are filtered and deduplicated before the
   three-pair cap. New duplicate or synthetic records cannot crowd out three
   independent reported real events. Signals remain preparation priorities only.

## Regression scope

Fifteen new synthetic tests reproduce the three reported failures and cover opposite
polarity, pending/conditional wording, preserved qualifications, hearsay, conflicting
sources, duplicate source aliases, mixed synthetic history, old/unrelated history,
cross-opportunity references, project ID collisions, ambiguous legacy records and
consent. The 108 pre-patch tests remain unchanged.
Validation: 123 tests passed using `python -m unittest discover -s tests -q`;
packaging / links / syntax validation passed. The 13-case structured benchmark has
no regressions. Additional integrated checks confirm scoped correction excludes the
affected opportunity from recall while retaining an unrelated project's same-name
claim, and conditional / unknown reports cannot set a terminal recruiting status.

## Model comparison scope

The same synthetic raw contexts are supplied to v0.1 and v0.2 Skill snapshots on
the same configured model, with tool execution disabled. Thirteen fixed cases and
two new denial/conditional holdouts are prepared. Raw outputs, run metadata and
version-hidden review evidence are required before making comparative claims.
Actual execution status: BLOCKED_MODEL_ACCESS. Codex CLI 0.153.0 with ChatGPT login
rejected configured model gpt-6.1-sol with HTTP 400 before generating a response.
Effective coverage: 0/30 responses and 0/15 reviewed pairs. No automatic model or
reasoning switch was made. A different evaluation model requires explicit user choice.
[Comparison plan and holdouts](../benchmark/host-comparison-plan.json) preserve
synthetic inputs, snapshot commits, settings, the rejection and zero coverage.
Initial startup configuration errors were corrected locally before the model-access
rejection; none produced an output. Raw setup logs remain outside the public repo.
This compares host instructions and selected references; it does not evaluate a
live installed-Skill discovery flow, Python guard execution or real hiring outcomes.

## Limits

The recruiting guard covers explicit bilingual patterns rather than all natural
language. Historical round/date distinctions require source review. Legacy references
without project identity cannot always be resolved. Real-world event labels remain
operator attestations. Model judgments are diagnostics, not an independent human
review or evidence that advice improves employment outcomes.

## Delivery and remaining work

IMPLEMENTED / TESTED: three reliability corrections, 15 new regressions and documented
contracts. MODEL-EVALUATED: not claimed; comparison blocked by model access.
REAL-WORLD-OBSERVED: no recruiting outcomes or effectiveness evidence. Remaining
authorized evaluation work is to run the prepared pairs on a user-permitted available
model, blind response order and record excerpt-backed judgments with failures intact.
