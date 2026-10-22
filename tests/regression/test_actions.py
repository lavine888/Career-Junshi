import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.actions import validate_actions, write_artifacts
from scripts.decision import action, decide
from scripts.models import ContractError
from scripts.install_skill import install
from tests.regression.test_decision import NOW, situation


class ActionRegression(unittest.TestCase):
    def test_external_actions_are_human(self):
        for kind in ("send_message", "apply", "negotiate", "accept_offer", "reject_offer", "career_decision"):
            with self.assertRaises(ContractError): validate_actions([action(kind, "do it", "codex")])
        bad = action("evidence_audit", "audit", "codex"); bad["status"] = "DONE"
        with self.assertRaises(ContractError): validate_actions([bad])

    def test_real_files_and_no_overwrite(self):
        d = decide(situation(), now=NOW)
        with tempfile.TemporaryDirectory() as tmp:
            files = write_artifacts(d, tmp)
            self.assertEqual(len(files), 3)
            before = {p: Path(p).read_text(encoding="utf-8") for p in files}
            self.assertIn("五层", before[str(Path(tmp) / "project-defense.md")])
            with self.assertRaises(ContractError): write_artifacts(d, tmp)
            self.assertEqual(before, {p: Path(p).read_text(encoding="utf-8") for p in files})

    def test_preparation_rejects_git_directories_and_worktree_markers_before_writing(self):
        decision = decide(situation(), now=NOW)
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for kind in ("directory", "file"):
                repo = base / kind
                repo.mkdir()
                if kind == "directory":
                    (repo / ".git").mkdir()
                else:
                    (repo / ".git").write_text("gitdir: synthetic-worktree", encoding="utf-8")
                sentinel = repo / "keep.txt"
                sentinel.write_text("existing user material", encoding="utf-8")
                target = repo / "preparation"
                with self.subTest(kind=kind), self.assertRaises(ContractError):
                    write_artifacts(decision, target)
                self.assertFalse(target.exists())
                self.assertEqual(sentinel.read_text(encoding="utf-8"), "existing user material")

    def test_linked_preparation_path_cannot_write_to_an_external_directory(self):
        decision = decide(situation(), now=NOW)
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            outside = base / "external"
            outside.mkdir()
            alias = base / "alias"
            if os.name == "nt":
                subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(outside)],
                               check=True, capture_output=True, shell=False)
            else:
                alias.symlink_to(outside, target_is_directory=True)
            try:
                with self.assertRaises(ContractError):
                    write_artifacts(decision, alias / "preparation")
                self.assertEqual(list(outside.iterdir()), [])
            finally:
                if os.name == "nt":
                    alias.rmdir()
                else:
                    alias.unlink()

    def test_installed_cli_rejects_preparation_inside_installation(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = install(base / "career-junshi")
            source = base / "input.json"
            source.write_text(json.dumps(situation()), encoding="utf-8")
            output = target / "candidate-material"
            result = subprocess.run(
                [sys.executable, str(target / "scripts/junshi.py"), "decide",
                 "--input", str(source), "--now", NOW.isoformat(), "--format", "json",
                 "--artifacts-dir", str(output)],
                cwd=base, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 2, result.stdout.decode("utf-8"))
            self.assertFalse(output.exists())
            self.assertIn("installation", result.stderr.decode("utf-8"))
