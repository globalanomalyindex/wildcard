#!/usr/bin/env python3
"""Validate sealed artifacts and analyze stored executions without rerunning JavaScript."""
import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import run
from catalog import canonical,digest,owner
from prompts import validate_response

HERE=Path(__file__).resolve().parent
ARMS=('D','R','X')
FAMILIES=('cache','queue','sync','ui')
REGIMES=tuple(run.REGIMES)
USAGE_KEYS=('input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens')


def require(condition,message):
    if not condition:raise ValueError(message)


def index_unique(rows,key,label):
    require(isinstance(rows,list),label+' must be a list')
    result={}
    for row in rows:
        require(isinstance(row,dict) and key in row,label+' missing identity')
        identity=row[key]
        require(isinstance(identity,str) and identity not in result,label+' has invalid or duplicate identity')
        result[identity]=row
    return result


def validate_execution(document,request,record,cases,checker):
    """Recompute checker verdicts from stored outputs, accepting valid alternatives."""
    task_id=request['taskId']
    require(document.get('id')==request['id'] and document.get('taskId')==task_id and document.get('arm')==request['arm'],'Execution identity mismatch')
    require(document.get('recordSHA256')==digest(record),'Execution source record changed')
    expected=index_unique(cases,'id','Corpus cases')
    observed=index_unique(document.get('cases'),'caseId','Execution cases')
    require(len(expected)==256 and set(observed)==set(expected),'Missing, unexpected, or duplicated execution cases')
    require(Counter(c['regime'] for c in cases)==Counter({r:64 for r in REGIMES}),'Expected exactly 64 cases per regime')
    counts={regime:0 for regime in REGIMES};statuses=Counter();exact=0
    require(record.get('status') in ('success','validation_error'),'Final record has unsupported status')
    for identity,case in expected.items():
        actual=observed[identity]
        require(case.get('taskId')==task_id and actual.get('regime')==case['regime'],'Case task or regime mismatch')
        require(type(actual.get('passed')) is bool,'Recorded pass flag must be boolean')
        expected_verdict=checker(task_id,case['input'],case['expected'])
        require(expected_verdict.get('passed') is True,'Reference expected output fails independent checker')
        status=actual.get('status');statuses[status]+=1
        if record['status']=='validation_error':
            require(status=='invalid_final','Invalid final artifact cannot acquire a successful execution')
        else:require(status in ('success','runtime_error'),'Successful final artifact has invalid execution status')
        if status=='success':
            verdict=checker(task_id,case['input'],actual.get('outputs'))
            exact+=canonical(actual.get('outputs'))==canonical(case['expected'])
        else:verdict={'passed':False,'violations':[status]}
        require(type(verdict.get('passed')) is bool and isinstance(verdict.get('violations'),list),'Checker returned invalid verdict')
        require(actual['passed']==verdict['passed'] and canonical(actual.get('violations'))==canonical(verdict['violations']),'Stored verdict differs from recomputed checker verdict')
        counts[case['regime']]+=int(verdict['passed'])
    passed=sum(counts.values())
    return {'passCount':passed,'totalCases':256,'passRate':passed/256,'fullSuite':passed==256,'regimePassCounts':counts,'regimePassRates':{r:counts[r]/64 for r in REGIMES},'executionStatuses':dict(sorted(statuses.items())),'exactExpectedMatches':exact,'exactExpectedMatchRole':'Descriptive only; correctness uses the independent checker.','finalStatus':record['status']}


def summarize_cost(records):
    totals={key:0 for key in USAGE_KEYS};missing={key:0 for key in USAGE_KEYS};latencies=[];attempt_count=0
    for record in records:
        for attempt in record['attempts']:
            attempt_count+=1
            elapsed=attempt['elapsedSeconds']
            require(type(elapsed) in (int,float) and math.isfinite(elapsed) and elapsed>=0,'Invalid attempt latency')
            latencies.append(elapsed)
            usage=attempt.get('usage')
            require(usage is None or isinstance(usage,dict),'Invalid usage object')
            for key in USAGE_KEYS:
                value=(usage or {}).get(key)
                if value is None:missing[key]+=1
                else:
                    require(type(value) is int and value>=0,'Invalid usage count: '+key)
                    totals[key]+=value
    return {'logicalCalls':len(records),'attempts':attempt_count,'statuses':dict(sorted(Counter(record['status'] for record in records).items())),
        'reportedUsageTotals':{key:totals[key] if missing[key]<attempt_count else None for key in USAGE_KEYS},'missingUsageAttemptCounts':missing,
        'summedAttemptLatencySeconds':math.fsum(latencies),'latencyInterpretation':'Sum of all attempt durations, not wall-clock elapsed time.',
        'requestedModels':sorted({record['requestedModel'] for record in records}),'knownReturnedModels':sorted({record['returnedModel'] for record in records if record.get('returnedModel') is not None}),
        'returnedModelUnknownCalls':sum(record.get('returnedModel') is None for record in records),'usdCost':None,
        'costInterpretation':'All recorded attempts, including transport retries and invalid delivered responses. Cached input and reasoning output are components, not additions to input/output totals. Missing usage remains unknown. No exact token matching.'}


def verify_record(target,request):
    record=run.record_for(target,request)
    require(record.get('id')==request['id'] and record.get('promptSHA256')==request['promptSHA256'],'Call record identity mismatch')
    require(record.get('requestedModel')==request['model'],'Requested model mismatch')
    require(record.get('status') in ('success','validation_error'),'Unsupported acquisition status')
    attempts=record.get('attempts')
    require(isinstance(attempts,list) and 1<=len(attempts)<=2,'Missing or excessive attempts')
    destination=target/'calls'/request['id']
    require([a.get('number') for a in attempts]==list(range(1,len(attempts)+1)),'Invalid attempt ordering')
    for i,attempt in enumerate(attempts):
        number=attempt['number']
        require(digest(run.read(destination/f'attempt-{number}.json'))==digest(attempt),'Attempt sidecar differs from record')
        observed=run.parse_events((destination/f'attempt-{number}.events.jsonl').read_text())
        for key in ('usage','completed','toolViolation','malformedEventLines'):
            require(digest(observed[key])==digest(attempt.get(key)),'Attempt metadata differs from raw events: '+key)
        require(not observed['toolViolation'],'Tool-policy violation prevents analysis')
        delivered=attempt['exitCode']==0 and observed['completed']
        require(delivered==(i==len(attempts)-1),'Retry or final transport violates acquisition rule')
    response=destination/'response.txt'
    require(response.exists() and response.read_text()==observed['text'],'Final delivered text differs from raw events')
    if record['status']=='validation_error':
        require(record.get('result') is None and record.get('resultSHA256') is None,'Invalid response carries a parsed result')
        try:validate_response(json.loads(response.read_text()),request['phase'])
        except (ValueError,TypeError):pass
        else:raise ValueError('Response marked invalid actually satisfies the frozen schema')
    return record


def validate_layout(manifest,final_requests):
    main=manifest.get('cohort')=='main'
    require(main or manifest.get('cohort') in ('development-1','development-2'),'Unknown cohort')
    tasks=index_unique(manifest.get('tasks'),'id','Tasks')
    require(len(tasks)==(32 if main else 8),'Wrong task count')
    require(Counter(t['family'] for t in tasks.values())==Counter({f:8 if main else 2 for f in FAMILIES}),'Wrong task-family counts')
    require(manifest.get('regimes')==list(REGIMES) and manifest.get('hiddenCasesPerRegime')==64,'Wrong hidden evaluation allocation')
    for identity,task in tasks.items():
        require(re.fullmatch(r'[a-z][a-z0-9_-]*',identity) is not None,'Unsafe task identity')
        require(task.get('split')==('main' if main else 'development'),'Task split mismatch')
    panels={}
    for stage,requests in [('initial',manifest.get('requests')),('final',final_requests)]:
        indexed=index_unique(requests,'id',stage+' requests')
        expected={f'{task}-{arm}-{stage}' for task in tasks for arm in ARMS}
        require(set(indexed)==expected,'Missing or unexpected '+stage+' request')
        for identity,request in indexed.items():
            require(request.get('taskId') in tasks and request.get('arm') in ARMS and request.get('phase')==stage and identity==f'{request["taskId"]}-{request["arm"]}-{stage}','Request assignment mismatch')
        panels[stage]=indexed
    return tasks,panels


def validate_corpus(manifest,sealed,corpus,tasks):
    seed=corpus.get('seed')
    require(isinstance(seed,str) and re.fullmatch('[0-9a-f]{64}',seed) is not None,'Invalid revealed seed')
    require(run.sha(seed.encode())==manifest['hiddenSeedSHA256']==corpus.get('seedSHA256'),'Hidden seed commitment mismatch')
    require(corpus.get('finalProgramSealSHA256')==digest(sealed),'Corpus does not bind the sealed final programs')
    indexed=index_unique(corpus.get('cases'),'id','Hidden corpus')
    expected_ids={f'{task}/{regime}/{i:02d}' for task in tasks for regime in REGIMES for i in range(64)}
    require(set(indexed)==expected_ids,'Missing or unexpected hidden corpus case')
    by_task={task:[] for task in tasks}
    for identity,case in indexed.items():
        task_id,regime,number=identity.split('/');index=int(number)
        require(case.get('taskId')==task_id and case.get('regime')==regime and type(case.get('index')) is int and case['index']==index,'Corpus case identity mismatch')
        module=owner(task_id)
        regenerated=module.make_case(task_id,regime,digest([seed,task_id,regime,index]))
        require(canonical(regenerated)==canonical(case['input']),'Hidden input differs from committed generator and seed')
        require(canonical(module.reference(task_id,regenerated))==canonical(case['expected']),'Revealed reference output differs from frozen reference')
        require(module.check(task_id,case['input'],case['expected']).get('passed') is True,'Revealed reference fails checker')
        by_task[task_id].append(case)
    return {task:sorted(cases,key=lambda c:c['id']) for task,cases in by_task.items()}


def load_dataset(target):
    """Strict complete-panel loader. No generation, JavaScript execution, or file writes."""
    target=Path(target)
    manifest=run.verify_manifest(target)
    finals=run.final_requests(target,manifest)
    tasks,panels=validate_layout(manifest,finals)
    sealed=run.read(target/'final-program-seal.json')
    require(sealed.get('manifestSHA256')==digest(manifest) and sealed.get('finalManifestSHA256')==digest(run.read(target/'final-manifest.json')),'Final program seal mismatch')
    require(set(sealed.get('recordsSHA256',{}))==set(panels['final']),'Incomplete or unexpected sealed record')
    records={}
    for stage in ('initial','final'):
        for identity,request in sorted(panels[stage].items()):
            record=verify_record(target,request);records[identity]=record
            if stage=='final':require(digest(record)==sealed['recordsSHA256'][identity],'Sealed final program changed')
    require({p.name for p in (target/'calls').iterdir() if p.is_dir()}==set(records),'Unexpected call directory')
    require({p.name for p in (target/'execution').glob('*.json')}=={identity+'.json' for identity in panels['final']},'Missing or unexpected execution artifact')
    corpus=run.read(target/'hidden-corpus.json');cases=validate_corpus(manifest,sealed,corpus,tasks)
    per_task=[];gates={arm:Counter() for arm in ARMS}
    for task_id,task in sorted(tasks.items()):
        arms={}
        for arm in ARMS:
            identity=f'{task_id}-{arm}-final';request=panels['final'][identity]
            document=run.read(target/'execution'/f'{identity}.json')
            arms[arm]=validate_execution(document,request,records[identity],cases[task_id],owner(task_id).check)
            feedback=run.read(target/'feedback'/f'{task_id}-{arm}.json')
            require(feedback.get('initialRecordSHA256')==digest(records[f'{task_id}-{arm}-initial']),'Feedback initial binding differs')
            contract=feedback['feedback']['contract']
            require(type(contract.get('admitted')) is bool,'Gate admission must be boolean')
            gates[arm]['admitted' if contract['admitted'] else 'rejected']+=1
            arms[arm]['contractAdmitted']=contract['admitted']
            arms[arm]['initialStatus']=records[f'{task_id}-{arm}-initial']['status']
        per_task.append({'taskId':task_id,'family':task['family'],'arms':arms})
    acquisition=summarize_cost(list(records.values()))
    acquisition['byArm']={arm:summarize_cost([record for identity,record in records.items() if panels['initial'].get(identity,panels['final'].get(identity))['arm']==arm]) for arm in ARMS}
    acquisition['byPhase']={stage:summarize_cost([records[identity] for identity in panels[stage]]) for stage in ('initial','final')}
    artifacts=['manifest.json','final-manifest.json','final-program-seal.json','hidden-corpus.json']
    artifacts += ['execution/'+identity+'.json' for identity in sorted(panels['final'])]
    artifacts += ['feedback/'+task+'-'+arm+'.json' for task in sorted(tasks) for arm in ARMS]
    artifacts += ['calls/'+identity+'/record.json' for identity in sorted(records)]
    return {'cohort':manifest['cohort'],'perTask':per_task,'acquisition':acquisition,
        'contractGates':{arm:{'admitted':gates[arm]['admitted'],'rejected':gates[arm]['rejected'],'nTasks':len(tasks),'descriptiveOnly':True} for arm in ARMS},
        'provenance':{'study':manifest['study'],'sourceCommit':manifest['sourceCommit'],'sourceSHA256':manifest['sourceSHA256'],'artifactSHA256':{name:run.sha((target/name).read_bytes()) for name in artifacts},
        'validation':'Frozen sources and snapshots, raw attempts and delivered responses, complete requests, final seals, seed-derived hidden inputs/reference outputs, and checker verdicts revalidated. JavaScript executions were not rerun.'}}


def analyze_dataset(data):
    node=os.environ.get('WILDCARD_NODE') or shutil.which('node')
    require(bool(node),'Node.js required; set WILDCARD_NODE if it is not on PATH')
    result=subprocess.run([node,str(HERE/'analyze.mjs')],input=canonical(data),capture_output=True,text=True,check=True)
    statistics=json.loads(result.stdout)
    return {'schemaVersion':1,**statistics,'perTask':data['perTask'],'contractGates':data['contractGates'],'acquisition':data['acquisition'],'provenance':data['provenance']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort',choices=['main','development-1','development-2'],default='main')
    parser.add_argument('--run-dir',type=Path,help='Explicit run directory, including when using its frozen-source implementation')
    modes=parser.add_mutually_exclusive_group();modes.add_argument('--check',action='store_true');modes.add_argument('--validate-only',action='store_true')
    args=parser.parse_args();target=(args.run_dir or HERE/'runs'/args.cohort).resolve()
    manifest=run.read(target/'manifest.json')
    # Reproduce old development with its complete frozen implementation after a
    # prospective source revision, rather than silently using new checker code.
    drift=any(not (HERE/name).exists() or run.sha((HERE/name).read_bytes())!=expected for name,expected in manifest['sourceSHA256'].items())
    if drift:
        frozen=target/'frozen-source'/'analysis.py'
        require(frozen.exists() and frozen.resolve()!=Path(__file__).resolve(),'Frozen analysis implementation is missing or changed')
        for name,expected in manifest['sourceSHA256'].items():require(run.sha((target/'frozen-source'/name).read_bytes())==expected,'Frozen source changed: '+name)
        flags=['--check'] if args.check else ['--validate-only'] if args.validate_only else []
        result=subprocess.run([sys.executable,str(frozen),'--run-dir',str(target),*flags],check=False)
        raise SystemExit(result.returncode)
    data=load_dataset(target)
    if args.validate_only:
        print(canonical({'valid':True,'cohort':data['cohort'],'tasks':len(data['perTask']),'finalPrograms':len(data['perTask'])*3,'effectsComputed':False}));return
    results=analyze_dataset(data);path=target/'results.json'
    if args.check:
        require(path.exists() and canonical(run.read(path))==canonical(results),'Stored analysis differs from validated recomputation')
        print('Stored analysis matches validated recomputation.');return
    run.write_new(path,results)
    print('Wrote deterministic validated analysis: '+str(path))

if __name__=='__main__':main()
