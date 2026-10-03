import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.install_skill import install
from scripts.models import ContractError
from scripts.validate_skill import validate

ROOT = Path(__file__).resolve().parents[2]


class InstalledCliRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.target = install(self.base / "skills" / "career-junshi")
        self.env = {**os.environ, "PYTHONUTF8": "1", "CAREER_JUNSHI_MEMORY_DIR": str(self.base / "private-memory")}

    def run_cli(self, script, *args):
        return subprocess.run([sys.executable, str(self.target / "scripts" / script), *args],
                              cwd=self.base, env=self.env, capture_output=True, text=True, encoding="utf-8", timeout=15)

    def test_installed_runtime_has_no_dev_or_memory_dependency(self):
        self.assertEqual(validate(self.target, runtime_only=True), [])
        for name in (".git", "cases", "tests", "README.md", "memory.sqlite3"):
            self.assertFalse((self.target / name).exists())
        check = self.run_cli("validate_skill.py", "--runtime-only")
        self.assertEqual(check.returncode, 0, check.stderr)
        routing = self.run_cli("junshi.py", "route", "--mode", "offer")
        self.assertEqual(routing.returncode, 0, routing.stderr)
        self.assertEqual(len(json.loads(routing.stdout)["references"]), 3)
        status = self.run_cli("memory_store.py", "status")
        self.assertEqual(json.loads(status.stdout)["state"], "uninitialized")
        self.assertFalse((self.base / "private-memory").exists())

    def test_installed_cli_real_artifacts(self):
        out = self.base / "output"
        run = self.run_cli("junshi.py", "decide", "--input", str(ROOT / "cases/interview/input.json"), "--now", "2026-10-03T12:00:00+08:00", "--format", "json", "--artifacts-dir", str(out))
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(len(result["generated_artifacts"]), 3)
        self.assertTrue(all(Path(p).is_file() for p in result["generated_artifacts"]))

    def test_installed_memory_consent_recall_revoke(self):
        self.assertEqual(self.run_cli("memory_store.py", "consent").returncode, 2)
        self.assertEqual(self.run_cli("memory_store.py", "consent", "--yes").returncode, 0)
        data = self.base / "profile.json"
        data.write_text(json.dumps({"summary": "synthetic profile", "source": "synthetic:user", "epistemic": "FACT"}), encoding="utf-8")
        saved = self.run_cli("memory_store.py", "update", "--kind", "profile", "--subject", "candidate", "--input", str(data))
        self.assertEqual(saved.returncode, 0, saved.stderr)
        recall = self.run_cli("memory_store.py", "recall", "--subject", "candidate")
        self.assertEqual(len(json.loads(recall.stdout)), 1)
        self.assertEqual(self.run_cli("memory_store.py", "revoke").returncode, 0)
        self.assertEqual(self.run_cli("memory_store.py", "recall", "--subject", "candidate").returncode, 2)
        viewed = self.run_cli("memory_store.py", "view")
        self.assertEqual(len(json.loads(viewed.stdout)), 1)
        self.assertEqual(self.run_cli("memory_store.py", "delete", "--yes").returncode, 0)

    def test_installer_preserves_existing_target(self):
        before = (self.target / "SKILL.md").read_bytes()
        with self.assertRaises(ContractError): install(self.target)
        self.assertEqual(before, (self.target / "SKILL.md").read_bytes())

    def test_broken_runtime_link_detected(self):
        skill = self.target / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\n[broken](references/missing.md)\n", encoding="utf-8")
        self.assertTrue(any("Broken link" in e for e in validate(self.target, runtime_only=True)))

    def test_bad_cli_input_nonzero_and_no_artifacts(self):
        source = self.base / "bad.json"; source.write_text('{"mode":"invented"}', encoding="utf-8")
        out = self.base / "not-created"
        run = self.run_cli("junshi.py", "decide", "--input", str(source), "--artifacts-dir", str(out))
        self.assertEqual(run.returncode, 2)
        self.assertFalse(out.exists())
