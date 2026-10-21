"""Replay an explicit, portable job-search journal; no discovery, sending or memory."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from scripts.actions import HUMAN, CODEX
from scripts.models import ContractError, audit_claim, choices, items, obj, revision_refs, text, timestamp
from scripts.resume_export import _output_path

REQUIRED_CHECKS = {"content_check": "PASSED", "compilation": "COMPILED", "page_check": "PASSED",
                   "text_check": "PASSED", "log_check": "PASSED", "visual_review": "PASSED"}
FEEDBACK_HINTS = {
    "skill_gap": "核对明确反馈与对应 Claim，优先练习或补一项证据；单次反馈不改变方向。",
    "role_cancelled": "停止为已取消岗位继续优化，核实岗位状态，把精力转向其他机会。",
    "process": "按招聘方已给时点观察或跟进，不因等待改写经历或推断拒绝。",
    "unknown": "先核实观察及来源，不猜测拒绝原因。",
}


def exact(value, fields, label):
    value = obj(value, label)
    if set(value) != set(fields.split()):
        raise ContractError(label + " requires " + fields)
    return value


def _when(value):
    return datetime.fromisoformat(timestamp(value, "event time").replace("Z", "+00:00"))


def _existing(mapping, key, label):
    key = text(key, label, 100)
    if key not in mapping:
        raise ContractError("unknown " + label + ": " + key)
    return mapping[key]


def _artifact_checks(artifacts, verify_files):
    items(artifacts, "resume artifacts", 8)
    if not artifacts:
        raise ContractError("resume needs artifact receipts")
    seen, verified = set(), True
    result = []
    for raw in artifacts:
        a = exact(raw, "kind path sha256", "artifact")
        kind = choices(a["kind"], {"tex", "text", "data", "pdf"}, "artifact kind")
        if kind in seen:
            raise ContractError("duplicate artifact kind")
        seen.add(kind)
        path = Path(text(a["path"], "artifact path", 1000))
        if not path.is_absolute() or not isinstance(a["sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", a["sha256"]):
            raise ContractError("artifact needs absolute path and SHA-256")
        status = "NOT_CHECKED"
        if verify_files:
            if not path.is_file():
                status = "MISSING"
            elif path.stat().st_size > 30 * 1024 * 1024:
                status = "TOO_LARGE"
            else:
                status = "MATCHED" if hashlib.sha256(path.read_bytes()).hexdigest() == a["sha256"] else "CHANGED"
        verified = verified and status == "MATCHED"
        result.append({**a, "file_check": status})
    return result, verified


def review_journey(packet, *, verify_files=False, now=None):
    """Recompute from supplied history. File reads require the explicit verify_files flag."""
    if not isinstance(verify_files, bool):
        raise ContractError("verify_files must be boolean")
    p = exact(packet, "schema_version case_id goal next_review_at events", "journey")
    if p["schema_version"] != "1":
        raise ContractError("unsupported journey version")
    if len(json.dumps(p, ensure_ascii=False, allow_nan=False).encode("utf-8")) > 256 * 1024:
        raise ContractError("journey exceeds 256 KiB; explicitly archive old work")
    case_id = text(p["case_id"], "case_id", 100)
    goal = text(p["goal"], "goal", 400)
    review_at = _when(p["next_review_at"]) if p["next_review_at"] else None
    clock = _when(now) if now else datetime.now(timezone.utc)
    claims, revisions, resumes, opportunities, actions, feedback, reviews, ids = {}, {}, {}, {}, {}, {}, [], set()

    def refs(raw):
        clean = revision_refs(raw)
        for ref in clean:
            previous = _existing(revisions, ref["revision_id"], "claim revision")
            if (previous["project_id"], previous["claim"]["id"]) != (ref["project_id"], ref["claim_id"]):
                raise ContractError("claim revision belongs to another project or claim")
        return clean

    for raw in items(p["events"], "journey events", 100):
        e = exact(raw, "id type at source origin payload", "event")
        eid = text(e["id"], "event id", 100)
        if eid in ids:
            raise ContractError("duplicate event id")
        ids.add(eid)
        at = _when(e["at"])
        if at > clock:
            raise ContractError("recorded events cannot be future work; use an action or next_review_at")
        source = text(e["source"], "event source", 240)
        origin = choices(e["origin"], {"synthetic", "real_world", "unknown"}, "origin")
        d = obj(e["payload"], "event payload")
        kind = e["type"]
        if kind == "claim":
            exact(d, "project_id claim supersedes", "claim event")
            project = text(d["project_id"], "project_id", 100)
            claim = audit_claim(d["claim"])
            key = (project, claim["id"])
            previous = claims.get(key)
            if d["supersedes"] != (previous["revision_id"] if previous else ""):
                raise ContractError("claim correction must explicitly supersede its current revision")
            current = {"project_id": project, "revision_id": eid, "claim": claim,
                       "source": source, "origin": origin, "at": e["at"]}
            claims[key] = current; revisions[eid] = current
        elif kind == "opportunity":
            exact(d, "opportunity_id company role", "opportunity event")
            oid = text(d["opportunity_id"], "opportunity_id", 100)
            if oid in opportunities:
                raise ContractError("opportunity identity already exists; append recruiting events")
            opportunities[oid] = {"id": oid, "company": text(d["company"], "company", 160),
                "role": text(d["role"], "role", 160), "status": "planned", "resume_id": "",
                "submitted_at": "", "latest_resume_id": "", "material_updates": [], "source": source, "origin": origin}
        elif kind == "resume":
            exact(d, "lineage artifacts checks", "resume event")
            line = exact(d["lineage"], "resume_id parent_resume_id opportunity_id claim_refs", "resume lineage")
            rid = text(line["resume_id"], "resume_id", 100)
            if rid in resumes:
                raise ContractError("resume version is immutable; create a new version")
            parent = text(line["parent_resume_id"], "parent resume", 100, empty=True)
            oid = text(line["opportunity_id"], "opportunity_id", 100, empty=True)
            if parent: _existing(resumes, parent, "parent resume")
            if oid: _existing(opportunities, oid, "opportunity")
            bindings = refs(line["claim_refs"])
            if not bindings:
                raise ContractError("journey resume needs explicit claim revisions")
            checks = obj(d["checks"], "resume checks")
            checks = {key: text(checks.get(key, "NOT_PERFORMED"), "check value", 80)
                      for key in REQUIRED_CHECKS}
            artifacts, verified = _artifact_checks(d["artifacts"], verify_files)
            has_pdf = any(a["kind"] == "pdf" for a in artifacts)
            ready = has_pdf and verified and all(checks.get(k) == v for k, v in REQUIRED_CHECKS.items())
            resumes[rid] = {"resume_id": rid, "parent_resume_id": parent, "opportunity_id": oid,
                "claim_refs": bindings, "artifacts": artifacts, "checks": copy.deepcopy(checks),
                "status": ("FILES_CHANGED" if verify_files and any(a["file_check"] in {"MISSING", "CHANGED", "TOO_LARGE"} for a in artifacts)
                           else "READY" if ready else "REVIEW_PENDING" if has_pdf else "SOURCE_ONLY"),
                "source": source, "origin": origin}
        elif kind == "submission":
            exact(d, "opportunity_id resume_id submitted_at", "submission event")
            opp = _existing(opportunities, d["opportunity_id"], "opportunity")
            resume = _existing(resumes, d["resume_id"], "resume")
            if opp["submitted_at"]:
                raise ContractError("duplicate submission for one opportunity; retain the first version")
            if resume["opportunity_id"] and resume["opportunity_id"] != opp["id"]:
                raise ContractError("resume targets a different opportunity")
            if _when(d["submitted_at"]) > at:
                raise ContractError("a reported submission cannot be in the future")
            opp.update(status="submitted", resume_id=resume["resume_id"], submitted_at=d["submitted_at"],
                       source=source, origin=origin, latest_resume_id=resume["resume_id"])
        elif kind == "material_update":
            exact(d, "opportunity_id resume_id sent_at summary", "material update")
            opp = _existing(opportunities, d["opportunity_id"], "opportunity")
            resume = _existing(resumes, d["resume_id"], "resume")
            if not opp["submitted_at"]:
                raise ContractError("material update needs an existing reported submission")
            if resume["opportunity_id"] and resume["opportunity_id"] != opp["id"]:
                raise ContractError("updated resume targets another opportunity")
            if not _when(opp["submitted_at"]) <= _when(d["sent_at"]) <= at:
                raise ContractError("material update time must follow submission and precede its report")
            opp["material_updates"].append({"event_id": eid, "resume_id": resume["resume_id"],
                "sent_at": d["sent_at"], "summary": text(d["summary"], "update summary", 400),
                "source": source, "origin": origin})
            opp["latest_resume_id"] = resume["resume_id"]
        elif kind == "recruiting":
            exact(d, "opportunity_id status summary", "recruiting event")
            opp = _existing(opportunities, d["opportunity_id"], "opportunity")
            status = choices(d["status"], {"waiting", "interview", "offer", "rejected", "withdrawn", "freeze"}, "recruiting status")
            if not opp["submitted_at"] and status not in {"withdrawn", "freeze"}:
                raise ContractError("recruiting progress requires a reported submission")
            opp.update(status=status, status_summary=text(d["summary"], "status summary", 400), source=source, origin=origin)
        elif kind == "action":
            exact(d, "kind description opportunity_id", "action event")
            action_kind = choices(d["kind"], HUMAN | CODEX, "action kind")
            oid = text(d["opportunity_id"], "opportunity_id", 100, empty=True)
            if oid: _existing(opportunities, oid, "opportunity")
            actions[eid] = {"id": eid, "kind": action_kind, "description": text(d["description"], "action", 1000),
                "opportunity_id": oid, "owner": "human" if action_kind in HUMAN else "assistant",
                "status": "PROPOSED", "receipts": []}
        elif kind == "execution":
            exact(d, "action_id status summary", "execution receipt")
            action = _existing(actions, d["action_id"], "action")
            status = choices(d["status"], {"DONE", "PARTIAL", "BLOCKED", "UNKNOWN"}, "execution status")
            summary = text(d["summary"], "execution summary", 400)
            action["receipts"].append({"event_id": eid, "status": status, "summary": summary,
                                       "source": source, "at": e["at"], "origin": origin})
            action["status"] = status
        elif kind == "feedback":
            exact(d, "opportunity_id category summary claim_refs", "feedback event")
            _existing(opportunities, d["opportunity_id"], "opportunity")
            category = choices(d["category"], set(FEEDBACK_HINTS), "feedback category")
            feedback[eid] = {"id": eid, "opportunity_id": d["opportunity_id"], "category": category,
                "summary": text(d["summary"], "feedback summary", 600), "claim_refs": refs(d["claim_refs"]),
                "source": source, "origin": origin, "next_step_hint": FEEDBACK_HINTS[category]}
        elif kind == "review":
            exact(d, "feedback_id conclusion reason next_action_id", "review event")
            f = _existing(feedback, d["feedback_id"], "feedback")
            action = _existing(actions, d["next_action_id"], "next action")
            if action["opportunity_id"] not in {"", f["opportunity_id"]}:
                raise ContractError("review action belongs to another opportunity")
            conclusion = choices(d["conclusion"], {"practice", "rewrite", "refresh_role", "stop", "verify", "continue"}, "review conclusion")
            reviews.append({"id": eid, "feedback_id": f["id"], "conclusion": conclusion,
                "reason": text(d["reason"], "review reason", 600), "next_action_id": action["id"],
                "source": source, "origin": origin})
        else:
            raise ContractError("unknown journey event type")

    for resume in resumes.values():
        affected = [ref for ref in resume["claim_refs"]
                    if claims[(ref["project_id"], ref["claim_id"])]["revision_id"] != ref["revision_id"]]
        resume["stale_claim_refs"] = affected
        if affected: resume["status"] = "STALE"
    for opp in opportunities.values():
        opp["submitted_resume_stale"] = bool(opp["resume_id"] and resumes[opp["resume_id"]]["stale_claim_refs"])
    pending = [a for a in actions.values() if a["status"] != "DONE"]
    priority = reviews[-1]["next_action_id"] if reviews else ""
    pending.sort(key=lambda a: a["id"] != priority)
    state = {"claims": list(claims.values()), "resumes": list(resumes.values()),
             "opportunities": list(opportunities.values()), "actions": list(actions.values()),
             "feedback": list(feedback.values()), "reviews": reviews}
    card = {"case_id": case_id, "goal": goal,
            "opportunities": [{k: o[k] for k in ("id", "company", "role", "status", "resume_id", "submitted_at", "latest_resume_id", "submitted_resume_stale")} for o in opportunities.values()],
            "stale_resume_ids": [x["resume_id"] for x in resumes.values() if x["status"] == "STALE"],
            "next_actions": [{k: a[k] for k in ("id", "description", "owner", "status")} for a in pending[:3]],
            "next_review_at": p["next_review_at"], "review_due": bool(review_at and review_at <= clock),
            "current_claims": [{"project_id": c["project_id"], "claim_id": c["claim"]["id"],
                                "revision_id": c["revision_id"], "wording": c["claim"]["safe_wording"],
                                "confidence": c["claim"]["confidence"], "source": c["source"]} for c in list(claims.values())[:5]],
            "latest_feedback": list(feedback.values())[-1] if feedback else None,
            "latest_review": reviews[-1] if reviews else None,
            "boundary": "Reported history, not authenticated hiring outcomes. Summary-only continuation must preserve missing sources as unknown."}
    return {"schema_version": "1", "case_id": case_id, "as_of": clock.isoformat(), "state": state, "handoff": card,
            "files_verified": verify_files, "memory_enabled": False, "external_actions_executed": False}


def render_handoff(report):
    c = report["handoff"]
    lines = ["# 求职接续卡", "", "目标：" + c["goal"], "记录：" + c["case_id"], ""]
    for o in c["opportunities"]:
        lines.append(f"- {o['company']} / {o['role']}：{o['status']}；已提交版本：{o['resume_id'] or '未确认投递'}")
        if o["latest_resume_id"] and o["latest_resume_id"] != o["resume_id"]:
            lines.append("  后续补交：" + o["latest_resume_id"] + "；同一流程，不新增投递，不代表招聘方已采纳。")
    if c["current_claims"]:
        lines += ["", "当前事实表述："]
        lines += ["- " + x["wording"] + "（" + x["confidence"] + "；来源：" + x["source"] + "）" for x in c["current_claims"]]
    if c["latest_feedback"]:
        f = c["latest_feedback"]
        lines += ["", "最新反馈：" + f["summary"] + "；来源：" + f["source"]]
    if c["latest_review"]:
        lines += ["当前判断：" + c["latest_review"]["reason"]]
    if c["stale_resume_ids"]:
        lines += ["", "事实已修正的旧版本：" + "、".join(c["stale_resume_ids"]) + "。保留历史；继续使用时应改用验收后的新版本，补交单独记录，不自动重发。"]
    lines += ["", "下一步："]
    lines += [f"- {a['owner']}：{a['description']}（{a['status']}）" for a in c["next_actions"]] or ["- 尚未记录下一步，先核对当前目标与反馈。"]
    lines += ["", "复查时间：" + (c["next_review_at"] or "未约定") + ("（已到观察时点）" if c["review_due"] else ""),
              "这是来源随附的记录摘要；不推断未回复为拒绝，不自动投递、发送或开启记忆。",
              "跨聊天带回此卡；有完整 journey.json 时一并提供，只有摘要时不能补造旧记录。", ""]
    return "\n".join(lines)


def write_checkpoint(packet, report, directory):
    """Explicit private file export, separate from consented long-term memory."""
    target = _output_path(directory)
    # Revalidate rather than saving an invalid packet with an unrelated report.
    current = review_journey(packet, verify_files=report["files_verified"], now=report["as_of"])
    if any(current[key] != report[key] for key in ("case_id", "state", "handoff")):
        raise ContractError("checkpoint report does not match supplied history")
    target.mkdir(parents=True, mode=0o700, exist_ok=False)
    for name, data in (("journey.json", packet), ("review.json", report)):
        (target / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (target / "continue.md").write_text(render_handoff(report), encoding="utf-8")
    for path in target.iterdir(): path.chmod(0o600)
    return str(target)
