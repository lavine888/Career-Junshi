"""Tool-disabled, frozen-prompt evaluator. CLI transport logs stay local."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
DIMENSIONS = ["Situation Understanding", "Evidence Discipline", "Fact / Inference / Unknown separation", "Bottleneck Identification", "Recommendation Clarity", "Actionability", "Opportunity Cost Awareness", "Counterfactual Quality", "Reconsider Condition", "Stop / Pivot Quality", "Personal-context usage", "Unsupported-claim avoidance"]
HARD_FAILURES = ["FABRICATED_FACT", "NEGATION_FLIP", "CONDITIONAL_AS_FACT", "HEARSAY_AS_FACT", "TEAM_TO_SOLE", "DEMO_TO_PRODUCTION", "NO_REPLY_TO_REJECTION", "SUCCESS_TO_CAUSATION", "UNSUPPORTED_METRIC", "IGNORED_CONSTRAINT", "NO_RECOMMENDATION", "NO_ACTION", "NO_STOP_CONDITION"]


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cli():
    if os.name == "nt" and Path("D:/Nodejs/node.exe").exists() and Path("D:/Nodejs/node_global/node_modules/@openai/codex/bin/codex.js").exists():
        return ["D:/Nodejs/node.exe", "D:/Nodejs/node_global/node_modules/@openai/codex/bin/codex.js"]
    executable = shutil.which("codex")
    if not executable:
        raise RuntimeError("Install and authenticate Codex CLI before reproducing")
    return [executable]


def command(model, effort):
    cmd = cli() + ["exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only", "--json", "--color", "never", "--cd", str(ROOT), "--model", model, "-c", 'web_search="disabled"', "-c", f'model_reasoning_effort="{effort}"', "-c", "project_doc_max_bytes=0"]
    for feature in ["shell_tool", "apps", "multi_agent", "remote_plugin", "hooks", "memories"]:
        cmd += ["--disable", feature]
    return cmd


def attempt(name, prompt_path, output_dir, schema, model, effort, timeout):
    output = ROOT / output_dir / (name + ".json")
    if output.exists():
        raise RuntimeError("Refusing to replace immutable output: " + output.name)
    record = {"attempt_id": name, "model": model, "settings": {"reasoning_effort": effort, "tools": "disabled", "timeout_seconds": timeout}, "started_at": now(), "raw_output_path": output_dir + "/" + output.name, "prompt_sha256": sha(prompt_path), "error": None}
    start = time.monotonic()
    try:
        process = subprocess.run(command(model, effort) + ["--output-schema", str(schema), "--output-last-message", str(output), "-"], input=prompt_path.read_text(encoding="utf-8"), capture_output=True, text=True, encoding="utf-8", timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        # Full transport logs can contain local/account metadata: never publish.
        (ROOT / "logs" / (name + ".jsonl")).write_text(process.stdout, encoding="utf-8")
        (ROOT / "logs" / (name + ".stderr")).write_text(process.stderr, encoding="utf-8")
        events = [json.loads(line) for line in process.stdout.splitlines() if line.startswith("{")]
        tools = [e for e in events if e.get("item", {}).get("type") in {"command_execution", "mcp_tool_call", "web_search", "file_change"}]
        record["tool_calls_observed"] = len(tools)
        record["exit_code"] = process.returncode
        record["usage"] = next((e.get("usage") for e in events if e.get("type") == "turn.completed"), None)
        if process.returncode:
            record["status"] = "MODEL_ERROR"
            record["error"] = [e.get("message", e.get("error")) for e in events if e.get("type") in {"error", "turn.failed"}] or ["Nonzero CLI exit"]
        elif tools or not output.exists():
            record["status"] = "INVALID_OUTPUT"
            record["error"] = "Tool invocation or missing final output"
        else:
            result = json.loads(output.read_text(encoding="utf-8"))
            if not isinstance(result, dict):
                raise ValueError("Final output must be an object")
            record["status"] = "VALID"
    except subprocess.TimeoutExpired as exc:
        record["status"] = "TIMEOUT"
        record["error"] = "Generation exceeded frozen timeout"
        for suffix, data in [("jsonl", exc.stdout), ("stderr", exc.stderr)]:
            if data:
                (ROOT / "logs" / (name + "." + suffix)).write_bytes(data.encode() if isinstance(data, str) else data)
    except (OSError, ValueError) as exc:
        record["status"] = "INVALID_OUTPUT"
        record["error"] = str(exc)
    record["completed_at"] = now()
    record["seconds"] = round(time.monotonic() - start, 2)
    if output.exists():
        record["raw_sha256"] = sha(output)
    return record


def generations():
    manifest = json.loads((ROOT / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    assert any(r.get("status") == "AVAILABLE" and r["model"] == manifest["generation_model"] for r in manifest["probe_attempts"]), "Probe actual model access before running"
    assert sha(ROOT / "cases.json") == manifest["case_sha256"]
    for p in manifest["prompts"]:
        assert sha(ROOT / p["path"]) == p["sha256"]
    jobs = []
    for i, case in enumerate(cases):
        for version in (["v01", "v021"] if i % 2 == 0 else ["v021", "v01"]):
            jobs.append((case["case_id"], version))
    assert not manifest["generation_attempts"], "Create a new run rather than overwrite attempts"
    manifest["status"] = "GENERATING"
    manifest["generation_started_at"] = now()
    dump(ROOT / "RUN_MANIFEST.json", manifest)
    with concurrent.futures.ThreadPoolExecutor(max_workers=manifest["parallelism"]) as pool:
        futures = {pool.submit(attempt, f"{cid}-{version}", ROOT / "prompts" / f"{cid}-{version}.txt", "raw", ROOT / "schemas" / "response-schema.json", manifest["generation_model"], manifest["reasoning_effort"], manifest["timeout_seconds"]): (cid, version) for cid, version in jobs}
        for future in concurrent.futures.as_completed(futures):
            cid, version = futures[future]
            record = future.result()
            record.update({"case_id": cid, "skill_version": version})
            if record["status"] == "VALID":
                obj = json.loads((ROOT / record["raw_output_path"]).read_text(encoding="utf-8"))
                if set(obj) != {"case_id", "response"} or obj["case_id"] != cid or not isinstance(obj["response"], str) or not obj["response"].strip():
                    record.update(status="INVALID_OUTPUT", error="Missing/mismatched final response")
                record["response_characters"] = len(obj.get("response", ""))
            manifest["generation_attempts"].append(record)
            dump(ROOT / "RUN_MANIFEST.json", manifest)
            print(json.dumps({"completed": len(manifest["generation_attempts"]), "total": 30, "case": cid, "version": version, "status": record["status"], "seconds": record["seconds"]}), flush=True)
    manifest["generation_completed_at"] = now()
    manifest["valid_generations"] = sum(r["status"] == "VALID" for r in manifest["generation_attempts"])
    manifest["status"] = "GENERATIONS_FROZEN"
    dump(ROOT / "RUN_MANIFEST.json", manifest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["generate", "probe"])
    parser.add_argument("--model")
    parser.add_argument("--reviewer", action="store_true")
    args = parser.parse_args()
    if args.mode == "generate":
        generations()
    else:
        if not args.model:
            parser.error("probe requires --model, using an identifier observed in this authenticated environment")
        p = ROOT / "logs" / "probe-prompt.txt"
        p.write_text('No tools or external information. Return JSON exactly {"answer":"READY"}.', encoding="utf-8")
        record = attempt("access-probe-" + args.model, p, "logs", ROOT / "schemas" / "probe-schema.json", args.model, "high", 120)
        # Probe schema requires a minimal JSON answer, distinct from case outputs.
        if record["status"] == "VALID":
            obj = json.loads((ROOT / record["raw_output_path"]).read_text(encoding="utf-8"))
            record["status"] = "AVAILABLE" if obj.get("answer") == "READY" else "INVALID_OUTPUT"
        if args.reviewer:
            dump(ROOT / "reviewer-probe.json", {**record, "reasoning_effort": "high"})
        else:
            manifest = json.loads((ROOT / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
            assert args.model == manifest["generation_model"], "Keep the selected generation model fixed"
            manifest["probe_attempts"].append(record)
            dump(ROOT / "RUN_MANIFEST.json", manifest)
        print(json.dumps(record, ensure_ascii=False), flush=True)
