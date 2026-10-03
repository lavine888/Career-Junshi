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
    if "recommendation" in decision:
        r = decision["recommendation"]
        contents["decision.md"] += "\n最强反对理由：" + r["strongest_counterargument"] + "\n\n重评：" + "；".join(r["reconsider_if"]) + "\n"
    if "direction" in decision:
        d = decision["direction"]
        contents["direction-comparison.md"] = "# 当前岗位主线\n\n" + decision["recommended_move"] + "\n\n" + "\n".join(
            f"## {c['name']}\n\n已有证据：{c['strongest_proof']}\n\n最大缺口：{c['largest_gap']}\n\n成本与可验证性：{c['assessment']['gap_cost']} / {c['market_test']}\n\n一版简历保留：{c['resume_case']}\n\n来源：{' / '.join(c['source_ids'])}\n"
            for c in d["comparison"]) + "\n判断依据是宿主有来源的定性比较，不是市场核验或客观分数。\n"
    if "ownership_defense" in decision:
        p = decision["ownership_defense"]
        lines = ["# Ownership Defense Pack", "", p["safe_claim"], "", p["boundary"], "",
                 "整体项目阶段：" + p["project_stage"], ""]
        lines += ["", "## Reported personal contributions", ""] + ["- " + v for v in p["reported_contributions"]]
        lines += [f"- {c['claim_id']}：主张阶段 {c['claim_stage']}；个人贡献阶段 {c['user_contribution_stage']}" for c in p["contributions"]]
        lines += ["", p["stage_boundary"], "", "## 最相关的追问", ""]
        lines += [f"{i}. {q}" for i, q in enumerate(p["defense_questions"], 1)]
        contents["ownership-defense.md"] = "\n".join(lines) + "\n"
    if "project_mapping" in decision:
        m = decision["project_mapping"]
        contents["decision.md"] += "\n项目映射：" + m["project_id"] + " → " + " / ".join(m["claim_ids"]) + "\n\n岗位侧重：" + "；".join(m["role_emphasis"]) + "\n\n故事待补：" + "；".join(m["gaps"]) + "\n"
    kinds = {a["kind"] for a in decision["actions"]}
    claims = decision["claims"]
    if kinds & {"risk_map", "evidence_audit", "write_material"}:
        lines = ["# Claim / 面试风险图", "", "逐条核对真实来源；风险触发器不是完整的语义事实检查。", ""]
        if not claims:
            supplied = {f["source_type"] for f in decision["facts"]}
            missing = [label for kind, label in (("resume", "简历原文"), ("jd", "JD 原文")) if kind not in supplied]
            lines.append("尚无结构化 Claim。先从已给材料整理项目表述并核实个人贡献，不能填入假经历。")
            if missing:
                lines.append("待提供：" + "、".join(missing) + "。")
        for c in claims:
            safe = decision["ownership_defense"]["safe_claim"] if "ownership_defense" in decision else c["safe_wording"]
            lines.extend([f"## {c['id']}", "", f"原表述：{c['claim']}", "", f"安全表述：{safe}", "",
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
        follow = decision.get("follow_up", {})
        contents["follow-up-draft.md"] = "# 跟进草稿\n\n发送时机：" + follow.get("timing", decision["recommended_move"]) + "\n\n" + draft + "\n\n观察：" + decision["observation_window"] + "\n\n停止：" + decision["stop_condition"] + "\n\n由你核对事实后发送。这里只生成文件，没有发送消息。\n"
    if "offer_comparison" in kinds:
        lines = ["# Offer 比较", "", decision["recommended_move"], "", "主观权重计算仅用于偏好比较，不代表客观公司价值。", "",
                 "| 选项 | 硬约束通过 | 偏好得分 | 已提供维度 |", "| --- | --- | --- | --- |"]
        for row in decision.get("comparison", []):
            def cell(value): return str(value).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {cell(row['name'])} | {row['eligible']} | {row['score'] if row['score'] is not None else '待核实'} | {cell(row.get('ratings', {}))} |")
        if "offer_priorities" in decision:
            lines[4] = "按已陈述目标的定性优先级比较已有维度；没有补造数字权重或综合分数。"
            lines += ["", "## 最可能改变选择的未知（最多三项）", ""]
            for u in decision["decision_unknowns"]:
                lines += ["- " + u["unknown"], "  - 为什么：" + u["why_it_matters"],
                          "  - 核实：" + u["how_to_verify"], "  - 反转：" + u["reversal_condition"]]
            lines += ["", "## 反转条件", ""] + ["- " + v for v in decision["reversal_conditions"]]
        else:
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
