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
from scripts.router import EXPERIENCES, ROUTES, route
from scripts.context import extract
from scripts.memory_store import MemoryStore
from scripts.io_utils import configure_cli_streams, load_json_input


def load_input(path: str):
    return load_json_input(path)


def main(argv=None) -> int:
    configure_cli_streams()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("route")
    r.add_argument("--mode", required=True, choices=sorted(ROUTES)); r.add_argument("--rejected", action="store_true")
    r.add_argument("--experience", choices=sorted(EXPERIENCES), help="Optional host-led experience; selects references without running a session")
    snapshot = sub.add_parser("import-context", help="adapt an explicitly provided private snapshot to the existing extraction packet")
    snapshot.add_argument("--input", required=True)
    snapshot.add_argument("--mode", required=True, choices=sorted(ROUTES))
    snapshot.add_argument("--output", required=True, help="New private extraction file outside Git repositories")
    resume = sub.add_parser("resume-export", help="Export reviewed, sourced resume text through a fixed LaTeX template")
    resume.add_argument("--input", required=True, help="Explicit private resume JSON")
    resume.add_argument("--output-dir", required=True, help="New private directory outside Git and the Skill installation")
    resume.add_argument("--compile", action="store_true", dest="compile_pdf", help="Request local XeLaTeX compilation and report actual checks")
    journey = sub.add_parser("journey", help="Review an explicitly supplied job-search journal; no memory or external actions")
    journey.add_argument("--input", required=True)
    journey.add_argument("--event", help="Append one supplied event to the in-memory packet; input remains unchanged")
    journey.add_argument("--output-dir", help="Explicit new private directory for checkpoint files")
    journey.add_argument("--verify-files", action="store_true", help="Read only listed resume artifacts and compare their hashes")
    journey.add_argument("--now", help="Explicit timezone-aware clock")
    journey.add_argument("--format", choices=["json", "markdown"], default="markdown")
    sub.add_parser("resume-doctor", help="Explicit synthetic English/Chinese XeLaTeX and PDF tool self-check; installs nothing")
    sources = sub.add_parser("sources", help="Browse source summaries or one detailed source card; no network or persistence")
    selection = sources.add_mutually_exclusive_group()
    selection.add_argument("--topic", help="job_search, career_choice, resume, interview, negotiation, offer, rights or safety")
    selection.add_argument("--id", dest="source_id", help="One detailed source card, such as R7")
    sources.add_argument("--limit", type=int, default=3, help="Maximum summary results, 1..10; catalog order is not a ranking")
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
        if args.command == "journey":
            from scripts.journey import review_journey, render_handoff, write_checkpoint
            packet = load_input(args.input)
            if args.event:
                packet = obj(packet, "journey")
                packet["events"] = [*items(packet.get("events"), "events", 100), load_input(args.event)]
            result = review_journey(packet, verify_files=args.verify_files, now=args.now)
            if args.output_dir:
                result["checkpoint_directory"] = write_checkpoint(packet, result, args.output_dir)
            if args.format == "markdown":
                print(render_handoff(result), end="")
                if args.output_dir: print("已生成私有接续文件：" + result["checkpoint_directory"])
                return 0
        elif args.command == "sources":
            from scripts.source_catalog import query_sources
            result = query_sources(topic=args.topic, source_id=args.source_id, limit=args.limit)
        elif args.command == "resume-doctor":
            from scripts.resume_doctor import diagnose_resume_environment
            result = diagnose_resume_environment()
            print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
            return 0 if result["status"] == "READY" else 2
        elif args.command == "resume-export":
            from scripts.resume_export import export_resume
            exported = export_resume(load_input(args.input), args.output_dir, compile_pdf=args.compile_pdf)
            result = {key: exported[key] for key in ("status", "directory", "checks")}
            print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
            failed = exported["status"] in {"COMPILATION_FAILED", "PDF_CHECKS_FAILED"}
            unavailable = args.compile_pdf and exported["checks"]["compilation"] != "COMPILED"
            return 2 if failed or unavailable else 0
        elif args.command == "import-context":
            from scripts.integration import adapt_snapshot, write_private_packet
            packet = adapt_snapshot(load_input(args.input), mode=args.mode)
            target = write_private_packet(packet, args.output)
            result = {"status": "CONTEXT_ADAPTED", "output": str(target), "memory_enabled": False,
                      "boundary": "Source labels preserved; no verification upgrade or semantic decision claimed."}
        elif args.command == "route":
            result = route(args.mode, rejected=args.rejected, experience=args.experience)
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
