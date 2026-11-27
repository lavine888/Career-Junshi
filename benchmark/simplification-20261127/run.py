"""Frozen A/B/C prompt comparison; no actual user materials or automatic publishing."""
import argparse
import hashlib
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


def command(cli, work, model, effort):
    cmd = [
        cli, "exec", "--ignore-user-config", "--ignore-rules", "--ephemeral",
        "--skip-git-repo-check", "--sandbox", "read-only", "--json",
        "--color", "never", "--cd", work, "--model", model,
        "-c", 'web_search="disabled"', "-c", f'model_reasoning_effort="{effort}"',
        "-c", "project_doc_max_bytes=0",
    ]
    for feature in ("shell_tool", "apps", "multi_agent", "multi_agent_v2", "remote_plugin", "hooks", "memories"):
        cmd += ["--disable", feature]
    return cmd


def invoke(cmd, out, label, prompt, timeout):
    dest = out / (label + ".response.txt")
    started = time.monotonic()
    record = {"id": label, "status": "ERROR", "usage": None, "tool_calls": None}
    try:
        result = subprocess.run(cmd + ["--output-last-message", str(dest), "-"], input=prompt, text=True, encoding="utf-8", capture_output=True, timeout=timeout)
        events = []
        for line in result.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
        # Execution items can emit started, updated and completed events.
        tools = {e["item"]["id"]: e["item"]["type"] for e in events
                 if "id" in e.get("item", {}) and e["item"].get("type")
                 not in ("agent_message", "reasoning", "error", "todo_list")}
        thread = next((e.get("thread_id") for e in events if e.get("type") == "thread.started"), None)
        record.update(exit_code=result.returncode, thread_id=thread, tool_calls=len(tools),
                      tool_types=list(tools.values()),
                      usage=next((e.get("usage") for e in events if e.get("type") == "turn.completed"), None))
        if tools:
            record["status"] = "TOOL_USED"
        elif (result.returncode == 0 and thread and record["usage"] and dest.exists()
              and dest.read_text(encoding="utf-8").strip()):
            record["status"] = "VALID"
        # Transport logs may include account metadata; do not publish them.
        (out / (label + ".stderr.txt")).write_text(result.stderr, encoding="utf-8")
        (out / (label + ".events.jsonl")).write_text(result.stdout, encoding="utf-8")
    except subprocess.TimeoutExpired as exc:
        record["status"] = "TIMEOUT"
        for suffix, partial in (("events.jsonl", exc.stdout), ("stderr.txt", exc.stderr)):
            if partial:
                (out / f"{label}.{suffix}").write_bytes(partial)
    except OSError as exc:
        record["error"] = str(exc)
    record["seconds"] = round(time.monotonic() - started, 2)
    return record


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--effort", default="medium", choices=("low", "medium", "high", "xhigh"))
    p.add_argument("--timeout", type=int, default=240)
    p.add_argument("--candidate", action="store_true",
                   help="Replay the nine frozen inputs with the current checkout, without changing A/B/C")
    args = p.parse_args()
    cli = shutil.which("codex.exe") or shutil.which("codex")
    if not cli:
        p.error("Install and authenticate Codex CLI first")
    out = args.output.expanduser().resolve()
    if ROOT == out or ROOT in out.parents:
        p.error("Choose an output directory outside the checkout")
    arm_names = ("D",) if args.candidate else ("A", "B", "C")
    prompts = {}
    for case in DATA["cases"]:
        for arm in arm_names:
            if arm == "D":
                paths = ["SKILL.md"]
                if not case["direct"]:
                    paths.append("references/practical/00-router.md")
                sections = [(ROOT / path).read_text(encoding="utf-8")
                            for path in (*paths, *case["refs"])]
            elif arm == "A":
                sections = [DATA["baseline"]]
            else:
                sections = [source(DATA["commits"][arm], "SKILL.md")]
                if arm == "B" and not case["direct"]:
                    sections.append(source(DATA["commits"][arm], "references/practical/00-router.md"))
                sections.extend(source(DATA["commits"][arm], path) for path in case["refs"])
            prompts[(case["id"], arm)] = "\n\n".join(sections) + "\n\nUser request:\n" + case["input"] + "\n\nAnswer the user directly. Use only supplied information; no external tools."
    out.mkdir(parents=True, exist_ok=False)
    metadata = {"model": args.model, "effort": args.effort, "commits": DATA["commits"],
                "candidate": args.candidate, "prompt_sha256": {}}
    for (cid, arm), prompt in prompts.items():
        name = f"{cid}-{arm}.prompt.txt"
        payload = prompt.encode("utf-8")
        (out / name).write_bytes(payload)
        metadata["prompt_sha256"][name] = hashlib.sha256(payload).hexdigest()
    records, packet, mapping = [], [], {}
    rng = random.SystemRandom()
    with tempfile.TemporaryDirectory(dir=out) as work:
        cmd = command(cli, work, args.model, args.effort)

        probe = invoke(cmd, out, "probe", "Return exactly READY, without tools.", args.timeout)
        (out / "probe.json").write_text(json.dumps(probe, indent=2), encoding="utf-8")
        if probe["status"] != "VALID" or (out / "probe.response.txt").read_text(encoding="utf-8").strip() != "READY":
            raise SystemExit("Model access probe failed; no generations started")
        for case in DATA["cases"]:
            arms = list(arm_names)
            rng.shuffle(arms)
            answers = {}
            for index, arm in enumerate(arms, 1):
                cid = case["id"]
                label = f"{cid}-{index}"
                mapping[label] = arm
                record = invoke(cmd, out, label, prompts[(cid, arm)], args.timeout)
                records.append(record)
                print(f"{label}: {record['status']} ({record['seconds']}s)", flush=True)
                if record["status"] == "VALID":
                    answers[label] = (out / (label + ".response.txt")).read_text(encoding="utf-8")
                (out / "manifest.json").write_text(json.dumps({**metadata, "records": records}, indent=2), encoding="utf-8")
                (out / "private-mapping.json").write_text(json.dumps(mapping, indent=2), encoding="utf-8")
            packet.append({"id": case["id"], "input": case["input"], "checks": case["checks"], "responses": answers})
            (out / "blind-packet.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    valid = sum(r["status"] == "VALID" for r in records)
    threads = {r["thread_id"] for r in records if r["status"] == "VALID"}
    print(f"Valid generations: {valid}/{len(records)}. Share only blind-packet.json for review.")
    return 0 if valid == len(records) == len(threads) else 1


if __name__ == "__main__":
    raise SystemExit(main())
