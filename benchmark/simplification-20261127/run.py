"""Frozen A/B/C prompt comparison; no actual user materials or automatic publishing."""
import argparse
import json
import random
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


def source(rev, path):
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=ROOT).decode("utf-8").replace("\r\n", "\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--effort", default="medium")
    p.add_argument("--timeout", type=int, default=240)
    args = p.parse_args()
    cli = shutil.which("codex")
    if not cli:
        p.error("Install and authenticate Codex CLI first")
    out = args.output.expanduser().resolve()
    if ROOT == out or ROOT in out.parents:
        p.error("Choose an output directory outside the checkout")
    prompts = {}
    for case in DATA["cases"]:
        for arm in ("A", "B", "C"):
            sections = [DATA["baseline"]] if arm == "A" else [source(DATA["commits"][arm], "SKILL.md")]
            if arm != "A":
                if arm == "B" and not case["direct"]:
                    sections.append(source(DATA["commits"][arm], "references/practical/00-router.md"))
                sections.extend(source(DATA["commits"][arm], path) for path in case["refs"])
            prompts[(case["id"], arm)] = "\n\n".join(sections) + "\n\nUser request:\n" + case["input"] + "\n\nAnswer the user directly. Use only supplied information; no external tools."
    out.mkdir(parents=True, exist_ok=False)
    for (cid, arm), prompt in prompts.items():
        (out / f"{cid}-{arm}.prompt.txt").write_text(prompt, encoding="utf-8")
    records, packet, mapping = [], [], {}
    rng = random.SystemRandom()
    with tempfile.TemporaryDirectory() as work:
        cmd = [cli, "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only", "--json", "--color", "never", "--cd", work, "--model", args.model, "-c", 'web_search="disabled"', "-c", f'model_reasoning_effort="{args.effort}"', "-c", "project_doc_max_bytes=0"]
        for feature in ("shell_tool", "apps", "multi_agent", "remote_plugin", "hooks", "memories"):
            cmd += ["--disable", feature]

        def invoke(label, prompt):
            dest = out / (label + ".response.txt")
            started = time.monotonic()
            record = {"id": label, "status": "ERROR", "usage": None, "tool_calls": None}
            try:
                result = subprocess.run(cmd + ["--output-last-message", str(dest), "-"], input=prompt, text=True, encoding="utf-8", capture_output=True, timeout=args.timeout)
                events = []
                for line in result.stdout.splitlines():
                    try:
                        events.append(json.loads(line))
                    except ValueError:
                        pass
                calls = sum(e.get("item", {}).get("type") in ("command_execution", "mcp_tool_call", "web_search", "file_change") for e in events)
                record.update(exit_code=result.returncode, tool_calls=calls, usage=next((e.get("usage") for e in events if e.get("type") == "turn.completed"), None))
                if result.returncode == 0 and not calls and dest.exists() and dest.read_text(encoding="utf-8").strip():
                    record["status"] = "VALID"
                # Transport logs may include account metadata; do not publish them.
                (out / (label + ".stderr.txt")).write_text(result.stderr, encoding="utf-8")
            except subprocess.TimeoutExpired:
                record["status"] = "TIMEOUT"
            except OSError as exc:
                record["error"] = str(exc)
            record["seconds"] = round(time.monotonic() - started, 2)
            return record

        probe = invoke("probe", "Return exactly READY, without tools.")
        (out / "probe.json").write_text(json.dumps(probe, indent=2), encoding="utf-8")
        if probe["status"] != "VALID" or (out / "probe.response.txt").read_text(encoding="utf-8").strip() != "READY":
            raise SystemExit("Model access probe failed; no generations started")
        for case in DATA["cases"]:
            arms = ["A", "B", "C"]
            rng.shuffle(arms)
            answers = {}
            for index, arm in enumerate(arms, 1):
                cid = case["id"]
                label = f"{cid}-{index}"
                mapping[label] = arm
                record = invoke(label, prompts[(cid, arm)])
                records.append(record)
                if record["status"] == "VALID":
                    answers[label] = (out / (label + ".response.txt")).read_text(encoding="utf-8")
                (out / "manifest.json").write_text(json.dumps({"model": args.model, "effort": args.effort, "commits": DATA["commits"], "records": records}, indent=2), encoding="utf-8")
                (out / "private-mapping.json").write_text(json.dumps(mapping, indent=2), encoding="utf-8")
            packet.append({"id": case["id"], "input": case["input"], "checks": case["checks"], "responses": answers})
            (out / "blind-packet.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Valid generations: {sum(r['status'] == 'VALID' for r in records)}/{len(records)}. Share only blind-packet.json for review.")


if __name__ == "__main__":
    main()
