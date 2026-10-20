# 简历导出交付：两个前向试用

日期：2026-10-20。基线 [3e81ec1](https://github.com/lavine888/Career-Junshi/commit/3e81ec1751514d5a79216601ff9ab0c3ff8c19d3)
加本轮导出参考修改；具体参考指纹见[生成前封存](BEFORE_GENERATION_FREEZE.json)。
全部姓名与经历为合成材料。

| 用户 | 请求与认可输入 | 实际答复与产物 |
| --- | --- | --- |
| A：不使用LaTeX，希望有PDF并能继续编辑 | [请求](trials/A/request.md) · [输入](trials/A/approved-input.json) | [答复](trials/A/response.md) · [产物](trials/A/export) |
| B：使用TeXstudio，只要源码、不编译 | [请求](trials/B/request.md) · [输入](trials/B/approved-input.json) | [答复](trials/B/response.md) · [产物](trials/B/export) |

两位生成代理分别从新上下文执行，未提供拟修问题、旧答复或[检查项](trials/checks.json)。
均读取实际安装后的运行资源并调用本地导出器。最终核对由编写修改的主代理完成，
不是独立盲评；具体模型标识与采样参数未单独暴露。

A在额度中断前已保存答复，恢复后原样交付，没有作为新样本重测；见主代理整理的[恢复记录](trials/A/recovery.json)。
[核对结果](review.json)区分编译不可用与未请求编译，均没有将源码交付说成完成PDF验收。

原始记录留在隔离目录，[原件指纹](CAPTURE_FREEZE.json)在公开路径替换前封存。
公开副本仅将本机运行目录改为 `<RUN_DIR>`，回复中的产物链接改为本例相对路径，
JSON可能重新排版；正文结论没有按核对结果改写。复用请求时须将 `<RUN_DIR>` 换成
仓库与Skill安装之外的新隔离目录。[MANIFEST.json](MANIFEST.json)记录公开副本指纹。
access记录为生成代理自报，不是完整认证工具轨迹。指纹也不认证模型执行或语义判断。

本次没有真实用户、PDF版面、Word文档生成或招聘收益验证；纯文本可复制到Word，
不等于已经生成Word文件。
