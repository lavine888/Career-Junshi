# Evaluation

<a id="core-first-use-trial"></a>

## 当前：五人项目表达首用试用

**状态：准备招募，尚无真人结果。** 本轮只观察“经历 → 可用表达 → 回答一题 →
改进表达”，不扩展功能，不等于广泛职业决策已通过
[旧 Holdout 门槛](V023_HOLDOUT_EVAL.md#real-user-readiness)。
已有[合成试用](HUMAN_LOOP_EVAL.md)只作问题线索，不计入这五人。

### 邀请谁、带什么

邀请 5 位未参与开发、做过真实项目、说不清个人贡献或担心被追问的求职者；
使用其已有、允许读取本地 Skill 的助手。包含首次安装者，并单独观察其安装链路。
每人带一段可分享、已脱敏的项目经历，按原有写法即可；不必准备完整简历、JD
或证据表。项目背景、本人动作、队友分工和已知结果有多少写多少，未知留空。

约 20–30 分钟，首次安装时间另记，可随时停止。只观察表达与追问，不投递、不发消息、
不启用记忆。材料仍受参与者选择的宿主数据政策约束，不能承诺“完全不上云”。

### 怎样旁观

1. 只给项目链接和 README，让用户自己找“开始使用”并发出请求。开发者不示范、
   不指定要点哪个入口、不替其填材料，也不提前解释个人贡献该怎么回答。
2. 观察：提供材料 → 得到第一版表达 → 回答一个追问 → 得到修订表达。
   如果材料不足，允许助手先问一件关键事实。用户最后确认采用、不采用或尚不能判断。
3. 不打断去纠正措辞。用户主动求助时记录卡点、时刻和实际帮助，区分独立完成与
   帮助后完成；隐私外传、明显事实冒认或用户不适时可中止并记录，不为“完成”强推。
4. 首次安装者额外记录：找到仓库 → 按 README 安装 → 触发 Skill → 提供材料 →
   实际读取所需参考 → 第一个可用结果。按实际顺序记时，参考预读也照实记录。
   记下宿主可见的文件读取路径／工具轨迹；
   计划读取或模型自报不等于读取成功，轨迹不可见就记“未知”。安装成功不等于此链路成功。
   [旧自主读取曾受宿主阻塞](REFERENCE_RETRIEVAL_EVAL.md)，本轮不把它当作已解决。
5. 结束后再问哪里卡、改了哪些事实、最终采用哪句、是否愿意再用及原因。用户
   明确说停或不需总结时即结束，阶段未完成也保留，不补造结果。

### 同材料做一个轻量对照

同一人用同一份冻结的脱敏原材料，在两个干净聊天中各完成上述流程：
A 是通用助手加下列合理提示词，B 是 Career-Junshi 按 README 的主请求。
尽量用同一宿主、模型、设置与时间上限（例如每组约 10 分钟）。记录实际版本；
不可见则记未知。两组均可按助手实际问题补充真实事实，不能把第一组润色结果
或后来回忆的新事实预先塞进第二组的起始材料。

通用助手提示词（不加载 Career-Junshi 或其参考）：

```text
这是我的一段项目经历：……
请用自然口语帮我讲清个人贡献，只使用我给的事实，保留队友分工和不确定之处。
材料够时先给一段可用表达，再问一个贴合经历的追问；
不够时只问最关键的一件事。等我回答后修改表达，不替我编个人贡献或成果。
不用先补完整简历或 JD；我只要一句或说停时请尊重。
```

两组不要共享聊天历史。通用组应禁用／隔离该 Skill，不能自动读到其文件。
能隔离时交替先后顺序；不能隔离时可在安装前先做通用组，并记录固定顺序的局限。
若发生 Skill 污染、额外教学或模型不一致，保留但注明，不能当成干净对照。
同一材料的重复练习会帮助回忆，5 人也不能消除学习效应或证明因果优势。

### 一份记录，复制五次即可

记录只放参与者同意的本地私有位置；开发者使用 D 盘、Git 与安装目录外的位置。
不收姓名或联系方式，不把真实材料、原始问答、录音或采用句上传／提交到仓库。
观察记录与结论仅供本地复盘，本轮不对外发布。
留原文、截图或录音需另获同意；未同意留存时只记可记录的指标与缺失，不还原原文。

```text
编号／日期：____
宿主／模型与可见设置；Skill 提交；A/B 顺序与隔离情况：____
原材料的私有定位／是否同意留存：____
首次安装（如适用）：各阶段时刻、实际读取证据、阻塞、求助及帮助：____

指标                           A 通用助手           B Career-Junshi
首次可用表达耗时               ____                 ____
事实／个人归属纠错轮次         ____                 ____
追问贴合程度与理由             ____                 ____
最终内容的修改负担             ____                 ____
是否愿意再次使用及原因         ____                 ____

两组第一版／答后修订版／最终采用表达（允许留存时）及其来源：____
事实纠正的原句→纠正（允许留存时）；具体卡点／中止阶段与原因：____
尚未观察到／无法判断的项目：____
```

耗时从各组提交同一段经历开始，到用户认为某版可用于自己的简历或口述；
安装耗时另列。未到达就记“未到达＋观察时长”，无法定位时记未知，不填零。
纠错只计事实／归属的纠正轮次，附其范围，普通润色不算；未核对不等于零错误。
追问由用户判断“贴合／部分／不贴合／未发生”并说明；修改负担记
“直接采用／少量调整／大改／弃用”，保留实际改动。愿意再用不等于已回访。

这些都是**待验证指标**。先逐人看哪一环受阻、用户采用了什么，再决定下一轮
最小修复；不预填结果，不用测试数量、喜爱评分或 5 人样本宣称提升面试／Offer 成功率。

### 可直接发送的邀请

> 我在试用一个叫“求职军师”的项目，想请你帮我体验约 20–30 分钟，首次安装另外计时。
> 你只需带一段能分享、已脱敏的真实项目经历，不用完整简历或 JD。
> 请用你已有、支持本地 Skill 的助手按 README 自己开始，完成“得到表达 → 回答一题 → 看改写”；
> 我会旁观，不提前教你操作。还会用同一材料和通用助手做一次简短对照。
> 不用配合说好话，卡住、不想继续或最后不用它都可以。不会公开你的材料，
> 原文留存需你同意；材料按你选择的助手数据政策处理。
> 项目：https://github.com/lavine888/Career-Junshi#start

---

## Historical evaluation evidence

Evidence status as of 2026-10-03: IMPLEMENTED / TESTED and MODEL-EVALUATED for the
limited frozen synthetic host comparison below. REAL-WORLD-OBSERVED: NO.
Private real-context dry-run remains a builder review, not a recruiting outcome study.

v0.2.1 has 123 tests and a [completed 15-pair model comparison](MODEL_EVAL_REPORT.md):
30/30 valid generations on gpt-5.6-sol/high and 15/15 version-hidden reviews by the
different model gpt-6-astra/high, tools disabled. v0.2.1 wins 2, v0.1 wins 0, ties 13;
one hard-failure label per version, with no reduction. The exact scope is Skill
instructions plus the same routed reference paths/count budget, not runtime helper
execution or installed-Skill discovery. Cross-opportunity identity and deduplication
are not assessable from these inputs. [Raw evidence and protocol](../benchmark/model-eval/README.md).

The original gpt-6.1-sol model-access rejection remains in the manifest as a zero-output
historical attempt. Replacement was explicitly authorized and actually probed before
generation; it stayed fixed for both snapshots. No private context was evaluated.
See [V021_REPORT.md](V021_REPORT.md) for corrected runtime boundaries.

## What is tested

Level 1 checks extraction spans and provenance, explicit epistemic errors, claim
boundaries, action ownership, consent, immutability, duplicate events, recency and
installed-runtime behavior. Level 2 tests fixed structured decisions, counterarguments,
reconsideration conditions, bounded relevant recall, prediction states, recurrent
preparation priority, hypothesis gates, freshness and role translation.

Original 61 v0.1 tests remain intact. Added extraction and v0.2 tests use synthetic
fixtures. Some memory fixtures deliberately declare real_world to exercise gates;
they are test data and supply **zero real-world evaluation observations**.
No failure is ignored to obtain a passing result.

## Golden cases and dimensions

[13 fixed synthetic cases](../benchmark/cases.json) cover unknown direction, SWE to
AI product, JD evaluation, prototype/production conflict, team leadership, tomorrow's
interview, technical rejection, recruiter silence with calendar ambiguity, offer
tradeoffs, negotiation without written terms, direction/constraints conflict,
positioning despite strong project evidence, and weak defense despite a strong resume.
Each case has source-labeled material excerpts, notices, forbidden assumptions,
tradeoffs, multiple acceptable recommendations, bad recommendations, required actions,
stopping conditions and all ten dimensions. No single golden sentence is required.

| Diagnostic dimension | Reviewer checks |
| --- | --- |
| Situation Understanding | Correct urgency, stage and context; decisive questions only |
| Evidence Discipline | Sources and personal scope; no invented achievements or status |
| Bottleneck Identification | Evidence versus expression, direction, timing or market |
| Recommendation Clarity | A clear conditional first choice, without overclaiming |
| Actionability | One to three feasible actions with owner and concrete artifact |
| Opportunity Cost Awareness | Time budget, competing options, stopping investment |
| Uncertainty Calibration | Alternatives and decisive unknowns; no hiring probabilities |
| Stop / Pivot Quality | Observable review triggers, stopping lines and guarded pivot |
| Personal Context Usage | Relevant source context without unrelated or stale contamination |
| Outcome Learnability | Topic predictions and observations; no success-causes-strategy claim |

Ratings are PASS / PARTIAL / FAIL / UNASSESSABLE, each with response excerpt,
source reference and diagnostic. Do not combine them into a Career Score.
[Benchmark protocol](DECISION_BENCHMARK.md) explains lower levels and host packets.

## Reproduce

```sh
python -m unittest discover -v
python scripts/validate_skill.py
python scripts/benchmark.py run --now 2026-10-03T12:00:00+08:00
python scripts/benchmark.py packet --output /new/private/eval-packet
python scripts/benchmark.py validate-host --input /private/reviewed-run.json
```

[Structured report](../benchmark/structured-report.json) records coverage, hard rules,
field properties and regressions. Repeats use the same clock, cases, Skill revision
and interpreter. The structured report retains its historical Level 3/4 NOT_RUN markers; the completed
instruction/reference model diagnostic is recorded separately in benchmark/model-eval.
Installed runtime excludes development cases; provide `--cases /checkout/benchmark/cases.json`.

For Level 3, run each host-input independently with the installed Skill, with rubric
hidden. Record model/version/settings, Skill commit, run ID, clock, tools and missing
context. Save complete outputs. A separate reviewer reads the held rubric and raw
materials, quotes the responses and records failures. validate-host checks structure
and excerpts; it cannot authenticate model execution or reviewer independence.

## What is not tested and current failures

- One separate-model blind comparison is complete, with twelve diagnostic dimensions;
  no independent human certification or repeated-sample reliability claim. Most pairs
  tied and hard-failure labels did not decline. Cross-opportunity/history cases remain
  missing from host coverage; exact quote validation does not certify reviewer judgment.
- Local counterarguments are mode defaults, not a guarantee of situation-specific
  competing options. The host must replace generic wording when context warrants it.
- The structured planner alone did not select a personalized role order in a private
  multi-project dry-run. Source-faithful main/secondary ordering depended on host review.
- Span checks catch explicit errors but cannot validate every paraphrase, personal
  decision, comparable-event key, observation label or source receipt.
- Old untagged memory is not automatically migrated. Three-event windows can miss
  longer patterns. Reported real-world flags are attestations, not authenticated events.
- No real action acceptance, execution or recruiting outcome was available in the
  selected private context. No live result calibration or causal benefit is claimed.

## Private real-world protocol

For the current five-person contribution-expression trial, use the
[short protocol above](#core-first-use-trial). The older decision/outcome fields
below are not a first-use intake form or a second participant record.


Keep raw and identifying material outside any public checkout, with explicit memory
consent separate from session use. Public output contains anonymous conclusions only.
Do not publish a synthetic replacement as an observed real case.

Before: case ID, date, current situation, goal, constraints, source/evidence references
and unknowns. Decision: chosen move, strongest alternative and counterargument,
actions with owner, expected topic predictions, observation window, stop conditions
and reconsider_if. After: linked decision ID, dated reported hard outcome, source
observations, actual execution (done / partial / not done / unknown), user explanation,
agent explanation, unknowns, prediction calibration and what_changed.

Ask which effect the user observed, allowing more than one: A decided faster; B
avoided wasted preparation; C noticed an overlooked risk; D no help. Ask separately
whether the actions were executed. A favorable rating or passing interview does not
prove the advice caused an outcome. Missing follow-up remains missing / unknown.

| Metric | Numerator / denominator and missingness |
| --- | --- |
| Recommendation accepted | Explicit user acceptance / reviewed recommendations with an explicit response; report no-response count separately |
| Action executed | Reported completed agreed actions / agreed actions whose window elapsed and execution was assessed; partial and unknown separate |
| Reconsidered | Decisions actually revised after new evidence / elapsed-window decisions with follow-up; record trigger, exclude mere wording edits |
| Repeated risk | Comparable reviewed windows with recurrent signal / reviewed windows meeting at least three independent real outcomes; counts below gate separate |
| Outcome returned | Decisions with sourced linked outcomes / consented feedback decisions whose observation window elapsed; report overdue missing outcomes |

All rates require explicit counts, dates, denominators and uncertainty; do not invent
percentages before collecting observations. Offer-success rate is not the primary
metric. Delays, role mix, market, candidate experience and action execution confound
outcomes. Collect useful decision evidence before making any effectiveness claim.

## v0.2.2 Decision Quality reevaluation

Baseline eea9f0a: 135 tests. Current: 154 tests, no regression in the original
13 structured benchmarks or five frozen property replays. Five fresh synthetic
model extractions and installed-Skill/reference-preloaded host outputs use
gpt-5.6-sol/high, Codex CLI 0.153.0; generation excludes rubrics and outcomes.
Operator semantic review gives Interview PASS, HR PASS, Offer PARTIAL, Direction
PASS and Ownership PARTIAL. This is not independent blind preference grading
or proof of hiring improvement. New extraction profiles and explicit SKILL
preload are disclosed harness changes. See the
[report](V022_DECISION_QUALITY_REPORT.md) and
[frozen results](../benchmark/decision-quality-v022/semantic-summary.json).
Autonomous reads were separately BLOCKED_BY_HOST on initial SKILL.md access,
including a recheck after the final compiler boundary fix. See
[retrieval evidence](REFERENCE_RETRIEVAL_EVAL.md); preload results do not certify
autonomous reference routing.
