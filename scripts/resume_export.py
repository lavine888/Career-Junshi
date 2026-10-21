"""Evidence-bound resume export; mechanical checks do not verify career claims."""
from __future__ import annotations

import copy
import hashlib
import uuid
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import quote, urlsplit

from scripts.models import CONFIDENCE, ContractError, revision_refs

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets/resume/single-column.tex"


def _object(value, required, optional=()):
    if not isinstance(value, dict) or set(value) - set(required) - set(optional) or set(required) - set(value):
        raise ContractError("Object has missing or unknown fields: " + ", ".join(required))


def _text(value, maximum=500, empty=False):
    if (not isinstance(value, str) or len(value) > maximum or (not empty and not value.strip())
            or any(unicodedata.category(c).startswith("C") for c in value)):
        raise ContractError("Text must be bounded, single-line, and free of control characters")


def _list(value, minimum=0, maximum=30):
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ContractError(f"Expected a list of {minimum}..{maximum} items")


def _references(value, known):
    _list(value, 1, 20)
    if any(not isinstance(v, str) or v not in known for v in value) or len(set(value)) != len(value):
        raise ContractError("source_ids must be unique references to supplied sources")


def validate_resume(data):
    """Return a deep copy with optional fields filled; never normalize claim wording."""
    _object(data, ("schema_version", "language", "name", "sources", "sections", "page_limit"),
            ("target_role", "contacts", "layout", "photo", "lineage"))
    if data["schema_version"] != "1" or data["language"] not in ("zh", "en"):
        raise ContractError("Expected schema_version '1' and language zh or en")
    if type(data["page_limit"]) is not int or data["page_limit"] not in (1, 2):
        raise ContractError("page_limit must be 1 or 2")
    if not isinstance(data.get("layout", "standard"), str) or data.get("layout", "standard") not in {"standard", "editorial"}:
        raise ContractError("layout must be standard or editorial")
    if not isinstance(data.get("photo", "none"), str) or data.get("photo", "none") not in {"none", "placeholder"}:
        raise ContractError("photo must be none or placeholder")
    if data.get("photo", "none") != "none" and data.get("layout", "standard") != "editorial":
        raise ContractError("photo placeholder requires editorial layout")
    if "lineage" in data:
        lineage = data["lineage"]
        _object(lineage, ("resume_id", "parent_resume_id", "opportunity_id", "claim_refs"))
        for key in ("resume_id", "parent_resume_id", "opportunity_id"):
            _text(lineage[key], 100, empty=key != "resume_id")
        revision_refs(lineage["claim_refs"])
        if not lineage["claim_refs"]:
            raise ContractError("linked resume needs at least one claim revision")
        if lineage["resume_id"] == lineage["parent_resume_id"]:
            raise ContractError("resume cannot be its own parent")
    _text(data["name"], 100)
    _text(data.get("target_role", ""), 150, empty=True)
    _list(data.get("contacts", []), maximum=8)
    for contact in data.get("contacts", []):
        _text(contact, 250)
    _list(data["sources"], 1, 100)
    known = set()
    for source in data["sources"]:
        _object(source, ("id", "description"))
        _text(source["id"], 80)
        _text(source["description"], 1500)
        if source["id"] in known:
            raise ContractError("Source ids must be unique")
        known.add(source["id"])
    _list(data["sections"], 1, 10)
    total_bullets = 0
    for section in data["sections"]:
        _object(section, ("title", "entries"))
        _text(section["title"], 100)
        _list(section["entries"], 1, 15)
        for entry in section["entries"]:
            _object(entry, ("title", "subtitle", "dates", "source_ids", "bullets"))
            for key in ("title", "subtitle", "dates"):
                _text(entry[key], 200, empty=key != "title")
            _references(entry["source_ids"], known)
            _list(entry["bullets"], 0, 12)
            total_bullets += len(entry["bullets"])
            for bullet in entry["bullets"]:
                _object(bullet, ("text", "source_ids", "confidence"))
                _text(bullet["text"], 1000)
                _references(bullet["source_ids"], known)
                if not isinstance(bullet["confidence"], str) or bullet["confidence"] not in CONFIDENCE:
                    raise ContractError("Unknown evidence confidence")
    if total_bullets > 80:
        raise ContractError("Resume may contain at most 80 bullets")
    result = copy.deepcopy(data)
    result.setdefault("target_role", "")
    result.setdefault("contacts", [])
    return result


def _escape(text):
    substitutions = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$",
                     "&": r"\&", "#": r"\#", "%": r"\%", "_": r"\_",
                     "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(substitutions.get(c, c) for c in text)


def _contact(value):
    """Only recognized web/email contacts become links; all labels stay text."""
    destination = None
    if re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value):
        destination = "mailto:" + quote(value, safe="@.+-_")
    elif re.fullmatch(r"[A-Za-z0-9:/?\[\]@!$&'()*+,;=._~%#-]+", value):
        try:
            parsed = urlsplit(value)
            if parsed.scheme in {"http", "https"} and parsed.hostname and not parsed.username and not parsed.password:
                destination = value
        except ValueError:
            pass
    if not destination:
        return _escape(value)
    # Discretionary breaks have no text-layer glyph, even within a long URL token.
    label = r"\allowbreak{}".join(_escape(char) for char in value)
    # Display-text escapes such as \textasciitilde{} alter URI targets.
    # Encode literal tildes before TeX escaping; preserve existing percent escapes.
    destination = destination.replace("~", "%7E")
    return r"\href{" + _escape(destination) + "}{" + label + "}"


def _render(data):
    if data.get("layout", "standard") == "editorial":
        return _render_editorial(data)
    body = [r"{\LARGE\bfseries " + _escape(data["name"]) + r"}\par"]
    plain = [data["name"], data["target_role"], *data["contacts"]]
    expected = [value for value in plain if value]
    if data["target_role"]:
        body.append(_escape(data["target_role"]) + r"\par")
    if data["contacts"]:
        body.append(r" \textbar{} \allowbreak{}".join(_contact(value) for value in data["contacts"]) + r"\par")
    for section in data["sections"]:
        plain.append(section["title"])
        expected.append(section["title"])
        body.append(r"\par\medskip\noindent{\large\bfseries " + _escape(section["title"]) + r"}\par\nobreak")
        for entry in section["entries"]:
            # A minipage keeps the heading with its first bullet; remaining bullets may flow.
            body.append(r"\begin{minipage}{\linewidth}")
            heading = " | ".join(entry[key] for key in ("title", "subtitle", "dates") if entry[key])
            body.append(r"\textbf{" + _escape(entry["title"]) + "}"
                        + (" | " + _escape(entry["subtitle"]) if entry["subtitle"] else "") + r"\par")
            if entry["dates"]:
                body.append(r"{\small\raggedleft " + _escape(entry["dates"]) + r"\par}")
            plain.append(heading)
            expected.extend(entry[k] for k in ("title", "subtitle", "dates") if entry[k])
            for index, bullet in enumerate(entry["bullets"]):
                prefix = "[PLANNED] " if bullet["confidence"] == "PLANNED" else ""
                body.append(r"\noindent\hangindent=1em\hangafter=1\textbullet\ " + _escape(prefix + bullet["text"]) + r"\par")
                plain.append("- " + prefix + bullet["text"])
                expected.append(prefix + bullet["text"])
                if index == 0:
                    body.append(r"\end{minipage}\par")
            if not entry["bullets"]:
                body.append(r"\end{minipage}\par")
    template = TEMPLATE.read_text(encoding="utf-8")
    # Replace the body last: user strings resembling template placeholders stay literal.
    tex = template.replace("@@CLASS@@", "ctexart" if data["language"] == "zh" else "article")
    tex = tex.replace("@@CLASS_OPTIONS@@", ",fontset=fandol" if data["language"] == "zh" else "")
    return tex.replace("@@BODY@@", "\n".join(body)), "\n".join(plain) + "\n", expected


def _render_editorial(data):
    """Escaped content through a bundled style; same fact boundaries as standard."""
    plain = [data["name"], data["target_role"], *data["contacts"]]
    expected = [v for v in plain if v]
    photo = data.get("photo", "none") == "placeholder"
    body = [r"\begin{minipage}[t]{" + (r"0.78\linewidth" if photo else r"\linewidth") + r"}\vspace{0pt}",
            r"{\color{navy}\fontsize{29}{33}\selectfont\bfseries " + _escape(data["name"]) + r"}\par\vspace{5pt}"]
    if data["target_role"]:
        body.append(r"{\fontsize{12}{16}\selectfont " + _escape(data["target_role"]) + r"}\par\vspace{7pt}")
    if data["contacts"]:
        body.append(r"{\fontsize{9.5}{14}\selectfont " + r" \textbar{} \allowbreak{}".join(_contact(v) for v in data["contacts"]) + r"\par}")
    body.append(r"\end{minipage}")
    if photo:
        body.append(r"\hfill\begin{minipage}[t]{0.18\linewidth}\vspace{0pt}\raggedleft\cvphoto\end{minipage}")
    body.append(r"\par\vspace{8pt}")
    for section in data["sections"]:
        body.append(r"\cvsection{" + _escape(section["title"]) + "}")
        plain.append(section["title"]); expected.append(section["title"])
        for entry in section["entries"]:
            body.append(r"\par\addvspace{7pt}\begin{minipage}{\linewidth}")
            body.append(r"\cventry{" + _escape(entry["title"]) + "}{" + _escape(entry["dates"]) + "}{" + _escape(entry["subtitle"]) + "}")
            plain.append(" | ".join(entry[k] for k in ("title", "dates", "subtitle") if entry[k]))
            expected.extend(entry[k] for k in ("title", "dates", "subtitle") if entry[k])
            for index, bullet in enumerate(entry["bullets"]):
                prefix = "[PLANNED] " if bullet["confidence"] == "PLANNED" else ""
                body.append(r"\cvbullet{" + _escape(prefix + bullet["text"]) + "}")
                plain.append("- " + prefix + bullet["text"]); expected.append(prefix + bullet["text"])
                if index == 0:
                    body.append(r"\end{minipage}\par")
            if not entry["bullets"]:
                body.append(r"\end{minipage}\par")
    template = (ROOT / "assets/resume/editorial.tex").read_text(encoding="utf-8")
    template = template.replace("@@CLASS@@", "ctexart" if data["language"] == "zh" else "article")
    template = template.replace("@@CLASS_OPTIONS@@", ",fontset=fandol" if data["language"] == "zh" else "")
    template = template.replace("@@CJK_FONT@@", r"\IfFontExistsTF{Microsoft YaHei}{\setCJKmainfont{Microsoft YaHei}}{}" if data["language"] == "zh" else "")
    return template.replace("@@BODY@@", "\n".join(body)), "\n".join(plain) + "\n", expected


def _output_path(directory):
    raw = Path(directory).expanduser().absolute()
    for parent in (raw, *raw.parents):
        linked = parent.is_symlink()
        if os.name == "nt" and parent.exists():
            linked = linked or bool(os.lstat(parent).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        if linked:
            raise ContractError("Output path must not use symlinks or junctions")
    target = raw.resolve()
    if target.exists() or target == ROOT or ROOT in target.parents:
        raise ContractError("Choose a new output directory outside the Skill installation")
    if any((parent / ".git").exists() or (parent / ".git").is_symlink() for parent in (target, *target.parents)):
        raise ContractError("Candidate artifacts must live outside Git repositories")
    return target


def _run(command, cwd):
    return subprocess.run(command, cwd=cwd, shell=False, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=60)


def _compact(value):
    return "".join(c for c in unicodedata.normalize("NFKC", value) if not c.isspace())


def _check_text(extracted, expected):
    """Check normalized coverage, monotonic reading order and expected multiplicity."""
    actual = _compact(extracted)
    segments = [_compact(value) for value in expected]
    missing = [i for i, value in enumerate(segments) if value not in actual]
    cursor, out_of_order, gaps = 0, [], []
    for index, value in enumerate(segments):
        position = actual.find(value, cursor)
        if position < 0:
            if index not in missing:
                out_of_order.append(index)
        else:
            gaps.append(actual[cursor:position])
            cursor = position + len(value)
    gaps.append(actual[cursor:])
    # Once every fragment is anchored in order, approved spans account for all
    # intended repetitions. Look for extra copies in the remaining gaps only:
    # removing whitespace must not create duplicates across two approved fields.
    unexpected, insufficient, seen = [], [], set()
    ordered = not missing and not out_of_order
    for index, value in enumerate(segments):
        if value in seen:
            continue
        seen.add(value)
        if ordered and any(value in gap for gap in gaps):
            unexpected.append(index)
        elif not ordered and actual.count(value) < sum(segment.count(value) for segment in segments):
            insufficient.append(index)
    occurrence = ("FAILED" if missing or unexpected or insufficient else
                  "PASSED" if ordered else "UNAVAILABLE")
    return {"text_check": "FAILED" if missing or out_of_order or occurrence == "FAILED" else "PASSED",
            "missing_text_indexes": missing,
            "text_order_check": "PASSED" if ordered else "FAILED",
            "out_of_order_text_indexes": out_of_order,
            "text_occurrence_check": occurrence,
            "unexpected_text_occurrence_indexes": unexpected,
            "insufficient_text_occurrence_indexes": insufficient}



def _compile(tex, target, expected, page_limit, *, disable_installer=False):
    compiler = shutil.which("xelatex")
    status = {"compilation": "UNAVAILABLE", "page_check": "UNAVAILABLE", "text_check": "UNAVAILABLE", "log_check": "UNAVAILABLE",
              "text_order_check": "UNAVAILABLE", "text_occurrence_check": "UNAVAILABLE",
              "visual_review": "REQUIRED", "pdf_file": None}
    if not compiler:
        status["detail"] = "xelatex is not on PATH; source files remain available"
        return status
    with tempfile.TemporaryDirectory(prefix="career-junshi-tex-") as tmp:
        work = Path(tmp)
        (work / "resume.tex").write_text(tex, encoding="utf-8")
        logs = []
        try:
            for _ in range(2):
                command = [compiler]
                if disable_installer or "miktex" in compiler.lower():
                    command.append("-disable-installer")
                result = _run([*command, "-no-shell-escape", "-halt-on-error", "-interaction=nonstopmode",
                               "resume.tex"], work)
                logs.append(result.stdout + result.stderr)
                if result.returncode:
                    status.update(compilation="FAILED", detail=(result.stdout + result.stderr)[-4000:])
                    return status
        except (OSError, subprocess.TimeoutExpired) as exc:
            status.update(compilation="FAILED", detail=type(exc).__name__)
            return status
        pdf = work / "resume.pdf"
        if not pdf.is_file():
            status.update(compilation="FAILED", detail="Compiler returned no PDF")
            return status
        shutil.copyfile(pdf, target / "resume.pdf")
        status.update(compilation="COMPILED", pdf_file="resume.pdf")
        log = "\n".join(logs)
        if (work / "resume.log").is_file():
            log += (work / "resume.log").read_text(encoding="utf-8", errors="replace")
        status["log_check"] = "FAILED" if re.search(r"Overfull \\[hv]box|Missing character:", log) else "PASSED"
        info, extract = shutil.which("pdfinfo"), shutil.which("pdftotext")
        for kind, command in (("page_check", [info, str(pdf)] if info else None),
                              ("text_check", [extract, "-enc", "UTF-8", str(pdf), "-"] if extract else None)):
            if not command:
                continue
            try:
                check = _run(command, work)
                if check.returncode:
                    status[kind] = "FAILED"
                    status.setdefault("tool_diagnostics", {})[kind] = (check.stderr or check.stdout)[-2000:]
                elif kind == "page_check":
                    match = re.search(r"^Pages:\s+(\d+)\s*$", check.stdout, re.MULTILINE)
                    status[kind] = "PASSED" if match and 1 <= int(match[1]) <= page_limit else "FAILED"
                    status["pages"] = int(match[1]) if match else None
                else:
                    status.update(_check_text(check.stdout, expected))
                    if status[kind] == "FAILED" and check.stderr:
                        status.setdefault("tool_diagnostics", {})[kind] = check.stderr[-2000:]
            except (OSError, subprocess.TimeoutExpired):
                status[kind] = "FAILED"
        return status


def export_resume(data, directory, compile_pdf=False):
    """Write new local artifacts; never claim visual approval or ATS certification."""
    if not isinstance(compile_pdf, bool):
        raise ContractError("compile_pdf must be a boolean")
    normalized = validate_resume(data)
    target = _output_path(directory)
    tex, plain, expected = _render(normalized)
    target.mkdir(parents=True, mode=0o700, exist_ok=False)
    for name, content in (("resume.tex", tex), ("resume.txt", plain),
                          ("resume-data.json", json.dumps(normalized, ensure_ascii=False, indent=2) + "\n")):
        (target / name).write_text(content, encoding="utf-8")
    checks = {"compilation": "NOT_REQUESTED", "page_check": "UNAVAILABLE", "text_check": "UNAVAILABLE", "log_check": "UNAVAILABLE",
              "text_order_check": "UNAVAILABLE", "text_occurrence_check": "UNAVAILABLE",
              "visual_review": "REQUIRED", "pdf_file": None}
    if compile_pdf:
        checks = _compile(tex, target, expected, normalized["page_limit"])
    status = "SOURCE_ONLY"
    if checks["compilation"] == "COMPILED":
        status = ("PDF_CHECKS_FAILED" if "FAILED" in (checks["page_check"], checks["text_check"], checks["log_check"])
                  else "PDF_COMPILED_AWAITING_VISUAL_REVIEW")
    elif checks["compilation"] == "FAILED":
        status = "COMPILATION_FAILED"
    lineage = normalized.get("lineage", {"resume_id": uuid.uuid4().hex,
        "parent_resume_id": "", "opportunity_id": "", "claim_refs": []})
    artifacts = [{"kind": kind, "path": str(target / name),
                  "sha256": hashlib.sha256((target / name).read_bytes()).hexdigest()}
                 for kind, name in (("tex", "resume.tex"), ("text", "resume.txt"),
                                    ("data", "resume-data.json"), ("pdf", "resume.pdf"))
                 if (target / name).is_file()]
    report = {"schema_version": "1", "status": status, "checks": checks,
              "lineage": lineage, "artifacts": artifacts, "layout": normalized.get("layout", "standard"),
              "page_limit": normalized["page_limit"], "expected_text": expected,
              "evidence_map": normalized, "semantic_verification": "NOT_PERFORMED",
              "ats_certification": "NOT_PERFORMED", "directory": str(target)}
    (target / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for artifact in target.iterdir():
        artifact.chmod(0o600)
    return report
