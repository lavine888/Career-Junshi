"""Create a separate repeat run while preserving published evidence."""
import argparse
import json
import shutil
from pathlib import Path
from run_eval import ROOT, dump, now

parser = argparse.ArgumentParser()
parser.add_argument("--target", required=True, type=Path)
args = parser.parse_args()
target = args.target.resolve()
if target.exists():
    raise SystemExit("Target already exists; choose a new directory")
target.mkdir(parents=True)
for directory in ["prompts", "schemas"]:
    shutil.copytree(ROOT / directory, target / directory)
for directory in ["raw", "logs", "blind", "reviews", "private"]:
    (target / directory).mkdir()
for name in ["cases.json", "review-case-checks.json", "run_eval.py", "blind_eval.py", "finalize_eval.py", "new_run.py", "verify_artifacts.py"]:
    shutil.copyfile(ROOT / name, target / name)
manifest = json.loads((ROOT / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
for field in ["generation_started_at", "generation_completed_at", "valid_generations", "blind_packet_sha256", "mapping_commitment_sha256", "rubric_sha256", "blinded_at", "reviewer_model", "reviewer_reasoning_effort", "reviewer_access_probe", "review_method", "review_started_at", "review_attempts", "reviews_frozen_at", "unblinded_at", "result_sha256"]:
    manifest.pop(field, None)
manifest.update(run_id=manifest["run_id"] + "-repeat-" + now(), generation_attempts=[], probe_attempts=[], status="FROZEN_PRE_GENERATION")
dump(target / "RUN_MANIFEST.json", manifest)
dump(target / "schemas" / "probe-schema.json", {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"], "additionalProperties": False})
print("Prepared isolated repeat. Probe both models, then generate/prepare/review/finalize.")
