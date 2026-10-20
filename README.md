<div align="center">

![求职军师——让经历，有据可讲。](assets/readme-hero-editorial.png)

# 求职军师 · Career Junshi

### 把真实经历，写成经得起追问的简历。

改简历、练面试、补证据、选 Offer，从你现在卡住的地方开始。

[![MIT](https://img.shields.io/badge/License-MIT-D8B466?style=flat-square)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-627EAA?style=flat-square)
[![Memory opt-in](https://img.shields.io/badge/Memory-opt--in-83D5BA?style=flat-square)](documentation/MEMORY.md)

[开始使用](#start) · [核心体验](#experiences) · [简历导出](#resume-export) · [职业参考库](#library) · [English](README_EN.md)

</div>

Career Junshi 是运行在 Codex 等支持本地 Skill 的助手中的求职工作流。
给它一段真实经历、一份 JD 或眼前的选择，拿走可用的表达、有依据的判断和最值得做的 1–3 件事。

<a id="demo"></a>

## 先看一段经历怎么改

> **简历原句**：「独立开发生产级 RAG 平台，准确率提升 30%。」
>
> **实际情况**：团队课程原型；本人做评测脚本和失败分类，队友写服务。
> 跑过 10 条内部问题，没有基线、没有生产用户。

军师从实际工作问起，一次只问一个问题：

```text
军师：这 10 条问题里，你用什么标准判定一条回答失败？

你：我和队友约定了三类：没有文档引用、引用段落错误、内容与文档冲突。
    我把检查写进脚本并记录结果。

军师：个人贡献更清楚了。目前仍是你的自述，代码和评测记录还需要核验。
```

**得到一条贡献范围清楚、现在可以使用的表述：**

> 参与团队课程 RAG 原型开发，负责评测脚本与失败分类，按团队约定标准完成
> 10 条内部问题评测，记录缺少文档引用、引用段落错误及回答与文档冲突三类问题。

<sub>改写自匿名合成材料的实际宿主试用，非真实候选人或招聘结果。[试用记录](documentation/EVOLUTION_EVAL.md) · [另行编写的完整示意](cases/experiences/defense/example.md)</sub>

<a id="start"></a>

## 两步开始

### 1. 安装 Skill

把这段发给支持本地 Skill 的助手：

```text
请将 https://github.com/lavine888/Career-Junshi 的 main 分支
安装为 career-junshi 本地 Skill，使用仓库安装器。
先检查已有同名安装，不要覆盖；安装后验证运行文件。
不要替我启用长期记忆。
```

<details>
<summary>手动安装与环境要求</summary>

需要支持本地 Skill 的宿主；仓库安装器和辅助脚本使用 Python 3.10+ 标准库。

```sh
git clone --branch main https://github.com/lavine888/Career-Junshi.git
cd Career-Junshi
python scripts/validate_skill.py
python scripts/install_skill.py --target /path/to/your/skills/career-junshi
python /path/to/your/skills/career-junshi/scripts/validate_skill.py --runtime-only
```

将 `/path/to/your/skills` 替换为宿主实际读取的目录，Windows 同样传入实际路径。
目标文件夹须名为 `career-junshi`；已有目标会保留并报错。
安装只复制运行文件与许可，不带案例、测试、`.git` 或数据库，也不会开启记忆。

</details>

### 2. 带一段真实材料来

```text
请使用 $career-junshi，带我做一次「简历守城」。

我的简历写：……
我实际做过：……
目标岗位 / JD：……
最近面试或截止时间：……

一次问一个问题，按我的回答继续追问。
最后给我可用的简历表述、证据缺口和最值得补的一步。
```

没有完整简历也能开始。可以直接说“帮我改这段经历”或“今晚该准备什么”。
已有材料先用，缺少会改变判断的信息才补问；第一次使用可以不开记忆。

<a id="experiences"></a>

## 四个核心体验

| 你现在卡在哪里 | 直接这样说 | 带走什么 |
| --- | --- | --- |
| **🛡 简历守城** · 怕项目被问穿 | “追问这句经历，一次问一个问题。” | 讲清个人贡献，找出证据缺口，得到当前可用表述 |
| **🎯 岗位表达** · 同一项目不知道怎么投 | “用这个项目适配这两份 JD，解释每版删留理由。” | 共用事实底稿、岗位版本与取舍依据 |
| **🧩 补证冲刺** · 知道缺什么，不知道怎么补 | “我本周有 4 小时，补一个最影响投递的证据。” | 具体产物、验收条件、时间预算和停止线 |
| **🔄 决策复盘** · 面试回来不知道怎么改 | “对照上次建议和这次反馈，哪些判断需要调整？” | 原判断与实际观察对照，修正下一步 |

你可以从任一环节进入，随时停止；不同岗位版本沿用同一套事实。

合成案例：[简历守城](cases/experiences/defense/example.md) · [岗位表达](cases/experiences/role-translation/example.md) ·
[补证冲刺](cases/experiences/proof-sprint/example.md) · [决策复盘](cases/experiences/decision-review/example.md)

<a id="resume-export"></a>

## 简历内容定了，再导出文件

```text
按这份 JD 整理中文单栏简历，优先一页。
保留真实贡献，先说明重要删留；给我 LaTeX 源码和纯文本。
输出到我指定的新私有目录；本机有 XeLaTeX 时再编译 PDF。
分别说明内容、编译、PDF 文字层和实际页面的检查结果。
```

导出保留 **LaTeX 源码、纯文本、带来源的内容数据和验收记录**。
内容先起草和审阅，再排版；独立审阅依宿主可用能力进行。

<details>
<summary>PDF 编译、页数与文件存放</summary>

源码导出不需要 LaTeX；PDF 编译需要本机 XeLaTeX、模板字体及宏包。
页数可选 1 或 2 页，不自动缩字或删除实质内容。
未完成编译或视觉检查时会明确标注，文字层检查也不等于通用 ATS 认证。
个人文件保存在仓库和 Skill 安装之外，由你指定的新目录中。

[合成输入与源码示意](cases/experiences/resume-export/example.md) · [完整导出流程](references/practical/resume-export.md)

</details>

## 更多场景，直接说出你的问题

| 直接这样说 | 军师会帮你做什么 |
| --- | --- |
| “我该主投哪个方向？” | 结合目标、经历和当前 JD，给主投 / 副投 / 探索及验证动作 |
| “按这份 JD 模拟面试，先说这一题看什么。” | 明确职责与观察点，一次一问，依据实际回答反馈 |
| “明天二面，今晚只有 90 分钟。” | 收敛最高风险和 1–3 个动作，明确今晚的停止线 |
| “HR 五天没回，要不要催？” | 核对对话、承诺日期和工作日，给时机、草稿与停止等待条件 |
| “这两个 Offer 怎么选？哪些条件先核实？” | 对照目标与书面条款，核实决定性未知；有费用或身份风险时优先处理 |
| “两版简历反馈不同，用这周 1 小时做一次投递实验。” | 选一个待验证问题、可比岗位、只改一项的方案和观察窗口 |
| “只有 15 分钟，一直在换模板，帮我开始。” | 给一个能检查的小结果、开始触发点、遇阻备用做法和停止时间 |

<details>
<summary>进阶用法：措辞核对、断点续练、隐藏结果复盘</summary>

- **措辞核对**：“检查这句的动词、贡献和因果，只改证据不支持的部分。”
  保留有依据的领导力，把前后观察与个人归因分开。[示意](cases/experiences/wording-audit/example.md)
- **断点续练**：“先停，给我可复制的断点。”下次贴回记录即可继续；断点默认留在聊天。
  [示意](cases/experiences/defense-resume/example.md)
- **隐藏结果复盘**：在未见结果的新聊天中先提供面试观察，固定初判后再揭晓结果。
  同一聊天删去结果不能让模型忘记；已知结果时按普通复盘处理。
  [示意](cases/experiences/outcome-blind-review/example.md)

投递实验保留原版本、分母和观察窗口；不同岗位或渠道的结果不能直接归因于模板。
未到观察窗口的投递保持待观察。[投递实验](cases/experiences/job-search-experiment/example.md) ·
[行动启动卡](cases/experiences/action-start/example.md)

</details>

<a id="library"></a>

## 职业参考库：建议有依据，也有边界

**18 条独立研究与官方资料，覆盖八个主题**：求职策略、职业选择、简历表达、
面试练习、谈判、Offer、劳动权益与求职安全。同一资料服务多个场景时只计一次。

每条标明资料类型、实际阅读深度、适用范围、限制和版本。
需要时问：**“这个建议有什么依据，哪些情况不适用？”** 军师按需展开相关条目。

[浏览完整索引](references/knowledge/08-research-and-application.md)。
资料支持方法选择；个案法律问题仍需核对当前适用规定。

## 真实贡献与使用边界

- **保留事实。** 讲清来源、个人贡献和项目阶段，区分已观察、推断与未知；
  证据不足时收窄表述、给补证动作。[证据契约](documentation/EVIDENCE.md)
- **行动由你决定。** 报告默认留在聊天；需要文件时指定目录。投递、发送消息、
  谈薪、接受 Offer 和对外分享由你执行。
- **记忆自选开启。** 明确同意后才保存本地压缩记录，默认不保存完整简历、JD 或聊天；
  支持查看、暂停、撤销与删除。[记忆说明](documentation/MEMORY.md)

本地数据库未加密，删除不保证擦除外部备份；对话材料仍受宿主的数据政策约束。

<a id="evaluation"></a>

## 验证进展

**237 项自动测试、13 个结构化合成基准**，以及有限的独立上下文试用，
覆盖安装、路由、证据处理和实际交互。它们尚不能证明提高面试通过率或 Offer 率。

<details>
<summary>查看验收记录与已知限制</summary>

| 范围 | 记录 |
| --- | --- |
| 四个核心体验 | [核心体验验收](documentation/EVOLUTION_EVAL.md) |
| 措辞核对、断点续练、隐藏结果复盘 | [细节验收](documentation/REFINEMENT_EVAL.md) |
| 简历源码导出与 PDF 检查边界 | [导出验收](documentation/RESUME_EXPORT_EVAL.md) |
| 投递实验、行动启动、研究外推 | [研究工作流验收](documentation/RESEARCH_EVOLUTION_EVAL.md) |
| 参考库、结构化面试、Offer 核验 | [参考库验收](documentation/CAREER_LIBRARY_EVAL.md) |

既有冻结案例仍有提取、交接和建议泛化等弱点，未全部重测，也未宣称达到原有真实用户试点门槛。
当前招聘、薪资与公司信息仍需新鲜来源，不提供候选人综合分数或录用概率。

[评测协议](documentation/EVAL.md) · [冻结 Holdout](documentation/V023_HOLDOUT_EVAL.md) ·
[体验方案](documentation/EVOLUTION_PLAN.md)

</details>

<details>
<summary>开发、架构与结构化 CLI</summary>

宿主负责理解材料和互动判断；Python 提供有界的结构化辅助、产物与可选记忆。
`route --experience` 只选择参考，不会自动运行对话或生成报告。

```sh
python -m unittest discover -s tests -v
python scripts/validate_skill.py
python scripts/benchmark.py run
python scripts/junshi.py route --mode interview --experience defense
python scripts/junshi.py sources --topic interview
python scripts/junshi.py sources --id R7
```

[Skill 入口](SKILL.md) · [任务指南](references) · [合成案例](cases) · [测试](tests) ·
[架构](documentation/ARCHITECTURE.md) · [提取契约](documentation/CONTEXT_EXTRACTION.md) ·
[决策契约](documentation/DECISION_INTELLIGENCE.md) · [可选快照集成](documentation/INTEGRATION.md) ·
[问题与建议](https://github.com/lavine888/Career-Junshi/issues)

独立的 [v0.3 Host-First 实验](https://github.com/lavine888/Career-Junshi/tree/experiment/v0.3-host-first)
尚未完成，其结果不代表当前版本的架构结论。

</details>

---

[MIT](LICENSE)
