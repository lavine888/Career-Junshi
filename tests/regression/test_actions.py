import tempfile
import unittest
from pathlib import Path

from scripts.actions import validate_actions, write_artifacts
from scripts.decision import action, decide
from scripts.models import ContractError
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
