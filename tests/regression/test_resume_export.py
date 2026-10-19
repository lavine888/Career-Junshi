"""Real local exports plus simulated external-tool failure boundaries, not PDF QA."""
import copy
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.models import ContractError
from scripts.resume_export import ROOT, export_resume, validate_resume


def sample():
    return {
        "schema_version": "1", "language": "zh", "name": "示例候选人",
        "contacts": ["sample@example.invalid"], "page_limit": 1,
        "sources": [{"id": "demo", "description": "Synthetic public test fixture, not a real candidate"}],
        "sections": [{"title": "项目经历", "entries": [{
            "title": "合成项目", "subtitle": "原型阶段", "dates": "",
            "source_ids": ["demo"], "bullets": [{"text": "计划完成三次合成场景验证",
                "source_ids": ["demo"], "confidence": "PLANNED"}]}]}],
    }


class ResumeExportTests(unittest.TestCase):
    def test_validation_preserves_original_and_returns_independent_data(self):
        data = sample()
        data["sections"][0]["entries"][0]["bullets"][0]["text"] = "  保留限定：仅团队原型  "
        result = validate_resume(data)
        self.assertEqual(result["sections"], data["sections"])
        result["sources"][0]["description"] = "changed"
        self.assertNotEqual(result["sources"], data["sources"])
        self.assertEqual(result["target_role"], "")

    def test_rejects_missing_duplicate_unknown_sources_and_metadata(self):
        bad = []
        for where in ("entry", "bullet"):
            for refs in ([], ["missing"], ["demo", "demo"]):
                data = sample()
                entry = data["sections"][0]["entries"][0]
                (entry if where == "entry" else entry["bullets"][0])["source_ids"] = refs
                bad.append(data)
        data = sample()
        data["sources"].append(copy.deepcopy(data["sources"][0]))
        bad.append(data)
        data = sample()
        del data["sections"][0]["entries"][0]["source_ids"]
        bad.append(data)
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ContractError):
                validate_resume(value)

    def test_rejects_extra_fields_controls_and_unbounded_values_before_writing(self):
        mutations = [("template", "arbitrary.tex"), ("name", "name\n\\input{x}"),
                     ("name", "n" * 101), ("page_limit", True), ("language", "xx"),
                     ("schema_version", 1), ("sources", []), ("sections", [])]
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "out"
            for key, value in mutations:
                data = sample()
                data[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ContractError):
                    export_resume(data, target)
                self.assertFalse(target.exists())

    def test_export_escapes_tex_but_preserves_original_and_planned_grade(self):
        data = sample()
        original = r"原型 20% & a_b #1 $x {team} ~ ^ \input{secret} @@CLASS@@"
        data["sections"][0]["entries"][0]["bullets"][0]["text"] = original
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "out"
            report = export_resume(data, target)
            self.assertEqual(report["status"], "SOURCE_ONLY")
            self.assertEqual({p.name for p in target.iterdir()},
                             {"resume.tex", "resume.txt", "resume-data.json", "verification.json"})
            tex = (target / "resume.tex").read_text(encoding="utf-8")
            for escaped in (r"20\%", r"\&", r"a\_b", r"\#1", r"\$x", r"\{team\}",
                            r"\textbackslash{}input\{secret\}", "[PLANNED]", "@@CLASS@@"):
                self.assertIn(escaped, tex)
            self.assertNotIn(r"\input{secret}", tex)
            self.assertIn(original, (target / "resume.txt").read_text(encoding="utf-8"))
            saved = json.loads((target / "resume-data.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["sections"], data["sections"])
            self.assertEqual(report["semantic_verification"], "NOT_PERFORMED")

    def test_english_uses_article_and_omitted_contacts_are_empty(self):
        data = sample()
        data["language"] = "en"
        del data["contacts"]
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "out"
            export_resume(data, target)
            tex = (target / "resume.tex").read_text(encoding="utf-8")
            self.assertIn(r"\documentclass[11pt,a4paper]{article}", tex)
            self.assertNotIn("fontset=fandol", tex)

    def test_education_without_bullets_exports_before_project_with_balanced_blocks(self):
        data = sample()
        data["sections"].insert(0, {"title": "教育经历", "entries": [{
            "title": "合成示例大学", "subtitle": "本科", "dates": "2020–2024",
            "source_ids": ["demo"], "bullets": []}]})
        original = copy.deepcopy(data)
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "out"
            report = export_resume(data, target)
            tex = (target / "resume.tex").read_text(encoding="utf-8")
            self.assertEqual(tex.count(r"\begin{minipage}"), 2)
            self.assertEqual(tex.count(r"\end{minipage}"), 2)
            self.assertLess(tex.index("合成示例大学"), tex.index(r"\end{minipage}"))
            self.assertLess(tex.index(r"\end{minipage}"), tex.index("项目经历"))
            self.assertIn("合成示例大学 | 本科 | 2020–2024", (target / "resume.txt").read_text(encoding="utf-8"))
            self.assertIn("[PLANNED] 计划完成三次合成场景验证", report["expected_text"])
            self.assertEqual(report["evidence_map"]["sections"], original["sections"])
            self.assertEqual(data, original)

    def test_rejects_existing_installation_and_git_ancestors(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            existing = root / "existing"
            existing.mkdir()
            with self.assertRaises(ContractError):
                export_resume(sample(), existing)
            with self.assertRaises(ContractError):
                export_resume(sample(), ROOT / "candidate-private")
            for marker in ("directory", "file"):
                repo = root / marker
                repo.mkdir()
                if marker == "directory":
                    (repo / ".git").mkdir()
                else:
                    (repo / ".git").write_text("gitdir: elsewhere", encoding="utf-8")
                target = repo / "new-parent" / "out"
                with self.assertRaises(ContractError):
                    export_resume(sample(), target)
                self.assertFalse(target.parent.exists())

    def test_compile_not_requested_does_not_probe_or_run_tools(self):
        with tempfile.TemporaryDirectory() as temp, patch("scripts.resume_export.shutil.which") as which:
            export_resume(sample(), Path(temp) / "out")
            which.assert_not_called()

    def test_linked_output_ancestor_is_rejected_without_touching_its_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            destination = root / "actual"
            destination.mkdir()
            sentinel = destination / "keep.txt"
            sentinel.write_text("preserve", encoding="utf-8")
            link = root / "linked"
            if os.name == "nt":
                subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(destination)],
                               check=True, capture_output=True, shell=False)
            else:
                link.symlink_to(destination, target_is_directory=True)
            try:
                with self.assertRaises(ContractError):
                    export_resume(sample(), link / "out")
                self.assertFalse((destination / "out").exists())
                self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")
            finally:
                link.rmdir() if os.name == "nt" else link.unlink()

    def test_missing_compiler_preserves_sources_and_reports_unavailable(self):
        with tempfile.TemporaryDirectory() as temp, patch("scripts.resume_export.shutil.which", return_value=None):
            report = export_resume(sample(), Path(temp) / "out", compile_pdf=True)
            self.assertEqual(report["status"], "SOURCE_ONLY")
            self.assertEqual(report["checks"]["compilation"], "UNAVAILABLE")
            self.assertIsNone(report["checks"]["pdf_file"])

    def test_failed_compiler_does_not_publish_pdf_and_disables_shell(self):
        with tempfile.TemporaryDirectory() as temp, patch("scripts.resume_export.shutil.which", return_value="xelatex"), \
                patch("scripts.resume_export.subprocess.run", return_value=subprocess.CompletedProcess([], 1, "bad", "error")) as run:
            report = export_resume(sample(), Path(temp) / "out", compile_pdf=True)
            self.assertEqual(report["status"], "COMPILATION_FAILED")
            self.assertIsNone(report["checks"]["pdf_file"])
            command = run.call_args.args[0]
            self.assertIn("-no-shell-escape", command)
            self.assertIn("-halt-on-error", command)
            self.assertFalse(run.call_args.kwargs["shell"])
            self.assertLessEqual(run.call_args.kwargs["timeout"], 60)

    def test_compiler_timeout_is_explicit(self):
        with tempfile.TemporaryDirectory() as temp, patch("scripts.resume_export.shutil.which", return_value="xelatex"), \
                patch("scripts.resume_export.subprocess.run", side_effect=subprocess.TimeoutExpired("xelatex", 60)):
            report = export_resume(sample(), Path(temp) / "out", compile_pdf=True)
            self.assertEqual(report["status"], "COMPILATION_FAILED")
            self.assertEqual(report["checks"]["detail"], "TimeoutExpired")

    def test_log_overflow_warning_is_not_hidden_by_successful_compilation(self):
        def run(command, **kwargs):
            (Path(kwargs["cwd"]) / "resume.pdf").write_bytes(b"simulated boundary result")
            return subprocess.CompletedProcess(command, 0, r"Overfull \hbox (9pt too wide)", "")
        with tempfile.TemporaryDirectory() as temp, \
                patch("scripts.resume_export.shutil.which", side_effect=lambda name: name if name == "xelatex" else None), \
                patch("scripts.resume_export.subprocess.run", side_effect=run):
            report = export_resume(sample(), Path(temp) / "out", compile_pdf=True)
            self.assertEqual(report["status"], "PDF_CHECKS_FAILED")
            self.assertEqual(report["checks"]["log_check"], "FAILED")

    def _simulated_compile(self, pages="1", text=None, tools=True):
        """Only exercises tool-result handling; the bytes below are not a valid PDF."""
        def which(name):
            return name if tools or name == "xelatex" else None

        def run(command, **kwargs):
            if command[0] == "xelatex":
                (Path(kwargs["cwd"]) / "resume.pdf").write_bytes(b"simulated boundary result")
                return subprocess.CompletedProcess(command, 0, "", "")
            if command[0] == "pdfinfo":
                return subprocess.CompletedProcess(command, 0, f"Pages: {pages}\n", "")
            return subprocess.CompletedProcess(command, 0, text or "missing resume text", "")

        return patch("scripts.resume_export.shutil.which", side_effect=which), patch("scripts.resume_export.subprocess.run", side_effect=run)

    def test_over_page_limit_is_failure_even_when_compilation_returns_pdf(self):
        which, run = self._simulated_compile(pages="3")
        with tempfile.TemporaryDirectory() as temp, which, run:
            report = export_resume(sample(), Path(temp) / "out", compile_pdf=True)
            self.assertEqual(report["status"], "PDF_CHECKS_FAILED")
            self.assertEqual(report["checks"]["page_check"], "FAILED")
            self.assertEqual(report["checks"]["pages"], 3)

    def test_missing_pdf_tools_remain_unavailable_and_require_visual_review(self):
        which, run = self._simulated_compile(tools=False)
        with tempfile.TemporaryDirectory() as temp, which, run:
            report = export_resume(sample(), Path(temp) / "out", compile_pdf=True)
            self.assertEqual(report["status"], "PDF_COMPILED_AWAITING_VISUAL_REVIEW")
            self.assertEqual(report["checks"]["page_check"], "UNAVAILABLE")
            self.assertEqual(report["checks"]["text_check"], "UNAVAILABLE")
            self.assertEqual(report["checks"]["visual_review"], "REQUIRED")

    def test_text_layer_requires_contacts_name_and_every_claim(self):
        data = sample()
        text = "示例候选人 sample@example.invalid 项目经历 合成项目 原型阶段 [PLANNED] 计划完成三次合成场景验证"
        which, run = self._simulated_compile(text=text)
        with tempfile.TemporaryDirectory() as temp, which, run:
            report = export_resume(data, Path(temp) / "out", compile_pdf=True)
            self.assertEqual(report["checks"]["text_check"], "PASSED")
            self.assertEqual(report["status"], "PDF_COMPILED_AWAITING_VISUAL_REVIEW")
        which, run = self._simulated_compile(text=text.replace("sample@example.invalid", ""))
        with tempfile.TemporaryDirectory() as temp, which, run:
            report = export_resume(data, Path(temp) / "out", compile_pdf=True)
            self.assertEqual(report["status"], "PDF_CHECKS_FAILED")
            self.assertTrue(report["checks"]["missing_text_indexes"])
        which, run = self._simulated_compile(text=text.replace("[PLANNED] ", ""))
        with tempfile.TemporaryDirectory() as temp, which, run:
            report = export_resume(data, Path(temp) / "out", compile_pdf=True)
            self.assertEqual(report["status"], "PDF_CHECKS_FAILED")
            self.assertTrue(report["checks"]["missing_text_indexes"])


if __name__ == "__main__":
    unittest.main()
