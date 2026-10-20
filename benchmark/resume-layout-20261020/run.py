"""Run four synthetic layout cases through the installed XeLaTeX export pipeline.

Example (output must be a new directory outside every Git repository):
  python benchmark/resume-layout-20261020/run.py --output-root D:/private/layout-run \
    --tool-bin D:/Tools/Poppler/poppler-26.09.0/Library/bin \
    --tool-bin D:/Tools/MiKTeX/miktex/bin/x64 --render

This checks mechanical results only. Every PDF page still needs human visual review.
The intentional overflow PDF is a rejected artifact, never an accepted resume.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY))
from scripts.models import ContractError
from scripts.resume_export import export_resume

CASES = {
    "dense-zh": 1,
    "two-page-zh": 2,
    "links-mixed": 1,
    "overflow": None,
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--tool-bin", type=Path, action="append", default=[],
                        help="Prepend a binary directory for this process only; repeat as needed")
    parser.add_argument("--render", action="store_true",
                        help="Render every page with pdftoppm; this does not grant visual approval")
    args = parser.parse_args(argv)
    if args.output_root.exists():
        parser.error("Choose a new output root; historical runs are never overwritten")
    for binary_dir in args.tool_bin:
        if not binary_dir.is_dir():
            parser.error("Tool directory does not exist: " + str(binary_dir))
    os.environ["PATH"] = os.pathsep.join([*(str(p.absolute()) for p in args.tool_bin),
                                         os.environ.get("PATH", "")])
    required = ["xelatex", "pdfinfo", "pdftotext"] + (["pdftoppm"] if args.render else [])
    unavailable = [name for name in required if not shutil.which(name)]
    if unavailable:
        parser.error("Required tools are not on PATH: " + ", ".join(unavailable))
    summary = {"schema_version": "1", "fixture_kind": "SYNTHETIC_PUBLIC",
               "visual_review": "REQUIRED", "cases": []}
    root = args.output_root.absolute()
    for name, expected_pages in CASES.items():
        row = {"case": name, "expected_pages": expected_pages,
               "delivery_status": "REJECTED", "rendered_pages": []}
        try:
            data = json.loads((Path(__file__).parent / "inputs" / (name + ".json")).read_text(encoding="utf-8"))
            report = export_resume(data, root / name, compile_pdf=True)
            checks = report["checks"]
            row.update(status=report["status"], checks=checks)
            if name == "overflow":
                passed = (report["status"] == "PDF_CHECKS_FAILED"
                          and checks.get("compilation") == "COMPILED"
                          and checks.get("page_check") == "FAILED"
                          and isinstance(checks.get("pages"), int) and checks["pages"] > 1)
            else:
                failed_checks = [key for key, value in checks.items()
                                 if key.endswith("_check") and value != "PASSED"]
                passed = (report["status"] == "PDF_COMPILED_AWAITING_VISUAL_REVIEW"
                          and checks.get("pages") == expected_pages and not failed_checks)
                row["delivery_status"] = "AWAITING_VISUAL_REVIEW" if passed else "REJECTED"
            if args.render and checks.get("compilation") == "COMPILED":
                render_dir = root / name / "rendered"
                render_dir.mkdir()
                result = subprocess.run([shutil.which("pdftoppm"), "-png", "-r", "120",
                                         str(root / name / "resume.pdf"), str(render_dir / "page")],
                                        capture_output=True, text=True, encoding="utf-8",
                                        errors="replace", timeout=120, check=False)
                images = sorted(render_dir.glob("page-*.png"))
                row["rendered_pages"] = [str(p.relative_to(root)) for p in images]
                render_ok = result.returncode == 0 and len(images) == checks.get("pages")
                if not render_ok:
                    row["render_error"] = result.stderr[-1000:]
                    passed = False
                    row["delivery_status"] = "REJECTED"
            row["expectation"] = "PASSED" if passed else "FAILED"
        except (ContractError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
            row.update(expectation="FAILED", delivery_status="REJECTED",
                       error=f"{type(exc).__name__}: {exc}")
        summary["cases"].append(row)
        print(name + ": " + row["expectation"], flush=True)
        # A rejected output root must not be created by the runner after validation fails.
        if not root.exists():
            print(json.dumps(row, ensure_ascii=False), file=sys.stderr)
            return 1
    summary["expectation"] = "PASSED" if all(r["expectation"] == "PASSED" for r in summary["cases"]) else "FAILED"
    (root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Summary: " + str(root / "summary.json"), flush=True)
    return 0 if summary["expectation"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
