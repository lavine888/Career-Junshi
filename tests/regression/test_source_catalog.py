"""Catalog integrity, bounded discovery and actual installed CLI behavior."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from scripts.install_skill import install
from scripts.models import ContractError
from scripts.source_catalog import CATALOG_FILES, load_catalog, query_sources, validate_catalog
from scripts.validate_skill import validate


class SourceCatalogTests(unittest.TestCase):
    def test_counts_are_computed_from_distinct_records_and_multitopic_membership(self):
        records = load_catalog()
        result = query_sources()
        self.assertEqual(result["total_sources"], len(records))
        self.assertEqual(sum(result["kind_counts"].values()), len(records))
        expected = Counter(topic for record in records for topic in record["topics"])
        self.assertEqual(result["topic_counts"], dict(expected))
        self.assertLessEqual(result["returned_sources"], 3)
        self.assertFalse(result["detail"])
        self.assertNotIn("finding", result["sources"][0])

    def test_detailed_card_keeps_limits_and_reading_depth_without_shared_mutation(self):
        result = query_sources(source_id="R7")
        self.assertTrue(result["detail"])
        self.assertEqual(result["returned_sources"], 1)
        self.assertTrue(result["sources"][0]["limits"])
        self.assertTrue(result["sources"][0]["read_depth"])
        result["sources"][0]["limits"].clear()
        self.assertTrue(query_sources(source_id="R7")["sources"][0]["limits"])

    def test_topic_discovery_filters_records_without_implying_an_evidence_ranking(self):
        result = query_sources(topic="rights", limit=10)
        self.assertTrue(result["sources"])
        self.assertTrue(all("rights" in source["topics"] for source in result["sources"]))
        self.assertEqual(result["matched_sources"], result["returned_sources"])
        self.assertNotIn("finding", result["sources"][0])

    def test_invalid_query_is_explicit(self):
        for args in ({"topic": "romance"}, {"source_id": "R9999"},
                     {"topic": "offer", "source_id": "R7"}, {"limit": 0},
                     {"limit": True}, {"limit": 11}):
            with self.subTest(args=args), self.assertRaises(ContractError):
                query_sources(**args)

    def test_duplicate_identity_or_url_cannot_inflate_the_count(self):
        original = load_catalog()[:2]
        for field in ("id", "url", "title"):
            changed = copy.deepcopy(original)
            changed[1][field] = changed[0][field]
            with self.subTest(field=field), self.assertRaises(ContractError):
                validate_catalog(changed)

    def test_missing_scope_unknown_fields_and_false_depth_are_rejected(self):
        original = load_catalog()[:1]
        for field, value in (("limits", []), ("read_depth", "assumed_full_text"),
                             ("kind", "scientifically_proven"), ("topics", ["interview", "interview"]),
                             ("checked_on", "yesterday"), ("url", "http://example.org"),
                             ("year", 2008), ("unsupported", "extra")):
            changed = copy.deepcopy(original)
            changed[0][field] = value
            with self.subTest(field=field), self.assertRaises(ContractError):
                validate_catalog(changed)
        for field in ("setting", "jurisdiction", "version"):
            changed = copy.deepcopy(original)
            del changed[0][field]
            with self.subTest(field=field), self.assertRaises(ContractError):
                validate_catalog(changed)

    def test_loader_rejects_malformed_or_oversized_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in CATALOG_FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"schema_version":"1","sources":[]}', encoding="utf-8")
            target = root / CATALOG_FILES[0]
            target.write_text("broken", encoding="utf-8")
            with self.assertRaises(ContractError):
                load_catalog(root)
            target.write_text("x" * (256 * 1024 + 1), encoding="utf-8")
            with self.assertRaises(ContractError):
                load_catalog(root)

    def test_installed_cli_discovers_cards_without_files_network_or_memory(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target = install(base / "skills/career-junshi")
            source_count = len(load_catalog())
            for args in ([], ["--topic", "interview"], ["--id", "R18"]):
                result = subprocess.run(
                    [sys.executable, str(target / "scripts/junshi.py"), "sources", *args],
                    cwd=base, capture_output=True, timeout=20,
                )
                self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
                packet = json.loads(result.stdout.decode("utf-8"))
                self.assertEqual(packet["total_sources"], source_count)
                self.assertEqual(packet["detail"], "--id" in args)
            self.assertEqual({p.name for p in base.iterdir()}, {"skills"})
            self.assertEqual(validate(target, runtime_only=True), [])

    def test_packaging_refuses_a_missing_or_corrupted_catalog(self):
        with tempfile.TemporaryDirectory() as temp:
            target = install(Path(temp) / "career-junshi")
            for name in CATALOG_FILES:
                path = target / name
                original = path.read_bytes()
                path.unlink()
                self.assertIn("Missing required file: " + name, validate(target, runtime_only=True))
                path.write_bytes(original)
            path = target / CATALOG_FILES[0]
            data = json.loads(path.read_text(encoding="utf-8"))
            data["sources"][0]["limits"] = []
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertTrue(any(error.startswith("Invalid research catalog:") for error in validate(target, runtime_only=True)))
