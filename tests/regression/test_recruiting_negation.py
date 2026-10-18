"""Synthetic extraction-to-decision cases; not real recruiting outcomes."""
import unittest
from datetime import datetime, timezone

from scripts.context import extract
from scripts.decision import decide
from scripts.models import ContractError


NOW = datetime(2026, 10, 19, tzinfo=timezone.utc)
OFFER_DENIALS = (
    "We have not offered you a position.",
    "We never offered you a position.",
    "We haven't offered you a position.",
    "You weren't offered a position.",
    "You have not been offered a position.",
    "You will not be offered a position.",
    "We can't offer you a position.",
    "We won’t offer you a position.",
    "You have not received an offer.",
    "We haven't issued an offer.",
    "We haven't sent an offer.",
    "We did not extend an offer.",
    "An offer has not been issued.",
    "An offer hasn't yet been extended.",
    "An offer has not been sent.",
    "The offer wasn't approved.",
    "No offer has been issued.",
)


def signal(source, assertion=None, *, status="waiting"):
    return {
        "schema_version": "1",
        "sources": [{"source_id": "HR1", "source_type": "hr_chat", "text": source}],
        "statements": [{"id": "F1", "text": source if assertion is None else assertion,
                        "source_id": "HR1", "source_type": "hr_chat", "source_span": source,
                        "epistemic": "FACT", "confidence": "direct",
                        "kind": "recruiting_signal", "modality": "observed"}],
        "situation": {"mode": "recruiting", "summary": "Synthetic HR update",
                      "recruiting": {"status": status}},
    }


class RecruitingNegationTests(unittest.TestCase):
    def test_offer_denial_cannot_be_rewritten_as_offer(self):
        for source in OFFER_DENIALS:
            with self.subTest(source=source), self.assertRaises(ContractError):
                decide(extract(signal(source, "We offered you a position.", status="offer")), now=NOW)

    def test_literal_denials_are_preserved_without_an_offer_terminal(self):
        for source in OFFER_DENIALS:
            with self.subTest(source=source):
                d = decide(extract(signal(source)), now=NOW)
                self.assertEqual(d["facts"][0]["text"], source)
                self.assertEqual(d["application_status"], "waiting")
                with self.assertRaises(ContractError):
                    extract(signal(source, status="offer"))

    def test_conditions_and_attribution_cannot_be_removed(self):
        for source in ("If approved, we would offer you a position.",
                       "We will offer you a position once approval is complete.",
                       "An offer is subject to approval.",
                       "We cannot confirm an offer.",
                       "Reportedly you were offered a position.",
                       "A colleague said you were offered a position.",
                       "I heard you received an offer."):
            with self.subTest(source=source):
                with self.assertRaises(ContractError):
                    extract(signal(source, "We offered you a position.", status="offer"))
                # Reporting what was said is allowed; the result remains unresolved.
                d = decide(extract(signal(source)), now=NOW)
                self.assertEqual(d["facts"][0]["text"], source)
                self.assertEqual(d["application_status"], "waiting")
                with self.assertRaises(ContractError):
                    extract(signal(source, status="offer"))

    def test_confirmed_results_still_reach_the_matching_terminal(self):
        for source, assertion, status in (
            ("We have offered you a position.", "You received an offer.", "offer"),
            ("An offer has been issued.", "An offer has been issued.", "offer"),
            ("We offered you a position and will contact you tomorrow.",
             "We offered you a position.", "offer"),
            ("You have passed this round.", "You passed this round.", "passed"),
            ("You were rejected this round.", "You were rejected this round.", "rejected"),
            ("You did not pass this round.", "You were rejected this round.", "rejected"),
        ):
            with self.subTest(source=source):
                d = decide(extract(signal(source, assertion, status=status)), now=NOW)
                self.assertEqual(d["application_status"], status)
                self.assertEqual(d["facts"][0]["source_span"], source)


if __name__ == "__main__":
    unittest.main()
