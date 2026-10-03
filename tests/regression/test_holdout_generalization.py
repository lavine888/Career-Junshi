"""General frozen-failure regressions; names, amounts, order and industry vary."""
import copy
import unittest
from datetime import timedelta
from scripts.decision import decide
from tests.regression.test_decision import NOW, situation
from tests.regression.test_decision_quality import candidate, direction, qualitative_offer


class HoldoutGeneralizationTests(unittest.TestCase):
    def test_unscored_singleton_is_not_comparative_evidence(self):
        for name, boundary in [("Saffron Robotics", "six months cash"), ("Bay Healthcare", "daily care schedule"), ("Delta Energy", "licensed location")]:
            with self.subTest(name=name):
                offer = {"constraints": [boundary], "priorities": {"ownership": "high"}, "source_ids": ["synthetic:user"], "options": [{"name": name, "constraint_status": "unknown", "ratings": {}}]}
                d = decide(situation("offer", offer=offer))
                self.assertIsNone(d["current_preference"])
                self.assertEqual(d["recommendation_type"], "BLOCKED")
                self.assertTrue(d["decision_sufficiency"]["blocking_unknowns"])
                self.assertTrue(all(c["score"] is None for c in d["comparison"]))

    def test_blocked_singleton_keeps_decisive_questions_without_winner(self):
        offer = qualitative_offer()
        offer["options"] = [offer["options"][1]]
        offer["constraints"] = ["Cash feasibility"]
        d = decide(situation("offer", offer=offer))
        self.assertIsNone(d["current_preference"])
        self.assertEqual(d["recommendation_type"], "BLOCKED")
        self.assertEqual(len(d["decision_unknowns"]), 3)
        self.assertTrue(d["reversal_conditions"])
        self.assertIn("condition-0", d["actions"][1]["description"])

    def test_known_comparison_retains_tilt_but_unknown_hard_constraint_blocks_acceptance(self):
        for industry, numbers in [("Clinical", (0,1)), ("Energy", (2,4)), ("Logistics", (4,5))]:
            for reverse in [False, True]:
                with self.subTest(industry=industry, ratings=numbers, reversed=reverse):
                    offer = copy.deepcopy(qualitative_offer())
                    chosen = industry + " technical role"
                    offer["constraints"] = ["No unbounded travel"]
                    offer["options"][0]["name"] = industry + " alternate"
                    offer["options"][1]["name"] = chosen
                    for i, option in enumerate(offer["options"]):
                        option["ratings"].update(learning=numbers[i], ownership=numbers[i])
                    for u in offer["critical_unknowns"]:
                        u["option"] = chosen
                    if reverse:
                        offer["options"].reverse()
                    d = decide(situation("offer", offer=offer))
                    self.assertEqual(d["current_preference"], chosen)
                    self.assertEqual(d["recommendation_type"], "BLOCKED")
                    self.assertTrue(d["decision_sufficiency"]["blocking_unknowns"])
                    next(o for o in offer["options"] if o["name"] == chosen)["constraint_status"] = "pass"
                    d = decide(situation("offer", offer=offer))
                    self.assertEqual(d["recommendation_type"], "CONDITIONAL")
                    self.assertFalse(d["decision_sufficiency"]["blocking_unknowns"])

    def test_nonblocking_unknowns_do_not_block_evidence_based_comparison(self):
        self.assertEqual(decide(situation("offer", offer=qualitative_offer()))["recommendation_type"], "CONDITIONAL")

    def test_single_feasible_survivor_of_real_comparison_is_not_lost(self):
        offer = qualitative_offer()
        offer["options"][0]["constraint_status"] = "fail"
        offer["options"][1]["constraint_status"] = "pass"
        self.assertEqual(decide(situation("offer", offer=offer))["current_preference"], "Willow")

    def test_outside_catalog_labels_compare_without_false_family(self):
        for names, months in [(("Clinical Systems Engineer", "Customer Integrator"), 8), (("Energy ML Engineer", "Field Research Engineer"), 26), (("Supply Chain Scientist", "Operations Developer"), 41)]:
            a = candidate(names[0], "unknown", "high")
            b = candidate(names[1], "unknown", "medium")
            a["strongest_proof"] = f"Reported {months} months of continuous deliveries; not independent verification"
            b["strongest_proof"] = f"Reported {months + 3} months of adjacent work; interpretation remains medium"
            for values in [[a, b], [b, a]]:
                d = decide(direction(values))
                self.assertEqual(d["primary_choice"], [names[0]])
                self.assertTrue(all(c["role_family"] == "unknown" for c in d["direction"]["comparison"]))
            a["assessment"]["goal_fit"] = "low"
            self.assertEqual(decide(direction([a,b]))["primary_choice"], [names[1]])

    def test_unknown_family_is_not_a_claim_of_evidence(self):
        a = candidate("Unknown technical path", "unknown", "unknown", "unknown")
        self.assertEqual(decide(direction([a]))["recommendation_type"], "BLOCKED")

    def test_deadline_overrides_wait_across_names_calendars_and_hours(self):
        for hours, event in [(8, "healthcare final"), (48, "energy interview"), (71, "retail screening")]:
            r = {"status": "waiting", "working_days": None, "promised_date": "later", "communication": {"stage": "interview", "tone": "neutral", "last_event": event, "source_ids": ["synthetic:user"]}}
            due = (NOW + timedelta(hours=hours)).isoformat()
            d = decide(situation("recruiting", recruiting=r, deadline=due), now=NOW)
            self.assertEqual(d["follow_up"]["action"], "send_now")
            self.assertIn(d["urgency"]["deadline"], d["follow_up"]["window"])
            self.assertEqual(d["application_status"], "waiting")
            self.assertLessEqual(len(d["actions"]), 3)

    def test_deadline_does_not_override_contact_ban_or_repeat_followup(self):
        due = (NOW + timedelta(hours=24)).isoformat()
        for r in [{"no_contact": True}, {"followups": 1}]:
            d = decide(situation("recruiting", recruiting=r, deadline=due), now=NOW)
            self.assertNotEqual(d["follow_up"]["action"], "send_now")

    def test_overdue_deadline_does_not_create_extension(self):
        due = (NOW - timedelta(hours=12)).isoformat()
        d = decide(situation("recruiting", recruiting={"working_days": None}, deadline=due), now=NOW)
        self.assertTrue(d["urgency"]["overdue"])
        self.assertNotEqual(d["follow_up"]["action"], "send_now")
        self.assertEqual(d["application_status"], "waiting")
