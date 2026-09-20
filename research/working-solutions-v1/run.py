#!/usr/bin/env python3
"""Prospectively frozen, two-stage acquisition with no hidden feedback."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from catalog import all_tasks,assignments,cards,canonical,digest,owner,public_material
from execution import run_cases,check_contract
from prompts import VERSION,MODEL,schemas,validate_response,initial_prompt,final_prompt
from benchmark.common import REGIMES

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
SCHEDULE_SEED='wildcard-working-solutions-schedule-v1'
SOURCE_NAMES=['run.py','catalog.py','prompts.py','execution.py','js_worker.py','analysis.py','analyze.mjs','protocol.md','runtime.json','requirements.txt','system-instructions.txt','cards.json']+['benchmark/'+x+'.py' for x in ('__init__','common','queue','cache','sync','ui')]
if (HERE/'development-revision.md').exists():SOURCE_NAMES.append('development-revision.md')


def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_text())
def write_new(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    content=json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2)+'\n'
    if path.exists():
        if path.read_text()!=content:raise ValueError('Immutable artifact already differs: '+str(path))
        return
    with path.open('x') as file:file.write(content)

def order(values,namespace):return sorted(values,key=lambda row:digest([SCHEDULE_SEED,namespace,row['id']]))

def source_card(assignment,arm,bank):
    if arm=='D':return None
    identity=assignment['matchedCardId' if arm=='R' else 'shuffledCardId']
    return next(card for card in bank if card['id']==identity)

def prepare(cohort,seed_path):
    target=HERE/'runs'/cohort
    if (target/'manifest.json').exists():verify_manifest(target);return
    calibration=None
    if cohort=='main':
        # Readiness depends only on complete D calibration, never an R advantage.
        development=HERE/'runs'/('development-2' if (HERE/'runs'/'development-2'/'manifest.json').exists() else 'development-1')
        verified,calibration=verified_calibration(development)
        if not verified['developmentGate']['readyForMain']:raise ValueError('Development floor/ceiling gate blocks main acquisition')
    elif cohort=='development-2':
        previous,calibration=verified_calibration(HERE/'runs'/'development-1')
        if previous['developmentGate']['readyForMain']:raise ValueError('A suitable development round cannot be optionally repeated')
        revision=HERE/'development-revision.md'
        if not revision.exists():raise ValueError('A second development round requires a declared revision')
        require_published(revision)
    split='main' if cohort=='main' else 'development'
    tasks=[task for task in all_tasks() if task['split']==split]
    if len(tasks)!=(32 if split=='main' else 8):raise ValueError('Unexpected task count')
    if not seed_path.exists():
        seed_path.parent.mkdir(parents=True,exist_ok=True)
        descriptor=os.open(seed_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(descriptor,'w') as file:file.write(os.urandom(32).hex()+'\n')
    seed=seed_path.read_text().strip()
    if len(seed)!=64 or any(c not in '0123456789abcdef' for c in seed):raise ValueError('Seed must be 32 bytes encoded as lowercase hex')
    bank=cards();chosen=assignments(tasks,bank);materials={task['id']:public_material(task['id']) for task in tasks}
    requests=[]
    for task,assignment in zip(tasks,chosen):
        for arm in ('D','R','X'):
            prompt=initial_prompt(task,materials[task['id']],source_card(assignment,arm,bank))
            requests.append(dict(id=f'{task["id"]}-{arm}-initial',phase='initial',taskId=task['id'],arm=arm,model=MODEL,prompt=prompt,promptSHA256=sha(prompt.encode())))
    source_hashes={name:sha((HERE/name).read_bytes()) for name in SOURCE_NAMES}
    for name in SOURCE_NAMES:
        snapshot=target/'frozen-source'/name;snapshot.parent.mkdir(parents=True,exist_ok=True)
        with snapshot.open('xb') as file:file.write((HERE/name).read_bytes())
    for stage,schema in schemas().items():write_new(target/'schemas'/f'{stage}.json',schema)
    manifest=dict(schemaVersion=1,study=VERSION,cohort=cohort,priorCalibration=calibration,frozenAt=now(),sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sourceSHA256=source_hashes,schemaSHA256={stage:digest(schema) for stage,schema in schemas().items()},hiddenSeedSHA256=sha(seed.encode()),tasks=tasks,cards=bank,assignments=chosen,publicMaterials=materials,requests=order(requests,cohort+'/initial'),requestedModel=MODEL,returnedModel=None,reasoningEffort='low',temperature=None,topP=None,maxOutputTokens=None,modelSamplingSeed=None,transportTimeoutSeconds=300,maximumTransportAttempts=2,hiddenCasesPerRegime=64,regimes=list(REGIMES),costBasis='Authenticated ChatGPT subscription; USD marginal cost unavailable; observed usage only.')
    write_new(target/'manifest.json',manifest)
    print(f'Frozen {cohort}: {len(tasks)} tasks, {len(requests)} initial requests; hidden seed committed, not disclosed.')

def verify_manifest(target):
    manifest=read(target/'manifest.json')
    if set(manifest['sourceSHA256'])!=set(SOURCE_NAMES):raise ValueError('Frozen source inventory changed')
    for name,expected in manifest['sourceSHA256'].items():
        if sha((HERE/name).read_bytes())!=expected or sha((target/'frozen-source'/name).read_bytes())!=expected:raise ValueError('Frozen source changed: '+name)
    expected_schemas=schemas()
    if manifest['schemaSHA256']!={stage:digest(schema) for stage,schema in expected_schemas.items()}:raise ValueError('Schema index changed')
    for stage,expected in manifest['schemaSHA256'].items():
        if digest(read(target/'schemas'/f'{stage}.json'))!=expected:raise ValueError('Schema changed')
    cohort=manifest['cohort']
    if cohort not in ('main','development-1','development-2'):raise ValueError('Unknown cohort')
    split='main' if cohort=='main' else 'development'
    tasks=[task for task in all_tasks() if task['split']==split]
    if len(tasks)!=(32 if split=='main' else 8):raise ValueError('Unexpected task count')
    bank=cards();chosen=assignments(tasks,bank);materials={task['id']:public_material(task['id']) for task in tasks}
    for key,value in [('tasks',tasks),('cards',bank),('assignments',chosen),('publicMaterials',materials)]:
        if digest(manifest[key])!=digest(value):raise ValueError('Frozen public material reconstruction differs: '+key)
    requests=[]
    for task,assignment in zip(tasks,chosen):
        for arm in ('D','R','X'):
            prompt=initial_prompt(task,materials[task['id']],source_card(assignment,arm,bank))
            requests.append(dict(id=f'{task["id"]}-{arm}-initial',phase='initial',taskId=task['id'],arm=arm,model=MODEL,prompt=prompt,promptSHA256=sha(prompt.encode())))
    if digest(manifest['requests'])!=digest(order(requests,cohort+'/initial')):raise ValueError('Initial prompts or schedule differ from frozen reconstruction')
    if manifest.get('study')!=VERSION or manifest.get('requestedModel')!=MODEL:raise ValueError('Study/model identity changed')
    calibration=manifest.get('priorCalibration')
    if cohort=='development-1':
        if calibration is not None:raise ValueError('First development cannot depend on a prior calibration')
    else:
        allowed=('development-1','development-2') if cohort=='main' else ('development-1',)
        if not isinstance(calibration,dict) or calibration.get('cohort') not in allowed:raise ValueError('Missing valid calibration binding')
        previous=target.parent/calibration['cohort']
        for filename,key in [('manifest.json','manifestSHA256'),('results.json','resultsSHA256')]:
            if sha((previous/filename).read_bytes())!=calibration[key]:raise ValueError('Bound calibration evidence changed')
    return manifest


def parse_events(raw):
    if isinstance(raw,bytes):raw=raw.decode('utf8',errors='replace')
    messages=[];usage=None;completed=False;violations=[];malformed=0
    for line in raw.splitlines():
        try:event=json.loads(line)
        except json.JSONDecodeError:malformed+=1;continue
        if not isinstance(event,dict):malformed+=1;continue
        if event.get('type')=='turn.completed':
            completed=True;usage=event.get('usage')
            if usage is not None and not isinstance(usage,dict):malformed+=1;usage=None
        item=event.get('item',{})
        if not isinstance(item,dict):malformed+=1;continue
        kind=item.get('type')
        if kind is not None and not isinstance(kind,str):malformed+=1;continue
        if kind in ('agent_message','assistant_message') and event.get('type')=='item.completed':
            text=item.get('text','')
            if isinstance(text,str):messages.append(text)
            else:malformed+=1
        elif kind and kind not in ('reasoning','error','todo_list'):violations.append(kind)
    return dict(text=messages[-1] if messages else '',usage=usage,completed=completed,toolViolation=bool(violations),toolTypes=violations,malformedEventLines=malformed)


def new_acquisition_allowed(target,phase):
    if (target/'final-program-seal.json').exists() or (target/'hidden-corpus.json').exists():raise ValueError('Acquisition is closed after final seal or hidden reveal')
    if phase=='initial' and (target/'final-manifest.json').exists():raise ValueError('Initial acquisition is closed after the final manifest')


def acquire(request,target):
    destination=target/'calls'/request['id']
    if (destination/'record.json').exists():
        record=record_for(target,request)
        return request['id'],record['status'],'existing'
    if list(destination.glob('attempt-*')):raise ValueError('Interrupted attempt requires explicit ledger adjudication: '+request['id'])
    new_acquisition_allowed(target,request['phase'])
    destination.mkdir(parents=True,exist_ok=True)
    write_new(destination/'request.json',request)
    empty=ROOT.parent/'working-model-sandbox';empty.mkdir(exist_ok=True)
    if any(empty.iterdir()):raise ValueError('Model working directory must be empty')
    cli=shutil.which('codex')
    if not cli:raise ValueError('Codex CLI unavailable')
    args=[cli,'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','-C',str(empty),'-m',request['model'],'-c','model_reasoning_effort="low"','-c','project_doc_max_bytes=0','-c','web_search="disabled"','-c','model_instructions_file='+json.dumps(str(HERE/'system-instructions.txt')),'--disable','shell_tool','--disable','plugins','--disable','apps','--disable','memories','--disable','multi_agent','--enable','skip_host_skill_discovery','--json','--output-schema',str(target/'schemas'/f'{request["phase"]}.json'),'-']
    started=now();attempts=[];result=None;status='acquisition_error';error=None
    for number in (1,2):
        start=time.monotonic()
        try:
            proc=subprocess.run(args,input=request['prompt'].encode('utf8'),capture_output=True,timeout=300,cwd=empty)
            stdout,stderr,code=proc.stdout,proc.stderr,proc.returncode
        except subprocess.TimeoutExpired as exc:
            stdout=exc.stdout or b'';stderr=exc.stderr or b'';code=-1
        if isinstance(stdout,str):stdout=stdout.encode('utf8')
        if isinstance(stderr,str):stderr=stderr.encode('utf8')
        # Persist exact bytes before interpreting any event, including malformed delivery.
        with (destination/f'attempt-{number}.events.jsonl').open('xb') as file:file.write(stdout)
        with (destination/f'attempt-{number}.stderr.txt').open('xb') as file:file.write(stderr)
        observed=parse_events(stdout)
        attempt=dict(number=number,exitCode=code,elapsedSeconds=time.monotonic()-start,usage=observed['usage'],completed=observed['completed'],toolViolation=observed['toolViolation'],malformedEventLines=observed['malformedEventLines'],eventsSHA256=sha(stdout),stderrSHA256=sha(stderr))
        write_new(destination/f'attempt-{number}.json',attempt);attempts.append(attempt)
        if observed['completed']:(destination/'response.txt').write_text(observed['text'])
        if observed['toolViolation']:
            status,error='tool_policy_violation',str(observed['toolTypes']);break
        if observed['completed'] and code!=0:
            status,error='acquisition_error','Completed model turn with failed CLI exit; no resampling';break
        if not observed['completed']:
            error='transport did not complete';continue
        try:
            result=json.loads(observed['text']);validate_response(result,request['phase']);status='success';error=None
        except (ValueError,TypeError) as exc:status,error,result='validation_error',str(exc),None
        break
    response=destination/'response.txt'
    record=dict(schemaVersion=1,id=request['id'],requestSHA256=digest(request),promptSHA256=request['promptSHA256'],status=status,error=error,startedAt=started,finishedAt=now(),requestedModel=request['model'],returnedModel=None,provider='OpenAI via Codex CLI',cliVersion=subprocess.check_output([cli,'--version'],text=True).strip(),reasoningEffort='low',temperature=None,topP=None,maxOutputTokens=None,attempts=attempts,result=result,resultSHA256=digest(result) if result is not None else None,rawOutputSHA256=sha(response.read_bytes()) if response.exists() else None)
    write_new(destination/'record.json',record)
    return request['id'],status,'new'

def record_for(target,request):
    path=target/'calls'/request['id']/'record.json'
    if not path.exists():raise ValueError('Missing call: '+request['id'])
    record=read(path);folder=path.parent
    if digest(read(folder/'request.json'))!=digest(request):raise ValueError('Request sidecar changed')
    if record.get('id')!=request['id'] or record.get('requestSHA256')!=digest(request) or record.get('promptSHA256')!=request['promptSHA256'] or record.get('requestedModel')!=request['model']:raise ValueError('Call identity mismatch')
    attempts=record.get('attempts')
    if not isinstance(attempts,list) or not 1<=len(attempts)<=2 or [a.get('number') for a in attempts]!=list(range(1,len(attempts)+1)):raise ValueError('Invalid attempt ledger')
    inventory={f'attempt-{a["number"]}.{suffix}' for a in attempts for suffix in ('json','events.jsonl','stderr.txt')}
    if {file.name for file in folder.glob('attempt-*')}!=inventory:raise ValueError('Unlisted or missing attempt artifact')
    for i,attempt in enumerate(attempts):
        if digest(read(folder/f'attempt-{attempt["number"]}.json'))!=digest(attempt):raise ValueError('Attempt sidecar changed')
        for suffix,key in [('events.jsonl','eventsSHA256'),('stderr.txt','stderrSHA256')]:
            if sha((folder/f'attempt-{attempt["number"]}.{suffix}').read_bytes())!=attempt[key]:raise ValueError('Raw attempt changed')
        observed=parse_events((folder/f'attempt-{attempt["number"]}.events.jsonl').read_bytes())
        for key in ('usage','completed','toolViolation','malformedEventLines'):
            if digest(observed[key])!=digest(attempt.get(key)):raise ValueError('Attempt metadata differs from raw events')
        if i<len(attempts)-1 and (observed['completed'] or observed['toolViolation']):raise ValueError('Completed or prohibited attempt was resampled')
    response=folder/'response.txt'
    if record.get('rawOutputSHA256')!=(sha(response.read_bytes()) if response.exists() else None):raise ValueError('Raw response changed')
    if observed['completed'] and (not response.exists() or response.read_text()!=observed['text']):raise ValueError('Delivered response differs from raw events')
    if record.get('status') in ('acquisition_error','tool_policy_violation'):raise ValueError('Acquisition integrity failure: '+request['id'])
    if record.get('status') not in ('success','validation_error') or attempts[-1]['exitCode']!=0 or not observed['completed'] or observed['toolViolation']:raise ValueError('Invalid final acquisition state')
    if record['status']=='success':
        validate_response(record['result'],request['phase'])
        if digest(record['result'])!=record['resultSHA256'] or json.loads(response.read_text())!=record['result']:raise ValueError('Parsed result changed')
    else:
        if record.get('result') is not None or record.get('resultSHA256') is not None:raise ValueError('Invalid response carries a parsed result')
        try:validate_response(json.loads(response.read_text()),request['phase'])
        except (ValueError,TypeError):pass
        else:raise ValueError('Response marked invalid satisfies schema')
    return record


def compact_output(outputs):
    if len(canonical(outputs).encode())<=4000:return {'outputs':outputs}
    return {'outputsOmitted':True,'outputCount':len(outputs),'outputSHA256':digest(outputs),'reason':'Uniform 4000-byte public-output feedback limit'}

def feedback_for(task,material,record):
    if record['status']!='success':return {'initialStatus':record['status'],'validationError':record['error'],'contract':{'admitted':False,'reason':'invalid initial response'},'publicExecution':[]}
    response=record['result'];gate=check_contract(response['applies'],response['holds'],material['examples'],material['incorrectExamples'])
    cases=[example['input'] for example in material['examples']]
    executions=run_cases(response['program'],cases);checks=[]
    module=owner(task['id'])
    for example,case,execution in zip(material['examples'],cases,executions):
        verdict=module.check(task['id'],case,execution['outputs']) if execution['status']=='success' else {'passed':False,'violations':['runtime_error']}
        checks.append({'id':example['id'],'status':execution['status'],'passed':verdict['passed'],'violations':verdict['violations'][:16],'error':execution.get('error'),**compact_output(execution.get('outputs',[]))})
    return {'initialStatus':'success','contract':gate,'publicExecution':checks}

def make_final(cohort):
    target=HERE/'runs'/cohort;manifest=verify_manifest(target);requests=[];inputs={}
    if (target/'final-manifest.json').exists():final_requests(target,manifest);print('Existing final requests verified.');return
    if (target/'final-program-seal.json').exists() or (target/'hidden-corpus.json').exists():raise ValueError('Cannot derive new final prompts after seal or reveal')
    tasks={task['id']:task for task in manifest['tasks']};chosen={a['taskId']:a for a in manifest['assignments']}
    # Verify the entire initial panel before any derived final request exists.
    initial=[(request,record_for(target,request)) for request in manifest['requests']]
    for request,record in initial:
        task=tasks[request['taskId']];material=manifest['publicMaterials'][task['id']]
        feedback=feedback_for(task,material,record)
        if record['status']=='success':first=record['result']
        else:
            response=target/'calls'/request['id']/'response.txt';raw=response.read_bytes() if response.exists() else b''
            first={'invalidResponsePrefix':raw[:12000].decode('utf8',errors='ignore'),'prefixTruncated':len(raw)>12000,'status':record['status']}
        payload={'initialRecordSHA256':digest(record),'firstShown':first,'feedback':feedback}
        write_new(target/'feedback'/f'{task["id"]}-{request["arm"]}.json',payload)
        prompt=final_prompt(task,material,first,feedback,source_card(chosen[task['id']],request['arm'],manifest['cards']))
        final=dict(id=f'{task["id"]}-{request["arm"]}-final',phase='final',taskId=task['id'],arm=request['arm'],model=MODEL,prompt=prompt,promptSHA256=sha(prompt.encode()),initialRecordSHA256=digest(record),feedbackSHA256=digest(payload))
        requests.append(final);inputs[request['id']]=digest(record)
    result={'schemaVersion':1,'manifestSHA256':digest(manifest),'initialRecordsSHA256':inputs,'requests':order(requests,cohort+'/final')}
    write_new(target/'final-manifest.json',result)
    print(f'Frozen {len(requests)} final requests from public feedback only.')

def first_shown(target,request,record):
    if record['status']=='success':return record['result']
    response=target/'calls'/request['id']/'response.txt';raw=response.read_bytes() if response.exists() else b''
    return {'invalidResponsePrefix':raw[:12000].decode('utf8',errors='ignore'),'prefixTruncated':len(raw)>12000,'status':record['status']}


def final_requests(target,manifest):
    final=read(target/'final-manifest.json')
    if final['manifestSHA256']!=digest(manifest):raise ValueError('Final manifest source changed')
    tasks={task['id']:task for task in manifest['tasks']};chosen={a['taskId']:a for a in manifest['assignments']}
    rebuilt=[];initial_hashes={}
    for request in manifest['requests']:
        record=record_for(target,request);initial_hashes[request['id']]=digest(record)
        task=tasks[request['taskId']];arm=request['arm']
        payload=read(target/'feedback'/f'{task["id"]}-{arm}.json')
        if set(payload)!={'initialRecordSHA256','firstShown','feedback'} or payload['initialRecordSHA256']!=digest(record) or digest(payload['firstShown'])!=digest(first_shown(target,request,record)):raise ValueError('Feedback initial artifact binding changed')
        feedback=payload['feedback']
        expected_keys={'initialStatus','contract','publicExecution'}|({'validationError'} if record['status']!='success' else set())
        if set(feedback)!=expected_keys or feedback['initialStatus']!=record['status']:raise ValueError('Unexpected public feedback fields')
        if record['status']!='success' and digest(feedback)!=digest(feedback_for(task,manifest['publicMaterials'][task['id']],record)):raise ValueError('Invalid-response feedback changed')
        prompt=final_prompt(task,manifest['publicMaterials'][task['id']],payload['firstShown'],feedback,source_card(chosen[task['id']],arm,manifest['cards']))
        rebuilt.append(dict(id=f'{task["id"]}-{arm}-final',phase='final',taskId=task['id'],arm=arm,model=MODEL,prompt=prompt,promptSHA256=sha(prompt.encode()),initialRecordSHA256=digest(record),feedbackSHA256=digest(payload)))
    if digest(initial_hashes)!=digest(final['initialRecordsSHA256']):raise ValueError('Initial panel changed')
    if digest(order(rebuilt,manifest['cohort']+'/final'))!=digest(final['requests']):raise ValueError('Final prompts, identities or schedule differ from frozen reconstruction')
    return final['requests']


def require_inventory_published(paths):
    files=[]
    for path in paths:
        path=Path(path)
        if not path.exists():raise ValueError('Missing required publication artifact: '+str(path))
        if path.is_dir():
            contents=sorted(p for p in path.rglob('*') if p.is_file())
            if not contents:raise ValueError('Empty required publication directory')
            files.extend(contents)
        else:files.append(path)
    for path in sorted(set(files)):
        relative=path.relative_to(ROOT).as_posix()
        if subprocess.check_output(['git','status','--porcelain','--',relative],cwd=ROOT,text=True).strip():raise ValueError('Publication artifact is uncommitted: '+relative)
        tracked=subprocess.run(['git','ls-files','--error-unmatch','--',relative],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if tracked.returncode:raise ValueError('Publication artifact is untracked: '+relative)
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    local=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/'+branch],cwd=ROOT,text=True).split()
    if not remote or remote[0]!=local:raise ValueError('Current commit must be publicly pushed before phase transition')


def require_published(path):require_inventory_published([path])


def phase_inventory(target,manifest,phase):
    paths=[target/'manifest.json',target/'frozen-source',target/'schemas']+[HERE/name for name in SOURCE_NAMES]
    if phase in ('final','reveal'):
        paths.extend(target/'calls'/r['id'] for r in manifest['requests'])
        paths.extend([target/'final-manifest.json',target/'feedback'])
    if phase=='reveal':
        paths.extend(target/'calls'/r['id'] for r in final_requests(target,manifest))
        paths.append(target/'final-program-seal.json')
    return paths


def verified_calibration(target):
    target=Path(target)
    result=subprocess.run([sys.executable,'-B',str(HERE/'analysis.py'),'--run-dir',str(target),'--check'],capture_output=True,text=True)
    if result.returncode:raise ValueError('Calibration does not reproduce under frozen analysis: '+result.stderr[-1000:])
    # All evidence, including the old source snapshot, precedes the new phase.
    require_inventory_published([target])
    result=read(target/'results.json');manifest=read(target/'manifest.json')
    return result,{'cohort':manifest['cohort'],'manifestSHA256':sha((target/'manifest.json').read_bytes()),'resultsSHA256':sha((target/'results.json').read_bytes())}


def collect(cohort,phase,workers,limit):
    target=HERE/'runs'/cohort;manifest=verify_manifest(target)
    requests=manifest['requests'] if phase=='initial' else final_requests(target,manifest)
    require_inventory_published(phase_inventory(target,manifest,phase))
    if limit is not None:requests=requests[:limit]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(acquire,request,target) for request in requests]
        for future in concurrent.futures.as_completed(futures):print(*future.result(),flush=True)

def seal(cohort):
    target=HERE/'runs'/cohort;manifest=verify_manifest(target);requests=final_requests(target,manifest)
    records={request['id']:digest(record_for(target,request)) for request in requests}
    write_new(target/'final-program-seal.json',{'manifestSHA256':digest(manifest),'finalManifestSHA256':digest(read(target/'final-manifest.json')),'recordsSHA256':records})
    print('All final artifacts sealed. Commit and publish before revealing hidden cases.')

def evaluate(cohort,seed_path):
    target=HERE/'runs'/cohort;manifest=verify_manifest(target);requests=final_requests(target,manifest)
    sealed=read(target/'final-program-seal.json')
    if sealed['manifestSHA256']!=digest(manifest) or sealed['finalManifestSHA256']!=digest(read(target/'final-manifest.json')):raise ValueError('Program seal does not match')
    for request in requests:
        if digest(record_for(target,request))!=sealed['recordsSHA256'][request['id']]:raise ValueError('Sealed program changed')
    require_inventory_published(phase_inventory(target,manifest,'reveal'))
    seed=seed_path.read_text().strip()
    if sha(seed.encode())!=manifest['hiddenSeedSHA256']:raise ValueError('Hidden seed commitment mismatch')
    corpus=[]
    for task in manifest['tasks']:
        module=owner(task['id'])
        for regime in REGIMES:
            for index in range(64):
                case_seed=digest([seed,task['id'],regime,index]);case=module.make_case(task['id'],regime,case_seed)
                expected=module.reference(task['id'],case)
                if not module.check(task['id'],case,expected)['passed']:raise ValueError('Hidden oracle disagreement; halt entire evaluation')
                corpus.append({'id':f'{task["id"]}/{regime}/{index:02d}','taskId':task['id'],'regime':regime,'index':index,'input':case,'expected':expected})
    write_new(target/'hidden-corpus.json',{'seed':seed,'seedSHA256':manifest['hiddenSeedSHA256'],'finalProgramSealSHA256':digest(sealed),'cases':corpus})
    for request in requests:
        path=target/'execution'/f'{request["id"]}.json'
        if path.exists():continue
        record=record_for(target,request);cases=[case for case in corpus if case['taskId']==request['taskId']];module=owner(request['taskId'])
        actual=run_cases(record['result']['program'],[case['input'] for case in cases]) if record['status']=='success' else [{'status':'invalid_final','outputs':[],'error':record['error']} for case in cases]
        if len(actual)!=len(cases):raise ValueError('Executor returned an incomplete batch; halt')
        results=[]
        for case,observed in zip(cases,actual):
            verdict=module.check(request['taskId'],case['input'],observed['outputs']) if observed['status']=='success' else {'passed':False,'violations':[observed['status']]}
            results.append({'caseId':case['id'],'regime':case['regime'],'status':observed['status'],'outputs':observed.get('outputs',[]),'error':observed.get('error'),'passed':verdict['passed'],'violations':verdict['violations']})
        write_new(path,{'id':request['id'],'taskId':request['taskId'],'arm':request['arm'],'recordSHA256':digest(record),'cases':results})
        print(request['id'],sum(case['passed'] for case in results),'/256',flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','collect','make-final','seal','evaluate','verify'])
    parser.add_argument('--cohort',choices=['development-1','development-2','main'],default='development-1')
    parser.add_argument('--phase',choices=['initial','final'],default='initial')
    parser.add_argument('--seed-path',type=Path)
    parser.add_argument('--workers',type=int,choices=range(1,5),default=3)
    parser.add_argument('--limit',type=int)
    args=parser.parse_args()
    if args.command in ('prepare','evaluate') and args.seed_path is None:parser.error('--seed-path is required outside the repository')
    if args.seed_path and (args.seed_path.resolve().is_relative_to(ROOT) or args.seed_path.resolve().is_relative_to(ROOT.parent/'working-model-sandbox')):parser.error('Seed path must remain outside repository and model directory')
    if args.command=='prepare':prepare(args.cohort,args.seed_path)
    elif args.command=='collect':collect(args.cohort,args.phase,args.workers,args.limit)
    elif args.command=='make-final':make_final(args.cohort)
    elif args.command=='seal':seal(args.cohort)
    elif args.command=='evaluate':evaluate(args.cohort,args.seed_path)
    else:verify_manifest(HERE/'runs'/args.cohort);print('Frozen sources verified')

if __name__=='__main__':main()
