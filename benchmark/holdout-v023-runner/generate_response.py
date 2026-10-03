"""Send one audited input-only message to a fresh Codex context; never load rubric.

Supply --node and --codex-js for a Node CLI installation; otherwise use codex on PATH.
Outputs and event records must be new files outside the frozen holdout directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--node")
    parser.add_argument("--codex-js")
    parser.add_argument("--extraction", action="store_true")
    args = parser.parse_args()
    if bool(args.node) != bool(args.codex_js):
        parser.error("--node and --codex-js must be supplied together")
    output = args.output.resolve()
    if "holdout-v023" in output.parts:
        parser.error("Never write into the frozen holdout corpus")
    events = output.with_name(output.name + ".events.jsonl")
    record = output.with_name(output.name + ".execution.json")
    if any(p.exists() for p in [output, events, record]):
        parser.error("Preserve outputs: use new paths")
    output.parent.mkdir(parents=True, exist_ok=True)
    prompt = args.prompt.read_text(encoding="utf-8")
    cmd = [args.node, args.codex_js] if args.node else ["codex"]
    cmd += ["exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only", "--json", "--color", "never", "--cd", str(args.workspace.resolve()), "--model", "gpt-5.6-sol", "-c", 'model_reasoning_effort="high"', "-c", 'web_search="disabled"', "-c", "project_doc_max_bytes=0", "-o", str(output)]
    for feature in ["apps", "multi_agent", "remote_plugin", "hooks", "memories", "browser_use", "browser_use_external", "computer_use", "image_generation", "sleep_tool", "shell_tool"]:
        cmd += ["--disable", feature]
    if args.extraction:
        schema = output.with_name(output.name + ".schema.json")
        schema.write_text(json.dumps({"type": "object", "properties": {"packet_json": {"type": "string"}}, "required": ["packet_json"], "additionalProperties": False}), encoding="utf-8")
        cmd += ["--output-schema", str(schema)]
    cmd += ["-"]
    result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=480)
    events.write_text(result.stdout, encoding="utf-8")
    record.write_text(json.dumps({"model": "gpt-5.6-sol", "effort": "high", "reference_mode": "CONTROLLED_PRELOAD", "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "exit_code": result.returncode, "stderr": result.stderr, "boundary": "No tool invocation authorized; no rubric loaded; inspect errors before accepting output."}, indent=2) + "\n", encoding="utf-8")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
