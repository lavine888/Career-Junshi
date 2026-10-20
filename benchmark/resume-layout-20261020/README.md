# 简历排版压力测试

这些输入全部为虚构人物与合成经历，不能作为真实候选人简历。

| 输入 | 验收预期 | 压力点 |
| --- | --- | --- |
| `dense-zh` | 1 页；机器检查全部通过 | 中文双实习、多项目，接近满页 |
| `two-page-zh` | 恰好 2 页；机器检查全部通过 | 长项目标题、长日期、自然跨页，无手动分页 |
| `links-mixed` | 1 页；机器检查全部通过 | 中英混排、`%` / `&` / `_`、长 HTTPS 联系方式 |
| `overflow` | 编译成功；超过 1 页；`page_check=FAILED`、`PDF_CHECKS_FAILED` | 明确超页负例，生成的 PDF 必须拒绝交付 |

从仓库根目录执行，输出必须是 Git 仓库外的全新目录：

```powershell
python benchmark/resume-layout-20261020/run.py --output-root D:/private/resume-layout-run --tool-bin D:/Tools/Poppler/poppler-26.09.0/Library/bin --tool-bin D:/Tools/MiKTeX/miktex/bin/x64 --render
```

`--tool-bin` 可重复指定，顺序即工具查找优先级；只对当前进程生效，不修改系统环境或安装依赖。在已经配置好工具的环境中可以省略。运行前需要 XeLaTeX、中文 CTEX/Fandol 与模板宏包、`pdfinfo`、`pdftotext`；`--render` 另需 `pdftoppm`。

脚本保留每例导出文件和 `verification.json`，写入汇总 `summary.json`。`--render` 将每一页渲染为 PNG；渲染不是视觉通过。三个正例机器通过后仍为 `AWAITING_VISUAL_REVIEW`，必须逐页检查重叠、截断、跨页断点和阅读顺序，并单独记录观察。负例的期望通过只表示拒绝机制奏效，不能将其 PDF 标成合格简历。

此套件会实际启动本机编译器，并非默认单元测试的一部分。测试结果只证明这些合成输入的机械与视觉表现，不证明经历真实性、ATS 认证或求职成效。

本轮已实跑的[机器汇总](summary.json)、[宿主逐页观察](visual-review.json)、[链接目标](link-annotations.txt)和[文件哈希](manifest.json)可直接查验。三个正例分别为 1／2／1 页；超页负例为 4 页并被拒绝。公开 artifacts 仅含合成材料，机器报告的视觉状态保持原样；完整说明见[本轮验收](../../documentation/RESUME_ITERATION_EVAL.md)。
