"""Evidence-bound resume export; mechanical checks do not verify career claims."""
from __future__ import annotations

import copy
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import unicodedata
from pathlib import Path

from scripts.models import CONFIDENCE, ContractError

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
            ("target_role", "contacts"))
    if data["schema_version"] != "1" or data["language"] not in ("zh", "en"):
        raise ContractError("Expected schema_version '1' and language zh or en")
    if type(data["page_limit"]) is not int or data["page_limit"] not in (1, 2):
        raise ContractError("page_limit must be 1 or 2")
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


def _render(data):
    body = [r"{\LARGE\bfseries " + _escape(data["name"]) + r"}\par"]
    plain = [data["name"], data["target_role"], *data["contacts"]]
    expected = [value for value in plain if value]
    for value in (data["target_role"], *data["contacts"]):
        if value:
            body.append(_escape(value) + r"\par")
    for section in data["sections"]:
        plain.append(section["title"])
        expected.append(section["title"])
        body.append(r"\par\medskip\noindent{\large\bfseries " + _escape(section["title"]) + r"}\par\nobreak")
        for entry in section["entries"]:
            # A minipage keeps the heading with its first bullet; remaining bullets may flow.
            body.append(r"\begin{minipage}{\linewidth}")
            heading = " | ".join(entry[key] for key in ("title", "subtitle", "dates") if entry[key])
            body.append(r"\textbf{" + _escape(heading) + r"}\par")
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


def _compile(tex, target, expected, page_limit):
    compiler = shutil.which("xelatex")
    status = {"compilation": "UNAVAILABLE", "page_check": "UNAVAILABLE", "text_check": "UNAVAILABLE", "log_check": "UNAVAILABLE",
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
                result = _run([compiler, "-no-shell-escape", "-halt-on-error", "-interaction=nonstopmode",
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
                elif kind == "page_check":
                    match = re.search(r"^Pages:\s+(\d+)\s*$", check.stdout, re.MULTILINE)
                    status[kind] = "PASSED" if match and 1 <= int(match[1]) <= page_limit else "FAILED"
                    status["pages"] = int(match[1]) if match else None
                else:
                    extracted = _compact(check.stdout)
                    missing = [index for index, text in enumerate(expected) if _compact(text) not in extracted]
                    status[kind] = "FAILED" if missing else "PASSED"
                    status["missing_text_indexes"] = missing
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
              "visual_review": "REQUIRED", "pdf_file": None}
    if compile_pdf:
        checks = _compile(tex, target, expected, normalized["page_limit"])
    status = "SOURCE_ONLY"
    if checks["compilation"] == "COMPILED":
        status = ("PDF_CHECKS_FAILED" if "FAILED" in (checks["page_check"], checks["text_check"], checks["log_check"])
                  else "PDF_COMPILED_AWAITING_VISUAL_REVIEW")
    elif checks["compilation"] == "FAILED":
        status = "COMPILATION_FAILED"
    report = {"schema_version": "1", "status": status, "checks": checks,
              "page_limit": normalized["page_limit"], "expected_text": expected,
              "evidence_map": normalized, "semantic_verification": "NOT_PERFORMED",
              "ats_certification": "NOT_PERFORMED", "directory": str(target)}
    (target / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for artifact in target.iterdir():
        artifact.chmod(0o600)
    return report
