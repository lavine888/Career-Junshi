#!/usr/bin/env python3
"""Validate distributable files, routing, links, context budget and Python syntax."""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.router import ROUTES, route

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DOCS = ["ARCHITECTURE.md", "EVIDENCE.md", "MEMORY.md", "INTEGRATION.md", "ACTIONS.md"]
RUNTIME_FILES = ["SKILL.md", "LICENSE", "agents/openai.yaml", "documentation/ATTRIBUTION.md"] + [f"documentation/{name}" for name in RUNTIME_DOCS] + [
    "documentation/licenses/Goutoujunshi.txt", "documentation/licenses/Career-Alpha.txt"]
SCRIPTS = ["__init__.py", "models.py", "router.py", "decision.py", "memory_store.py", "feedback_loop.py",
           "method_adapter.py", "actions.py", "junshi.py", "validate_skill.py", "install_skill.py"]


def validate(root: Path, *, runtime_only=False) -> list[str]:
    root = root.resolve()
    errors = []
    required = RUNTIME_FILES + [f"scripts/{s}" for s in SCRIPTS]
    required += list(dict.fromkeys(p for refs in ROUTES.values() for p in refs))
    required += ["references/practical/rejection.md", "references/practical/00-router.md", "references/practical/career-memory.md"]
    if not runtime_only:
        required += ["README.md", "README_EN.md", "documentation/ATTRIBUTION.md", "documentation/MVP_REPORT.md",
                     "tests/scenarios/test_scenarios.py", "tests/regression/test_evidence.py"]
        required += [f"cases/{case}/{name}" for case in ("interview", "follow-up", "offer") for name in ("input.json", "request.md", "output.md")]
    for path in required:
        if not (root / path).is_file():
            errors.append(f"Missing required file: {path}")
    skill = root / "SKILL.md"
    if skill.is_file():
        content = skill.read_text(encoding="utf-8")
        match = re.match(r"\A---\nname: career-junshi\ndescription: ([^\n]+)\n---\n", content)
        if not match or (match and not 20 <= len(match[1]) <= 1024):
            errors.append("Invalid Skill name or frontmatter description")
        if len(content) > 5500 or len(content.splitlines()) > 150:
            errors.append("Skill exceeds lightweight context budget: 5500 chars / 150 lines")
        if re.search(r"\b(?:TODO|TBD|FIXME)\b", content):
            errors.append("Skill contains unfinished instructions")
    metadata = root / "agents/openai.yaml"
    if metadata.is_file():
        content = metadata.read_text(encoding="utf-8")
        if '$career-junshi' not in content or 'allow_implicit_invocation: true' not in content:
            errors.append("Metadata lacks invocation or changes automatic discovery")
        short = re.search(r'^  short_description: "([^"]+)"$', content, re.M)
        if not short or not 25 <= len(short[1]) <= 64:
            errors.append("Metadata short_description must be 25–64 characters")
    for mode in ROUTES:
        refs = route(mode)["references"]
        if not 1 <= len(refs) <= 3:
            errors.append(f"Invalid reference budget: {mode}")
    files = [skill] + list((root / "references").rglob("*.md"))
    files += [root / "documentation" / n for n in RUNTIME_DOCS]
    if not runtime_only:
        files += [root / "README.md", root / "README_EN.md", root / "documentation/ATTRIBUTION.md", root / "documentation/MVP_REPORT.md"]
    for f in files:
        if not f.is_file():
            continue
        content = f.read_text(encoding="utf-8")
        for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            if re.match(r"^[a-z][a-z0-9+.-]*://|^#|^mailto:", href, re.I):
                continue
            href = unquote(href.split("#")[0]).strip("<>")
            target = (f.parent / href).resolve()
            if root not in target.parents and target != root:
                errors.append(f"Link escapes package: {f.relative_to(root)} → {href}")
            elif not target.exists():
                errors.append(f"Broken link: {f.relative_to(root)} → {href}")
        if re.search(r"[A-Z]:[\\/]Codex-Workspace[\\/]Obsidian|[A-Z]:[\\/]Users[\\/]", content, re.I):
            errors.append(f"Machine-specific private dependency: {f.relative_to(root)}")
    for f in (root / "scripts").rglob("*.py"):
        try:
            ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        except (SyntaxError, UnicodeError) as exc:
            errors.append(f"Invalid Python: {f.name}: {exc}")
    for f in root.rglob("*"):
        if ".git" in f.relative_to(root).parts:
            continue
        if f.is_symlink():
            errors.append(f"Distributable contains symlink: {f.relative_to(root)}")
        if f.is_file() and (f.suffix in {".sqlite3", ".db"} or f.name == ".env"):
            errors.append(f"Private state in package: {f.relative_to(root)}")
    return errors


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--runtime-only", action="store_true")
    args = p.parse_args(argv)
    errors = validate(args.root, runtime_only=args.runtime_only)
    print(json.dumps({"valid": not errors, "errors": errors, "scope": "packaging / links / routing / syntax, not model behavior"}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
