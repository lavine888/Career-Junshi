# Career Junshi v0.1 vs v0.2.1 — frozen host-model blind evaluation

MODEL-EVALUATED: 30/30 valid generations, 15/15 valid comparison pairs and 15/15
valid separate-model blind reviews. The reviewer preferred v0.2.1 in 2 pairs,
preferred v0.1 in 0, and tied 13. Both versions received one FABRICATED_FACT label
in the same recruiter-date case. These are model diagnostics, not human-certified
errors or hiring effectiveness. REAL-WORLD-OBSERVED: NO.

## Setup

Date: 2026-10-03, Asia/Shanghai. The case clock stays 2026-10-03T12:00:00+08:00.
Evaluation base commit: `b30e82c12b3231bc427ba7de3a4ef2dba0fa5ef9`. Codex CLI: 0.153.0.
Generation ran 14:08:44–14:16:03; review ran 14:16:38–14:22:58; unblinding followed
at 14:23:16 (Asia/Shanghai). UTC timestamps remain in the manifest.
No product files changed during generation or review. Evaluation helpers were kept
outside the checkout and are delivered under benchmark/, outside the installed runtime.

For every pair the supplied surrounding instruction, raw input, host model, effort,
tool configuration, timeout and reference paths/count budget were identical. Only
the frozen Skill and reference contents differed. References number 2–3 per case,
with a maximum of 3; naturally different document lengths were not token-matched.
No rubric or canonical answers appeared in generation prompts.

Every request used a fresh ephemeral read-only CLI context, ignored user model/MCP
configuration and set project document budget to zero. Web search and shell/apps/
multi-agent/remote-plugin/hooks/memories flags were disabled; prompts forbade tool
use. Event audits observed zero tool calls in all 45 evaluation requests. Codex still
supplies host instructions; server-side context was not independently captured or
hashed. The surrounding-instruction invariant is verified for supplied prompts and
settings, not for undocumented provider-internal messages.

## Model

Generation: `gpt-5.6-sol`, reasoning `high`, timeout 240 seconds, three independent
concurrent requests. The model first returned READY successfully in the current
authenticated CLI environment; a cached listing was not treated as proof of access.
This candidate was explicitly acceptable in the task authorization and stayed fixed
for all 30 generations. Persistent model configuration was not changed.

Reviewer: `gpt-6-astra`, reasoning `high`, timeout 300 seconds, three independent
concurrent contexts. It also returned READY in an actual access probe. It differs
from the generation model. Access probes are separate from case coverage.

The previous `gpt-6.1-sol` attempt remains recorded as a model-access error with
zero responses: “The 'gpt-6.1-sol' model is not supported when using Codex with a
ChatGPT account.” It was not a Career Junshi product failure. The task explicitly
authorized a different accessible model before this new frozen run began.

## Skill snapshots

| Snapshot | Commit |
| --- | --- |
| v0.1 | `96174ae688071501b219b0343b557299f8d4a9a9` |
| v0.2.1 | `b30e82c12b3231bc427ba7de3a4ef2dba0fa5ef9` |

The old prepared packet pointed at v0.2. Its 15 inputs were preserved, but document
contents were rebuilt with git show from the v0.2.1 commit before generation.
Neither snapshot was edited or optimized for these cases. Frozen prompts and hashes
are available in [the evidence package](../benchmark/model-eval/README.md).

## Cases

Thirteen existing synthetic cases cover role direction, SWE-to-AI-product transition,
JD fit, prototype/production and ownership boundaries, urgent interviews, rejection,
recruiter silence, offer priorities, negotiation, location/time constraints,
positioning and claim defense. H01 supplies an explicitly denied interview round;
H02 supplies hearsay plus conditional headcount/compensation approval.

Prepared reference selection was preserved, including follow-up for rejection and
denial cases and offer for negotiation. This controls paths equally between versions
but does not test correct automatic routing. No private candidate material, vault,
live market information, memory lookup or recruiting outcome was used.

Negation, conditions and hearsay are directly assessable. Cross-opportunity Claim
identity and duplicate historical observations are NOT ASSESSABLE: no claim-reference
history or duplicate observations exist in these fixed inputs. They remain covered
by the existing runtime regression tests, not by this model comparison. There is
also no success outcome on which to test causal over-attribution. Zero failure
labels on unexercised behavior do not establish that behavior's reliability.

## Generation coverage

| Attempt scope | VALID | MODEL_ERROR | TIMEOUT | INVALID_OUTPUT |
| --- | --- | --- | --- | --- |
| Frozen generations | 30 | 0 | 0 | 0 |
| Blind reviews | 15 | 0 | 0 | 0 |

Valid pairs: 15/15. Unassessable pair verdicts: 0. One dimension in one case was not
assessable. Response lengths: 374–492 characters. No outputs were dropped or rewritten.
Each attempt records case/version (generation only), model, settings, start/end,
status, raw output path, hash and error. Failed historical access remains separate.

## Review method

Option A: a different accessible model reviewed each pair in a fresh context.
It compared twelve concrete dimensions and marked thirteen hard-failure labels;
material evidence/constraint failures took priority over style. There was no overall
intelligence score. Case checks came from the existing synthetic benchmark; holdout
checks addressed their supplied source boundaries, without specifying a version winner.

Every nonempty excerpt is an exact contiguous substring of the judged response.
Empty excerpts represent missing behavior. Validation checks structure and quotes,
not semantic correctness. No independent human confirmation was performed.

## Blind protocol

Each pair was randomly mapped to A/B using SystemRandom. The mapping stayed in a
separate local private directory; its SHA-256 commitment was saved before review:
`d9ac1e7858226c6190e61f94f72f94a0bc571f7a5724a2c3561b03ff3532a6a2`.
Review prompts contained only case, rubric, Response A and Response B, with no Skill
text, version, commit, file path, mapping, implementation report or expected winner.
Version-leak checks passed on every review packet. All reviews and their hashes
were frozen before unblinding. Raw responses and reviews are preserved byte-for-byte
and set read-only locally. Full CLI transport logs remain local; only safe final
synthetic outputs are published. This local timestamp/hash chain is not an externally
witnessed preregistration. [Run manifest](../benchmark/model-eval/RUN_MANIFEST.json).

## Pairwise results

v0.1 wins: 0. v0.2.1 wins: 2. Ties: 13. Unassessable: 0.
The two preferences were narrow: G09 supplied a more complete deadline/extension
fallback, and H01 supplied an explicit opportunity-reopening trigger and rest option.
Both versions correctly rejected the denied round and refused to treat hearsay or
pending approval as an established offer. The holdouts therefore do not demonstrate
a new evidence-boundary advantage over v0.1.

| Case | Winner | Decisive v0.1 excerpt | Decisive v0.2.1 excerpt | Frozen review |
| --- | --- | --- | --- | --- |
| G01 | Tie | 先做一周的“双假设、有界测试”，再确定主方向 | 先用一周做有边界的方向验证，再确定一个主投方向 | [Judgment](../benchmark/model-eval/reviews/review-G01.json) |
| G02 | Tie | 第 5—7 天选择匹配度最高的岗位做少量定向投递或从业者交流 | 用匹配度最高的2—3个岗位做小规模投递或交流 | [Judgment](../benchmark/model-eval/reviews/review-G02.json) |
| G03 | Tie | 一周或完成 5 个可比机会后复盘 | 观察一周或累计5个可比机会后复盘 | [Judgment](../benchmark/model-eval/reviews/review-G03.json) |
| G04 | Tie | 建议：立即把“production”和“30% improvement”从简历中撤下，改为边界清楚的原型表述。 | 停止线：在证据补齐前，不升级为“生产”“主导”或量化提升。 | [Judgment](../benchmark/model-eval/reviews/review-G04.json) |
| G05 | Tie | 无法提供决策权或领导行为证据，就保持“参与并负责”，不要升级。 | 若证据仅覆盖评测工作，就停止升级措辞并沿用保守版本 | [Judgment](../benchmark/model-eval/reviews/review-G05.json) |
| G06 | Tie | 练习满2小时或能稳定回答上述五问即停止 | 现有材料只支持“参与团队原型”，不能证明生产使用，也不能证明独立完成 | [Judgment](../benchmark/model-eval/reviews/review-G06.json) |
| G07 | Tie | 用真实项目准备两轮递进追问，并在下一场同类面试前完成一次模拟讲述 | 做一次聚焦复盘，同时继续投递同类岗位。 | [Judgment](../benchmark/model-eval/reviews/review-G07.json) |
| G08 | Tie | 发送一次后再观察约三个工作日；若仍无回复，降低该机会投入并推进替代选项，但仍不记录为拒绝。 | 发出一次跟进后再观察约三个工作日；若仍无回复，就降低该机会投入、继续其他流程，但不记为拒绝。 | [Judgment](../benchmark/model-eval/reviews/review-G08.json) |
| G09 | v0.2.1 | 若两方答复仍含糊，暂缓定夺至真实截止前 | 优先争取延期，不能延期则依据现有证据仍偏向 A | [Judgment](../benchmark/model-eval/reviews/review-G09.json) |
| G10 | Tie | 若三至五个工作日仍无明确条件或审批节点，降低投入并继续求职；任何方案触碰你的薪资、地点或入职时间硬约束，就停止推进。 | 若始终拒绝提供核心书面条件，则暂停承诺；若完整方案触及你的硬约束，停止推进 | [Judgment](../benchmark/model-eval/reviews/review-G10.json) |
| G11 | Tie | 先把“量化”作为30天、每周10小时的有界验证，不立即把它当主转型方向 | 暂不把量化作为立即转职主线，先做30天有边界的可逆验证 | [Judgment](../benchmark/model-eval/reviews/review-G11.json) |
| G12 | Tie | 暂不补新项目，先把现有项目按目标岗位的任务重写 | 先暂停扩充项目，把下一步集中在“岗位任务对齐” | [Judgment](../benchmark/model-eval/reviews/review-G12.json) |
| G13 | Tie | 若任一表述仍无法用真实细节回答两轮追问，就继续降级措辞 | 整理一页“主张—证据—缺口—安全措辞” | [Judgment](../benchmark/model-eval/reviews/review-G13.json) |
| H01 | v0.2.1 | 复盘条件：若5—10个可比机会反复出现同一缺口，再判断是优化表达、补证据，还是调整方向。 | 若 HR 后续明确恢复流程或重新发出面试安排，再重启准备；否则停止跟进该机会。 | [Judgment](../benchmark/model-eval/reviews/review-H01.json) |
| H02 | Tie | “同事听说你通过了”只是转述，不能等同于正式录用。 | HR 的原话明确表示 HC 和薪酬仍待审批，正式 Offer 尚未成立 | [Judgment](../benchmark/model-eval/reviews/review-H02.json) |

Detailed dimension reasons, excerpts and hard failures remain in the frozen reviews
and [unblinded result](../benchmark/model-eval/MODEL_EVAL_RESULT.json).

## Dimension results

Counts use all 15 valid reviews. NOT_ASSESSABLE is separate from a tie. These are
dimension-level preferences, not additional independent samples or a weighted score.

| Dimension | v0.1 better | v0.2.1 better | Tie | Not assessable |
| --- | --- | --- | --- | --- |
| Situation Understanding | 0 | 0 | 15 | 0 |
| Evidence Discipline | 0 | 1 | 14 | 0 |
| Fact / Inference / Unknown separation | 2 | 2 | 11 | 0 |
| Bottleneck Identification | 0 | 0 | 15 | 0 |
| Recommendation Clarity | 0 | 0 | 15 | 0 |
| Actionability | 1 | 5 | 9 | 0 |
| Opportunity Cost Awareness | 1 | 4 | 9 | 1 |
| Counterfactual Quality | 0 | 2 | 13 | 0 |
| Reconsider Condition | 2 | 2 | 11 | 0 |
| Stop / Pivot Quality | 1 | 1 | 13 | 0 |
| Personal-context usage | 0 | 0 | 15 | 0 |
| Unsupported-claim avoidance | 0 | 0 | 15 | 0 |

## Hard failures

Each count is the number of responses carrying that reviewer label, counted at most
once per response/label. The same response can carry several different labels.
There was one response with a hard-failure label per version, both in G08.

| Reviewer label | v0.1 responses | v0.2.1 responses |
| --- | --- | --- |
| FABRICATED_FACT | 1 | 1 |
| NEGATION_FLIP | 0 | 0 |
| CONDITIONAL_AS_FACT | 0 | 0 |
| HEARSAY_AS_FACT | 0 | 0 |
| TEAM_TO_SOLE | 0 | 0 |
| DEMO_TO_PRODUCTION | 0 | 0 |
| NO_REPLY_TO_REJECTION | 0 | 0 |
| SUCCESS_TO_CAUSATION | 0 | 0 |
| UNSUPPORTED_METRIC | 0 | 0 |
| IGNORED_CONSTRAINT | 0 | 0 |
| NO_RECOMMENDATION | 0 | 0 |
| NO_ACTION | 0 | 0 |
| NO_STOP_CONDITION | 0 | 0 |

G08 explicitly says the promised date is unknown. The reviewer flagged v0.1's
“未给承诺日期” and v0.2.1's “没有给确定日期” as turning that unknown into absence.
Both answers also tell the user to verify dates and do not equate silence with
rejection. The phrasing may refer to the supplied excerpt, which contains no date,
so the severity should be confirmed by a human. Frozen labels and counts are retained
without being upgraded to certified facts or adjusted by the unblinded builder.

## v0.1 regressions / strengths

The baseline already gives source-conscious recommendations, bounded preparation,
one-to-three actions and stopping/review conditions. It ties 13 core decisions;
relative weaknesses appear in G09's
deadline fallback and H01's reopening trigger. There is no no-Skill arm, so these
strengths cannot be attributed to the Skill rather than the host/common instruction.
Its clearer local details sometimes outperform the upgrade, as preserved below.

## v0.2.1 regressions / strengths

No overall pair was lost to v0.1, but seven dimension judgments favor v0.1. These
weaker behaviors are preserved rather than hidden by the aggregate pair counts.

| Case | Dimension favoring v0.1 | v0.1 excerpt | v0.2.1 excerpt |
| --- | --- | --- | --- |
| G01 | Fact / Inference / Unknown separation | 项目内容、教育背景、数学/编程能力及岗位硬约束均未知 | 现在直接选方向依据不足，但也不能据此判定任一方向不适合 |
| G02 | Reconsider Condition | 持续指向同一硬缺口、硬约束不符或补齐成本过高 | 持续否定核心假设，且排除市场等混杂因素 |
| G07 | Actionability | 用真实项目准备两轮递进追问，并在下一场同类面试前完成一次模拟讲述 | 按面试题逐项还原：当时回答、被追问处、未答出的细节，以及哪些内容能由真实项目证据支撑 |
| G08 | Reconsider Condition | 若出现真实Offer截止，则提前如实告知并请求明确时间表。 | 若收到具体时间表，则按新承诺日复核。 |
| G10 | Opportunity Cost Awareness | 若三至五个工作日仍无明确条件或审批节点，降低投入并继续求职 | 若始终拒绝提供核心书面条件，则暂停承诺 |
| G11 | Fact / Inference / Unknown separation | 当前已知仅来自你的自述 | 未知的是符合地点约束的岗位数量，以及现有经历能否迁移 |
| G13 | Stop / Pivot Quality | 若任一表述仍无法用真实细节回答两轮追问，就继续降级措辞 | 若没有，就坚持降级。 |

G02 is plausibly linked to the added hypothesis wording: the response uses “核心假设”
and excluding “市场等混杂因素”, closely matching the frozen Skill's new pivot gate,
whereas the baseline names concrete cost/constraint triggers. This is an association,
not proof of instruction causation; classification: unclear, possible instruction
abstraction and candidate product issue requiring independent replication.

For G01/G11 (unknowns/provenance), G07 (practice output), G08 (external deadline),
G10 (continued search/window), and G13 (defense threshold), no changed rule clearly
explains the omission. Existing principles remain present in both snapshots.
Possible explanations include model variance and competition for the 300–500-character
budget; classification: unclear. The common output constraint can be a benchmark
artifact. None is established as a real Skill regression by one sample.

The unblinded builder additionally notes G08's “今天” versus the baseline's next
working-day wording, and reviewer caveats about G05's design/organizing scope and
G13's inability-to-explain versus missing-baseline distinction. These are post-review
audit notes, not additional blind scores. No product rule was patched in this task.

## What actually improved

On this fixed synthetic set, the reviewer preferred v0.2.1's G09 fallback and H01
restart/rest behavior. Actionability had 5 upgrade preferences versus 1 baseline
preference; opportunity cost 4 versus 1; counterfactual quality 2 versus 0.
The result supports these narrow observed diagnostic differences. It does not
establish a general quality improvement or isolate which added rule caused them.

## What did not improve

Hard-failure counts did not decline: one flagged date-unknown assertion per version.
Evidence boundary holdouts passed for both. Core situation, bottleneck, recommendation,
personal-context use and unsupported-claim avoidance dimensions tied all 15 pairs.
Reconsideration and fact/inference/unknown separation had two preferences each way.
Cross-opportunity identity, deduplication and Python guard behavior were not tested
by the supplied host inputs. There is no evidence here of better hiring outcomes.

## Limitations

Only 15 synthetic cases, one generation per version/case and one model reviewer;
no repeated sampling, variance estimate, human calibration or significance claim.
The shared prompt already requests good recommendation structure and stopping rules,
which may mask Skill effects. Reference contents/lengths differ with version, so the
comparison bundles Skill plus routed references. Automatic retrieval/routing, runtime
helpers and consented memory are excluded. Host context is not independently hashed.
Model identifiers and access are verified by actual CLI requests, not by an independent
attestation of backend weights. Reviewer judgments can be wrong, even when quotes match.

## Real-world claims NOT supported

REAL-WORLD-OBSERVED: NO. No genuine recruiting outcomes, user action execution,
recommendation acceptance, time saved, offer success or employment benefit were observed.
No “percent better career advice” claim, hiring probability or causal success claim is
supported. Labels on synthetic fixtures are not real recruiting observations.

## Recommended next step

Have a human independently review only the blind packet, especially G08 and the two
narrow wins. Then preregister a separate fixed set that supplies cross-opportunity
claim identity, duplicate historical events, ambiguous dates and concrete reconsider
triggers, with repeated samples. Keep this run unchanged. Consider a general rule
change only after an observed weakness is confirmed as a product problem; do not
encode benchmark IDs or answers in runtime instructions.
