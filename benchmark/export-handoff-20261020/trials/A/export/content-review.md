# 简历交付自查

本次为普通自查，未进行独立审阅。内容仅来自用户已确认的合成输入，没有外部核验，没有修改正文或数字。

| Claim ID | 主张与来源定位 | 证据状态、贡献与限制 |
| --- | --- | --- |
| C1 | approved-input.json /name：沈简（合成测试） | SELF_REPORTED；用户明确标为合成姓名。 |
| C2 | approved-input.json /sections/0/entries/0；S1：云桥学院（虚构），信息管理本科，2022.09—2026.06 | SELF_REPORTED；虚构教育经历；未独立核验。 |
| C3 | approved-input.json /sections/1/entries/0；S2：借阅周报课程项目，数据整理与脚本，2026.03—2026.05；使用SQL整理课程样例借阅记录，并用Python生成每周CSV报表。 | SELF_REPORTED；个人课程项目自述，作者范围未独立核验；没有真实上线或收益指标，不扩大为生产成果。 |

内容核对：原始 JSON 所有字段值保留，导出器仅补入空 target_role；纯文本逐行与输入重建结果一致；姓名、日期、项目句子均在纯文本与 LaTeX 源码中完整保留。没有删减内容，没有加入职位或成果。

编译：实际调用 --compile，返回 SOURCE_ONLY；PATH 中未找到 xelatex。未安装依赖，未上传材料。没有 PDF，1 页仅为用户目标；实际页数、编译警告、PDF 文字层和逐页视觉检查均未完成。

后续编辑：优先打开 resume.txt，可复制到 Word 或其他编辑器；它是纯文本，不是 Word 文档。resume-data.json 保留结构化输入与来源，resume.tex 保留 LaTeX 排版源码。以后若本机具备 XeLaTeX，可使用原安装目录的导出命令，选择另一个新的输出目录并加 --compile；应对新 PDF 重新做文字与视觉检查。
