"""Experience routing and installed resources, not natural-language quality."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.install_skill import install
from scripts.models import ContractError
from scripts.router import EXPERIENCES, ROUTES, route
from scripts.validate_skill import validate


class ExperienceRoutingTests(unittest.TestCase):
    def test_default_routes_preserve_the_existing_contract(self):
        for mode in ROUTES:
            r = route(mode)
            self.assertEqual(set(r), {"mode", "references", "method_plan"})
            self.assertEqual(r["references"], ROUTES[mode])
        self.assertEqual(route("recruiting", rejected=True)["references"][-1], "references/practical/rejection.md")

    def test_supported_experiences_have_bounded_distinct_resources(self):
        for name, profile in EXPERIENCES.items():
            for mode in profile["modes"]:
                with self.subTest(experience=name, mode=mode):
                    r = route(mode, experience=name)
                    self.assertEqual(r["mode"], mode)
                    self.assertEqual(r["experience"], name)
                    self.assertEqual(r["execution"], "host-led")
                    self.assertTrue(1 <= len(r["references"]) <= 3)
                    self.assertEqual(len(r["references"]), len(set(r["references"])))
                    self.assertTrue(r["suggested_artifact"].endswith((".md", ".tex")))

    def test_invalid_experience_and_mode_combinations_fail_explicitly(self):
        for mode, experience in (("offer", "defense"), ("interview", "proof-sprint"),
                                 ("job", "role-translation"), ("interview", "wording-audit"),
                                 ("interview", "unknown")):
            with self.subTest(mode=mode, experience=experience), self.assertRaises(ContractError):
                route(mode, experience=experience)

    def test_wording_audit_selects_claim_evidence_without_changing_the_default(self):
        result = route("positioning", experience="wording-audit")
        self.assertEqual(result["references"], [
            "references/knowledge/01-evidence-and-claims.md",
            "references/practical/wording-audit.md",
        ])
        self.assertEqual(result["suggested_artifact"], "wording-audit.md")
        self.assertIn("references/practical/resume.md", route("positioning")["references"])

    def test_blind_review_is_available_in_each_situation_and_ignores_rejection_shortcut(self):
        for mode in ROUTES:
            with self.subTest(mode=mode):
                ordinary = route(mode, experience="outcome-blind-review")
                rejected = route(mode, rejected=True, experience="outcome-blind-review")
                self.assertEqual(ordinary, rejected)
                self.assertEqual(ordinary["references"], [
                    "references/knowledge/02-career-decision.md",
                    "references/practical/outcome-blind-review.md",
                ])
                self.assertEqual(ordinary["suggested_artifact"], "outcome-blind-review.md")

    def test_returned_references_do_not_mutate_the_catalog(self):
        first = route("interview", experience="defense")
        first["references"].clear()
        self.assertTrue(route("interview", experience="defense")["references"])

    def test_installed_cli_routes_without_running_or_saving_a_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = install(base / "career-junshi")
            self.assertEqual(validate(target, runtime_only=True), [])
            for name, profile in EXPERIENCES.items():
                for mode in profile["modes"]:
                    for ref in route(mode, experience=name)["references"]:
                        self.assertTrue((target / ref).read_text(encoding="utf-8"))
                mode = sorted(profile["modes"])[0]
                result = subprocess.run([sys.executable, str(target / "scripts/junshi.py"), "route",
                                         "--mode", mode, "--experience", name],
                                        cwd=base, capture_output=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
                routed = json.loads(result.stdout.decode("utf-8"))
                self.assertEqual(routed["experience"], name)
                self.assertFalse((base / routed["suggested_artifact"]).exists())
            self.assertEqual({p.name for p in base.iterdir()}, {"career-junshi"})

    def test_packaging_rejects_missing_experience_playbooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = install(Path(tmp) / "career-junshi")
            playbooks = {ref for profile in EXPERIENCES.values() for ref in profile["references"] if ref.startswith("references/practical/")}
            for relative in sorted(playbooks):
                path = target / relative
                content = path.read_bytes()
                path.unlink()
                try:
                    self.assertIn("Missing required file: " + relative, validate(target, runtime_only=True))
                finally:
                    path.write_bytes(content)
