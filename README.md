<a id="top"></a>

<div align="center">

[![求职军师 · Career Junshi：下一程，从真实的你开始。](assets/brand/readme-hero-zh.svg)](#start)

**把真实经历讲清楚，把下一场面试练具体。**

<sub>求职军师 · Career Junshi — 运行在助手中的求职 Skill，从你手边的材料开始。</sub>

<p>
  <a href="#start"><img src="assets/brand/cta-start-zh.svg" width="136" height="42" alt="快速开始"></a>
</p>

[看交付样例](#demo) &nbsp; · &nbsp; [官网 ↗](https://career-junshi.lavinex.chatgpt.site) &nbsp; · &nbsp; [English](README_EN.md)

</div>

---

<a id="demo"></a>

## 先看，你会拿到什么

### 一段能讲清贡献的经历

> **原句**：「独立开发生产级 RAG 平台，准确率提升 30%。」

实际材料是团队课程原型：本人负责评测脚本和失败分类，队友实现服务；
跑过 10 条内部问题，没有基线，也没有生产用户。追问个人工作与判断标准后：

> 参与团队课程 RAG 原型开发，负责评测脚本与失败分类，按团队约定标准完成
> 10 条内部问题评测，记录缺少文档引用、引用段落错误及回答与文档冲突三类问题。

**留下可用表述，也标清还缺什么。** 没有效果数据，不抹掉你做过的工作，也不补写成果。

<sub>改写自合成材料的实际宿主试用，非真人简历或招聘结果。[查看记录](documentation/EVOLUTION_EVAL.md)</sub>

<details>
<summary>看这句改写背后的一次追问</summary>

```text
军师：这 10 条问题里，你用什么标准判定一条回答失败？

你：我和队友约定了三类：没有文档引用、引用段落错误、内容与文档冲突。
    我把检查写进脚本并记录结果。

军师：个人贡献更清楚了。目前仍是你的自述，代码和评测记录还需要核验。
```

[完整守城示意](cases/experiences/defense/example.md)为另行编写的合成案例。

</details>

<a id="resume-export"></a>

### 一份可以继续编辑的简历

从岗位表达到排版，保留同一套事实。可交付 **LaTeX 源码、纯文本**；
本机具备 XeLaTeX 时，再编译、检查 PDF。精排版可预留照片位。

<p align="center">
  <a href="benchmark/journey-20261021/artifacts/editorial-zh/resume.pdf">
    <img src="benchmark/journey-20261021/artifacts/editorial-zh/page-1.png" width="360" alt="实际编译的中文精排合成简历，预留照片位；点击查看PDF">
  </a>
  <br>
  <sub>实际编译的合成样例 · 可预留照片位 · 点击查看 PDF</sub>
</p>

<p align="center">
  <a href="benchmark/journey-20261021/artifacts/editorial-zh/resume.pdf">查看 PDF ↗</a>
  &nbsp; · &nbsp;
  <a href="benchmark/journey-20261021/artifacts/editorial-zh/resume.tex">查看 LaTeX 源码</a>
</p>

<details>
<summary>想直接导出简历？复制这段</summary>

```text
请用 $career-junshi，按这份 JD 整理中文单栏简历，优先一页。
使用精排版，预留照片位。保留真实贡献，说明重要改写与删留。
导出 LaTeX 源码和纯文本到我指定的新私有目录。
本机有 XeLaTeX 时再编译 PDF，说明内容、编译、文字层和版面检查结果。
```

`resume.txt` 可粘贴到 Word 等编辑器，它是纯文本，不是 Word 文档。
`resume.tex` 用于继续排版；`resume.pdf` 只有实际生成并检查后才作为 PDF 交付。
材料与文件写入你指定、位于 Git 仓库和 Skill 安装目录之外的私有位置。

</details>

<a id="start"></a>

## 两步，开始这一轮

### 1. 安装到你的助手

把这段发给 Codex 等支持本地 Skill 的助手：

```text
请将 https://github.com/lavine888/Career-Junshi 的 main 分支
安装为 career-junshi 本地 Skill，使用仓库安装器。
先检查已有同名安装，不要覆盖；安装后验证运行文件。
不要替我启用长期记忆。
```

<details>
<summary>手动安装 · Python 3.10+ · 仅标准库</summary>

```sh
git clone --branch main https://github.com/lavine888/Career-Junshi.git
cd Career-Junshi
python scripts/validate_skill.py
python scripts/install_skill.py --target /path/to/your/skills/career-junshi
python /path/to/your/skills/career-junshi/scripts/validate_skill.py --runtime-only
```

替换为宿主实际读取的目录，Windows 同样使用实际路径；目标文件夹须名为
`career-junshi`，已有目标会保留并报错。安装只复制运行文件和许可，不带案例、
测试、`.git` 或数据库，也不会开启记忆。符号链接与 Windows 目录联接路径会被拒绝。

</details>

### 2. 带来手边的一点材料

```text
请用 $career-junshi。我想投【方向】。
这是我的【简历／项目经历／GitHub 链接】：……
先给我一个现在能用的结果，再带我做一个小步骤。
暂时不生成文件，不开启长期记忆。
```

没有完整简历也能开始，JD 和截止时间不知道可以留空。
只有 GitHub 时，先筛项目、给短介绍；个人职责不清楚的部分会继续核实。
[看项目起步示意](cases/experiences/public-projects/example.md)。

<a id="experiences"></a>

## 从你正卡住的地方进入

| 你现在的处境 | 直接这样说 | 本轮拿到什么 |
| --- | --- | --- |
| **项目做过，简历说不清** | “改这段经历，解释哪些该留、哪些该删。” | 可用表达、贡献边界、重要改写依据 |
| **怕被追问，想先练一遍** | “追问这个项目，一次一题，先听我回答。” | 依据实际回答的追问与一个练习点 |
| **收到反馈，不知怎么继续** | “对照这次反馈，帮我选下一步。” | 保留已发生的事实，调整一项具体行动 |

> 也可以说：“今天只想说两句”“只给我一句能用的话”“先停，不用总结”。
> 不必每次都带走一份计划。

<details>
<summary>四种核心体验与更多用法</summary>

- **简历守城**：“追问这句经历，一次问一个问题。”[看案例](cases/experiences/defense/example.md)
- **岗位表达**：“适配这两份 JD，解释每版删留。”[看案例](cases/experiences/role-translation/example.md)
- **补证冲刺**：“本周有 4 小时，补一个关键缺口。”[看案例](cases/experiences/proof-sprint/example.md)
- **决策复盘**：“对照上次建议与这次反馈，调整下一步。”[看案例](cases/experiences/decision-review/example.md)

还没定方向，可以问“我该主投哪个方向？”；招聘环节也能问“HR 没回，何时跟进？”
或“两个 Offer 怎么选？”。[跟进示例](cases/follow-up/request.md) ·
[Offer 比较示例](cases/offer/request.md)

还可以做 [JD 缺口分流](cases/experiences/jd-gap/example.md)、
[AI 开发贡献复盘](cases/experiences/development-recap/example.md)、
[变题复练](cases/experiences/interview-retry/example.md)、
[措辞核对](cases/experiences/wording-audit/example.md)、
[断点续练](cases/experiences/defense-resume/example.md)、
[投递实验](cases/experiences/job-search-experiment/example.md)与
[行动启动卡](cases/experiences/action-start/example.md)。

只有未见结果的新上下文才能做[隐藏结果复盘](cases/experiences/outcome-blind-review/example.md)。
以上为合成案例；不同岗位或渠道的结果不能直接归因于模板。

</details>

<a id="interview-loop"></a>

## 面试前后，接着用

**面试前 · 用实际回答，练一次追问。**<br>
“围绕这个项目模拟三题，一次一问，最后再点评。”逐题纠偏与整场模拟可以切换，
从实际回答选下一问；不知道用哪段经历，就先练选一个事件、说一句开场。

**面试后 · 还原问答，再选一个练习点。**<br>
“刚面完，没有录音，我还记得这道追问。”分开实际问答、本人感受和明确反馈；
复盘发现的卡点，可以回到下一轮变题练习。

**谈薪时 · 先对齐条件，再演练回应。**<br>
“HR 开始问预期了，先判断阶段，再扮 HR 陪我练一句。”区分预期沟通与 Offer 协商，
核对固定收入、浮动奖金和条件；私有底线不进入外发草稿，草稿由本人发送。

[看三段衔接的合成示例](cases/experiences/interview-loop/example.md)

<a id="journey"></a>

## 这一轮结束，下次接得上

**真实材料 → 简历版本 → 实际投递 → 招聘反馈 → 下一步**

已投的 R1 不被新改的 R2 覆盖，补交单独记录。
旧反馈回填不顶掉当前判断，同刻反馈并列保留。需要继续时，接续卡带回机会、
实际版本、反馈来源和未完成的一步；你不想总结时，也可以直接停下。

<details>
<summary>复制下次继续的提示词</summary>

```text
请用 $career-junshi，继续我的求职。
这是上次的接续卡／记录，这次发生了：……
对照当时建议，说明哪些已做、哪些仍未知，给我一个下一步。
如果改简历，保留原投递版本并生成新版；需要时更新接续卡。
先在聊天处理，不开启长期记忆。
```

![事实底稿、简历版本、实际投递、招聘反馈与下一步](assets/brand/journey-zh.svg)

默认只在聊天中交付；你明确要求私有接续文件后，才生成记录、检查结果与
`continue.md`，下次主动带回。[接续契约](references/practical/job-search-journey.md) ·
[合成起点](cases/experiences/journey/request.md) · [实际验收](documentation/JOURNEY_EVAL.md)

</details>

<a id="evaluation"></a>

## 能力有展示，验证有记录

| 已做的检查 | 可以查看的证据 |
| --- | --- |
| **软件回归** | 最近记录：286 项，285 通过、1 项文件符号链接权限跳过；目录联接已实测。[修复与验收](documentation/HUMAN_LOOP_EVAL.md) |
| **真实 PDF 编译** | 合成简历实际编译、提取文字和检查页数；含超页失败例。[排版检查](benchmark/resume-layout-20261020/README.md) · [精排与接续](documentation/JOURNEY_EVAL.md) |
| **合成交互试用** | 新上下文代理、多轮问答与前后对照，保留原始记录和局限。[低负担交互](documentation/HUMAN_LOOP_EVAL.md#独立上下文合成试用) · [GitHub 起步](documentation/PUBLIC_PROJECT_FIRST_USE_EVAL.md) |

这些检查**不能证明提高面试通过率、Offer 率或谈薪结果**。合成案例不是真人背书，
软件回归与对话试用也分别报告。

<details>
<summary>全部验证记录与已知限制</summary>

[面试前后流程](documentation/INTERVIEW_COACH_EVAL.md) ·
[五个合成用户、十五轮交互](documentation/MOCK_USER_TRIALS.md) ·
[改写定位与结果性质](documentation/RESUME_POSITIONING_EVAL.md) ·
[五组改写对照](cases/experiences/resume-positioning/example.md) ·
[缺口、开发复盘与复练](documentation/EVIDENCE_TO_PRACTICE_EVAL.md) ·
[新上下文可靠性试用](benchmark/reliability-20261023/forward-trial.md) ·
[四种核心体验](documentation/EVOLUTION_EVAL.md) ·
[措辞、续练与盲评](documentation/REFINEMENT_EVAL.md) ·
[简历导出](documentation/RESUME_EXPORT_EVAL.md) ·
[导出文件选择](documentation/EXPORT_HANDOFF_EVAL.md) ·
[简历迭代](documentation/RESUME_ITERATION_EVAL.md) ·
[研究工作流](documentation/RESEARCH_EVOLUTION_EVAL.md) ·
[参考库与 Offer 核验](documentation/CAREER_LIBRARY_EVAL.md)。

另有 13 个结构化合成基准。冻结案例仍有提取、交接和建议泛化等弱点，
未全部重测，也未宣称达到真实用户试点门槛。
[评测协议](documentation/EVAL.md) · [冻结 Holdout](documentation/V023_HOLDOUT_EVAL.md)

</details>

<a id="boundaries"></a>
<a id="library"></a>

## 事实可追溯，节奏由你定

<details>
<summary>没有 JD、完整简历或 LaTeX，也能用吗？</summary>

可以，从一段经历、项目链接或招聘消息开始。没有 JD 时，岗位建议是待验证假设。
没有 XeLaTeX 时仍可交付源码与纯文本，PDF 保持未编译、未验证。

PDF 编译需要 XeLaTeX、CTEX/Fandol、geometry、hyperref 及其依赖；精排版另需
fontspec、xcolor、graphicx。运行 `python scripts/junshi.py resume-doctor` 可实际编译
中英文合成小样检查环境，不读取你的简历、不安装组件。`READY` 只说明小样通过；
实际简历还需单独验收，文字提取不等于通用 ATS 认证。
[完整导出流程](references/practical/resume-export.md)

</details>

<details>
<summary>会自动记住我，或替我投递、发消息吗？</summary>

默认不会自动跨聊天记住你，也不会自动读取个人目录。把接续卡主动带回来即可继续。
长期记忆另需同意，支持查看、暂停、撤销和删除；默认不保存完整简历、JD 或聊天。
数据库位于 Git 与安装目录外，未加密；删除不保证擦除外部备份，宿主仍有自己的数据政策。

军师准备材料与草稿，实际投递、发送、谈薪和接受 Offer 由你决定并执行。
[记忆说明](documentation/MEMORY.md) · [证据契约](documentation/EVIDENCE.md)

</details>

<details>
<summary>建议有什么依据？哪些结论不能下？</summary>

[职业参考库](references/knowledge/08-research-and-application.md)按阅读深度、适用范围
和限制整理研究与官方资料。可以直接问：“这个建议依据什么，哪些情况不适用？”

当前招聘、公司、薪资和个案法律信息需新鲜来源；不编造职责、指标或归属。
单次沉默或拒绝不足以判断职业方向，不提供候选人综合分数或录用概率。

</details>

---

<details>
<summary>开发者入口与手动验证</summary>

[Skill 入口](SKILL.md) · [任务指南](references) · [合成案例](cases) ·
[架构](documentation/ARCHITECTURE.md) · [问题与建议](https://github.com/lavine888/Career-Junshi/issues)

宿主理解材料并进行互动判断；Python 提供有界的结构化辅助、产物与可选记忆。
`route --experience` 只选择参考，不自动运行对话或生成报告。

```sh
python -m unittest discover -s tests -v
python scripts/validate_skill.py
python scripts/benchmark.py run
python scripts/junshi.py route --mode interview --experience defense
python scripts/junshi.py sources --topic interview
```

[提取契约](documentation/CONTEXT_EXTRACTION.md) ·
[决策契约](documentation/DECISION_INTELLIGENCE.md) ·
[可选快照集成](documentation/INTEGRATION.md)

独立的 [v0.3 Host-First 实验](https://github.com/lavine888/Career-Junshi/tree/experiment/v0.3-host-first)
尚未完成，其结果不代表当前版本的架构结论。

</details>

<div align="center">

[开始这一轮 ↑](#start) &nbsp; · &nbsp; [官网 ↗](https://career-junshi.lavinex.chatgpt.site) &nbsp; · &nbsp; [GitHub Issues](https://github.com/lavine888/Career-Junshi/issues)

<sub>[MIT](LICENSE) · Python 3.10+ · [English](README_EN.md) · [回到顶部](#top)</sub>

</div>
