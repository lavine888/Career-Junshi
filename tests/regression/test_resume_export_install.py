"""Actual installed exporter and CLI behavior; no mock compilation success."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.install_skill import install
from scripts.validate_skill import validate

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "cases/experiences/resume-export/input.json"


class InstalledResumeExportTests(unittest.TestCase):
    def test_requested_compile_without_an_engine_returns_nonzero_and_keeps_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            output = base / "source-only"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/junshi.py"), "resume-export",
                 "--input", str(SAMPLE), "--output-dir", str(output), "--compile"],
                cwd=base, env={**os.environ, "PATH": ""}, capture_output=True, timeout=20,
            )
            self.assertEqual(result.returncode, 2)
            report = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(report["checks"]["compilation"], "UNAVAILABLE")
            self.assertTrue((output / "resume.tex").is_file())
            self.assertTrue((output / "verification.json").is_file())
            self.assertFalse((output / "resume.pdf").exists())

    def test_installed_export_preserves_source_map_and_requires_no_tex_or_memory(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target = install(base / "skills/career-junshi")
            output = base / "private/new-resume"
            result = subprocess.run(
                [sys.executable, str(target / "scripts/junshi.py"), "resume-export",
                 "--input", str(SAMPLE), "--output-dir", str(output)],
                cwd=base, capture_output=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
            report = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(report["status"], "SOURCE_ONLY")
            self.assertEqual(report["checks"]["compilation"], "NOT_REQUESTED")
            self.assertNotIn("evidence_map", report)
            original = json.loads(SAMPLE.read_text(encoding="utf-8"))
            self.assertEqual(json.loads((output / "resume-data.json").read_text(encoding="utf-8")), original)
            plain = (output / "resume.txt").read_text(encoding="utf-8")
            self.assertIn(original["name"], plain)
            self.assertNotIn("[SUPPORTED]", plain)
            self.assertEqual(
                json.loads((output / "verification.json").read_text(encoding="utf-8"))["evidence_map"],
                original,
            )
            self.assertFalse((output / "resume.pdf").exists())
            self.assertEqual({p.name for p in base.iterdir()}, {"skills", "private"})
            self.assertEqual(validate(target, runtime_only=True), [])

    def test_installed_template_and_license_are_required_resources(self):
        with tempfile.TemporaryDirectory() as temp:
            target = install(Path(temp) / "career-junshi")
            for name in ("assets/resume/single-column.tex", "documentation/licenses/ai-job-search.txt",
                         "documentation/licenses/interview-coach-skill.txt"):
                path = target / name
                data = path.read_bytes()
                self.assertEqual(data, (ROOT / name).read_bytes())
                path.unlink()
                try:
                    self.assertIn("Missing required file: " + name, validate(target, runtime_only=True))
                finally:
                    path.write_bytes(data)

    def test_cli_invalid_data_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "invalid.json"
            source.write_text('{"schema_version":"1","language":"zh"}', encoding="utf-8")
            output = base / "untouched"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/junshi.py"), "resume-export",
                 "--input", str(source), "--output-dir", str(output)],
                cwd=base, capture_output=True, timeout=20,
            )
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())
