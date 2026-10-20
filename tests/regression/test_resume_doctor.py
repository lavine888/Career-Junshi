"""Doctor CLI/environment boundaries; actual TeX probes are documented separately."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.install_skill import install
from scripts.resume_doctor import diagnose_resume_environment

ROOT = Path(__file__).resolve().parents[2]


class ResumeDoctorTests(unittest.TestCase):
    def test_missing_tools_do_not_run_a_command_or_compile(self):
        with patch("scripts.resume_doctor.shutil.which", return_value=None), \
                patch("scripts.resume_doctor._run") as run, patch("scripts.resume_doctor._compile") as compile_pdf:
            result = diagnose_resume_environment()
        self.assertEqual(result["status"], "NOT_READY")
        self.assertEqual(result["probes"], [])
        run.assert_not_called()
        compile_pdf.assert_not_called()

    def test_tool_version_timeout_is_structured(self):
        with patch("scripts.resume_doctor.shutil.which", return_value="tool"), \
                patch("scripts.resume_doctor._run", side_effect=subprocess.TimeoutExpired("tool", 60)):
            result = diagnose_resume_environment()
        self.assertEqual(result["status"], "NOT_READY")
        self.assertTrue(all(t["detail"] == "TimeoutExpired" for t in result["tools"].values()))

    def test_available_binaries_with_broken_chinese_extraction_are_not_ready(self):
        with patch("scripts.resume_doctor.shutil.which", side_effect=lambda name: name), \
                patch("scripts.resume_doctor._run", return_value=subprocess.CompletedProcess([], 0, "version", "")), \
                patch("scripts.resume_doctor._compile", return_value={"compilation": "COMPILED", "page_check": "PASSED", "text_check": "FAILED", "log_check": "PASSED"}) as compiled:
            result = diagnose_resume_environment()
        self.assertEqual(result["status"], "NOT_READY")
        self.assertEqual(compiled.call_count, 2)
        self.assertEqual([p["language"] for p in result["probes"]], ["zh", "en"])

    def test_installed_doctor_runs_without_inputs_and_returns_nonzero_if_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = install(root / "skills/career-junshi")
            result = subprocess.run([sys.executable, str(target / "scripts/junshi.py"), "resume-doctor"],
                                    cwd=root, env={**os.environ, "PATH": ""}, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 2, result.stderr.decode("utf-8"))
            report = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual(report["status"], "NOT_READY")
            self.assertEqual({p.name for p in root.iterdir()}, {"skills"})

    def test_miktex_probe_explicitly_disables_implicit_package_downloads(self):
        with patch("scripts.resume_doctor.shutil.which", side_effect=lambda name: name), \
                patch("scripts.resume_doctor._run", return_value=subprocess.CompletedProcess([], 0, "MiKTeX test version", "")), \
                patch("scripts.resume_doctor._compile", return_value={"compilation": "COMPILED", "page_check": "PASSED", "text_check": "PASSED", "log_check": "PASSED"}) as compiled:
            result = diagnose_resume_environment()
        self.assertEqual(result["status"], "READY")
        self.assertTrue(all(call.kwargs["disable_installer"] for call in compiled.call_args_list))
