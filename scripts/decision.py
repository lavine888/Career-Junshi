"""Conservative offline decisions for structured scenarios, not an LLM or job feed."""
from __future__ import annotations

from datetime import datetime, timezone

from scripts.models import ContractError, audit_claim, claim_references, choices, items, number, obj, text, timestamp
from scripts.router import route
from scripts.method_adapter import method_plan
from scripts.actions import validate_actions
from scripts.context import SOURCE_TYPES
from scripts.intelligence import enrich

DIMENSIONS = {"learning", "ownership", "manager", "team", "career_direction", "technical_depth",
              "brand", "optionality", "compensation", "location", "lifestyle", "downside"}


def action(kind: str, description: str, mode: str, artifact: str = "") -> dict:
    return {"kind": kind, "description": description, "execution_mode": mode,
            "artifact": artifact, "status": "PROPOSED"}


def normalize_situation(value: dict, *, now: datetime | None = None) -> dict:
    s = obj(value, "situation")
    allowed = {"mode", "summary", "goal", "facts", "inferences", "unknowns", "claims", "deadline", "job", "recruiting", "offer", "metadata", "predictions", "project_story", "career_hypothesis", "claim_refs"}
    if set(s) - allowed:
        raise ContractError(f"unknown situation fields: {sorted(set(s) - allowed)}")
    mode = choices(s.get("mode"), {"job", "positioning", "interview", "recruiting", "offer"}, "mode")
    facts = []
    for f in items(s.get("facts", []), "facts", 30):
        f = obj(f, "fact")
        if set(f) - {"text", "source", "source_type", "id", "source_id", "source_span", "source_locator", "epistemic", "confidence", "kind", "modality", "freshness"}:
            raise ContractError("unknown fact fields")
        if f.get("epistemic", "FACT") != "FACT":
            raise ContractError("fact must have FACT epistemic status")
        if f.get("kind") == "feeling" or f.get("confidence") in {"interpretation", "unknown"}:
            raise ContractError("interpretation or feeling cannot enter facts")
        facts.append({"label": "FACT", "text": text(f.get("text"), "fact", 400),
                      "source": text(f.get("source"), "fact source", 240),
                      "source_type": choices(f.get("source_type", "user_report"), SOURCE_TYPES, "source_type"),
                      **{k: f[k] for k in ("id", "source_id", "source_span", "source_locator", "epistemic", "confidence", "kind", "modality", "freshness") if k in f}})
    inferences = []
    for v in items(s.get("inferences", []), "inferences"):
        if isinstance(v, dict):
            if v.get("epistemic") != "INFERENCE":
                raise ContractError("structured inference must have INFERENCE status")
            inferences.append({**v, "label": "INFERENCE", "text": text(v.get("text"), "inference", 400)})
        else:
            inferences.append({"label": "INFERENCE", "text": text(v, "inference", 400)})
    unknowns = [text(v, "unknown", 240) for v in items(s.get("unknowns", []), "unknowns")]
    if not facts:
        unknowns.append("尚未提供可追溯的局势事实")
    claims = [audit_claim(c) for c in items(s.get("claims", []), "claims", 20)]
    if len({c["id"] for c in claims}) != len(claims):
        raise ContractError("claim IDs must be unique")
    for c in claims:
        if c["risk"]:
            unknowns.append(f"{c['id']} 的强表述与个人贡献仍需补证")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ContractError("now must have a timezone")
    urgency = {"deadline": None, "hours_remaining": None, "within_72h": False, "overdue": False}
    if s.get("deadline"):
        due = timestamp(s["deadline"], "deadline")
        hours = (datetime.fromisoformat(due.replace("Z", "+00:00")) - now).total_seconds() / 3600
        urgency = {"deadline": due, "hours_remaining": round(hours, 2), "within_72h": 0 <= hours <= 72, "overdue": hours < 0}
    return {"mode": mode, "summary": text(s.get("summary"), "summary", 600),
            "goal": text(s.get("goal", ""), "goal", 400, empty=True), "facts": facts,
            "inferences": inferences, "unknowns": list(dict.fromkeys(unknowns)), "claims": claims,
            "urgency": urgency}


def recruiting_plan(value: dict, normalized: dict) -> dict:
    r = obj(value, "recruiting")
    if set(r) - {"status", "working_days", "promised_date", "promised_date_passed", "followups", "no_contact", "feedback"}:
        raise ContractError("unknown recruiting fields")
    status = choices(r.get("status", "waiting"), {"waiting", "rejected", "passed", "offer", "freeze"}, "recruiting status")
    days = r.get("working_days")
    if days is not None:
        number(days, "working_days", 0, 365)
    followups = r.get("followups", 0)
    number(followups, "followups", 0, 20)
    if int(followups) != followups:
        raise ContractError("followups must be an integer")
    for key in ("no_contact", "promised_date_passed"):
        if key in r and not isinstance(r[key], bool):
            raise ContractError(f"{key} must be boolean")
    feedback = text(r.get("feedback", ""), "feedback", 400, empty=True)
    promised = text(r.get("promised_date", ""), "promised_date", 100, empty=True)
    unknowns = normalized["unknowns"]
    inferences = normalized["inferences"]
    if status == "waiting":
        unknowns.extend(["最终评价与候选人排序", "招聘名额与内部审批状态"])
        inferences.append({"label": "INFERENCE", "text": "可能是排期、审批、比较或优先级变化；沉默不足以确定结果"})
    else:
        unknowns.append("本次结果的完整原因与策略因果效果")
    draft = "您好，想确认一下本次面试的后续进度。如需我补充材料，我可以配合。谢谢。"
    window = "按实际承诺日期；未约定时约 3 个工作日（可调整的经验默认，非承诺）"
    if r.get("no_contact"):
        recommendation = "停止联系该招聘者，继续其他机会。"
        acts = [action("pipeline_review", "记录对方明确的联系边界，更新机会投入", "codex", "机会记录"),
                action("apply", "继续其他岗位投递", "human")]
    elif status == "rejected":
        recommendation = "结束本次机会；针对明确反馈做一个小修正，再用下一批同类机会验证。" if feedback else "结束本次机会；拒信原因未知，先复盘事实，不因此否定整个方向。"
        inferences.append({"label": "INFERENCE", "text": "单次反馈只限定本次机会，不支持普遍结论"})
        acts = [action("feedback_review", "记录拒信原文、来源与未知原因", "codex", "反馈卡"),
                action("question_ladder", "针对明确技术反馈练习一条真实项目追问" if feedback else "整理本次被追问最深的三个问题", "codex", "五层追问"),
                action("apply", "继续一小批可比岗位，收集实际反馈", "human")]
        window = "下一周或下 5 个可比机会"
    elif status in {"passed", "offer"}:
        recommendation = "推进下一阶段，同时记录本次追問与结果；通过不证明准备策略导致成功。"
        inferences.append({"label": "INFERENCE", "text": "准备内容可能相关，但通过面试不是策略的因果证明"})
        acts = [action("feedback_review", "分开记录通过结果、被问内容、个人解释与未知原因", "codex", "结果卡"),
                action("confirm_terms", "向招聘方确认下一轮或书面 Offer 信息", "human")]
    elif status == "freeze":
        recommendation = "降低该机会投入，继续其他机会；冻结招聘不等于你的能力不匹配。"
        acts = [action("pipeline_review", "记录招聘方报告的冻结与来源", "codex", "机会记录"),
                action("apply", "继续其他岗位", "human")]
    elif followups >= 1:
        recommendation = "先停止继续催；按上次跟进后的观察窗口等待，同时继续其他机会。"
        acts = [action("pipeline_review", "记录最后跟进时间和观察窗口", "codex", "机会记录"),
                action("apply", "继续其他机会，窗口过后降低此机会投入", "human")]
    elif promised and not r.get("promised_date_passed", False):
        recommendation = f"先等到招聘方承诺日期（{promised}），再根据实际截止时间决定跟进。"
        acts = [action("pipeline_review", "记录承诺日期和真实紧迫约束", "codex", "机会记录")]
    elif (promised and r.get("promised_date_passed")) or (days is not None and days >= 3):
        recommendation = "可以礼貌跟进一次；现在不能判断已经被拒。"
        acts = [action("draft_message", draft, "codex", "可发送的跟进草稿"),
                action("send_message", "核对草稿与事实后，由你发送一次", "human")]
    else:
        recommendation = "先等到约定日期或确认已过约 3 个工作日，再礼貌跟进一次；不能把沉默当拒绝。"
        unknowns.append("日历天 / 工作日、承诺日期及真实截止时间")
        acts = [action("pipeline_review", "核对最后联系日期、工作日与承诺时间", "codex", "跟进时间计划")]
    return {"bottleneck": "Timing" if status == "waiting" else "Market" if status == "freeze" else "Interview",
            "recommended_move": recommendation, "why": ["以可见流程与明确反馈为依据，不猜招聘者内心", "停止高频追问，保留其他机会"],
            "actions": acts, "observation_window": window,
            "stop_condition": "明确拒绝 / 要求不联系时停止；一次跟进后再约 3 个工作日无回复，降低投入",
            "pivot_condition": "真实截止时间变化即调整；同一缺口在 5–10 个可比机会反复出现，再 REFINE / PIVOT",
            "application_status": status, "draft": draft if any(a["kind"] == "draft_message" for a in acts) else None}


def offer_plan(value: dict, normalized: dict) -> dict:
    offer = obj(value, "offer")
    normalized["inferences"].append({"label": "INFERENCE", "text": "用户提供的偏好评分可提示当前选择，但不保证入职后的真实体验"})
    if set(offer) - {"weights", "constraints", "options"}:
        raise ContractError("unknown offer fields")
    options = items(offer.get("options", []), "options", 5)
    weights = obj(offer.get("weights", {}), "weights")
    if set(weights) - DIMENSIONS:
        raise ContractError("unknown offer dimension")
    weights = {k: number(v, f"weight:{k}", 0, 100) for k, v in weights.items()}
    constraints = [text(c, "constraint", 240) for c in items(offer.get("constraints", []), "constraints", 10)]
    scores = []
    missing = []
    names = set()
    for raw in options:
        raw = obj(raw, "offer option")
        if set(raw) - {"name", "constraint_status", "ratings"}:
            raise ContractError("unknown offer option fields")
        name = text(raw.get("name"), "offer name", 120)
        if name in names:
            raise ContractError("offer names must be unique")
        names.add(name)
        status = choices(raw.get("constraint_status", "unknown"), {"pass", "fail", "unknown"}, "constraint_status")
        ratings = obj(raw.get("ratings", {}), "ratings")
        if set(ratings) - DIMENSIONS:
            raise ContractError("unknown rating dimension")
        ratings = {k: number(v, f"rating:{k}", 0, 5) for k, v in ratings.items()}
        if status == "fail":
            scores.append({"name": name, "eligible": False, "score": None, "reason": "违反用户硬约束"})
            continue
        gaps = [k for k, v in weights.items() if v > 0 and k not in ratings]
        if status == "unknown" or gaps:
            missing.append(f"{name}: {', '.join(gaps) if gaps else '硬约束是否满足'}")
        total = sum(weights.values())
        score = sum(weights[k] * ratings[k] for k in weights if k in ratings) / total if total and not gaps and status == "pass" else None
        scores.append({"name": name, "eligible": status == "pass", "score": round(score, 3) if score is not None else None,
                       "ratings": ratings, "reason": "用户主观偏好的加权比较，非公司客观质量"})
    enough = bool(normalized["goal"] and "constraints" in offer and sum(weights.values()) > 0 and len(options) >= 2 and not missing)
    ranked = sorted([s for s in scores if s["eligible"] and s["score"] is not None], key=lambda x: x["score"], reverse=True)
    if not enough:
        recommendation = "先确认你的目标、硬约束和缺失的关键 Offer 条件，再选；现在先不接受任何一方。"
        normalized["unknowns"].extend(missing + ["足以改变选择的目标、硬约束或用户权重仍未确认"])
    elif not ranked:
        recommendation = "目前没有满足硬约束的选项，先确认条件或寻找替代，暂不接受。"
    elif len(ranked) > 1 and ranked[0]["score"] - ranked[1]["score"] <= 0.25:
        recommendation = f"{ranked[0]['name']} 与 {ranked[1]['name']} 接近；先核实最能改变选择的经理、ownership 与团队信息，再决定。"
        normalized["unknowns"].append("接近分数下的权重敏感性与关键条件是否真实")
    else:
        recommendation = f"按你提供的目标、权重和已确认约束，首选 {ranked[0]['name']}；接受前核对书面条款与关键团队信息。"
    return {"bottleneck": "Direction", "recommended_move": recommendation,
            "why": ["目标与硬约束优先于公司品牌", "评分仅计算用户提供的偏好；未知不补平均分"],
            "actions": [action("offer_comparison", "整理确认条件、未知与偏好敏感点", "codex", "Offer 比较表"),
                        action("confirm_terms", "确认经理、团队、ownership、书面薪酬、地点与截止时间", "human"),
                        action("career_decision", "关键未知确认后由你接受或拒绝", "human")],
            "observation_window": "最早的真实 Offer 截止时间之前",
            "stop_condition": "任一硬约束不满足则停止接受该选项；目标未明确先暂停排名",
            "pivot_condition": "确认信息或权重变化足以改变首选时重新比较",
            "comparison": scores, "constraints": constraints}


def decide(value: dict, *, now: datetime | None = None, history: list | None = None) -> dict:
    n = normalize_situation(value, now=now)
    mode = n["mode"]
    claims = sorted(n["claims"], key=lambda c: (len(c["risk"]), c["confidence"] in {"PLANNED", "SELF_REPORTED"}), reverse=True)
    riskiest = claims[0] if claims else None
    if mode == "recruiting":
        plan = recruiting_plan(value.get("recruiting", {}), n)
    elif mode == "offer":
        plan = offer_plan(value.get("offer", {}), n)
    elif mode == "interview":
        target = f"{riskiest['id']}：{riskiest['claim']}" if riskiest else "简历上最强、证据最薄的项目表述（资料尚未给齐）"
        n["inferences"].append({"label": "INFERENCE", "text": "强 Claim 的证据与个人贡献缺口可能成为追问风险；不是已知面试题"})
        if not claims:
            n["unknowns"].append("简历 / JD 原文及可核实的个人贡献")
        plan = {"bottleneck": "Evidence" if riskiest and riskiest["risk"] else "Interview",
                "recommended_move": f"先降低 {riskiest['id']} 的缺证强表述，按真实阶段与个人贡献练五层防守；今晚不临时开新项目。" if riskiest and riskiest["risk"] else f"本轮准备先守住 {target}，再练架构取舍与失败。",
                "why": ["截止时间附近应优先降低被问穿风险", "真实 ownership 与可解释证据比题目数量有用"],
                "actions": [action("risk_map", f"审计 {target} 并生成安全措辞与缺证清单", "codex", "一页面试风险图"),
                            action("question_ladder", "针对该项目准备 what / why / alternatives / measurement / failure 五层追问", "codex", "项目防守提纲"),
                            action("practice", "练一次 90 秒真实故事，安排休息并参加面试", "human")],
                "observation_window": "下次面试结束后记录被追问最深的三个问题与原话反馈",
                "stop_condition": "准备时间到即停；强表述无法补证就降低措辞，今晚不补做大型项目",
                "pivot_condition": "明确新反馈后调整下一轮准备；单次结果不证明方向或策略因果"}
    elif mode == "positioning":
        plan = {"bottleneck": "Evidence" if not riskiest or riskiest["risk"] else "Positioning",
                "recommended_move": "先确认真实个人贡献和项目阶段，再改写；当前缺证的‘主导 / production’表述先降低。" if not riskiest or riskiest["risk"] else "用已有证据翻译岗位语言，保持原有 scope 与 ownership。",
                "why": ["一句话应经得住五层追问", "措辞升级不能替代证据"],
                "actions": [action("evidence_audit", "核对 Claim、来源、个人贡献与项目阶段", "codex", "Claim 审计卡"),
                            action("write_material", "根据已确认贡献产出保守经历表述", "codex", "安全简历句"),
                            action("practice", "用五层追问检验表述", "human")],
                "observation_window": "补证或下一次模拟追问后复核",
                "stop_condition": "无法确认个人贡献或结果时停止升级措辞",
                "pivot_condition": "岗位职责变化或新证据出现时重新定位"}
    else:
        j = obj(value.get("job", {}), "job")
        if set(j) - {"fit", "gap", "gap_days", "role"}:
            raise ContractError("unknown job fields")
        fit = choices(j.get("fit", "unknown"), {"supported", "gap", "unknown"}, "role fit")
        gap = text(j.get("gap", ""), "gap", 240, empty=True)
        gap_days = j.get("gap_days")
        if gap_days is not None:
            number(gap_days, "gap_days", 0, 365)
        if fit == "supported" and any(c["confidence"] in {"SUPPORTED", "VERIFIED"} and not c["risk"] for c in claims) and n["goal"]:
            recommendation = "将这个岗位作为主投的有界试验：用最强已支持经历对齐 JD，再验证真实反馈。"
            bottleneck = "Market"
        elif fit == "gap" and gap:
            recommendation = f"先补或验证这个具体缺口：{gap}；把该方向作为有界副投试验，不立即重开大项目。"
            bottleneck = "Evidence"
            if gap_days is not None and gap_days > 14:
                recommendation = f"这个缺口（{gap}）预计超过两周，当前先降低投入，主投已有证据更强的方向。"
        else:
            recommendation = "先从三个真实经历形成两个岗位假设，对照五份当前 JD，选一个主投试验；现在不凭热度定方向。"
            bottleneck = "Direction"
            n["unknowns"].extend(["目标岗位的实际职责与新鲜 JD", "候选人的可防守证据与关键约束"])
        plan = {"bottleneck": bottleneck, "recommended_move": recommendation,
                "why": ["已有证据、职责匹配与机会成本共同决定下一步", "一次反馈不等于市场结论"],
                "actions": [action("evidence_audit", "整理三个真实项目和个人贡献", "codex", "证据卡"),
                            action("jd_map", "比较两个岗位假设与五份新鲜 JD，标出 gap 与补齐成本", "codex", "岗位假设对照表"),
                            action("apply", "选择一小批岗位验证反馈", "human")],
                "observation_window": "一周或下 5 个可比机会",
                "stop_condition": "真实硬约束不满足或补证成本超过当前预算时降低投入",
                "pivot_condition": "5–10 个同类机会重复同一缺口时 REFINE / PIVOT；一条反馈不作普遍结论"}
    if n["urgency"]["overdue"]:
        n["unknowns"].append("截止时间已过；需要确认机会是否仍可处理")
        plan["recommended_move"] = "先确认已过期的面试 / Offer / 机会是否仍有效，再执行下面的准备或比较。"
    n["unknowns"] = list(dict.fromkeys(n["unknowns"]))
    validate_actions(plan["actions"])
    routing = route(mode, rejected=mode == "recruiting" and plan.get("application_status") == "rejected")
    result = {"schema_version": "1", "current_situation": n["summary"], "mode": mode,
            "urgency": n["urgency"], "facts": n["facts"], "inferences": n["inferences"],
            "unknowns": [{"label": "UNKNOWN", "text": v} for v in n["unknowns"]],
            "current_goal": n["goal"] or "待确认；先处理可逆的下一步", "claims": n["claims"],
            "highest_risk": riskiest["id"] if riskiest else "关键证据或目标尚未确认",
            "options": ["执行首选的可逆动作", "补足会改变建议的信息后重评", "触发停止线时降低投入"],
            "references": routing["references"],
            "method_plan": method_plan(mode, evidence_gap=plan["bottleneck"] == "Evidence", urgent=n["urgency"]["within_72h"]), **plan,
            "boundary": "Deterministic structured support; not a verified prediction, authenticated receipt or career outcome."}
    result = enrich(result, value, now=now)
    result["claim_refs"] = claim_references(value.get("claim_refs", []), claim_ids=[c["id"] for c in result["claims"]])
    from scripts.calibration import predictions, apply_history
    result["predictions"] = predictions(value.get("predictions", []))
    apply_history(result, history or [], now=now)
    if "project_story" in value:
        from scripts.role_story import map_story
        result["project_mapping"] = map_story(value["project_story"], result["claims"], result["metadata"]["role_family"])
    if "career_hypothesis" in value:
        from scripts.hypothesis import review_hypothesis
        result["career_hypothesis"] = review_hypothesis(value["career_hypothesis"])
    return result


def render(decision: dict, *, details: bool = False) -> str:
    d = decision
    lines = [d["recommended_move"], "", "现在最值得做："]
    for i, a in enumerate(d["actions"], 1):
        actor = "Codex 可做" if a["execution_mode"] == "codex" else "你来执行"
        lines.append(f"{i}. {a['description']}（{actor}）")
    lines.extend(["", "为什么：" + "；".join(d["why"]), "风险：" + d["highest_risk"],
                  "重评：" + "；".join(d["recommendation"]["reconsider_if"])])
    if details and d["facts"]:
        lines.extend(["", "已知："] + [f"- {f['text']}（来源：{f['source']}；{f['source_type']}）" for f in d["facts"]])
    if details and d["inferences"]:
        lines.extend(["", "推测："] + [f"- {v['text']}" for v in d["inferences"]])
    consequential = d["unknowns"] if details else d["unknowns"][:2]
    lines.extend(["", "仍需确认："] + [f"- {v['text']}" for v in consequential])
    lines.extend(["", "观察：" + d["observation_window"], "停止：" + d["stop_condition"], "转向：" + d["pivot_condition"]])
    return "\n".join(lines) + "\n"
