"""Explicit local TeX/PDF probe with synthetic content; never reads candidate files."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from scripts.resume_export import _compile, _render, _run


def diagnose_resume_environment():
    tools = {}
    with tempfile.TemporaryDirectory(prefix="career-junshi-doctor-") as temporary:
        work = Path(temporary)
        for name, flag in (("xelatex", "--version"), ("pdfinfo", "-v"), ("pdftotext", "-v")):
            executable = shutil.which(name)
            item = {"path": executable, "version": None, "status": "UNAVAILABLE"}
            if executable:
                try:
                    result = _run([executable, flag], work)
                    lines = (result.stdout + result.stderr).splitlines()
                    item.update(status="AVAILABLE" if result.returncode == 0 else "FAILED",
                                version=lines[0][:300] if lines else None)
                except (OSError, subprocess.TimeoutExpired) as exc:
                    item.update(status="FAILED", detail=type(exc).__name__)
            tools[name] = item
        probes = []
        if tools["xelatex"]["status"] == "AVAILABLE":
            for language, name, sentence in (
                    ("zh", "中文字体自检", "仅用于中文提取检查：原型 100% & quality_check。"),
                    ("en", "Synthetic Resume Probe", "Literal labels: 100% & quality_check; no candidate data.")):
                data = {"language": language, "name": name, "target_role": "", "contacts": [],
                        "sections": [{"title": "Probe", "entries": [{"title": "Synthetic example",
                            "subtitle": "", "dates": "", "bullets": [{"text": sentence, "confidence": "SELF_REPORTED"}]}]}]}
                target = work / language
                target.mkdir()
                tex, _, expected = _render(data)
                probes.append({"language": language, "checks": _compile(
                    tex, target, expected, 1,
                    disable_installer="miktex" in (tools["xelatex"]["version"] or "").lower())})
        ready = (all(t["status"] == "AVAILABLE" for t in tools.values()) and len(probes) == 2
                 and all(p["checks"]["compilation"] == "COMPILED"
                         and all(p["checks"][k] == "PASSED" for k in ("page_check", "text_check", "log_check"))
                         for p in probes))
    return {"status": "READY" if ready else "NOT_READY", "tools": tools, "probes": probes,
            "temporary_probe_files": "REMOVED",
            "scope": "Local synthetic English/Chinese compilation and PDF text checks only; no candidate files read, no package installation, no visual or ATS certification.",
            "next_step": ("Run resume-export with the reviewed private input; inspect every actual PDF page."
                          if ready else "Use the failing probe and tool paths to repair the local environment, then rerun; source-only export remains available.")}
