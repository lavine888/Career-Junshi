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

MODEL-EVALUATED: the frozen v0.1 and v0.2.1 snapshots produced 30/30 valid responses
on gpt-5.6-sol/high, tools disabled, for 13 fixed synthetic cases plus two prepared
denial/conditional holdouts. A different accessible model, gpt-6-astra/high, reviewed
15/15 pairs in fresh contexts with random A/B identity hidden. All outputs and
reviews were hashed and frozen before unblinding. v0.2.1 won 2 pairs, v0.1 won 0,
and 13 tied. Both versions received one FABRICATED_FACT date-unknown label in G08;
there was no reduction in hard-failure counts. Labels remain model judgments.

The previous configured gpt-6.1-sol rejection is preserved as a historical
BLOCKED_MODEL_ACCESS attempt with zero outputs, not a product failure. The user
explicitly authorized an accessible replacement before this new run. No persistent
model setting changed and no model changed during generation. The previously prepared
v0.2 packet was rebuilt against the v0.2.1 commit while preserving all 15 case inputs.

[Model evaluation report](MODEL_EVAL_REPORT.md) and [frozen evidence](../benchmark/model-eval/README.md)
record setup, exact commits, settings, failures, raw outputs, blind mapping and
excerpt-backed judgments. This compares host instructions and selected references,
not live installed-Skill discovery, Python guard execution or real hiring outcomes.
The fixed inputs contain no cross-opportunity Claim history or duplicate historical
observations, so these two runtime corrections remain outside model-evaluation coverage.

## Limits

The recruiting guard covers explicit bilingual patterns rather than all natural
language. Historical round/date distinctions require source review. Legacy references
without project identity cannot always be resolved. Real-world event labels remain
operator attestations. Model judgments are diagnostics, not an independent human
review or evidence that advice improves employment outcomes.

## Delivery and remaining work

IMPLEMENTED / TESTED: three reliability corrections, 15 new regressions and documented
contracts; all 123 tests pass. MODEL-EVALUATED: the limited 15-pair synthetic Skill-plus-
reference comparison above, with separate-model blind review and immutable evidence.
REAL-WORLD-OBSERVED: NO. No recruiting outcome or effectiveness evidence. Remaining
research is independent human review, repeated samples and a separately frozen
history-focused case set; no product feature or benchmark-specific rule was added.
