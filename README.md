# 求职军师 · Career Junshi

不只帮你改简历，更帮你看清机会、守住面试、理解反馈、决定下一步。

“这是我的简历和 JD，明天面试，我今晚准备什么？”

“HR 三天没回，要不要催？”

“两个 Offer 怎么选？”

“这段项目到底能不能写‘主导’？”

“我不知道自己应该投什么。”

求职军师先判断：**现在真正限制你的是什么？** 然后给一个明确首选、
1–3 个行动、观察窗口和停止 / 转向条件。证据薄就补证或降低表述；
拿到真实反馈后，修正判断。

[English](README_EN.md) · [三个合成示例](cases) · [MVP 交付报告](documentation/MVP_REPORT.md)

## 四个核心能力

| 能力 | 对你意味着什么 |
| --- | --- |
| Evidence First | 不把原型写成生产，不把团队成果写成独立完成 |
| Career Memory | 同意后只在本机保存有用的压缩信息，可查看、暂停、撤销、删除 |
| Decision Loop | 记住当时为什么这样建议，把真实结果与原预测分开复盘 |
| Actionable Next Move | 先给今晚 / 现在值得做的事，Codex 能做的产出材料 |

第一版覆盖：岗位决策、定位与简历、面试防守、招聘跟进与拒信、Offer 比较。
内部参考 Career Alpha 方法，用户不必学八个命令。

## 安装后直接提问

把这段话发给支持本地 Skill 的助手：

```text
请将 https://github.com/lavine888/Career-Junshi 下载并安装为 career-junshi 本地 Skill。
先检查已有同名安装，不要覆盖；安装后验证运行文件。不要替我启用长期记忆。
```

也可手动安装。Python 3.10+，只用标准库：

```sh
git clone https://github.com/lavine888/Career-Junshi.git
cd Career-Junshi
python scripts/validate_skill.py
```

安装到宿主实际扫描的 Skill 目录。按 [OpenAI 官方文档](https://learn.chatgpt.com/docs/build-skills)，
当前 Codex 用户级目录是 `~/.agents/skills`；配置了其他目录的宿主按实际配置选择。

macOS / Linux：

```sh
python scripts/install_skill.py --target "$HOME/.agents/skills/career-junshi"
python "$HOME/.agents/skills/career-junshi/scripts/validate_skill.py" --runtime-only
```

Windows PowerShell：

```powershell
python scripts/install_skill.py --target "$env:USERPROFILE\.agents\skills\career-junshi"
python "$env:USERPROFILE\.agents\skills\career-junshi\scripts\validate_skill.py" --runtime-only
```

安装器复制运行所需文件，带上 MIT 与上游声明，不带 `.git`、测试、案例或数据库；
已有目标会报错并保留。新聊天中可说：

```text
请使用 $career-junshi。这是我的简历和 JD，明天下午一面。我今晚最该准备什么？
```

也可自然语言触发匹配。首次优先提取已有资料，只补问会改变建议的信息。
没有资料时，说明当前阶段、目标、三个经历、眼前问题和截止时间即可；不必填齐。
自然语言能力由宿主模型提供，项目不含自建模型服务，也不要求 API key。

## 它会怎样回答

**明天面试，简历声称 production、实际是团队原型：**

> 今晚先降低没有证据的 production 与 30% 表述，守住你真实做过的评测和失败分类。
> 再练一条五层追问和 90 秒真实故事；不要临时开新项目。

**HR 已过三个工作日，未承诺日期、尚未跟进：**

> 可以礼貌跟进一次。未回复不能说明挂了。
> 再观察约三个工作日，继续无回复就降低投入，不继续高频追问。

**两个 Offer：**

> 先确认目标和硬约束，才给首选。在合成示例里，用户重视学习与 ownership，
> 因此选 A；改成优先薪酬则选 B。

完整输入、CLI 实际输出、当前构建会话的 Skill 示范与产物：
[面试](cases/interview)、[跟进](cases/follow-up)、[Offer](cases/offer)。
**全部为合成案例，测试成功不代表真实求职结果已验证。**

## 检查可重复的脚本行为

以下输入是结构化 JSON；不是把任意简历 / 聊天原文直接交给 CLI。
宿主先理解材料和来源，再用助手检查边界：

```sh
python scripts/junshi.py route --mode interview
python scripts/junshi.py audit --input cases/interview/input.json
python scripts/junshi.py decide --input cases/interview/input.json --now 2026-10-03T12:00:00+08:00
python scripts/junshi.py decide --input cases/follow-up/input.json --now 2026-10-03T12:00:00+08:00
python scripts/junshi.py decide --input cases/offer/input.json --now 2026-10-03T12:00:00+08:00
```

加 `--format json` 查看内部字段；加 `--artifacts-dir <新的私有输出目录>` 生成真实
风险图、项目追问、HR 草稿或 Offer 比较文件。已有文件不会被覆盖。
CLI 不抓取岗位、验证远端来源、发送消息或自动做职业决定。

## 长期记忆默认关闭

在安装后的 Skill 根目录运行 `python scripts/memory_store.py status`。
你明确同意压缩信息在本机持久保存后，才执行 `consent --yes`。之后支持
recall / update / view / pause / revoke / delete；暂停禁自动读写，撤销需要重新同意，
删除清除记录并撤销同意。默认存用户数据目录，绝不存安装目录。
完整简历、JD、邮件与聊天默认不保存，MVP 仅接受压缩字段。
Decision 与 Outcome 关联，结果、观察、解释与因果未知分别保存。

详见 [记忆命令](documentation/MEMORY.md)。数据库未加密，删除是逻辑删除，
不清除外部备份。无需 LavineOS；可选显式快照仅有
[接口契约](documentation/INTEGRATION.md)，尚无同步。

## 验证与边界

```sh
python -m unittest discover -s tests -v
python scripts/validate_skill.py
```

回归覆盖十个指定情境，以及计划、团队、Demo、源码作者、回测、奖项、HR 沉默、
因果推断、主观权重、记忆并发、Decision → Outcome 和安装后独立 CLI。
运行证据见 [MVP 报告](documentation/MVP_REPORT.md)。

VERIFIED 需要针对精确主张的真实核查。JSON 核查记录是操作者声明，脚本无法
认证虚构记录；文本触发器不能替代语义审计。当前公司、岗位、市场和政策需要新鲜来源。
真实投递、消息发送、谈薪、面试与接受 / 拒绝 Offer 由你执行。

## 来源与开源协议

Inspired by / adapted from [Goutoujunshi](https://github.com/shengjidaguai-china/goutoujunshi)：
轻量内核、参考路由、本地记忆哲学、先给行动、观察与停止线。
Conceptually informed by [Career Alpha](https://github.com/lavine888/career-alpha)：
Evidence First、Claim–Evidence Ledger、面试防守与市场反馈。

Career Junshi 新增职业局势模型、统一决策、职业证据边界、决策与结果记忆、
可执行材料及回归。没有复制恋爱内容，不依赖私人 Vault。
采用 [MIT](LICENSE)，上游许可完整保留，详见 [Attribution](documentation/ATTRIBUTION.md)。
