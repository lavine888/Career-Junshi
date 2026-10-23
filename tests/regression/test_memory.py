import sqlite3
import os
import subprocess
import tempfile
import unittest
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from scripts.memory_store import MemoryStore
from scripts.models import ContractError
from tests.regression.test_evidence import claim

BASE = {"summary": "synthetic candidate", "source": "synthetic:user", "epistemic": "FACT"}


class MemoryRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = MemoryStore(self.tmp.name)

    def test_no_consent_no_files_or_writes(self):
        self.assertEqual(self.store.status()["state"], "uninitialized")
        self.assertFalse(self.store.path.exists())
        with self.assertRaises(ContractError): self.store.consent()
        with self.assertRaises(ContractError): self.store.put("profile", "candidate", BASE)
        self.assertFalse(self.store.path.exists())

    def test_persist_recall_update(self):
        self.store.consent(confirmed=True)
        first = self.store.put("profile", "candidate", BASE)
        newer = MemoryStore(self.tmp.name)
        data = {**BASE, "summary": "changed", "epistemic": "INFERENCE"}
        newer.put("profile", "candidate", data, record_id=first["id"])
        records = self.store.read(subject="candidate")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["data"]["summary"], "changed")
        self.assertEqual(records[0]["data"]["epistemic"], "INFERENCE")
        with self.assertRaises(ContractError): self.store.read()

    def test_pause_revoke_view_reconsent_and_delete(self):
        self.store.consent(confirmed=True)
        self.store.put("project", "P1", BASE)
        for state in ("paused", "revoked"):
            self.store.set_state(state)
            with self.assertRaises(ContractError): self.store.read(subject="P1")
            with self.assertRaises(ContractError): self.store.put("project", "P2", BASE)
            self.assertEqual(len(self.store.read(administrative=True)), 1)
        with self.assertRaises(ContractError): self.store.set_state("paused")
        self.store.consent(confirmed=True)
        self.assertEqual(len(self.store.read(subject="P1")), 1)
        with self.assertRaises(ContractError): self.store.delete()
        self.assertEqual(self.store.delete(confirmed=True)["deleted"], 1)
        self.assertEqual(self.store.status()["state"], "revoked")

    def test_raw_documents_rejected(self):
        self.store.consent(confirmed=True)
        for data in ({**BASE, "resume": "entire document"}, {**BASE, "summary": "x" * 401}):
            with self.assertRaises(ContractError): self.store.put("profile", "candidate", data)

    def test_claim_cannot_bypass_normalization(self):
        self.store.consent(confirmed=True)
        self.store.put("claim", "C1", {**BASE, "claim": claim(claim="production", stage="demo")})
        record = self.store.read(kind="claim")[0]["data"]["claim"]
        self.assertNotEqual(record["confidence"], "VERIFIED")
        self.assertIn("missing_evidence:production", record["risk"])

    def test_kind_subject_cannot_be_changed(self):
        self.store.consent(confirmed=True)
        first = self.store.put("project", "P1", BASE)
        with self.assertRaises(ContractError): self.store.put("profile", "P1", BASE, record_id=first["id"])

    def test_capacity_atomic_under_concurrency(self):
        self.store.consent(confirmed=True)
        def add(i):
            try:
                self.store.put("project", f"P{i}", BASE)
                return True
            except ContractError:
                return False
        with patch("scripts.memory_store.MAX_RECORDS", 3):
            with ThreadPoolExecutor(max_workers=5) as pool:
                results = list(pool.map(add, range(5)))
        self.assertEqual(sum(results), 3)
        self.assertEqual(self.store.status()["records"], 3)

    def test_no_memory_in_installation(self):
        root = Path(__file__).resolve().parents[2]
        with self.assertRaises(ContractError): MemoryStore(root / ".memory")

    def test_policy_change_fails_closed(self):
        self.store.consent(confirmed=True)
        with closing(sqlite3.connect(self.store.path)) as c:
            with c:
                c.execute("UPDATE settings SET value='future' WHERE key='policy_version'")
        with self.assertRaises(ContractError): self.store.status()
        with self.assertRaises(ContractError): self.store.consent(confirmed=True)


    def test_memory_refuses_other_git_checkout_and_worktree_without_creating_files(self):
        for marker in ("directory", "worktree-file"):
            with self.subTest(marker=marker):
                root = Path(self.tmp.name) / marker
                root.mkdir()
                if marker == "directory":
                    (root / ".git").mkdir()
                else:
                    (root / ".git").write_text("gitdir: external-worktree-metadata", encoding="utf-8")
                with self.assertRaises(ContractError):
                    MemoryStore(root / "private-memory").consent(confirmed=True)
                self.assertFalse((root / "private-memory").exists())

    def test_existing_store_checks_if_parent_became_git_before_any_access(self):
        self.store.consent(confirmed=True)
        self.store.put("profile", "candidate", BASE)
        before = self.store.path.read_bytes()
        (Path(self.tmp.name) / ".git").mkdir()
        for operation in (self.store.status, lambda: self.store.read(subject="candidate"),
                          lambda: self.store.put("profile", "candidate", BASE),
                          lambda: self.store.delete(confirmed=True)):
            with self.subTest(operation=operation):
                with self.assertRaises(ContractError): operation()
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_database_link_is_refused_before_existing_store_reads_or_writes(self):
        self.store.consent(confirmed=True)
        self.store.put("profile", "candidate", BASE)
        archive = self.store.path.with_name("original.sqlite3")
        self.store.path.rename(archive)
        try:
            self.store.path.symlink_to(archive)
        except OSError:
            archive.rename(self.store.path)
            self.skipTest("symbolic links unavailable")
        before = archive.read_bytes()
        with self.assertRaises(ContractError): self.store.status()
        with self.assertRaises(ContractError): self.store.read(subject="candidate")
        with self.assertRaises(ContractError): self.store.put("profile", "candidate", BASE)
        self.assertEqual(archive.read_bytes(), before)


    def test_directory_link_is_refused_initially_and_after_store_construction(self):
        base = Path(self.tmp.name)
        original, alias = base / "original", base / "alias"
        original.mkdir()
        store = MemoryStore(original)
        store.consent(confirmed=True)
        store.put("profile", "candidate", BASE)
        before = store.path.read_bytes()
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(original)],
                           check=True, capture_output=True)
        else:
            alias.symlink_to(original, target_is_directory=True)
        try:
            with self.assertRaises(ContractError): MemoryStore(alias)
        finally:
            if os.name == "nt": alias.rmdir()
            else: alias.unlink()
        moved = base / "moved"
        original.rename(moved)
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(original), str(moved)],
                           check=True, capture_output=True)
        else:
            original.symlink_to(moved, target_is_directory=True)
        try:
            for operation in (store.status, lambda: store.read(subject="candidate"),
                              lambda: store.put("profile", "candidate", BASE),
                              lambda: store.delete(confirmed=True)):
                with self.subTest(operation=operation):
                    with self.assertRaises(ContractError): operation()
            self.assertEqual((moved / "memory.sqlite3").read_bytes(), before)
        finally:
            if os.name == "nt": original.rmdir()
            else: original.unlink()
            moved.rename(original)
