#!/usr/bin/env python3
"""Career Junshi structured helpers. Natural-language conversations run in the Skill host."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.actions import write_artifacts
from scripts.decision import decide, render
from scripts.feedback_loop import feedback_next_move
from scripts.method_adapter import review_pattern
from scripts.models import ContractError, audit_claim, items, obj, timestamp
from scripts.router import ROUTES, route


def load_input(path: str):
    source = Path(path)
    if source.stat().st_size > 256 * 1024:
        raise ContractError("Structured input must be <= 256 KiB; extract compact context first")
    return json.loads(source.read_text(encoding="utf-8-sig"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("route")
    r.add_argument("--mode", required=True, choices=sorted(ROUTES)); r.add_argument("--rejected", action="store_true")
    for cmd in ("decide", "audit", "feedback", "pattern"):
        p = sub.add_parser(cmd); p.add_argument("--input", required=True)
        if cmd == "decide":
            p.add_argument("--now", help="Explicit ISO timestamp for reproducible scenarios")
            p.add_argument("--format", choices=["json", "markdown"], default="markdown")
            p.add_argument("--artifacts-dir", help="Explicit output directory; existing files are preserved")
    args = parser.parse_args(argv)
    try:
        if args.command == "route":
            result = route(args.mode, rejected=args.rejected)
        else:
            data = load_input(args.input)
            if args.command == "decide":
                now = datetime.fromisoformat(timestamp(args.now, "now").replace("Z", "+00:00")) if args.now else None
                result = decide(obj(data, "situation"), now=now)
                if args.artifacts_dir:
                    result["generated_artifacts"] = write_artifacts(result, args.artifacts_dir)
                if args.format == "markdown":
                    print(render(result), end="")
                    if args.artifacts_dir:
                        print("\n已生成：\n" + "\n".join(result["generated_artifacts"]))
                    return 0
            elif args.command == "audit":
                claims = data.get("claims", [data]) if isinstance(data, dict) else data
                result = [audit_claim(c) for c in items(claims, "claims", 20)]
            elif args.command == "feedback":
                result = feedback_next_move(obj(data, "outcome"))
            else:
                result = review_pattern(data)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ContractError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
