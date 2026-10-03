#!/usr/bin/env python3
"""Install a reviewed runtime-only Skill copy; never overwrite an existing target."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.models import ContractError
from scripts.validate_skill import ROOT, RUNTIME_FILES, SCRIPTS, validate


def install(target: Path, *, source: Path = ROOT) -> Path:
    target = target.expanduser().resolve()
    source = source.resolve()
    if target.name != "career-junshi":
        raise ContractError("Target folder must be named career-junshi")
    if target.exists():
        raise ContractError("Target exists; preserve it and choose a new installation parent")
    if source == target or source in target.parents:
        raise ContractError("Installation cannot be inside the source repository")
    errors = validate(source, runtime_only=True)
    if errors:
        raise ContractError("Source invalid: " + "; ".join(errors))
    target.parent.mkdir(parents=True, exist_ok=True)
    # Build and validate separately; failures do not leave a discoverable partial Skill.
    with tempfile.TemporaryDirectory(prefix=".career-junshi-install-", dir=target.parent) as tmp:
        staging = Path(tmp) / "career-junshi"
        staging.mkdir()
        paths = RUNTIME_FILES + [f"scripts/{s}" for s in SCRIPTS]
        paths += [str(f.relative_to(source)) for f in (source / "references").rglob("*.md")]
        for name in paths:
            src = source / name
            if src.is_symlink():
                raise ContractError("Cannot install symlinked files")
            dst = staging / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        errors = validate(staging, runtime_only=True)
        if errors:
            raise ContractError("Installation invalid: " + "; ".join(errors))
        staging.rename(target)
    return target


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", type=Path, required=True, help="Host-discoverable destination ending in career-junshi")
    args = p.parse_args(argv)
    try:
        result = install(args.target)
        print(json.dumps({"installed": str(result), "memory_enabled": False, "runtime_only": True}, ensure_ascii=False))
        return 0
    except (ContractError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
