"""Actual linked-directory boundaries; synthetic temporary files only."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.install_skill import install
from scripts.models import ContractError
from scripts.validate_skill import validate


class PackageLinkBoundaryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="junshi-package-links-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.source = install(self.base / "source" / "career-junshi")

    def link_directory(self, link, destination):
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(destination)],
                           check=True, capture_output=True, shell=False)
            self.addCleanup(link.rmdir)
        else:
            link.symlink_to(destination, target_is_directory=True)
            self.addCleanup(link.unlink)

    def test_external_reference_directory_is_rejected_before_catalog_reads_or_copy(self):
        external = self.base / "outside"
        external.mkdir()
        note = external / "synthetic-private-note.md"
        note.write_text("SYNTHETIC PRIVATE MARKER", encoding="utf-8")
        before = (self.source / "SKILL.md").read_bytes()
        self.link_directory(self.source / "references" / "linked-private", external)
        target = self.base / "must-not-be-created" / "career-junshi"
        with patch("scripts.validate_skill.load_catalog") as load:
            errors = validate(self.source, runtime_only=True)
            self.assertTrue(any("linked-private" in error for error in errors))
            load.assert_not_called()
            with self.assertRaises(ContractError):
                install(target, source=self.source)
            load.assert_not_called()
        self.assertFalse(target.parent.exists())
        self.assertEqual(note.read_text(encoding="utf-8"), "SYNTHETIC PRIVATE MARKER")
        self.assertEqual((self.source / "SKILL.md").read_bytes(), before)
        self.assertEqual({p.name for p in external.iterdir()}, {note.name})

    def test_linked_source_root_and_ancestor_are_not_hidden_by_resolve(self):
        alias = self.base / "source-alias"
        self.link_directory(alias, self.source.parent)
        source = alias / "career-junshi"
        self.assertTrue(validate(source, runtime_only=True))
        with self.assertRaises(ContractError):
            install(self.base / "not-created" / "career-junshi", source=source)
        self.assertFalse((self.base / "not-created").exists())
        direct = self.base / "direct-source-alias"
        self.link_directory(direct, self.source)
        self.assertTrue(validate(direct, runtime_only=True))
        with self.assertRaises(ContractError):
            install(self.base / "not-created" / "career-junshi", source=direct)

    def test_linked_installation_parent_is_rejected_without_external_writes(self):
        external = self.base / "outside-target"
        external.mkdir()
        alias = self.base / "target-alias"
        self.link_directory(alias, external)
        with self.assertRaises(ContractError):
            install(alias / "career-junshi", source=self.source)
        self.assertEqual(list(external.iterdir()), [])

    def test_reference_cycle_is_pruned_before_traversal(self):
        self.link_directory(self.source / "references" / "cycle", self.source / "references")
        with patch("scripts.validate_skill.load_catalog") as load:
            errors = validate(self.source, runtime_only=True)
            load.assert_not_called()
        self.assertEqual(len(errors), 1)
        self.assertIn("cycle", errors[0])
