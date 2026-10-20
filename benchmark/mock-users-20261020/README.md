# 五个模拟用户的三轮试用

日期：2026-10-20。测试对象为 [a1eccf8](https://github.com/lavine888/Career-Junshi/commit/a1eccf82a2e5e838441b083cc8191c863e715299)
实际安装后的运行包。这里全部是合成材料，没有真人候选人或真实招聘结果。

| 案例 | 场景 | 原始请求 | 助手答复 |
| --- | --- | --- | --- |
| U01 | 无亮眼指标的应届生：改句子、保留主导权、停止 | [第1轮](inputs/U01/turn-1.md) · [第2轮](inputs/U01/turn-2.md) · [第3轮](inputs/U01/turn-3.md) | [第1轮](responses/U01/turn-1.md) · [第2轮](responses/U01/turn-2.md) · [第3轮](responses/U01/turn-3.md) |
| U02 | 运营转岗：选方向、单次拒信、成果边界 | [第1轮](inputs/U02/turn-1.md) · [第2轮](inputs/U02/turn-2.md) · [第3轮](inputs/U02/turn-3.md) | [第1轮](responses/U02/turn-1.md) · [第2轮](responses/U02/turn-2.md) · [第3轮](responses/U02/turn-3.md) |
| U03 | 明天技术面试：逐题追问、承认不会、诚实过渡 | [第1轮](inputs/U03/turn-1.md) · [第2轮](inputs/U03/turn-2.md) · [第3轮](inputs/U03/turn-3.md) | [第1轮](responses/U03/turn-1.md) · [第2轮](responses/U03/turn-2.md) · [第3轮](responses/U03/turn-3.md) |
| U04 | Offer 选择：接送孩子、真实截止、新条款 | [第1轮](inputs/U04/turn-1.md) · [第2轮](inputs/U04/turn-2.md) · [第3轮](inputs/U04/turn-3.md) | [第1轮](responses/U04/turn-1.md) · [第2轮](responses/U04/turn-2.md) · [第3轮](responses/U04/turn-3.md) |
| U05 | 简历新手：先审草稿、再实际导出、核对文件 | [第1轮](inputs/U05/turn-1.md) · [第2轮](inputs/U05/turn-2.md) · [第3轮](inputs/U05/turn-3.md) | [第1轮](responses/U05/turn-1.md) · [第2轮](responses/U05/turn-2.md) · [第3轮](responses/U05/turn-3.md) |

## 执行与评审

- 五个案例分别使用未继承主聊天的独立 subagent；同一案例在同一上下文继续三轮。
- 用户消息与检查项在生成前固定。生成者只获得当轮用户消息、安装后的 Skill
  和自行选择的相关运行参考；看不到后续消息、检查项、其他案例或旧 example。
- 每一轮完成后才投递下一条已固定消息；没有让同一个代理同时编造用户与助手。
  用户的认可、补充和停止均是剧本，不是实际采纳、执行或留存的观察。
- 全部输出冻结后，另一个新上下文 AI 依据原材料和检查项评审。
  这不是独立真人评审或不同模型盲评；具体模型标识和采样参数未另行暴露。
- U04 第3轮的投递通知额外提醒“不要推断前轮建议已被用户执行”。
  该轮不能独立证明助手会自主避免这种错误；没有重采样或覆盖输出。
- U05 导出在隔离目录实际执行。公开的 [产物副本](artifacts/U05) 也是合成材料；
  具体编译、页数和检查状态应以实际文件及评审为准。

[预先协议](protocol.json) · [生成记录与偏差](generation.json) · [检查项](rubrics) ·
[独立上下文评审](review.json) · [软件检查](software-checks.json)

## 记录完整性与复用

原始日志在隔离运行目录封存；公开副本仅对本机路径作机械替换：运行目录改为
`<RUN_DIR>`，答复及评审引文中的产物链接改为指向公开副本的相对路径。
路径的斜杠形式亦一并处理，JSON 可能重新排版。正文结论没有按评审结果改写。
`access-*.json` 是生成代理的活动记录，不是完整、独立认证的工具执行轨迹。

生成前的原始字节指纹见 [BEFORE_GENERATION_FREEZE.json](BEFORE_GENERATION_FREEZE.json)，
输出原始字节指纹见 [CAPTURE_FREEZE.json](CAPTURE_FREEZE.json)。它们针对封存原件，
路径替换后的公开副本使用单独的 [MANIFEST.json](MANIFEST.json)。指纹只检查完整性，
不能认证模型执行、评审独立性或评分正确性。

运行 `python benchmark/mock-users-20261020/verify.py` 可检查公开副本的指纹、
15 轮答复是否齐全，以及评审引文是否确实存在。脚本不自动判定语义质量。

复用时，新建助手会话、使用对应版本 Skill，按顺序逐轮提供用户消息；
U05 的 `<RUN_DIR>` 须替换为你选定的新隔离目录。生成前不要给出检查项和旧答复。
这只能复用情境，不能保证复现相同的模型采样。

未测试真实用户的完成耗时、采纳、回访或录用效果；没有据这五例推断总体通过率。
