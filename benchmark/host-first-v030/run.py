"""Fresh input-only A/B experiment. Preserve every attempt; never load a rubric.

Run from a reviewed checkout before freezing results. A executes the supplied
v023 baseline CLI; B executes this checkout's host envelope/validator/compiler.
The output root must be new. Model/tools/reference settings are fixed below.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.envelope import validate_decision_envelope, repair_request

GUIDE = """Return only {envelope_json: JSON string of a Decision Envelope v2}.
Understand raw context and choose your own recommendation. Python will only
validate boundaries and compile your supplied content; it will not rank roles.
Do not call tools, read memory or invent future outcomes. Use Chinese user prose.
Core fields:
schema_version='2'; situation={summary,mode,goal?}; mode is job/offer/recruiting/positioning/interview.
facts=[{id,statement,epistemic:'FACT',confidence:direct/self_reported,source_ids:[existing IDs],source_spans:[{source_id,quote:EXACT substring of original source}]}].
Personal accounts/resume accomplishments stay self_reported; source visibility
does not independently verify them. The reserved source REQUEST is the user question.
inferences=[{id,statement,basis:[source or statement IDs]}]; unknowns=[{id,statement,decision_relevance:blocking/reversal/confidence_only}].
bottleneck={type,explanation}; recommendation={type:SUFFICIENT/CONDITIONAL/BLOCKED,move,why:[reasons],avoided_action:[efforts to avoid],basis_ids:[linked source or statement IDs]}.
alternatives=[{option,why_not_now}]; actions=1-3 [{description,execution_mode:codex/human,priority:1-3}].
reconsider_if:[observable conditions]; observation_window; stop_condition;
evidence_used:[existing source IDs]; claims_used:[] unless tracking audited Claim records.
Additional labels are optional; no finite role-family/rating table is required.
Optional extensions: {direction/offer/recruiting/ownership/interview:{content:ready-to-use Markdown material}}.
Only the current mode's extension applies (direction=job, ownership=positioning).
Supply a concrete draft/comparison/defense material when useful, following your
recommendation. Drafts do not execute external actions. Claim tracking optionally
uses the existing audited claims model and project-scoped claim_refs. Do not add
unsupported receipts. Explicit situation.deadline requires timezone and deadline_source_ids.
Do not expose schema names or statuses in user prose. Judgment and 1-3 next actions
should be clear immediately. Remaining unknowns do not automatically block reversible advice.
"""


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(value)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--private-runtime', type=Path, required=True)
    p.add_argument('--node', required=True)
    p.add_argument('--codex-js', required=True)
    p.add_argument('--workers', type=int, choices=[1, 2, 3], default=3)
    args = p.parse_args()
    baseline, output, private = args.baseline.resolve(), args.output.resolve(), args.private_runtime.resolve()
    if output.exists() or private.exists() or 'holdout-v023' in output.parts:
        p.error('Preserve evidence: output/private runtime must be new and outside frozen corpus')
    output.mkdir(parents=True)
    private.mkdir(parents=True)
    installs = {}
    for name, source in [('A', baseline), ('B', ROOT)]:
        workspace = private/name
        workspace.mkdir()
        installed = workspace/'skills'/'career-junshi'
        run = subprocess.run([sys.executable, str(source/'scripts/install_skill.py'), '--target', str(installed)], capture_output=True, text=True, encoding='utf-8', timeout=60)
        if run.returncode:
            raise RuntimeError(run.stderr)
        installs[name] = workspace
    core = [ROOT/'SKILL.md', ROOT/'scripts/envelope.py', ROOT/'scripts/junshi.py']
    core += sorted((ROOT/'scripts').glob('*.py'))
    cases = sorted(p for p in (baseline/'benchmark/holdout-v023').iterdir() if (p/'input/context.json').is_file())
    if len(cases) != 10:
        raise RuntimeError('Exactly ten frozen cases required')
    runtime = {str(path.relative_to(ROOT)).replace('\\','/'):digest(path) for path in dict.fromkeys(core)}
    dump(output/'PROTOCOL_FREEZE.json', {'baseline_commit':'acf2a34363bda9f67a47f3645fbd772b16f94508', 'model':'gpt-5.6-sol', 'effort':'high', 'reference_mode':'CONTROLLED_PRELOAD',
        'repair_budget':1, 'reviewer':'Current Codex AI assistant; not independent human or second-model review',
        'runtime_files':runtime, 'inputs':{case.name:digest(case/'input/context.json') for case in cases},
        'generation_has_rubric':False, 'A':'fresh extraction + baseline CLI + host presentation', 'B':'fresh host envelope + current validator + at most one host repair + compiler',
        'success_criteria':{'noninferior_integrity':True,'pass_or_strong_partial_minimum':7,'pure_schema_transport_failures_maximum':1},
        'created_at':datetime.now(timezone.utc).isoformat()})

    def invoke(prompt, folder, name, arm, wrapper=None):
        prompt_path = folder/(name+'.prompt.txt')
        write(prompt_path,prompt)
        response = folder/(name+'.response.txt')
        cmd = [args.node,args.codex_js,'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json','--color','never','--cd',str(installs[arm]),'--model','gpt-5.6-sol','-c','model_reasoning_effort="high"','-c','web_search="disabled"','-c','project_doc_max_bytes=0','-o',str(response)]
        for feature in ['apps','multi_agent','remote_plugin','hooks','memories','browser_use','browser_use_external','computer_use','image_generation','sleep_tool','shell_tool']:
            cmd += ['--disable',feature]
        if wrapper:
            schema = private/(folder.parent.name+'-'+arm+'-'+name+'.schema.json')
            dump(schema, {'type':'object','properties':{wrapper:{'type':'string'}},'required':[wrapper],'additionalProperties':False})
            cmd += ['--output-schema',str(schema)]
        cmd += ['-']
        start = datetime.now(timezone.utc).isoformat()
        t = time.monotonic()
        result = subprocess.run(cmd,input=prompt,capture_output=True,text=True,encoding='utf-8',timeout=480,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        write(private/(folder.parent.name+'-'+arm+'-'+name+'.events.jsonl'),result.stdout)
        # Raw runtime logs stay private. Public provenance has hashes/usage and
        # completed messages, no credentials or runtime-specific path prefixes.
        events = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
        completed = [event for event in events if event.get('type')=='turn.completed']
        tool_events = [event for event in events if event.get('item',{}).get('type') in {'command_execution','mcp_tool_call','web_search'}]
        dump(folder/(name+'.execution.json'), {'model':'gpt-5.6-sol','effort':'high','reference_mode':'CONTROLLED_PRELOAD','prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
            'started_at':start,'completed_at':datetime.now(timezone.utc).isoformat(),'seconds':round(time.monotonic()-t,2),'exit_code':result.returncode,
            'event_log_sha256':hashlib.sha256(result.stdout.encode()).hexdigest(),'usage':[event.get('usage') for event in completed],
            'tool_invocations':len(tool_events),'response_sha256':digest(response) if response.exists() else None,
            'stderr_present':bool(result.stderr.strip()),'generation_has_rubric':False})
        print(folder.parent.name,arm,name,result.returncode,flush=True)
        if result.returncode or tool_events or not response.is_file():
            raise RuntimeError('Model transport failed or unauthorized tools; raw log retained privately')
        return response.read_text(encoding='utf-8')

    def cli(source, folder, label, params):
        run = subprocess.run([sys.executable,str(source/'scripts/junshi.py'),*params],capture_output=True,text=True,encoding='utf-8',timeout=60)
        write(folder/(label+'.stdout.txt'),run.stdout)
        write(folder/(label+'.stderr.txt'),run.stderr)
        dump(folder/(label+'.execution.json'),{'exit_code':run.returncode,'runtime':'baseline' if source==baseline else 'experiment'})
        return run

    def run_case(case):
        raw = json.loads((case/'input/context.json').read_text(encoding='utf-8'))
        folders = {arm:output/case.name/arm for arm in ['A','B']}
        for folder in folders.values():
            folder.mkdir(parents=True)
        old_prompt = (baseline/f'benchmark/holdout-v023-runner/after-prompts/after-extract-{case.name}.txt').read_text(encoding='utf-8')
        preload = json.loads(old_prompt.splitlines()[1])
        reference_digest = hashlib.sha256(json.dumps(preload['allowed_references'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        dump(output/case.name/'pair-provenance.json', {'input_sha256':digest(case/'input/context.json'),'same_raw_input':True,'same_allowed_reference_payload_sha256':reference_digest,'model':'gpt-5.6-sol','effort':'high','reference_mode':'CONTROLLED_PRELOAD',
            'A_skill_sha256':hashlib.sha256(preload['installed_skill_content'].encode()).hexdigest(),'B_skill_sha256':digest(ROOT/'SKILL.md')})
        def arm_a():
            folder = folders['A']
            packet = json.loads(json.loads(invoke(old_prompt,folder,'extract','A','packet_json'))['packet_json'])
            dump(folder/'extraction-packet.json',packet)
            given = {s['source_id']:{k:s[k] for k in ['source_id','source_type','text']} for s in raw['materials']}
            actual = {s['source_id']:s for s in packet['sources']}
            identity = all(actual.get(k)==v for k,v in given.items()) and all(s.get('source_type')=='user_report' and s.get('text')==raw['request'] for k,s in actual.items() if k not in given)
            if identity:
                run = cli(baseline,folder,'decision',['decide','--extraction',str(folder/'extraction-packet.json'),'--now',raw['as_of'],'--format','json','--artifacts-dir',str(folder/'artifacts')])
                compiled = json.loads(run.stdout) if not run.returncode else {'pipeline_error':run.stderr}
            else:
                compiled = {'pipeline_error':'Source identity mismatch'}
            dump(folder/'structured-result.json',compiled)
            host_preload = json.loads((baseline/f'benchmark/holdout-v023-runner/after-prompts/after-host-{case.name}.txt').read_text(encoding='utf-8').splitlines()[1])
            prompt = 'Present the actual structured-first result in Chinese using the supplied Skill and source context. Preserve traceable conclusions; clearly disclose a failed pipeline or evidence error. Do not fabricate outcome or execution. No tools, memory or rubric.\n'+json.dumps(host_preload,ensure_ascii=False)+'\nRAW CONTEXT:\n'+json.dumps(raw,ensure_ascii=False)+'\nBASELINE STRUCTURED RESULT:\n'+json.dumps(compiled,ensure_ascii=False)
            invoke(prompt,folder,'host','A')
        def arm_b():
            folder = folders['B']
            bpreload = {**preload,'installed_skill_content':(ROOT/'SKILL.md').read_text(encoding='utf-8')}
            prompt = GUIDE+'\n'+json.dumps(bpreload,ensure_ascii=False)+'\nRAW CONTEXT:\n'+json.dumps(raw,ensure_ascii=False)
            candidate = json.loads(json.loads(invoke(prompt,folder,'envelope','B','envelope_json'))['envelope_json'])
            dump(folder/'envelope.json',candidate)
            v = validate_decision_envelope(candidate,raw,now=datetime.fromisoformat(raw['as_of']))
            dump(folder/'initial-validation.json',v)
            params = ['host-decide','--input',str(folder/'envelope.json'),'--context',str(case/'input/context.json'),'--now',raw['as_of'],'--format','json','--debug-decision','--artifacts-dir',str(folder/'artifacts')]
            if v['status'] != 'ACCEPT':
                repair_prompt = prompt+'\nORIGINAL ENVELOPE:\n'+json.dumps(candidate,ensure_ascii=False)+'\nRELEVANT VALIDATION ISSUES ONLY:\n'+json.dumps(repair_request(v),ensure_ascii=False)+'\nReturn one corrected envelope in envelope_json. No rubric is available.'
                repaired = json.loads(json.loads(invoke(repair_prompt,folder,'repair','B','envelope_json'))['envelope_json'])
                dump(folder/'repaired-envelope.json',repaired)
                params += ['--repair-input',str(folder/'repaired-envelope.json')]
            run = cli(ROOT,folder,'host-decision',params)
            if run.stdout:
                dump(folder/'result.json',json.loads(run.stdout))
        # Alternate arm order; no prompts include other arm's generation.
        try:
            if int(case.name[1:3]) % 2:
                arm_b(); arm_a()
            else:
                arm_a(); arm_b()
            return {'case':case.name,'generation':'COMPLETE'}
        except Exception as exc:
            dump(output/case.name/'error.json',{'type':type(exc).__name__,'error':str(exc),'boundary':'Failed attempt retained; do not substitute mock output'})
            return {'case':case.name,'generation':'FAILED','error':str(exc)}

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        rows = [future.result() for future in as_completed([executor.submit(run_case,case) for case in cases])]
    dump(output/'generation-summary.json',{'cases':sorted(rows,key=lambda r:r['case']),'actual_generations':len(list(output.rglob('*.response.txt'))),'boundary':'Completion is transport only, not semantic PASS.'})
    files = {str(path.relative_to(output)).replace('\\','/'):digest(path) for path in sorted(output.rglob('*')) if path.is_file()}
    dump(output/'OUTPUT_FREEZE.json',{'files':files,'created_at':datetime.now(timezone.utc).isoformat(),'boundary':'Frozen before rubric-informed AI review. No case/rubric editing.'})
    return 0 if all(r['generation']=='COMPLETE' for r in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
