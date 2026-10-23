"""CLI boundaries use UTF-8 even when Windows starts Python in a legacy encoding."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CliEncodingTests(unittest.TestCase):
    def run_cli(self, script, *args):
        env = {**os.environ, "PYTHONUTF8": "0", "PYTHONIOENCODING": "cp1252"}
        return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args],
                              env=env, capture_output=True, timeout=20)

    def test_decide_outputs_utf8_under_legacy_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text(json.dumps({"mode": "job", "summary": "测试当前方向"}, ensure_ascii=False), encoding="utf-8-sig")
            result = self.run_cli("junshi.py", "decide", "--input", str(path), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
            self.assertEqual(json.loads(result.stdout.decode("utf-8"))["current_situation"], "测试当前方向")

    def test_install_returns_utf8_success_and_preserves_existing_unicode_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "合成安装目录" / "career-junshi"
            result = self.run_cli("install_skill.py", "--target", str(target))
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
            self.assertEqual(json.loads(result.stdout.decode("utf-8"))["installed"], str(target))
            self.assertTrue((target / "SKILL.md").is_file())
            sentinel = target / "keep.txt"
            sentinel.write_text("preserve existing installation", encoding="utf-8")
            before = (target / "SKILL.md").read_bytes()
            repeated = self.run_cli("install_skill.py", "--target", str(target))
            self.assertEqual(repeated.returncode, 2)
            self.assertIn("Target exists", json.loads(repeated.stderr.decode("utf-8"))["error"])
            self.assertEqual((target / "SKILL.md").read_bytes(), before)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve existing installation")

    def test_validator_returns_utf8_diagnostics_for_unicode_broken_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "career-junshi"
            installed = self.run_cli("install_skill.py", "--target", str(target))
            self.assertEqual(installed.returncode, 0, installed.stderr.decode("utf-8"))
            skill = target / "SKILL.md"
            skill.write_text(skill.read_text(encoding="utf-8") + "\n[示例](references/不存在.md)\n", encoding="utf-8")
            result = self.run_cli("validate_skill.py", "--runtime-only", "--root", str(target))
            self.assertEqual(result.returncode, 1, result.stderr.decode("utf-8"))
            report = json.loads(result.stdout.decode("utf-8"))
            self.assertFalse(report["valid"])
            self.assertTrue(any("references/不存在.md" in error for error in report["errors"]))

    def test_memory_accepts_bom_and_returns_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = str(Path(tmp) / "private-memory")
            consent = self.run_cli("memory_store.py", "--directory", directory, "consent", "--yes")
            self.assertEqual(consent.returncode, 0, consent.stderr.decode("utf-8"))
            path = Path(tmp) / "profile.json"
            path.write_text(json.dumps({"summary": "合成候选人", "source": "synthetic:user", "epistemic": "FACT"}, ensure_ascii=False), encoding="utf-8-sig")
            saved = self.run_cli("memory_store.py", "--directory", directory, "update", "--kind", "profile", "--subject", "synthetic", "--input", str(path))
            self.assertEqual(saved.returncode, 0, saved.stderr.decode("utf-8"))
            recalled = self.run_cli("memory_store.py", "--directory", directory, "recall", "--subject", "synthetic")
            self.assertEqual(recalled.returncode, 0, recalled.stderr.decode("utf-8"))
            self.assertEqual(json.loads(recalled.stdout.decode("utf-8"))[0]["data"]["summary"], "合成候选人")

    def test_memory_rejects_oversized_input_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "uninitialized-memory"
            path = Path(tmp) / "large.json"
            path.write_text(" " * (256 * 1024) + "{}", encoding="utf-8")
            result = self.run_cli("memory_store.py", "--directory", str(directory), "update", "--kind", "profile", "--subject", "synthetic", "--input", str(path))
            self.assertEqual(result.returncode, 2)
            self.assertFalse(json.loads(result.stderr.decode("utf-8"))["saved"])
            self.assertFalse(directory.exists())
