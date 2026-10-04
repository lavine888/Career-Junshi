"""Host-owned Decision Envelope v2: bounded provenance and integrity checks.

ACCEPT is not proof of arbitrary prose entailment or real-world truth. No career
ranking, capability diagnosis, or recommendation fallback is performed here.
"""
from __future__ import annotations

import copy
import re
from datetime import datetime, timezone
from decimal import Decimal

from scripts.models import ContractError, audit_claim, claim_references, choices, items, obj, text, timestamp
from scripts.intelligence import metadata

MODES = {"job", "offer", "recruiting", "positioning", "interview"}
EXTENSIONS = {"direction": "job", "offer": "offer", "recruiting": "recruiting",
              "ownership": "positioning", "interview": "interview"}
ARTIFACTS = {"direction": "direction-comparison.md", "offer": "offer-verification.md",
             "recruiting": "follow-up-draft.md", "ownership": "ownership-defense.md",
             "interview": "interview-risk.md"}


def source_registry(context):
    """Session-only source binding. Input is caller supplied, never host replaced."""
    c = obj(context, "context")
    result = {}
    for raw in items(c.get("materials", c.get("sources", [])), "session sources", 30):
        s = obj(raw, "source")
        sid = text(s.get("source_id"), "source_id", 80)
        if sid in result:
            raise ContractError("duplicate session source ID")
        result[sid] = {"text": text(s.get("text"), "source text", 30000),
                       "source_type": text(s.get("source_type", "user_report"), "source_type", 80)}
    if c.get("request"):
        if "REQUEST" in result:
            raise ContractError("REQUEST is reserved for the exact user request")
        result["REQUEST"] = {"text": text(c["request"], "request", 30000), "source_type": "user_report"}
    if not result:
        raise ContractError("session sources are required")
    return result


def _strings(value, label, limit=6, width=600):
    return [text(v, label, width) for v in items(value, label, limit)]


def _clauses(value):
    return [c.strip() for c in re.split(r"[。；;\n]|(?<!\d)\.(?!\d)", value) if c.strip()]


def _positive(clause, pattern):
    """Finite explicit patterns only; negation is scoped before each assertion."""
    for match in re.finditer(pattern, clause, re.I):
        prefix = re.split(r"[,，:]", clause[:match.start()])[-1][-24:]
        # Subjects may be part of the match: checking only the preceding prefix
        # misread 'I have not solely implemented' and '我没有独立开发'. A negated
        # ownership predicate is different from 'not merely assisting, I alone...'.
        internal_negation = re.search(r"(?:没有|未|不曾)(?:亲自)?(?:独立|全部|设计|实现|编写|完成|开发)|\bnot\s+(?:(?:personally|solely|alone)\s+)?(?:implemented?|architected?|built|wrote|build|write)\b|\bdidn't\s+(?:implement|architect|build|write)\b", match.group(), re.I)
        if not internal_negation and not re.search(r"不能|不应|不要|不得|并非|不等于|不足以|无法|未能|没有|不是|不代表|不证明|未知|尚未|不把|不将|not\b|never\b|no\b|without\b|cannot\b|don't\b", prefix, re.I):
            yield match


def validate_decision_envelope(value, context, *, now=None):
    """Return ACCEPT / REPAIR_REQUIRED / BLOCK; never rewrite a host move.

    Invalid optional metadata is isolated. Invalid required evidence/actions block
    compilation. Safe fields are names for review, never an authorization token.
    """
    issues = []
    clean = {}
    def issue(code, field, explanation, severity="REPAIR_REQUIRED"):
        item = {"code": code, "severity": severity, "field": field, "explanation": explanation}
        if item not in issues:
            issues.append(item)
    try:
        sources = source_registry(context)
        e = obj(value, "envelope")
        if e.get("schema_version") != "2":
            raise ContractError("schema_version must be '2'")
        s = obj(e.get("situation"), "situation")
        clean = {"schema_version": "2", "situation": {
            "summary": text(s.get("summary"), "summary", 600),
            "mode": choices(s.get("mode"), MODES, "mode")}}
        if "goal" in s:
            clean["situation"]["goal"] = text(s["goal"], "goal", 600)
        # Only explicit timestamps are calculated; absent deadline stays absent.
        due = s.get("deadline")
        instant = now or datetime.now(timezone.utc)
        if instant.tzinfo is None:
            raise ContractError("now requires timezone")
        clean["urgency"] = {"deadline": None, "hours_remaining": None}
        if due:
            due = timestamp(due, "deadline")
            refs = _strings(s.get("deadline_source_ids", []), "deadline source IDs", width=80)
            if not refs or set(refs) - sources.keys():
                issue("FACT_WITHOUT_SOURCE", "situation.deadline", "Explicit deadline needs session source IDs.", "BLOCK")
            clean["situation"].update(deadline=due, deadline_source_ids=refs)
            clean["urgency"] = {"deadline": due, "hours_remaining": round((datetime.fromisoformat(due.replace("Z", "+00:00")) - instant).total_seconds()/3600, 2)}
        registry = {}
        clean["facts"] = []
        for index, raw in enumerate(items(e.get("facts", []), "facts", 30)):
            f = obj(raw, "fact")
            field = f"facts[{index}]"
            fid = text(f.get("id"), "fact ID", 80)
            refs = _strings(f.get("source_ids", []), "source IDs", width=80)
            statement = text(f.get("statement"), "fact", 1200)
            confidence = choices(f.get("confidence"), {"direct", "self_reported", "interpretation", "unknown"}, "confidence")
            if not refs or set(refs) - sources.keys():
                issue("FACT_WITHOUT_SOURCE", field, "Every fact needs existing session source IDs.", "BLOCK")
            if f.get("epistemic", "FACT") != "FACT" or confidence in {"interpretation", "unknown"}:
                issue("UNKNOWN_AS_FACT", field, "Inferred or unknown statements cannot be facts.", "BLOCK")
            spans = []
            for span in items(f.get("source_spans", []), "fact spans", 8):
                span = obj(span, "span")
                sid, quote = text(span.get("source_id"), "span ID", 80), text(span.get("quote"), "quote", 6000)
                if sid not in refs or sid not in sources or quote not in sources[sid]["text"]:
                    issue("SOURCE_SPAN_MISMATCH", field, "Quote must occur verbatim in the linked original source.", "BLOCK")
                spans.append({"source_id": sid, "quote": quote})
            if not refs or {p["source_id"] for p in spans} != set(refs):
                issue("FACT_WITHOUT_SOURCE", field, "Each fact source needs an exact quote anchor.", "BLOCK")
            reported_percentages = {Decimal(m.group(1)) for p in spans for m in re.finditer(r"([+-]?\d+(?:\.\d+)?)\s*[%％]", p["quote"].replace("−", "-"))}
            asserted_percentages = {Decimal(m.group(1)) for m in re.finditer(r"([+-]?\d+(?:\.\d+)?)\s*[%％]", statement.replace("−", "-"))}
            if asserted_percentages - reported_percentages:
                issue("UNSUPPORTED_METRIC", field, "A factual percentage must occur in its source anchor; derived arithmetic belongs in an explicit inference, not a reported fact.", "BLOCK")
            if s["mode"] == "recruiting" or any(sources.get(r, {}).get("source_type") in {"hr_chat", "interview_recap"} for r in refs):
                # Preserve the existing polarity/conditional/hearsay protection
                # without requiring a statement-kind enum for every observation.
                from scripts.context import recruiting_assertion
                asserted, qualifications = recruiting_assertion(statement)
                original, original_qualifications = recruiting_assertion("\n".join(p["quote"] for p in spans))
                if asserted - original or (asserted and original_qualifications - qualifications) or (len(original) > 1 and asserted != original):
                    issue("RECRUITING_RESULT_PROMOTED", field, "Preserve hiring-result polarity, pending conditions and hearsay attribution; narrow conflicting source scope or retain UNKNOWN.", "BLOCK")
            if confidence == "direct" and any(sources.get(r, {}).get("source_type") in {"user_report", "resume"} for r in refs):
                issue("FALSE_VERIFICATION", field, "Visible self-report is not independent verification.")
            if fid in registry:
                raise ContractError("statement IDs must be unique")
            registry[fid] = "FACT"
            clean["facts"].append({"id": fid, "statement": statement, "source_ids": refs, "source_spans": spans, "epistemic": "FACT", "confidence": confidence})
        clean["inferences"], clean["unknowns"] = [], []
        for category in ("inferences", "unknowns"):
            for index, raw in enumerate(items(e.get(category, []), category, 20)):
                f = obj(raw, category)
                fid = text(f.get("id"), "statement ID", 80)
                if fid in registry:
                    raise ContractError("statement IDs must be unique")
                registry[fid] = "INFERENCE" if category == "inferences" else "UNKNOWN"
                entry = {"id": fid, "statement": text(f.get("statement"), category, 1200)}
                if category == "inferences":
                    entry["basis"] = _strings(f.get("basis", []), "inference basis", 10, 80)
                else:
                    entry["decision_relevance"] = choices(f.get("decision_relevance"), {"blocking", "reversal", "confidence_only"}, "unknown relevance")
                clean[category].append(entry)
        for i, f in enumerate(clean["inferences"]):
            if not f["basis"] or set(f["basis"]) - (registry.keys() | sources.keys()):
                issue("INFERENCE_WITHOUT_BASIS", f"inferences[{i}]", "Interpretation needs existing source/statement IDs.")
        b = obj(e.get("bottleneck"), "bottleneck")
        clean["bottleneck"] = {"type": text(b.get("type"), "bottleneck type", 100), "explanation": text(b.get("explanation"), "explanation", 1200)}
        r = obj(e.get("recommendation"), "recommendation")
        clean["recommendation"] = {"type": choices(r.get("type"), {"SUFFICIENT", "CONDITIONAL", "BLOCKED"}, "recommendation type"),
            "move": text(r.get("move"), "move", 1200), "why": _strings(r.get("why", []), "why", 4, 1200),
            "avoided_action": _strings(r.get("avoided_action", []), "avoided action", 3, 600),
            "basis_ids": _strings(r.get("basis_ids", []), "basis IDs", 30, 80)}
        if not clean["recommendation"]["why"] or not clean["recommendation"]["basis_ids"] or set(clean["recommendation"]["basis_ids"]) - (registry.keys() | sources.keys()):
            issue("RECOMMENDATION_WITHOUT_BASIS", "recommendation", "Decision needs a reason and linked evidence or explicitly labeled inference.", "BLOCK")
        if any(registry.get(k) == "UNKNOWN" for k in clean["recommendation"]["basis_ids"]):
            # Unknowns may justify blocking or verification, never certainty.
            if r["type"] == "SUFFICIENT":
                issue("UNKNOWN_AS_FACT", "recommendation.basis_ids", "A sufficient decision cannot cite an unknown as established support.", "BLOCK")
        clean["alternatives"] = []
        for raw in items(e.get("alternatives", []), "alternatives", 3):
            a = obj(raw, "alternative")
            clean["alternatives"].append({"option": text(a.get("option"), "option", 600), "why_not_now": text(a.get("why_not_now"), "why not now", 1200)})
        clean["actions"] = []
        for i, raw in enumerate(items(e.get("actions", []), "actions", 12)):
            a = obj(raw, "action")
            desc = text(a.get("description"), "action description", 1800)
            actor = choices(a.get("execution_mode"), {"codex", "human"}, "execution mode")
            priority = a.get("priority", i + 1)
            if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 3:
                issue("ACTION_TOO_BROAD", f"actions[{i}]", "Use at most three bounded primary priorities.")
            if a.get("status", "PROPOSED") != "PROPOSED":
                issue("FALSE_EXECUTION", f"actions[{i}]", "A proposed action cannot be marked executed.", "BLOCK")
            # Local drafts are allowed; sending, applying and signing are human.
            if actor == "codex" and re.search(r"^(?:发送|投递|签署|接受\s*Offer|拒绝\s*Offer|谈薪|send\b|apply\b|accept\b|negotiate\b)", desc, re.I):
                issue("ACTION_OWNERSHIP", f"actions[{i}]", "External or consequential career actions belong to the human.", "BLOCK")
            clean["actions"].append({"description": desc, "execution_mode": actor, "priority": priority})
        if not clean["actions"] or len(clean["actions"]) > 3:
            issue("ACTION_TOO_BROAD", "actions", "Return one to three actionable primary actions.")
        clean["reconsider_if"] = _strings(e.get("reconsider_if", []), "reconsider", 3, 1200)
        if not clean["reconsider_if"]:
            issue("NO_REVERSAL_CONDITION", "reconsider_if", "Important decisions require an observable reconsideration condition.")
        if not r.get("avoided_action"):
            issue("NO_AVOIDED_ACTION", "recommendation.avoided_action", "Identify one effort to avoid.", "WARNING")
        clean["observation_window"] = text(e.get("observation_window"), "observation window", 1200)
        clean["stop_condition"] = text(e.get("stop_condition"), "stop condition", 1200)
        clean["evidence_used"] = _strings(e.get("evidence_used", []), "evidence used", 30, 80)
        if set(clean["evidence_used"]) - sources.keys():
            issue("FACT_WITHOUT_SOURCE", "evidence_used", "Unknown source references cannot support this decision.", "BLOCK")
        clean["claims_used"] = _strings(e.get("claims_used", []), "claims used", 20, 80)
        claims = items(e.get("claims", []), "claims", 20)
        audited = [audit_claim(c) for c in claims]
        if len({c["id"] for c in audited}) != len(audited) or set(clean["claims_used"]) - {c["id"] for c in audited}:
            issue("CLAIM_IDENTITY", "claims_used", "Used claims require distinct existing claim records.", "BLOCK")
        clean["claims"], clean["claim_refs"] = copy.deepcopy(claims), claim_references(e.get("claim_refs", []), claim_ids=clean["claims_used"])
        for i, (raw, checked) in enumerate(zip(claims, audited)):
            if raw.get("confidence", "SELF_REPORTED") != checked["confidence"]:
                issue("FALSE_VERIFICATION", f"claims[{i}]", "Claim confidence exceeds the existing evidence audit; host must correct it.")
            if any("stage_conflict" in k or "ownership_conflict" in k or "missing_evidence:authorship" in k for k in checked["risk"]):
                issue("UNSUPPORTED_AUTHORSHIP", f"claims[{i}]", "Strong authorship/stage claim exceeds audited evidence; use bounded wording.")
            if any(v["source"] not in sources for v in checked["evidence"]):
                issue("FACT_WITHOUT_SOURCE", f"claims[{i}].evidence", "Claim evidence must bind to session source IDs.", "BLOCK")
        if "metadata" in e:
            try:
                m = metadata(e["metadata"])
                if m["mode"] != s["mode"]:
                    raise ContractError("metadata mode mismatch")
                clean["metadata"] = m
            except ContractError as exc:
                issue("OPTIONAL_METADATA_IGNORED", "metadata", str(exc), "WARNING")
        if "predictions" in e:
            try:
                from scripts.calibration import predictions
                clean["predictions"] = predictions(e["predictions"])
            except ContractError as exc:
                issue("OPTIONAL_METADATA_IGNORED", "predictions", str(exc), "WARNING")
        clean["extensions"] = {}
        extensions = e.get("extensions", {})
        if not isinstance(extensions, dict):
            issue("EXTENSION_IGNORED", "extensions", "Optional extensions must be an object; omitted from compilation.", "WARNING")
            extensions = {}
        for key, ext in extensions.items():
            if key not in EXTENSIONS or EXTENSIONS[key] != s["mode"]:
                issue("EXTENSION_IGNORED", "extensions." + key, "Optional extension belongs to a different mode or is unknown.", "WARNING")
                continue
            try:
                ext = obj(ext, key)
                clean["extensions"][key] = {"content": text(ext.get("content"), "artifact content", 12000)}
            except ContractError as exc:
                issue("EXTENSION_IGNORED", "extensions." + key, str(exc), "WARNING")
        known = {"schema_version", "situation", "facts", "inferences", "unknowns", "bottleneck", "recommendation", "alternatives", "actions", "reconsider_if", "observation_window", "stop_condition", "claims_used", "evidence_used", "claims", "claim_refs", "metadata", "predictions", "extensions"}
        for key in e.keys() - known:
            issue("OPTIONAL_METADATA_IGNORED", str(key), "Unrecognized optional annotation is not compiled or persisted.", "WARNING")
        _integrity(clean, sources, issue)
    except (ContractError, TypeError, KeyError) as exc:
        issue("CORE_SCHEMA", "envelope", str(exc), "REPAIR_REQUIRED")
    status = "BLOCK" if any(v["severity"] == "BLOCK" for v in issues) else "REPAIR_REQUIRED" if any(v["severity"] == "REPAIR_REQUIRED" for v in issues) else "ACCEPT"
    unsafe = {v["field"].split("[")[0].split(".")[0] for v in issues if v["severity"] != "WARNING"}
    return {"status": status, "issues": issues, "safe_fields": sorted(set(clean) - unsafe),
            "envelope": clean, "boundary": "Source anchors and finite integrity checks, not complete semantic verification or source authentication."}


def _integrity(e, sources, issue):
    source_text = "\n".join(s["text"] for s in sources.values())
    # Inspect commitments, factual claims, and executable material. Unknowns,
    # rejected alternatives and avoided actions are not positive assertions.
    fields = [("recommendation.move", e["recommendation"]["move"])]
    fields += [(f"recommendation.why[{i}]", v) for i, v in enumerate(e["recommendation"]["why"])]
    fields += [(f"facts[{i}]", f["statement"]) for i, f in enumerate(e["facts"])]
    fields += [(f"actions[{i}]", a["description"]) for i, a in enumerate(e["actions"])]
    fields += [(f"extensions.{k}", v["content"]) for k, v in e["extensions"].items()]
    for field, prose in fields:
        severity = "BLOCK" if field.startswith("recommendation") else "REPAIR_REQUIRED"
        for clause in _clauses(prose):
            # A quoted bad resume assertion is a fact of the source report,
            # not endorsement. Executable replacement wording is still checked.
            if field.startswith("facts") and re.search(r"简历(?:原文|写)|resume (?:says|states)|原表述|声称", clause, re.I):
                continue
            patterns = []
            if re.search(r"口头|verbal|later|以后|未来|没有.*(?:协议|合同)|未.*书面", source_text, re.I):
                patterns += [("VERBAL_PROMISE_PROMOTED", r"(?:股权|equity).{0,20}(?:保证|确定归属|已落实|guaranteed|contractual)|(?:保证|guaranteed).{0,20}(?:股权|equity)", "Verbal or future equity cannot be treated as guaranteed compensation.")]
            if re.search(r"未回复|没回|沉默|消失|下架|未收到|no (?:HR )?(?:response|reply)|silence|removed", source_text, re.I):
                patterns += [("SILENCE_TO_REJECTION", r"(?:你|我|候选人|you|candidate).{0,8}(?:已经|确定|肯定|已|are|was).{0,5}(?:被拒|拒绝|rejected)|(?:确定|肯定).{0,6}(?:被拒|rejected)", "Silence or listing removal does not establish a hiring result.")]
            if re.search(r"团队|team|同时|several changes", source_text, re.I):
                patterns += [("METRIC_ATTRIBUTION", r"(?:我|本人|个人|你|\bI\b).{0,18}(?:提高|提升|改善|improved|increased|带来).{0,18}\d+(?:\.\d+)?\s*[%％]", "Team aggregate metrics cannot be attributed to individual impact without isolation.")]
                patterns += [("TEAM_TO_SOLE", r"(?:我|本人|你|\bI\b).{0,12}(?:独立|全部|solely|alone).{0,12}(?:实现|完成|编写|built|implemented|wrote)", "Team participation does not establish sole authorship.")]
            if re.search(r"没有.*(?:独立|归因|拆分)|无法.*(?:归因|拆分)|无.*因果|同时|caus.{0,10}unknown", source_text, re.I):
                patterns += [("UNSUPPORTED_CAUSATION", r"共同(?:作用|推动|带来)|(?:导致|带来|caused|led to).{0,18}(?:增长|提升|成功|通过|\d+\s*[%％])", "Observed change or success does not identify a cause.")]
            if re.search(r"没有(?:编写|实现)|未(?:编写|实现)|不是.*(?:实现者|作者)|did not implement|didn't implement", source_text, re.I):
                patterns += [("UNSUPPORTED_AUTHORSHIP", r"(?:我|本人|你|\bI\b).{0,15}(?:设计|实现|architected|implemented).{0,10}(?:整个|全部|whole|entire).{0,8}(?:系统|system)", "Reported subsystem non-authorship does not support whole-system authorship.")]
            if re.search(r"拒绝|拒信|rejection|被拒", source_text, re.I):
                patterns += [("UNSUPPORTED_PIVOT_CERTAINTY", r"(?:根本|确定|fundamentally|definitely).{0,8}(?:不适合|unsuitable|wrong role)", "Outcome count alone cannot prove fundamental role unsuitability.")]
            if re.search(r"原型|demo|prototype", source_text, re.I) and not re.search(r"生产使用已确认|verified production", source_text, re.I):
                patterns += [("STAGE_PROMOTED", r"(?:已|已经|confirmed).{0,6}(?:生产上线|生产使用|production)", "Demo is not confirmed production use.")]
            if re.search(r"回测|backtest", source_text, re.I):
                patterns += [("STAGE_PROMOTED", r"(?:已|已经|achieved).{0,6}(?:实盘盈利|live profit)", "Backtest is not a live result.")]
            for code, pattern, explanation in patterns:
                if any(_positive(clause, pattern)):
                    issue(code, field, explanation, severity)


def repair_request(validation):
    if validation["status"] == "ACCEPT":
        return None
    essential = validation["status"] == "BLOCK"
    return {"instruction": ("Reconsider the move where an essential premise is invalid; do not invent replacement evidence." if essential else "Preserve the valid recommendation; repair only the listed boundaries or required structure."),
            "issues": [v for v in validation["issues"] if v["severity"] != "WARNING"],
            "max_repair_rounds": 1}


def review_with_repair(value, context, repair=None, *, now=None):
    """Host callback receives original envelope + relevant issues, not a rubric.

    Caller retains original source context. Exactly one callback; invalid repair
    cannot generate artifacts. Returned attempts retain rejected/raw candidates.
    """
    attempts = []
    candidate = copy.deepcopy(value)
    for round_number in range(2):
        v = validate_decision_envelope(candidate, context, now=now)
        attempts.append({"round": round_number, "raw_envelope": copy.deepcopy(candidate), "validation": v})
        if v["status"] == "ACCEPT" or repair is None or round_number == 1:
            return {"status": v["status"], "attempts": attempts, "envelope": v["envelope"] if v["status"] == "ACCEPT" else None,
                    "repair_request": repair_request(v)}
        candidate = repair(copy.deepcopy(candidate), repair_request(v))


def accepted_envelope(value, context, *, now=None):
    v = validate_decision_envelope(value, context, now=now)
    if v["status"] != "ACCEPT":
        raise ContractError("Envelope needs host correction before compilation or memory: " + v["status"])
    return v["envelope"]


def render_envelope(e):
    """Present the accepted host judgment unchanged, without pipeline internals."""
    r = e["recommendation"]
    lines = ["我的判断：" + r["move"], "", "现在做什么："]
    for i, a in enumerate(e["actions"], 1):
        lines.append(f"{i}. {a['description']}（{'你来执行' if a['execution_mode'] == 'human' else 'Codex 可做'}）")
    lines += ["", "为什么：" + "；".join(r["why"]), "", "不要做什么：" + "；".join(r["avoided_action"]),
              "", "什么会让我改判断：" + "；".join(e["reconsider_if"]),
              "观察：" + e["observation_window"], "停止：" + e["stop_condition"]]
    return "\n".join(lines) + "\n"


def compile_artifacts(value, context, directory=None, *, now=None):
    """No strategy choice: copy validated host content into fixed safe filenames."""
    from pathlib import Path
    e = accepted_envelope(value, context, now=now)
    content = {"next-actions.md": render_envelope(e)}
    for key, ext in e["extensions"].items():
        content[ARTIFACTS[key]] = ext["content"].rstrip() + "\n"
    if directory is None:
        return content
    target = Path(directory).expanduser().resolve()
    if any((target / name).exists() for name in content):
        raise ContractError("Artifact exists; use a fresh directory")
    target.mkdir(parents=True, exist_ok=True)
    for name, body in content.items():
        with (target / name).open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(body)
    return [str(target / name) for name in content]


def memory_handoff(value, context, *, now=None):
    """Existing consented append-only memory contract; never persist raw sources."""
    e = accepted_envelope(value, context, now=now)
    r = e["recommendation"]
    # Explicit budgets, no silent truncation or invented prediction.
    result = {"situation": text(e["situation"]["summary"], "memory situation", 400),
              "decision": text(r["move"], "memory decision", 600),
              "why": text("；".join(r["why"]), "memory why", 600),
              "expected_outcome": text(e["observation_window"], "expected observation", 400),
              "source": "host-envelope-v2", "observation_window": text(e["observation_window"], "memory window", 400),
              "stop_condition": text(e["stop_condition"], "memory stop", 400),
              "pivot_condition": text("；".join(e["reconsider_if"]), "memory reconsider", 400),
              "claim_ids": e["claims_used"], "claim_refs": e["claim_refs"],
              "decision_trace": {"situation": e["situation"]["summary"], "bottleneck": e["bottleneck"]["type"],
                "chosen": r["move"], "evidence_used": e["evidence_used"], "why": r["why"],
                "options_considered": [r["move"]] + [a["option"] for a in e["alternatives"]],
                "rejected_options": [{"option": a["option"], "why": a["why_not_now"]} for a in e["alternatives"]],
                "reconsider_if": e["reconsider_if"]}}
    if "metadata" in e:
        result["metadata"] = e["metadata"]
    if "predictions" in e:
        result["predictions"] = e["predictions"]
    # Reuse exact old trace budgets. Over-budget handoff fails, not core judgment.
    from scripts.intelligence import memory_trace
    result["decision_trace"] = memory_trace(result["decision_trace"])
    return result
