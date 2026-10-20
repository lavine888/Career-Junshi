"""Check archive integrity and review excerpts, not semantic grades or hiring effects."""
from pathlib import Path
import hashlib
import json


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    expected = manifest["sha256"]
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.name != "MANIFEST.json"
    }
    assert actual == set(expected), "Archive has missing or unexpected files"
    for name, digest in expected.items():
        path = (root / name).resolve()
        assert path.is_relative_to(root), "Archive path escapes its root"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
    cases = ["U01", "U02", "U03", "U04", "U05"]
    for case in cases:
        for turn in (1, 2, 3):
            assert (root / "inputs" / case / f"turn-{turn}.md").read_text(encoding="utf-8").strip()
            assert (root / "responses" / case / f"turn-{turn}.md").read_text(encoding="utf-8").strip()
    review = json.loads((root / "review.json").read_text(encoding="utf-8"))
    assert {case["id"] for case in review["cases"]} == set(cases)
    excerpt_count = 0
    for case in review["cases"]:
        assert case["overall"] in {"PASS", "PARTIAL", "FAIL", "UNASSESSABLE"}
        for item in case["checks"]:
            assert item["rating"] in {"PASS", "PARTIAL", "FAIL", "UNASSESSABLE"}
        for item in case["checks"] + case.get("frictions", []):
            for evidence in item["evidence"]:
                answer = (root / "responses" / case["id"] / f"turn-{evidence['turn']}.md").read_text(encoding="utf-8")
                assert evidence["quote"] and evidence["quote"] in answer, (case["id"], evidence)
                excerpt_count += 1
    print(json.dumps({"archive_files": len(expected), "synthetic_cases": 5,
                      "captured_assistant_turns": 15, "matching_review_excerpts": excerpt_count,
                      "scope": "File integrity and exact excerpts only; not semantic grade validation"}, indent=2))


if __name__ == "__main__":
    main()
