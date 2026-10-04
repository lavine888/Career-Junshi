"""Offline tests of checkpoint safety. Simulated transport is not a model run."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import resume_manifest as gate


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)/'checkpoint'
        self.directory.mkdir()
        self.contract=gate.read(gate.HERE/'RESUME_EVAL.json')
        self.ledger=gate.Ledger(self.directory,self.contract)

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_inventory_and_completed_skips(self):
        self.assertEqual(len(self.ledger.initial),9)
        self.assertEqual(len(self.ledger.value['pending_calls']),23)
        for row in self.ledger.initial:
            with self.assertRaisesRegex(RuntimeError,'completed call'):
                self.ledger.allowed(row['case_id'],row['arm'],row['call'])

    def test_deterministic_order_rejects_later_case(self):
        self.assertEqual(self.ledger.allowed('H01-years-gate','A','host')['status'],'PENDING')
        with self.assertRaisesRegex(RuntimeError,'order violated'):
            self.ledger.allowed('H04-equity-gap','A','extract')

    def test_checkpoint_cannot_drop_pending_calls(self):
        self.ledger.value['pending_calls'].pop()
        self.ledger.save()
        with self.assertRaisesRegex(RuntimeError,'inventory changed'):
            gate.Ledger(self.directory,self.contract)

    def test_hash_mismatch_stops_without_overwrite(self):
        f=self.directory/'captured.txt'; f.write_text('original',encoding='utf-8')
        row={'call_id':'test','output_path':'captured.txt','output_hash':gate.digest(f),
             'prompt_path':'captured.txt','prompt_hash':gate.digest(f)}
        f.write_text('changed',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'hash mismatch'):gate.check_call(row,self.directory)
        self.assertEqual(f.read_text(encoding='utf-8'),'changed')

    def test_atomic_checkpoint_keeps_previous_on_failed_replace(self):
        before=self.ledger.path.read_bytes()
        with patch.object(gate.os,'replace',side_effect=OSError('simulated disk failure')):
            with self.assertRaises(OSError):self.ledger.save()
        self.assertEqual(self.ledger.path.read_bytes(),before)
        self.assertTrue(self.ledger.path.with_name('state.json.new').exists())

    def test_exclusive_run_lock(self):
        with gate.exclusive(self.directory):
            with self.assertRaises(FileExistsError):
                with gate.exclusive(self.directory):pass
        self.assertFalse((self.directory/'RUNNING.lock').exists())

    def command(self,response):
        cmd=['node','codex','exec','--model','gpt-5.6-sol','--sandbox','read-only','-o',str(response)]
        for c in ['model_reasoning_effort="high"','web_search="disabled"','project_doc_max_bytes=0']:cmd+=['-c',c]
        for feature in gate.DISABLED:cmd+=['--disable',feature]
        return cmd

    def transport_paths(self):
        cohort=self.directory/'cohorts/run-0001'
        folder=cohort/'H01-years-gate/A';folder.mkdir(parents=True)
        prompt=folder/'host.prompt.txt';prompt.write_text('test-only prompt',encoding='utf-8')
        return cohort,prompt,folder/'host.response.txt'

    def test_success_is_checkpointed_and_never_rerun(self):
        cohort,prompt,response=self.transport_paths();calls=[]
        def simulated(cmd,**kw):
            calls.append(cmd);response.write_text('test-only response',encoding='utf-8')
            return subprocess.CompletedProcess(cmd,0,'{"type":"turn.completed","usage":{}}\n','')
        run=gate.guarded_transport(self.ledger,cohort,simulated)
        run(self.command(response),input=prompt.read_text(encoding='utf-8'))
        restored=gate.Ledger(self.directory,self.contract)
        self.assertEqual(len(restored.value['pending_calls']),22)
        self.assertEqual(len(restored.value['completed_calls']),1)
        with self.assertRaisesRegex(RuntimeError,'completed call'):
            run(self.command(response),input='other')
        self.assertEqual(len(calls),1)

    def test_quota_stops_cleanly_without_model_fallback(self):
        cohort,prompt,response=self.transport_paths();calls=[]
        def unavailable(cmd,**kw):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd,1,'{"type":"error","message":"You have hit your usage limit"}\n','')
        run=gate.guarded_transport(self.ledger,cohort,unavailable)
        result=run(self.command(response),input=prompt.read_text(encoding='utf-8'))
        self.assertEqual(result.returncode,1)
        self.assertEqual(self.ledger.value['status'],'BLOCKED_MODEL_ACCESS')
        self.assertEqual(len(self.ledger.value['pending_calls']),23)
        self.assertEqual(len(calls),1)
        with self.assertRaisesRegex(RuntimeError,'no further calls'):
            run(self.command(response),input='test')
        self.assertEqual(len(calls),1)

    def test_timeout_is_uncertain_and_cannot_auto_retry(self):
        cohort,prompt,response=self.transport_paths()
        def timeout(cmd,**kw):raise subprocess.TimeoutExpired(cmd,480)
        with self.assertRaises(subprocess.TimeoutExpired):
            gate.guarded_transport(self.ledger,cohort,timeout)(self.command(response),input=prompt.read_text(encoding='utf-8'))
        with self.assertRaisesRegex(RuntimeError,'uncertain completion'):self.ledger.recover()

    def test_no_overwrite_even_for_pending_call(self):
        cohort,prompt,response=self.transport_paths();response.write_text('unexpected existing output',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'overwrite'):
            gate.guarded_transport(self.ledger,cohort,lambda *a,**k:self.fail('transport must not run'))(
                self.command(response),input=prompt.read_text(encoding='utf-8'))

    def test_model_or_reasoning_changes_stop_before_transport(self):
        cohort,prompt,response=self.transport_paths();cmd=self.command(response)
        cmd[cmd.index('--model')+1]='another-model'
        with self.assertRaisesRegex(RuntimeError,'configuration changed'):
            gate.guarded_transport(self.ledger,cohort,lambda *a,**k:self.fail('transport must not run'))(cmd,input='test')
        cmd=self.command(response)
        cmd[cmd.index('model_reasoning_effort="high"')]='model_reasoning_effort="low"'
        with self.assertRaisesRegex(RuntimeError,'configuration changed'):
            gate.guarded_transport(self.ledger,cohort,lambda *a,**k:self.fail('transport must not run'))(cmd,input='test')

    def test_repair_inventory_preserves_single_round_and_moves(self):
        accounting=gate.read(gate.HERE/'REPAIR_ACCOUNTING.json')
        self.assertEqual(accounting['original_metrics']['repairs_attempted'],2)
        self.assertEqual(accounting['original_metrics']['recommendation_changed_by_repair_count'],0)
        for row in accounting['cases']:
            if row['repair_requested']:
                self.assertEqual(row['host_repair_count'],1)
                self.assertTrue(row['recommendation_move_preserved_exactly'])

    def test_new_repair_is_queued_once_by_frozen_validator(self):
        pending=next(r for r in self.ledger.value['pending_calls'] if r['case_id']=='H04-equity-gap' and r['call']=='envelope')
        folder=self.directory/'cohorts/run-0001/H04-equity-gap/B';folder.mkdir(parents=True)
        prompt=folder/'envelope.prompt.txt';prompt.write_text('test-only',encoding='utf-8')
        response=folder/'envelope.response.txt'
        response.write_text(json.dumps({'envelope_json':json.dumps({'schema_version':'2'})}),encoding='utf-8')
        self.ledger.finish(pending,{'execution':{'exit_code':0}},prompt,response)
        self.ledger.schedule_repairs()
        repairs=[r for r in self.ledger.value['pending_calls'] if r['call_id']=='H04-equity-gap/B/repair']
        self.assertEqual(len(repairs),1)


if __name__=='__main__':unittest.main()
