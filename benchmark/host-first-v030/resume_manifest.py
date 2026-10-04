"""Manifest-gated wrapper for the unchanged, frozen resume.py.

No rubric interpretation, product edits or model fallback. Checkpoints live outside
the repository; original evidence is read-only. --plan-only never invokes a model.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import resume as frozen_runner
from run import ROOT, digest, dump

HERE = Path(__file__).resolve().parent
DISABLED = ['apps', 'multi_agent', 'remote_plugin', 'hooks', 'memories',
            'browser_use', 'browser_use_external', 'computer_use',
            'image_generation', 'sleep_tool', 'shell_tool']


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic(path, value):
    """Same-directory replace; readers see a complete old or new checkpoint."""
    temporary = path.with_name(path.name + '.new')
    with temporary.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def under(path, parent):
    return path == parent or parent in path.parents


def verify_map(parent, files):
    for relative, expected in files.items():
        path = (parent/relative).resolve()
        if not under(path, parent.resolve()) or not path.is_file() or digest(path) != expected:
            raise RuntimeError('Frozen hash mismatch: '+relative)


def verify_cohort(path):
    manifest = path/('OUTPUT_FREEZE.json' if (path/'OUTPUT_FREEZE.json').exists()
                     else 'RESUME_OUTPUT_FREEZE.json')
    value = read(manifest)
    verify_map(path, value['files'])
    actual = {p.relative_to(path).as_posix() for p in path.rglob('*')
              if p.is_file() and p != manifest and '__pycache__' not in p.parts}
    if actual != set(value['files']):
        raise RuntimeError('Frozen cohort file set changed')


def verify_contract(manifest, baseline):
    value = read(manifest)
    if (value['model'], value['reasoning_level'], value['reference_mode'],
        value['repair_limit'], value['tools_enabled']) != (
            'gpt-5.6-sol', 'high', 'CONTROLLED_PRELOAD', 1, False):
        raise RuntimeError('Evaluation configuration changed')
    verify_map(ROOT, value['immutable_files_sha256'])
    verify_map(ROOT, read(HERE/'RESUME_TOOLING_FREEZE.json')['files'])
    base = read(HERE/'BASELINE_RUNTIME.json')
    for relative, expected in base['normalized_utf8_lf_sha256'].items():
        path = baseline/relative
        if not path.is_file() or hashlib.sha256(path.read_text(encoding='utf-8').encode()).hexdigest() != expected:
            raise RuntimeError('Baseline differs: '+relative)
    # Hashing opaque rubric bytes is not interpreting or supplying a rubric.
    for relative, expected in value['baseline_evaluation_sha256'].items():
        path = baseline/relative
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError('Baseline evaluation input changed: '+relative)
    verify_cohort(HERE/'fresh')
    return value


def check_call(record, parent):
    for field, hash_field in [('output_path', 'output_hash'), ('prompt_path', 'prompt_hash')]:
        path = (parent/record[field]).resolve()
        if not under(path,parent.resolve()) or not path.is_file() or digest(path) != record[hash_field]:
            raise RuntimeError('Completed call hash mismatch: '+record['call_id'])


class Ledger:
    def __init__(self, directory, manifest):
        self.directory = directory
        self.path = directory/'state.json'
        self.contract = manifest
        self.manifest_sha256 = digest(HERE/'RESUME_EVAL.json')
        if self.path.exists():
            self.value = read(self.path)
            if self.value['manifest_sha256'] != self.manifest_sha256:
                raise RuntimeError('Checkpoint belongs to another frozen experiment')
        else:
            self.value = {'manifest_sha256': self.manifest_sha256,
                          'status': 'INCOMPLETE', 'completed_calls': [],
                          'pending_calls': read(HERE/'REMAINING_CALLS.json'),
                          'attempts': [], 'cohorts': []}
            self.save()
        initial = read(HERE/'COMPLETED_CALLS.json')
        for record in initial:
            check_call(record, ROOT)
        for record in self.value['completed_calls']:
            check_call(record, directory)
        self.initial_ids = {record['call_id'] for record in initial}
        self.initial = initial
        self.verify_inventory()
        self.schedule_repairs()

    def save(self):
        self.value['updated_at'] = now()
        atomic(self.path, self.value)

    def verify_inventory(self):
        base={r['call_id'] for r in read(HERE/'REMAINING_CALLS.json')}
        rows=self.value['completed_calls']+self.value['pending_calls']
        ids=[r['call_id'] for r in rows]
        if len(ids)!=len(set(ids)) or self.initial_ids.intersection(ids) or not base.issubset(ids):
            raise RuntimeError('Checkpoint call inventory changed')
        for r in rows:
            case=r['case_id'];arm=r['arm'];call=r['call']
            if (case not in self.contract['case_inputs'] or
                r['call_id']!=case+'/'+arm+'/'+call or
                r['input_hash']!=self.contract['case_inputs'][case]['sha256'] or
                (r['call_id'] not in base and (arm,call)!=('B','repair'))):
                raise RuntimeError('Unknown call or input in checkpoint')

    def allowed(self, case, arm, call):
        identity = case+'/'+arm+'/'+call
        if identity in self.initial_ids or any(r['call_id']==identity for r in self.value['completed_calls']):
            raise RuntimeError('Refusing to rerun completed call: '+identity)
        pending = next((r for r in self.value['pending_calls'] if r['call_id']==identity), None)
        if pending is None:
            raise RuntimeError('Call is not PENDING in manifest: '+identity)
        order = {'extract': 0, 'host': 1, 'envelope': 2, 'repair': 3}
        first = min(self.value['pending_calls'], key=lambda r:(r['case_id'], order[r['call']]))
        if first['call_id'] != identity:
            raise RuntimeError('Deterministic call order violated: '+identity)
        return pending

    def finish(self, pending, execution, prompt, response):
        identity = pending['call_id']
        record = {**pending, 'status': 'COMPLETED', **execution,
                  'prompt_hash': digest(prompt), 'output_hash': digest(response),
                  'prompt_path': prompt.relative_to(self.directory).as_posix(),
                  'output_path': response.relative_to(self.directory).as_posix()}
        self.value['completed_calls'].append(record)
        self.value['pending_calls'] = [r for r in self.value['pending_calls'] if r['call_id'] != identity]
        self.save()
        self.schedule_repairs()

    def schedule_repairs(self):
        for pending in self.value['completed_calls']:
            if pending['call'] != 'envelope':
                continue
            repair_id=pending['case_id']+'/B/repair'
            known=self.initial_ids | {r['call_id'] for r in self.value['completed_calls']} | {r['call_id'] for r in self.value['pending_calls']}
            if repair_id in known:
                continue
            raw = read(ROOT/self.contract['case_inputs'][pending['case_id']]['path'])
            try:
                candidate = json.loads(read(self.directory/pending['output_path'])['envelope_json'])
            except (KeyError, ValueError, TypeError):
                self.value['status']='BLOCKED_EXECUTION'
                self.save()
                raise RuntimeError('Completed envelope cannot be parsed; preserve output, do not regenerate')
            v = frozen_runner.validate_decision_envelope(candidate, raw, now=datetime.fromisoformat(raw['as_of']))
            if v['status'] != 'ACCEPT':
                self.value['pending_calls'].append({'case_id':pending['case_id'], 'architecture':'host-first',
                    'call_id':repair_id, 'arm':'B','call':'repair', 'stage':'repair', 'status':'PENDING',
                    'input_hash':pending['input_hash'],
                    'conditional_on':'Frozen validator requested the sole repair',
                    'initial_validator_result':v['status']})
                self.save()

    def recover(self):
        """Freeze interrupted cohorts; never re-sample an ambiguous started call."""
        if any(a['status']=='RUNNING' for a in self.value['attempts']):
            self.value['status']='BLOCKED_RECOVERY'
            self.save()
            raise RuntimeError('Interrupted model call has uncertain completion; inspect private log/response, do not rerun')
        for record in self.value['cohorts']:
            cohort = self.directory/record['path']
            if record['status'] == 'OPEN':
                # A ledger commit can precede the original runner execution-file write.
                self.recover_execution_files(cohort)
                self.freeze(cohort)
                record['status']='FROZEN'
                self.save()
            verify_cohort(cohort)

    def recover_execution_files(self, cohort):
        for call in self.value['completed_calls']:
            response = self.directory/call['output_path']
            if under(response, cohort):
                execution_path = response.with_name(call['call']+'.execution.json')
                if not execution_path.exists():
                    dump(execution_path, call['execution'])

    @staticmethod
    def freeze(cohort):
        manifest = cohort/'RESUME_OUTPUT_FREEZE.json'
        if not manifest.exists():
            dump(manifest, {'files':{p.relative_to(cohort).as_posix():digest(p)
                for p in sorted(cohort.rglob('*')) if p.is_file()}, 'created_at':now()})


def execution_record(result, prompt, response, started):
    events = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
    errors = [e.get('message',e.get('error',{}).get('message','')) for e in events if e.get('type') in {'error','turn.failed'}]
    tools = [e for e in events if e.get('item',{}).get('type') in {'command_execution','mcp_tool_call','web_search'}]
    quota = any('usage limit' in str(message).casefold() for message in errors)
    return {'model':'gpt-5.6-sol', 'effort':'high', 'reference_mode':'CONTROLLED_PRELOAD',
            'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
            'response_sha256':digest(response) if response.exists() else None,
            'exit_code':result.returncode, 'tool_invocations':len(tools),
            'started_at':started, 'completed_at':now(), 'usage_limit':quota,
            'event_log_sha256':hashlib.sha256(result.stdout.encode()).hexdigest(),
            'usage':[e.get('usage') for e in events if e.get('type')=='turn.completed']}


def guarded_transport(ledger, cohort, real_run):
    def run(command, **kwargs):
        if 'exec' not in command or '--model' not in command:
            return real_run(command, **kwargs)
        if ledger.value['status'].startswith('BLOCKED'):
            raise RuntimeError('Stopped after model access/execution failure; no further calls this run')
        response = Path(command[command.index('-o')+1]).resolve()
        case, arm, filename = response.relative_to(cohort).parts
        call = filename.removesuffix('.response.txt')
        pending = ledger.allowed(case, arm, call)
        required = {'--model':'gpt-5.6-sol', '--sandbox':'read-only'}
        if any(command[command.index(k)+1] != v for k,v in required.items()):
            raise RuntimeError('Model or sandbox configuration changed')
        configs = [command[i+1] for i,x in enumerate(command) if x=='-c']
        if configs != ['model_reasoning_effort="high"','web_search="disabled"','project_doc_max_bytes=0']:
            raise RuntimeError('Reasoning/reference/tool configuration changed')
        disabled = [command[i+1] for i,x in enumerate(command) if x=='--disable']
        if disabled != DISABLED:
            raise RuntimeError('Tool permissions changed')
        if response.exists():
            raise RuntimeError('Refusing to overwrite an existing response')
        attempt = {'call_id':pending['call_id'], 'cohort':cohort.relative_to(ledger.directory).as_posix(),
                   'status':'RUNNING', 'started_at':now()}
        ledger.value['attempts'].append(attempt)
        ledger.save()
        try:
            result = real_run(command, **kwargs)
        except Exception:
            # Completion is uncertain after timeout/interruption. Do not auto retry.
            ledger.value['status']='BLOCKED_RECOVERY'
            ledger.save()
            raise
        execution = execution_record(result, kwargs['input'], response, attempt['started_at'])
        ok = result.returncode==0 and response.is_file() and not execution['tool_invocations']
        attempt.update(status='COMPLETED' if ok else 'FAILED', execution=execution)
        if ok:
            ledger.finish(pending, {'execution':execution, 'timestamp':execution['completed_at'],
                'model':execution['model'], 'reasoning_setting':execution['effort']},
                response.with_name(call+'.prompt.txt'), response)
        else:
            ledger.value['status']='BLOCKED_MODEL_ACCESS' if execution['usage_limit'] or result.returncode else 'BLOCKED_EXECUTION'
            ledger.save()
        return result
    return run


@contextmanager
def exclusive(directory):
    lock = directory/'RUNNING.lock'
    with lock.open('x', encoding='utf-8') as stream:
        stream.write(str(os.getpid()))
    try:
        yield
    finally:
        lock.unlink()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--state-dir', type=Path, required=True)
    parser.add_argument('--private-runtime', type=Path)
    parser.add_argument('--node')
    parser.add_argument('--codex-js')
    parser.add_argument('--plan-only', action='store_true')
    args=parser.parse_args()
    baseline=args.baseline.resolve(); directory=args.state_dir.resolve()
    if under(directory, ROOT) or under(directory, baseline):
        parser.error('Checkpoint must be outside the repository and baseline')
    contract=verify_contract(HERE/'RESUME_EVAL.json', baseline)
    directory.mkdir(parents=True,exist_ok=True)
    with exclusive(directory):
        ledger=Ledger(directory, contract)
        ledger.recover()
        if args.plan_only:
            print(json.dumps({'status':ledger.value['status'], 'pending_calls':len(ledger.value['pending_calls']),
                'completed_model_calls':len(ledger.initial)+len(ledger.value['completed_calls']), 'model_calls_this_run':0}))
            return 0
        if not args.private_runtime or not args.node or not args.codex_js:
            parser.error('Actual resume requires --private-runtime, --node and --codex-js')
        private=args.private_runtime.resolve()
        if under(private, ROOT) or under(private, baseline) or under(private,directory) or under(directory,private):
            parser.error('Private runtime must be outside repositories and separate from checkpoint')
        index=len(ledger.value['cohorts'])+1
        cohort=directory/'cohorts'/('run-%04d'%index)
        previous=[directory/r['path'] for r in reversed(ledger.value['cohorts'])]+[HERE/'fresh']
        record={'path':cohort.relative_to(directory).as_posix(),'status':'OPEN'}
        ledger.value['cohorts'].append(record);ledger.value['status']='INCOMPLETE';ledger.save()
        original_run=subprocess.run; original_argv=sys.argv
        argv=['resume.py','--baseline',str(baseline),'--output',str(cohort),
              '--private-runtime',str(private/('run-%04d'%index)), '--node',args.node,'--codex-js',args.codex_js]
        for prior in previous: argv+=['--previous',str(prior)]
        try:
            sys.argv=argv
            subprocess.run=guarded_transport(ledger,cohort,original_run)
            result=frozen_runner.main()
        finally:
            subprocess.run=original_run;sys.argv=original_argv
            if cohort.exists():
                ledger.recover_execution_files(cohort)
                ledger.freeze(cohort);record['status']='FROZEN'
                verify_cohort(cohort)
                ledger.save()
        if result==0 and not ledger.value['pending_calls']:
            ledger.value['status']='GENERATIONS_COMPLETE_REVIEW_PENDING';ledger.save()
        print(json.dumps({'status':ledger.value['status'],'pending_calls':len(ledger.value['pending_calls']),
            'boundary':'No final architecture decision or semantic grade is calculated by this runner'}))
        return result


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (RuntimeError, FileExistsError) as exc:
        print(str(exc),file=sys.stderr)
        raise SystemExit(2)
