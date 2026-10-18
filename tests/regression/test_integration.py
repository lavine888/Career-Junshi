"""Synthetic snapshot boundary tests; LavineOS need not be installed."""
import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.context import extract
from scripts.decision import decide
from scripts.integration import adapt_snapshot, write_private_packet
from scripts.models import ContractError


def snapshot():
    return {'schema_version':'1','context_id':'synthetic-context','purpose':'Prepare a bounded interview',
            'privacy':'local-only','records':[{'id':'claim-example','type':'Claim',
                'summary':'Owned evaluation in a team prototype; service authored by teammate',
                'source_ref':'selected-note.md','source_fingerprint':'a'*64,
                'observed_at':'2026-10-04T00:00:00+00:00','last_updated':'2026-10-04',
                'freshness':'CURRENT','epistemic':'FACT','confidence':'SELF_REPORTED',
                'ownership':'team evaluation','level':1}], 'unknowns':['Current interview round not confirmed']}


class IntegrationTests(unittest.TestCase):
    def test_c_original_confidence_and_ownership_preserved_no_upgrade(self):
        value=snapshot()
        original=copy.deepcopy(value)
        packet=adapt_snapshot(value,mode='interview')
        result=extract(packet)
        self.assertEqual(result['facts'][0]['confidence'],'self_reported')
        self.assertIn('"confidence":"SELF_REPORTED"',packet['sources'][0]['text'])
        self.assertIn('team evaluation',packet['sources'][0]['text'])
        self.assertEqual(value,original)
        self.assertEqual(packet['situation']['claims'],[])

    def test_b_stale_or_missing_freshness_never_enters_current_facts(self):
        for state in ('STALE','UNKNOWN'):
            value=snapshot(); value['records'][0]['freshness']=state
            result=extract(adapt_snapshot(value,mode='interview'))
            self.assertEqual(result['facts'],[])
            self.assertTrue(result['unknowns'])

    def test_planned_and_reported_verification_not_accomplishment_upgrade(self):
        for confidence in ('PLANNED','VERIFIED'):
            value=snapshot();value['records'][0]['confidence']=confidence
            packet=adapt_snapshot(value,mode='interview')
            result=extract(packet)
            if confidence=='PLANNED':
                self.assertEqual(result['facts'],[])
            else:
                self.assertEqual(result['facts'][0]['confidence'],'self_reported')
                self.assertIn('"confidence":"VERIFIED"',packet['sources'][0]['text'])

    def test_f_independent_junshi_decision_without_lavine(self):
        result=decide(extract(adapt_snapshot(snapshot(),mode='interview')))
        self.assertEqual(result['mode'],'interview')
        self.assertTrue(result['recommended_move'])
        self.assertLessEqual(len(result['actions']),3)

    def test_invalid_fingerprint_duplicate_unknown_fields_rejected(self):
        value=snapshot();value['records'][0]['source_fingerprint']='not-a-sha'
        with self.assertRaises(ContractError): adapt_snapshot(value)
        value=snapshot();value['records'].append(copy.deepcopy(value['records'][0]))
        with self.assertRaises(ContractError): adapt_snapshot(value)
        value=snapshot();value['sync']=True
        with self.assertRaises(ContractError): adapt_snapshot(value)

    def test_source_refs_are_not_read_and_outputs_not_written_into_git(self):
        value=snapshot();value['records'][0]['source_ref']='nonexistent-private-vault/note.md'
        packet=adapt_snapshot(value)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            target=root/'extraction.json'
            write_private_packet(packet,target)
            before=target.read_bytes()
            with self.assertRaises(FileExistsError): write_private_packet(packet,target)
            self.assertEqual(target.read_bytes(),before)
            (root/'repo/.git').mkdir(parents=True)
            with self.assertRaises(ContractError): write_private_packet(packet,root/'repo/private.json')

    def test_long_unknown_record_stays_within_existing_decision_contract(self):
        value=snapshot();value['records'][0].update(summary='x'*350,freshness='UNKNOWN')
        result=decide(extract(adapt_snapshot(value,mode='interview')))
        self.assertTrue(result['unknowns'])

    def test_opportunity_cannot_be_refreshed_by_a_current_label(self):
        value=snapshot()
        value['records'][0].update(type='Opportunity',observed_at='2026-08-01T00:00:00+00:00')
        now=datetime(2026,10,4,tzinfo=timezone.utc)
        result=extract(adapt_snapshot(value,mode='interview',now=now))
        self.assertFalse(result['facts'])
        self.assertTrue(result['unknowns'])
