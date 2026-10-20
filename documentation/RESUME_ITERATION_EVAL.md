# 简历改写与导出迭代验收

日期：2026-10-20。基线为 [062b049](https://github.com/lavine888/Career-Junshi/commit/062b04955e5afdaf20dc38c42b5dc887464a9f3f)。
本轮全部使用公开合成材料；尚未收到用户本人的简历，不能据此宣称已经验证真人改写效果。

## 已实现

- 共用简历参考要求展示重要原句、改写、理由和待确认事实，沿用来源定位；普通润色不反复等待确认。
- 岗位取舍解释前置、压缩与省略原因。JD 提供职责，不提供候选人能力证据；无 JD 时按已给方向继续。
- 导出器在文字覆盖外增加单调阅读顺序和重复片段检查，分别报告 `text_order_check` 与 `text_occurrence_check`。重复缺失、额外复制和乱序会使 `text_check` 失败；乱序无法可靠定位片段时，计数可为 `UNAVAILABLE`，整体仍失败。
- 新增显式 `resume-doctor`：报告实际工具路径与版本，编译中英文小样并检查其 PDF；临时小样随后删除，不读取候选人文件。MiKTeX 探测编译传入 `-disable-installer`，不靠用户的全局设置来保证不自动下载依赖。
- 固定模板保留 11pt 正文字号与 A4 单栏，日期单独右对齐，联系方式合并并允许换行；提供的邮箱与 HTTP/HTTPS 地址可点击。标题和第一条经历保持在一起，其余条目可自然跨页。
- 中英文 README 提供对照说明、自检命令、已编译样例和本报告入口。原有 JSON 输入 schema、`resume-export` 参数及源码导出文件集合保持兼容。

## 实际内容试用

[原始请求、固定验收项、两次答复及评审](../benchmark/resume-content-20261020/README.md)。
两个助手均从新上下文开始，仅拿到请求、Skill 和自行选择的最多三份参考，没有看到 rubric 或拟修问题。

首次请求只加载通用 `resume.md`，没有触达当时仅在导出参考中的对照指导；答复有可用安全草稿，但缺少准确原句与改写、未决事实的清楚对应。因此将共用指导放入 `resume.md`，由导出参考链接复用。
相同请求在另一个新上下文中复测，实际答复逐条引用准确原句、给改写位置、理由与已解决的未知项；保留个人产品贡献、队友实现和样例数据边界，删除没有测量依据的 40%／20%，没有等待用户逐句确认才交付内容。

这是每版一次的合成试用和主代理语义评审，不是受控因果实验；模型的具体版本标识与采样参数未单独暴露。不能推断长期稳定性或真人采纳。

## 真实 XeLaTeX 排版结果

环境：MiKTeX-XeTeX 4.18（MiKTeX 26.5），独立 Poppler 26.09.0；CTEX/Fandol、geometry、hyperref 及依赖已安装。
使用[四份输入与运行器](../benchmark/resume-layout-20261020/README.md)，实际编译、提取并渲染全部 8 页：

| 合成场景 | 实际页数 | 机器检查 | 页面观察与交付 |
| --- | --- | --- | --- |
| 双实习、多项目中文内容 | 1 | 页数、覆盖、顺序、重复、日志通过 | 接近满页，无裁切或重叠，日期和标题可读；[PDF](../benchmark/resume-layout-20261020/artifacts/dense-zh/resume.pdf) |
| 长项目名、长日期与自然跨页 | 2 | 上述检查通过 | 标题与首条经历保持在一起，后续条目自然跨页；[PDF](../benchmark/resume-layout-20261020/artifacts/two-page-zh/resume.pdf) |
| 中英、特殊字符与长链接 | 1 | 上述检查通过 | 联系方式换行，文字层保留原字符，邮箱及 URL 注释目标已核对；[PDF](../benchmark/resume-layout-20261020/artifacts/links-mixed/resume.pdf) |
| 一页上限的超量负例 | 4 | `page_check=FAILED`、`PDF_CHECKS_FAILED`，其余检查通过 | 按页数拒绝；负例验收通过只说明拒绝机制生效，不是合格简历 |

[机器汇总](../benchmark/resume-layout-20261020/summary.json) ·
[独立的宿主视觉记录](../benchmark/resume-layout-20261020/visual-review.json) ·
[PDF 链接注释](../benchmark/resume-layout-20261020/link-annotations.txt) ·
[源文件与产物哈希](../benchmark/resume-layout-20261020/manifest.json)。

每份 `verification.json` 保留机器产生的 `visual_review=REQUIRED`，不把程序状态改成视觉通过。
宿主检查单独记录：首次查看全部八页；最终正例四页重新查看，负例四页渲染图片与此前已查看版本逐字节相同。
公开 PDF、源码、PNG 原样复制；仅替换验收中的本机输出路径与自检工具路径，提取文本统一为 UTF-8/LF。
编译原件和先前失败运行保留在 Git 外，未覆盖历史记录。

## 环境自检的实际失败与恢复

只改变工具查找顺序，分别实际运行相同 `resume-doctor`：

| 环境 | 实际结果 | 依据 |
| --- | --- | --- |
| 本机 MiKTeX 自带 PDF 工具优先 | `NOT_READY`，退出码 2 | 中文编译成功，但提取器报告缺少 Adobe-GB1 语言映射，中文检查失败；[记录](../benchmark/resume-layout-20261020/doctor-miktex-first.json) |
| 完整独立 Poppler 优先 | `READY`，退出码 0 | 中英文小样的编译、页数、文字顺序、出现次数与日志全部通过；[记录](../benchmark/resume-layout-20261020/doctor-poppler-first.json) |

这是本机版本组合的观察，不是对所有 MiKTeX 安装的结论。自检可以提前暴露这种同名工具冲突；它不安装宏包、不修改系统设置，也不代替真实简历逐页检查。

## 修正的边界与验证

自查复现并修复了两项实现问题：去空白后跨字段拼成的文字不应算额外重复；用于显示文字的波浪号转义不应改变 PDF 超链接目标。
现已分别建立聚焦回归，并对真实 PDF 注释确认 `%7E`、下划线、查询参数和锚点的目标语义保留。

- 完整 `python -m unittest discover -s tests -v`：251 项通过。
- `python scripts/validate_skill.py` 与 Skill Creator 基础校验通过。
- 安装后的缺引擎自检、源码导出及原有 CLI 失败退出行为有回归覆盖。
- 四个真实压力场景与两种环境自检不由模拟替代，且不并入无需 TeX 的默认单元测试。

这些检查验证有限合成输入的改写边界、文件完整性和版式，不认证经历真实性、通用 ATS 兼容性或录用效果。尚未覆盖所有字体、操作系统、简历内容及第三方解析器。
