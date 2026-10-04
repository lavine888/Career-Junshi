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
from scripts.context import extract
from scripts.memory_store import MemoryStore


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
    h = sub.add_parser("host-decide", help="Validate a host judgment; never choose its career strategy")
    h.add_argument("--input", required=True, help="Host-produced Decision Envelope v2")
    h.add_argument("--context", required=True, help="Original session-only source context")
    h.add_argument("--repair-input", help="One host correction; original attempt retained in debug output")
    h.add_argument("--now", help="Explicit timezone-aware scenario clock")
    h.add_argument("--format", choices=["markdown", "json"], default="markdown")
    h.add_argument("--debug-decision", action="store_true")
    h.add_argument("--artifacts-dir")
    h.add_argument("--save-subject", help="Append compressed decision only to an already active consented store")
    h.add_argument("--memory-directory")
    for cmd in ("decide", "extract", "audit", "feedback", "pattern"):
        p = sub.add_parser(cmd)
        if cmd == "decide":
            inputs = p.add_mutually_exclusive_group(required=True)
            inputs.add_argument("--input"); inputs.add_argument("--extraction")
        else:
            p.add_argument("--input", required=True)
        if cmd == "decide":
            p.add_argument("--now", help="Explicit ISO timestamp for reproducible scenarios")
            p.add_argument("--format", choices=["json", "markdown"], default="markdown")
            p.add_argument("--details", action="store_true", help="Show sourced facts and inference detail in Markdown")
            p.add_argument("--artifacts-dir", help="Explicit output directory; existing files are preserved")
            p.add_argument("--use-similar", action="store_true", help="Recall only from already active, explicitly consented memory")
            p.add_argument("--memory-directory", help="Private memory directory")
    args = parser.parse_args(argv)
    try:
        if args.command == "host-decide":
            from scripts.envelope import review_with_repair, render_envelope, compile_artifacts, memory_handoff
            now = datetime.fromisoformat(timestamp(args.now, "now").replace("Z", "+00:00")) if args.now else None
            raw, context = load_input(args.input), load_input(args.context)
            repair = (lambda original, issues: load_input(args.repair_input)) if args.repair_input else None
            result = review_with_repair(raw, context, repair, now=now)
            if result["status"] != "ACCEPT":
                if args.debug_decision or args.format == "json":
                    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
                else:
                    print("材料边界仍需修正；当前建议暂不执行。先核对缺证表述与来源。")
                return 2
            e = result["envelope"]
            if args.artifacts_dir:
                result["artifacts"] = compile_artifacts(e, context, args.artifacts_dir, now=now)
            if args.save_subject:
                result["memory"] = MemoryStore(args.memory_directory).record_decision(args.save_subject, memory_handoff(e, context, now=now))
            if args.debug_decision or args.format == "json":
                print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
            else:
                print(render_envelope(e), end="")
            return 0
        if args.command == "route":
            result = route(args.mode, rejected=args.rejected)
        else:
            data = load_input(args.extraction if args.command == "decide" and args.extraction else args.input)
            if args.command == "decide":
                now = datetime.fromisoformat(timestamp(args.now, "now").replace("Z", "+00:00")) if args.now else None
                if args.extraction:
                    data = extract(obj(data, "extraction"), now=now)
                result = decide(obj(data, "situation"), now=now)
                if args.use_similar:
                    pairs = MemoryStore(args.memory_directory).similar(result["metadata"], now=now)
                    result = decide(data, now=now, history=pairs)
                if args.artifacts_dir:
                    result["generated_artifacts"] = write_artifacts(result, args.artifacts_dir)
                if args.format == "markdown":
                    print(render(result, details=args.details), end="")
                    if args.artifacts_dir:
                        print("\n已生成：\n" + "\n".join(result["generated_artifacts"]))
                    return 0
            elif args.command == "extract":
                result = extract(obj(data, "extraction"))
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
