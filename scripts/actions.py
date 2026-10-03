"""Validate action ownership and produce reviewable local materials."""
from __future__ import annotations

from pathlib import Path

from scripts.models import ContractError, choices, items, obj, text

HUMAN = {"apply", "practice", "send_message", "confirm_terms", "career_decision", "negotiate", "accept_offer", "reject_offer"}
CODEX = {"evidence_audit", "write_material", "risk_map", "question_ladder", "mother_story",
         "jd_map", "offer_comparison", "draft_message", "feedback_review", "pipeline_review"}


def validate_actions(value: list) -> list:
    actions = items(value, "actions", 3)
    if not actions:
        raise ContractError("A decision must have at least one action")
    for raw in actions:
        a = obj(raw, "action")
        if set(a) != {"kind", "description", "execution_mode", "artifact", "status"}:
            raise ContractError("invalid action fields")
        kind = choices(a["kind"], HUMAN | CODEX, "action kind")
        expected = "human" if kind in HUMAN else "codex"
        if a["execution_mode"] != expected:
            raise ContractError(f"{kind} must be executed by {expected}")
        if a["status"] != "PROPOSED":
            raise ContractError("Planning cannot mark an action completed")
        text(a["description"], "action description", 1000)
        text(a["artifact"], "artifact", 100, empty=True)
    return actions


def artifact_contents(decision: dict) -> dict[str, str]:
    validate_actions(decision["actions"])
    contents = {"decision.md": "# 当前判断\n\n" + decision["recommended_move"] + "\n\n"
                + "来源边界：根据提供的结构化材料生成，脚本没有独立核查外部来源。\n\n"
                + f"观察：{decision['observation_window']}\n\n停止：{decision['stop_condition']}\n\n转向：{decision['pivot_condition']}\n"}
    kinds = {a["kind"] for a in decision["actions"]}
    claims = decision["claims"]
    if kinds & {"risk_map", "evidence_audit", "write_material"}:
        lines = ["# Claim / 面试风险图", "", "逐条核对真实来源；风险触发器不是完整的语义事实检查。", ""]
        if not claims:
            lines.append("尚无 Claim。需要实际简历、JD 和个人贡献，不能填入假经历。")
        for c in claims:
            lines.extend([f"## {c['id']}", "", f"原表述：{c['claim']}", "", f"安全表述：{c['safe_wording']}", "",
                          f"个人贡献：{c['ownership']['contribution'] or '未知'}；ownership：{c['ownership']['scope']}", "",
                          "风险：" + "；".join(c["risk"] or ["仍需人工检验五层追问"]), "",
                          "来源：" + "；".join(e["source"] for e in c["evidence"]) if c["evidence"] else "来源：仅用户陈述 / 未给证据", ""])
        contents["claim-risk-map.md"] = "\n".join(lines).rstrip() + "\n"
    if "question_ladder" in kinds:
        lines = ["# 五层项目防守", "", "只填写能由真实经历支持的答案；未验证部分保持未知。", ""]
        target = next((c for c in claims if c["id"] == decision["highest_risk"]), claims[0] if claims else None)
        lines.extend(["目标：" + (target["claim"] if target else "待提供实际项目 Claim"), "",
                      "1. 你具体实现了哪一部分？展示真实文件 / 产物，划清团队与 AI 工具贡献。",
                      "2. 为什么采用该架构？约束与自己做过的关键决策是什么？",
                      "3. 比较过哪些替代方案？什么条件下会改选它们？",
                      "4. 如何测量结果？基线、样本、失败分类与误差是什么？",
                      "5. 什么失败了？哪里不是你做的？下一次会怎样改？", "",
                      "回答证据槽：已确认事实 / 来源 / 个人动作 / 未知。脚本不生成虚构技术答案。"])
        contents["project-defense.md"] = "\n".join(lines) + "\n"
    if "draft_message" in kinds:
        draft = next(a["description"] for a in decision["actions"] if a["kind"] == "draft_message")
        contents["follow-up-draft.md"] = "# 跟进草稿\n\n" + draft + "\n\n由你核对事实后发送。这里只生成文件，没有发送消息。\n"
    if "offer_comparison" in kinds:
        lines = ["# Offer 比较", "", decision["recommended_move"], "", "主观权重计算仅用于偏好比较，不代表客观公司价值。", "",
                 "| 选项 | 硬约束通过 | 偏好得分 | 已提供维度 |", "| --- | --- | --- | --- |"]
        for row in decision.get("comparison", []):
            def cell(value): return str(value).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {cell(row['name'])} | {row['eligible']} | {row['score'] if row['score'] is not None else '待核实'} | {cell(row.get('ratings', {}))} |")
        lines.extend(["", "需要确认："] + ["- " + v["text"] for v in decision["unknowns"]])
        contents["offer-comparison.md"] = "\n".join(lines) + "\n"
    if "jd_map" in kinds:
        contents["role-hypotheses.md"] = "# 岗位假设对照\n\n" + decision["recommended_move"] + "\n\n需用实际的五份当前 JD，逐一记录职责、来源和日期、对应的个人证据、缺口与补齐成本。\n资料未给齐，不能声称已核查市场或匹配完成。\n"
    return contents


def write_artifacts(decision: dict, directory: str | Path) -> list[str]:
    contents = artifact_contents(decision)
    target = Path(directory).expanduser().resolve()
    if any((target / name).exists() for name in contents):
        raise ContractError("Artifact already exists; use a new output directory to preserve existing work")
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, content in contents.items():
        path = target / name
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        paths.append(str(path))
    return paths
