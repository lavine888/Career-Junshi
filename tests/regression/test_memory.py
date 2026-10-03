import sqlite3
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
