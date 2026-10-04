"""Continue missing model calls into a NEW directory, preserving frozen attempts.

Completed responses are reused only after hash/prompt verification. An existing
host repair is never repeated. Stop on the first service usage-limit rejection.
This script does not read rubrics, grade outputs or change model/settings.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from run import ROOT, GUIDE, digest, dump, write
from scripts.envelope import validate_decision_envelope, repair_request


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous', type=Path, required=True, action='append', help='Explicit prior output roots, newest first; repeat to reuse several frozen cohorts')
    for name in ('baseline', 'output', 'private-runtime'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--plan-only', action='store_true', help='Verify inputs and write a pending-call plan without any model invocation')
    p.add_argument('--node', required=True)
    p.add_argument('--codex-js', required=True)
    args = p.parse_args()
    previous = [path.resolve() for path in args.previous]
    baseline, output, private = [getattr(args, key).resolve() for key in ['baseline', 'output', 'private_runtime']]
    if output.exists() or private.exists() or 'holdout-v023' in output.parts:
        p.error('Use new output/private-runtime paths outside the frozen corpus')
    parent_hashes=[]
    for old in previous:
        manifest=old/('OUTPUT_FREEZE.json' if (old/'OUTPUT_FREEZE.json').exists() else 'RESUME_OUTPUT_FREEZE.json')
        freeze = json.loads(manifest.read_text(encoding='utf-8'))
        for name, sha in freeze['files'].items():
            if not (old/name).is_file() or digest(old/name) != sha:
                p.error('Previous frozen output changed: '+name)
        parent_hashes.append(digest(manifest))
    baseline_manifest = json.loads((Path(__file__).parent/'BASELINE_RUNTIME.json').read_text(encoding='utf-8'))
    for name, sha in baseline_manifest['normalized_utf8_lf_sha256'].items():
        path = baseline/name
        if not path.is_file() or hashlib.sha256(path.read_text(encoding='utf-8').encode()).hexdigest() != sha:
            p.error('Not the frozen v023 baseline: '+name)
    output.mkdir(parents=True)
    def cached_file(case, arm, name):
        return next((root/case/arm/name for root in previous if (root/case/arm/name).is_file()), None)
    if args.plan_only:
        pending=[]
        for case in sorted(c for c in (baseline/'benchmark/holdout-v023').iterdir() if (c/'input/context.json').is_file()):
            for arm,name in [('A','extract'),('A','host'),('B','envelope')]:
                completed=any((root/case.name/arm/(name+'.response.txt')).exists() and (root/case.name/arm/(name+'.execution.json')).exists() and json.loads((root/case.name/arm/(name+'.execution.json')).read_text(encoding='utf-8'))['exit_code']==0 for root in previous)
                if not completed:
                    pending.append({'case':case.name,'arm':arm,'call':name})
        dump(output/'PENDING_CALLS.json',{'model':'gpt-5.6-sol','effort':'high','reference_mode':'CONTROLLED_PRELOAD','parent_freeze_sha256':parent_hashes,'pending_base_calls':pending,'additional_repairs':'At most one per B case; existing repairs must be reused, never repeated','model_calls_in_plan':0})
        print(json.dumps({'pending_base_calls':len(pending),'model_calls':0}))
        return 0
    private.mkdir(parents=True)
    workspaces = {}
    for arm, source in [('A', baseline), ('B', ROOT)]:
        workspace = private/arm
        workspace.mkdir()
        run = subprocess.run([sys.executable, str(source/'scripts/install_skill.py'), '--target', str(workspace/'skills/career-junshi')],capture_output=True,text=True,encoding='utf-8',timeout=60)
        if run.returncode:
            raise RuntimeError(run.stderr)
        workspaces[arm] = workspace
    dump(output/'RESUME_PROTOCOL.json', {'parent_output_freeze_sha256':parent_hashes,
        'model':'gpt-5.6-sol','effort':'high','reference_mode':'CONTROLLED_PRELOAD','repair_budget_per_case':1,
        'runtime_files':{str(path.relative_to(ROOT)).replace('\\','/'):digest(path) for path in [ROOT/'SKILL.md',*sorted((ROOT/'scripts').glob('*.py'))]},
        'boundary':'Separate resumed cohort. Prior generations/repair budget retained. No independent unseen-case claim.',
        'created_at':datetime.now(timezone.utc).isoformat()})
    records = []

    def invoke(case, arm, name, prompt, wrapper=None):
        for root in previous:
            prior = root/case/arm
            prior_response, prior_record = prior/(name+'.response.txt'), prior/(name+'.execution.json')
            if not prior_response.exists() or not prior_record.exists():
                continue
            execution = json.loads(prior_record.read_text(encoding='utf-8'))
            if execution['exit_code'] == 0:
                if digest(prior_response) != execution['response_sha256'] or execution['tool_invocations']:
                    raise RuntimeError('Cached response integrity failure')
                # Prompt changes require a fresh explicitly separate experiment,
                # not a silent reinterpretation of an existing generation.
                if hashlib.sha256(prompt.encode()).hexdigest() != execution['prompt_sha256']:
                    raise RuntimeError('Cached prompt changed; preserve prior generation')
                records.append({'case':case,'arm':arm,'call':name,'reused':True,'response_sha256':digest(prior_response)})
                return prior_response.read_text(encoding='utf-8')
        folder = output/case/arm
        folder.mkdir(parents=True,exist_ok=True)
        write(folder/(name+'.prompt.txt'),prompt)
        response = folder/(name+'.response.txt')
        cmd = [args.node,args.codex_js,'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json','--color','never','--cd',str(workspaces[arm]),'--model','gpt-5.6-sol','-c','model_reasoning_effort="high"','-c','web_search="disabled"','-c','project_doc_max_bytes=0','-o',str(response)]
        for feature in ['apps','multi_agent','remote_plugin','hooks','memories','browser_use','browser_use_external','computer_use','image_generation','sleep_tool','shell_tool']:
            cmd += ['--disable',feature]
        if wrapper:
            schema = private/(case+'-'+arm+'-'+name+'.schema.json')
            dump(schema, {'type':'object','properties':{wrapper:{'type':'string'}},'required':[wrapper],'additionalProperties':False})
            cmd += ['--output-schema',str(schema)]
        start = datetime.now(timezone.utc).isoformat()
        run = subprocess.run(cmd+['-'],input=prompt,capture_output=True,text=True,encoding='utf-8',timeout=480,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        write(private/(case+'-'+arm+'-'+name+'.events.jsonl'),run.stdout)
        events = [json.loads(line) for line in run.stdout.splitlines() if line.startswith('{')]
        errors = [e.get('message',e.get('error',{}).get('message','')) for e in events if e.get('type') in {'error','turn.failed'}]
        tools = [e for e in events if e.get('item',{}).get('type') in {'command_execution','mcp_tool_call','web_search'}]
        quota = any('usage limit' in message.casefold() for message in errors)
        execution = {'model':'gpt-5.6-sol','effort':'high','reference_mode':'CONTROLLED_PRELOAD','prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
            'exit_code':run.returncode,'tool_invocations':len(tools),'response_sha256':digest(response) if response.exists() else None,
            'started_at':start,'completed_at':datetime.now(timezone.utc).isoformat(),'event_log_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),
            'usage':[e.get('usage') for e in events if e.get('type')=='turn.completed'],'usage_limit':quota}
        dump(folder/(name+'.execution.json'),execution)
        records.append({'case':case,'arm':arm,'call':name,'reused':False,**execution})
        print(case,arm,name,run.returncode,flush=True)
        if quota:
            raise RuntimeError('USAGE_LIMIT: stopped without further model attempts')
        if run.returncode or tools or not response.exists():
            raise RuntimeError('Actual model call failed; raw logs retained privately')
        return response.read_text(encoding='utf-8')

    def cli(case, arm, source, params):
        folder=output/case/arm
        folder.mkdir(parents=True,exist_ok=True)
        run=subprocess.run([sys.executable,str(source/'scripts/junshi.py'),*params],capture_output=True,text=True,encoding='utf-8',timeout=60)
        write(folder/'runtime.stdout.json',run.stdout)
        write(folder/'runtime.stderr.txt',run.stderr)
        dump(folder/'runtime.execution.json',{'exit_code':run.returncode})
        return run

    rows=[]
    try:
        for case in sorted(c for c in (baseline/'benchmark/holdout-v023').iterdir() if (c/'input/context.json').is_file()):
            raw=json.loads((case/'input/context.json').read_text(encoding='utf-8'))
            old_extract=(baseline/f'benchmark/holdout-v023-runner/after-prompts/after-extract-{case.name}.txt').read_text(encoding='utf-8')
            preload=json.loads(old_extract.splitlines()[1])
            packet=json.loads(json.loads(invoke(case.name,'A','extract',old_extract,'packet_json'))['packet_json'])
            folder=output/case.name/'A'; folder.mkdir(parents=True,exist_ok=True)
            dump(folder/'extraction-packet.json',packet)
            given={s['source_id']:{k:s[k] for k in ['source_id','source_type','text']} for s in raw['materials']}
            actual={s['source_id']:s for s in packet['sources']}
            identity=all(actual.get(k)==v for k,v in given.items()) and all(s.get('source_type')=='user_report' and s.get('text')==raw['request'] for k,s in actual.items() if k not in given)
            if not identity:
                compiled={'pipeline_error':'Source identity mismatch'}
            elif cached_file(case.name,'A','structured-result.json') is not None:
                compiled=json.loads(cached_file(case.name,'A','structured-result.json').read_text(encoding='utf-8'))
            else:
                run=cli(case.name,'A',baseline,['decide','--extraction',str(folder/'extraction-packet.json'),'--now',raw['as_of'],'--format','json','--artifacts-dir',str(folder/'artifacts')])
                compiled=json.loads(run.stdout) if not run.returncode else {'pipeline_error':run.stderr}
            dump(folder/'structured-result.json',compiled)
            host_preload=json.loads((baseline/f'benchmark/holdout-v023-runner/after-prompts/after-host-{case.name}.txt').read_text(encoding='utf-8').splitlines()[1])
            a_prompt='Present the actual structured-first result in Chinese using the supplied Skill and source context. Preserve traceable conclusions; clearly disclose a failed pipeline or evidence error. Do not fabricate outcome or execution. No tools, memory or rubric.\n'+json.dumps(host_preload,ensure_ascii=False)+'\nRAW CONTEXT:\n'+json.dumps(raw,ensure_ascii=False)+'\nBASELINE STRUCTURED RESULT:\n'+json.dumps(compiled,ensure_ascii=False)
            invoke(case.name,'A','host',a_prompt)
            b_preload={**preload,'installed_skill_content':(ROOT/'SKILL.md').read_text(encoding='utf-8')}
            b_prompt=GUIDE+'\n'+json.dumps(b_preload,ensure_ascii=False)+'\nRAW CONTEXT:\n'+json.dumps(raw,ensure_ascii=False)
            candidate=json.loads(json.loads(invoke(case.name,'B','envelope',b_prompt,'envelope_json'))['envelope_json'])
            folder=output/case.name/'B'; folder.mkdir(parents=True,exist_ok=True)
            dump(folder/'envelope.json',candidate)
            v=validate_decision_envelope(candidate,raw,now=datetime.fromisoformat(raw['as_of']))
            dump(folder/'initial-validation.json',v)
            params=['host-decide','--input',str(folder/'envelope.json'),'--context',str(case/'input/context.json'),'--now',raw['as_of'],'--format','json','--debug-decision','--artifacts-dir',str(folder/'artifacts')]
            if v['status'] != 'ACCEPT':
                b_repair=b_prompt+'\nORIGINAL ENVELOPE:\n'+json.dumps(candidate,ensure_ascii=False)+'\nRELEVANT VALIDATION ISSUES ONLY:\n'+json.dumps(repair_request(v),ensure_ascii=False)+'\nReturn one corrected envelope in envelope_json. No rubric is available.'
                repaired=json.loads(json.loads(invoke(case.name,'B','repair',b_repair,'envelope_json'))['envelope_json'])
                dump(folder/'repaired-envelope.json',repaired)
                params+=['--repair-input',str(folder/'repaired-envelope.json')]
            run=cli(case.name,'B',ROOT,params)
            rows.append({'case':case.name,'B_exit_code':run.returncode,'new_or_reused_generations_retained':True})
    except Exception as exc:
        dump(output/'interruption.json',{'type':type(exc).__name__,'error':str(exc),'boundary':'Incomplete comparison; do not declare architectural success.'})
    dump(output/'resume-summary.json',{'completed_pairs':rows,'calls':records,'boundary':'No semantic grades; reused generations are not fresh model calls.'})
    dump(output/'RESUME_OUTPUT_FREEZE.json',{'files':{str(path.relative_to(output)).replace('\\','/'):digest(path) for path in sorted(output.rglob('*')) if path.is_file()},'created_at':datetime.now(timezone.utc).isoformat()})
    return 0 if len(rows)==10 else 1


if __name__ == '__main__':
    raise SystemExit(main())
