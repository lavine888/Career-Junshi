import tempfile
import unittest

from scripts.decision import decide
from scripts.feedback_loop import decision_record, feedback_next_move
from scripts.memory_store import MemoryStore
from scripts.models import ContractError
from tests.regression.test_decision import NOW, situation


class DecisionOutcomeRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = MemoryStore(self.tmp.name)
        self.store.consent(confirmed=True)
        self.d = decide(situation(), now=NOW)
        self.raw = decision_record(self.d, source="synthetic:session", expected_outcome="architecture may be discussed")
        self.saved = self.store.record_decision("interview-A", self.raw)

    def outcome(self, **extra):
        data = {"decision_id": self.saved["id"], "hard_outcome": "passed",
                "observed_facts": [{"text": "Architecture was discussed for 12 minutes", "source": "synthetic:user report"}],
                "user_interpretation": "I passed because of prep", "agent_interpretation": "Preparation may have been relevant",
                "unknowns": ["interviewer rating"], "source": "synthetic:user report"}
        data.update(extra)
        return data

    def test_persistent_decision_to_outcome(self):
        outcome = self.outcome()
        result = self.store.record_outcome("interview-A", outcome)
        loaded = MemoryStore(self.tmp.name).read(kind="outcome", subject="interview-A")[0]
        self.assertEqual(loaded["id"], result["id"])
        self.assertEqual(loaded["parent_id"], self.saved["id"])
        self.assertEqual(loaded["data"]["hard_outcome"], "passed")
        self.assertIn("不证明", loaded["data"]["learning"])
        self.assertEqual(feedback_next_move(outcome)["causal_status"], "UNKNOWN")
        self.assertEqual(feedback_next_move(outcome)["profile_auto_updates"], [])

    def test_interpretation_does_not_set_outcome(self):
        self.store.record_outcome("interview-A", self.outcome(hard_outcome="waiting", user_interpretation="silence means rejected"))
        saved = self.store.read(kind="outcome")[0]["data"]
        self.assertEqual(saved["hard_outcome"], "waiting")
        self.assertIn("silence", saved["user_interpretation"])

    def test_history_append_only(self):
        with self.assertRaises(ContractError): self.store.put("decision", "interview-A", self.raw, record_id=self.saved["id"])
        second = self.store.record_decision("interview-A", {**self.raw, "decision": "new recommendation"})
        self.assertNotEqual(second["id"], self.saved["id"])
        self.assertEqual(len(self.store.read(kind="decision")), 2)

    def test_outcome_parent_must_exist_and_match_subject(self):
        with self.assertRaises(ContractError): self.store.record_outcome("interview-B", self.outcome())
        with self.assertRaises(ContractError): self.store.record_outcome("interview-A", self.outcome(decision_id="missing"))

    def test_delete_decision_cascades_to_outcome(self):
        self.store.record_outcome("interview-A", self.outcome())
        self.assertEqual(self.store.delete(self.saved["id"], confirmed=True)["deleted"], 2)
        self.assertEqual(self.store.status()["records"], 0)
