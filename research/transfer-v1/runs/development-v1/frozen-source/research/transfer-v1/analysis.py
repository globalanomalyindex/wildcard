#!/usr/bin/env python3
"""Strict, read-only record validation and scoring; explicit CLI generation afterward.

Main failures retain zero scores. Missing required acquisitions or judges never become
silent zero observations. Global bank-match propagation is conservative and explicit.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess
from prompts import (score_set, generation_prompt, judge_prompt, diagnostic_prompt,
                     validate_generation, validate_judgment, validate_diagnostic)
from run import canonical, hash_json, stable_shuffle, parse_events, SEED

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ARMS = ('S', 'R', 'LR', 'XR')
JUDGES = ('j1', 'j2')
GOOD = ('success', 'abstention')
FAILURES = ('acquisition_error', 'validation_error', 'tool_policy_violation')
ZERO = dict(qnm=0, qdm=0, qualified_actions=0, total_actions=0)


def read(path):
    with Path(path).open() as f:
        return json.load(f)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def timestamp(value):
    result = datetime.fromisoformat(value)
    require(result.tzinfo is not None, 'Timestamps require an explicit timezone')
    return result


def artifact(path):
    path = Path(path)
    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError:
        relative = str(path)
    return dict(path=relative, sha256=sha(path))


def score_task(ratings, links):
    """Conservative global baseline propagation; preserve raw rows separately.

    mechanism_group names are local to one task and judge. If any candidate in the
    task's group matches the bank, every arm's copy of that group is non-new.
    """
    require(len({r['id'] for r in ratings}) == len(ratings), 'Duplicate rating identity')
    require(len({r['id'] for r in links}) == len(links), 'Duplicate candidate link')
    require({r['id'] for r in ratings} == {r['id'] for r in links}, 'Incomplete task ratings')
    by_group = defaultdict(list)
    for row in ratings:
        by_group[row['mechanism_group']].append(row)
    matches = {group: next(r['baseline_match'] for r in rows if r['baseline_match'] is not None)
               for group, rows in by_group.items() if any(r['baseline_match'] is not None for r in rows)}
    normalized = {r['id']: dict(r, baseline_match=matches.get(r['mechanism_group'])) for r in ratings}
    scores = {arm: score_set([normalized[l['id']] for l in links if l['arm'] == arm]) for arm in ARMS}
    contradictions = [dict(mechanism_group=group, candidate_ids=[r['id'] for r in rows],
                           matched_ids=[r['id'] for r in rows if r['baseline_match'] is not None],
                           null_match_ids=[r['id'] for r in rows if r['baseline_match'] is None])
                      for group, rows in by_group.items()
                      if group in matches and any(r['baseline_match'] is None for r in rows)]
    return dict(scores=scores, normalized=normalized, contradictions=contradictions)


def verify_record(target, request, frozen_at):
    directory = target / 'calls' / request['id']
    record_path = directory / 'record.json'
    require(record_path.is_file(), f'Missing scheduled record: {request["id"]}')
    record = read(record_path)
    require(read(directory/'request.json') == request, f'Request envelope changed: {request["id"]}')
    require(record['id'] == request['id'] and record['request_sha256'] == hash_json(request), 'Request identity hash mismatch')
    prompt_hash = hashlib.sha256(request['prompt'].encode()).hexdigest()
    require(request['prompt_sha256'] == prompt_hash == record['prompt_sha256'], 'Prompt hash mismatch')
    require(record['requested_model'] == request['model'], 'Requested model mismatch')
    require(record['status'] in GOOD + FAILURES, 'Unrecognized record status')
    require(record['reasoning_effort'] == 'low', 'Reasoning configuration mismatch')
    require(all(record[k] is None for k in ('returned_model','temperature','top_p','max_output_tokens')), 'Unexpected unregistered model or decoding metadata')
    require(timestamp(record['started_at']) >= timestamp(frozen_at), 'Acquisition predates source freeze')
    require(timestamp(record['finished_at']) >= timestamp(record['started_at']), 'Acquisition timestamps inverted')
    attempts = record['attempts']
    require(1 <= len(attempts) <= 2, 'Incorrect transport attempt count')
    expected_files = set()
    for index, attempt in enumerate(attempts, 1):
        require(attempt['number'] == index, 'Nonsequential attempt record')
        require(read(directory/f'attempt-{index}.json') == attempt, 'Attempt summary changed')
        events, stderr = directory/f'attempt-{index}.events.jsonl', directory/f'attempt-{index}.stderr.txt'
        require(sha(events) == attempt['events_sha256'], 'Attempt event hash mismatch')
        require(sha(stderr) == attempt['stderr_sha256'], 'Attempt stderr hash mismatch')
        observed = parse_events(events.read_text())
        require(attempt['completed'] == observed['completed'] and attempt['tool_violation'] == observed['tool_violation'], 'Attempt flags disagree with events')
        require(attempt['usage'] == observed['usage'], 'Usage disagrees with event stream')
        require(isinstance(attempt['elapsed_seconds'], (float, int)) and math.isfinite(attempt['elapsed_seconds']) and attempt['elapsed_seconds'] >= 0, 'Invalid latency')
        if attempt['usage'] is not None:
            require(isinstance(attempt['usage'], dict), 'Malformed usage')
            require(all(type(v) is int and v >= 0 for v in attempt['usage'].values()), 'Invalid usage value')
        if index < len(attempts):
            require((attempt['exit_code'] != 0 or not attempt['completed']) and not attempt['tool_violation'], 'Unregistered retry after completed output')
        expected_files.update([f'attempt-{index}.json', f'attempt-{index}.events.jsonl', f'attempt-{index}.stderr.txt'])
    require({p.name for p in directory.glob('attempt-*')} == expected_files, 'Unregistered partial/extra transport attempts')
    response = directory/'response.txt'
    require(record['raw_output_sha256'] == (sha(response) if response.exists() else None), 'Raw response hash mismatch')
    final = attempts[-1]
    if record['status'] in GOOD:
        require(final['exit_code'] == 0 and final['completed'] and not final['tool_violation'], 'Successful record did not complete without tools')
        require(response.exists() and read(response) == record['result'], 'Delivered JSON differs from recorded result')
        require(hash_json(record['result']) == record['result_sha256'], 'Result hash mismatch')
        require(parse_events((directory/f'attempt-{len(attempts)}.events.jsonl').read_text())['text'] == response.read_text(), 'Raw output differs from final event message')
        require(record['error'] is None, 'Successful record carries an error')
        if request['schema'] == 'generation':
            validate_generation(record['result'], request['count'])
            require((record['status'] == 'abstention') == (not record['result']['actions']), 'Abstention state contradicts actions')
        elif request['schema'] == 'judgment':
            validate_judgment(record['result'], request['candidate_ids'], request['bank_ids'])
            require(record['status'] == 'success', 'Judgment cannot abstain')
        elif request['schema'] == 'diagnostic':
            validate_diagnostic(record['result'])
            require(record['status'] == 'success', 'Diagnostic record status must be success')
        else:
            raise ValueError('Unknown response schema')
    else:
        require(record['result'] is None and record['result_sha256'] is None, 'Failed acquisition cannot retain analyzed result')
        require(isinstance(record['error'], str) and record['error'], 'Failed acquisition needs an explicit reason')
        if record['status'] == 'tool_policy_violation':
            require(any(a['tool_violation'] for a in attempts), 'Tool failure lacks observed violation')
        elif record['status'] == 'acquisition_error':
            require(final['exit_code'] != 0 or not final['completed'], 'Acquisition error contradicts completed transport')
        elif record['status'] == 'validation_error':
            require(final['exit_code'] == 0 and final['completed'] and response.exists(), 'Validation failure lacks delivered response')
            try:
                result = read(response)
                if request['schema'] == 'generation': validate_generation(result, request['count'])
                elif request['schema'] == 'judgment': validate_judgment(result, request['candidate_ids'], request['bank_ids'])
                else: validate_diagnostic(result)
            except (ValueError, TypeError):
                pass
            else:
                raise ValueError('Validation-error status contains a valid response')
    return record


def load_dataset(target, *, source_root=HERE, expected_count=None):
    target, source_root = Path(target), Path(source_root)
    manifest = read(target/'manifest.json')
    cohort = manifest['cohort']
    require(cohort in ('main','development'), 'Unrecognized cohort')
    expected_count = expected_count if expected_count is not None else (32 if cohort == 'main' else 4)
    require(len(manifest['tasks']) == expected_count, 'Incorrect prespecified task count')
    require(len({t['id'] for t in manifest['tasks']}) == expected_count, 'Duplicate task ID')
    source_paths = {}
    for name, expected in manifest['source_sha256'].items():
        snapshot = manifest.get('source_snapshots', {}).get(name)
        path = target/snapshot if snapshot else source_root/name
        require(path.is_file() and sha(path) == expected, f'Frozen source mismatch: {name}')
        if cohort == 'main' and name.endswith(('.py','.mjs')):
            require(sha(source_root/name) == expected, f'Executing analysis dependency differs from frozen source: {name}')
        source_paths[name] = path
    if cohort == 'main' and expected_count == 32:
        require({'analysis.py','analyze.mjs','../lib/stats.mjs'} <= set(source_paths), 'Main analysis source was not frozen')
        require(sorted(Counter(t['family'] for t in manifest['tasks']).values()) == [8,8,8,8], 'Main strata are not four fixed eight-task families')
    require(read(source_paths['tasks.json'])[cohort] == manifest['tasks'], 'Task statements differ from frozen materials')
    cards = read(source_paths['cards.json'])['cards']
    card_by_id = {c['id']:c for c in cards}
    order = stable_shuffle(cards,'card-order')
    expected_assignments = [dict(task_id=t['id'],card_id=order[i%len(order)]['id'],wrong_label_card_id=order[(i+len(order)//2)%len(order)]['id']) for i,t in enumerate(manifest['tasks'])]
    require(manifest['assignments'] == expected_assignments, 'Task/card assignment changed')
    for name, expected in manifest['schema_sha256'].items():
        require(hash_json(read(target/'schemas'/f'{name}.json')) == expected, 'Frozen schema changed')
    requests = manifest['requests']
    require(len({r['id'] for r in requests}) == len(requests), 'Duplicate acquisition request')
    expected_ids = {f'{t["id"]}-{arm}' for t in manifest['tasks'] for arm in ARMS}
    expected_ids |= {f'{t["id"]}-bank-{rep}' for t in manifest['tasks'] for rep in (1,2)}
    diagnostic_specs = read(source_paths['diagnostics.json'])
    if cohort == 'main': expected_ids |= {f'{f["id"]}-{v}' for f in diagnostic_specs['fixtures'] for v in ('a','b')}
    require({r['id'] for r in requests} == expected_ids, 'Scheduled acquisitions do not match full design')
    scheduled = stable_shuffle([{k:v for k,v in r.items() if k!='prompt_sha256'} for r in requests],f'{cohort}-acquisition')
    require([r['id'] for r in requests] == [r['id'] for r in scheduled], 'Acquisition schedule does not reproduce frozen ordering')
    task_by_id = {t['id']:t for t in manifest['tasks']}
    assignment_by_id = {a['task_id']:a for a in manifest['assignments']}
    fixture_by_id = {f['id']:f for f in diagnostic_specs['fixtures']}
    for r in requests:
        require(r['model'] == manifest['generator'], 'Generator alias differs across arms')
        if r['phase'] in ('main','bank'):
            a = assignment_by_id[r['task_id']]
            count = 8 if r['phase'] == 'bank' else 4
            require(r['count'] == count and r['schema'] == 'generation', 'Output budget/schema mismatch')
            require((r['arm']=='S') if r['phase']=='bank' else r['arm'] in ARMS, 'Invalid assigned generation arm')
            require(r['id'] in ([f'{r["task_id"]}-bank-{i}' for i in (1,2)] if r['phase']=='bank' else [f'{r["task_id"]}-{r["arm"]}']), 'Request ID contradicts assigned arm/task')
            expected_prompt = generation_prompt(task_by_id[r['task_id']],r['arm'],card_by_id[a['card_id']],card_by_id[a['wrong_label_card_id']]['label'],count=count)
        elif r['phase'] == 'diagnostic':
            require(cohort=='main' and r['schema']=='diagnostic', 'Unexpected diagnostic request')
            require(r['id']==f'{r["task_id"]}-{r["variant"]}', 'Diagnostic ID contradicts assigned variant')
            expected_prompt = diagnostic_prompt(fixture_by_id[r['task_id']],r['variant'],diagnostic_specs['output_contract'])
        else: raise ValueError('Unrecognized acquisition phase')
        require(r['prompt'] == expected_prompt, 'Rendered request differs from frozen template')
    records = {r['id']:verify_record(target,r,manifest['frozen_at']) for r in requests}
    banks = [records[r['id']] for r in requests if r['phase']=='bank']
    main_records = [records[r['id']] for r in requests if r['phase']=='main']
    require(all(r['status'] in GOOD for r in banks), 'Invalid independent bank blocks main analysis')
    require(max(timestamp(r['finished_at']) for r in banks) <= min(timestamp(r['started_at']) for r in main_records), 'Main acquisition started before bank freeze')
    judges_manifest = read(target/'judge-manifest.json')
    require(judges_manifest['source_manifest_sha256'] == hash_json(manifest), 'Judge source-manifest hash mismatch')
    judge_requests = judges_manifest['requests']
    require(len(judge_requests) == expected_count*2 and {r['id'] for r in judge_requests} == {f'{t["id"]}-judge-{i}' for t in manifest['tasks'] for i in (1,2)}, 'Required judge blocks incomplete or duplicated')
    require(judge_requests == stable_shuffle(judge_requests,cohort+'-judge-order'), 'Judge acquisition schedule changed')
    mapping_document = read(target/'mask-map.json')
    mappings = mapping_document['mappings']
    require(len(mappings)==expected_count and {m['task_id'] for m in mappings}==set(task_by_id), 'Mask mapping task coverage incorrect')
    by_map = {m['task_id']:m for m in mappings}
    judged = {r['id']:verify_record(target,r,manifest['frozen_at']) for r in judge_requests}
    require(all(r['status']=='success' for r in judged.values()), 'Missing or invalid required judge block prevents primary analysis')
    scheduled_dirs = {r['id'] for r in requests+judge_requests}
    require({p.name for p in (target/'calls').iterdir() if p.is_dir()} == scheduled_dirs, 'Unregistered call directory present')
    per_problem, contradictions = [], []
    agree = Counter(candidate_actions=0,grouping_pairs=0)
    for task in manifest['tasks']:
        taskid = task['id'];bank=[];candidates=[];links=[];actions_by_request=defaultdict(list)
        for req in [r for r in requests if r['task_id']==taskid]:
            record = records[req['id']]
            if record['status'] not in GOOD:continue
            for i,action in enumerate(record['result']['actions']):
                masked = hashlib.sha256(canonical([SEED,cohort,req['id'],i]).encode()).hexdigest()[:16]
                item = dict(id=masked,**action)
                if req['phase']=='bank':bank.append(item)
                else:
                    candidates.append(item);actions_by_request[req['id']].append(item)
                    links.append(dict(id=masked,request_id=req['id'],arm=req['arm'],action_index=i))
        bank=stable_shuffle(bank,f'{cohort}-{taskid}-bank');candidates=stable_shuffle(candidates,f'{cohort}-{taskid}-candidates')
        require(len({a['id'] for a in bank+candidates})==len(bank+candidates), 'Masked ID collision')
        require(by_map[taskid]==dict(task_id=taskid,candidates=links,bank_ids=[b['id'] for b in bank]), 'Mask map does not reproduce exact raw-action coverage')
        scored, raw_by_judge = {}, {}
        for i,judgeid in enumerate(JUDGES,1):
            req=next(r for r in judge_requests if r['id']==f'{taskid}-judge-{i}')
            require(req['task_id']==taskid and req['phase']=='judge' and req['schema']=='judgment', 'Judge request design metadata mismatch')
            require(req['model']==manifest['judges'][i-1] and req['judge_id']==judgeid, 'Judge configuration identity mismatch')
            require(req['candidate_ids']==[c['id'] for c in candidates] and req['bank_ids']==[b['id'] for b in bank], 'Judge candidate/bank identity list changed')
            require(req['prompt']==judge_prompt(task,bank,candidates if i==1 else list(reversed(candidates))), 'Judge block is not exact masked raw actions with prescribed order')
            require(timestamp(judged[req['id']]['started_at'])>=max(timestamp(records[f'{taskid}-{arm}']['finished_at']) for arm in ARMS), 'Judge began before candidate acquisition ended')
            ratings=judged[req['id']]['result']['ratings']
            scored[judgeid]=score_task(ratings,links);raw_by_judge[judgeid]={r['id']:r for r in ratings}
            contradictions.extend(dict(task_id=taskid,judge_id=judgeid,**c) for c in scored[judgeid]['contradictions'])
        for candidate in candidates:
            ident=candidate['id'];agree['candidate_actions']+=1
            for field in ('constraint_valid','feasible','actionable'):
                agree[field+'_agree']+=raw_by_judge['j1'][ident][field]==raw_by_judge['j2'][ident][field]
            agree['bank_newness_agree']+=(scored['j1']['normalized'][ident]['baseline_match'] is None)==(scored['j2']['normalized'][ident]['baseline_match'] is None)
            agree['qualified_agree']+=all(raw_by_judge['j1'][ident][k] for k in ('constraint_valid','feasible','actionable'))==all(raw_by_judge['j2'][ident][k] for k in ('constraint_valid','feasible','actionable'))
        for a,b in itertools.combinations([c['id'] for c in candidates],2):
            agree['grouping_pairs']+=1
            same1=raw_by_judge['j1'][a]['mechanism_group']==raw_by_judge['j1'][b]['mechanism_group']
            same2=raw_by_judge['j2'][a]['mechanism_group']==raw_by_judge['j2'][b]['mechanism_group']
            agree['grouping_agree']+=same1==same2
            agree['same_group_j1']+=same1;agree['same_group_j2']+=same2;agree['same_group_both']+=same1 and same2
        assignment=assignment_by_id[taskid]
        arms={}
        for arm in ARMS:
            requestid=f'{taskid}-{arm}';record=records[requestid]
            scores={j:scored[j]['scores'][arm] for j in JUDGES}
            arms[arm]=dict(requestId=requestid,status=record['status'],error=record['error'],judges=scores,
                score={key:sum(scores[j][key] for j in JUDGES)/2 for key in ZERO},
                actions=[dict(**a,ratings={j:raw_by_judge[j][a['id']] for j in JUDGES},
                              globallyBankMatched={j:scored[j]['normalized'][a['id']]['baseline_match'] is not None for j in JUDGES}) for a in actions_by_request[requestid]],
                sources=[artifact(target/'calls'/requestid/f) for f in ('request.json','record.json')]+([artifact(target/'calls'/requestid/'response.txt')] if (target/'calls'/requestid/'response.txt').exists() else []))
        per_problem.append(dict(taskId=taskid,task=task,assignedCard=card_by_id[assignment['card_id']],
            mismatchLabel=card_by_id[assignment['wrong_label_card_id']]['label'],mismatchLabelCardId=assignment['wrong_label_card_id'],arms=arms,
            bank=dict(realizedActions=len(bank),actions=bank,requests=[dict(id=f'{taskid}-bank-{i}',status=records[f'{taskid}-bank-{i}']['status'],sources=[artifact(target/'calls'/f'{taskid}-bank-{i}'/f) for f in ('request.json','record.json','response.txt')]) for i in (1,2)]),
            judgeSources={j:[artifact(target/'calls'/f'{taskid}-judge-{i}'/f) for f in ('request.json','record.json','response.txt')] for i,j in enumerate(JUDGES,1)}))
    usage=defaultdict(lambda:dict(logicalCalls=0,attempts=0,attemptsWithUsage=0,elapsedSeconds=0,statusCounts=Counter(),tokens=Counter()))
    for req in requests+judge_requests:
        record=(judged if req['phase']=='judge' else records)[req['id']]
        key=req['phase']+(':'+req['arm'] if req['phase']=='main' else '')
        bucket=usage[key];bucket['logicalCalls']+=1;bucket['statusCounts'][record['status']]+=1
        for attempt in record['attempts']:
            bucket['attempts']+=1;bucket['elapsedSeconds']+=attempt['elapsed_seconds']
            if attempt['usage'] is not None:bucket['attemptsWithUsage']+=1;bucket['tokens'].update(attempt['usage'])
    diagnostics=[]
    if cohort=='main':
        for fixture in diagnostic_specs['fixtures']:
            variants=[]
            for variant in ('a','b'):
                record=records[f'{fixture["id"]}-{variant}'];result=record['result']
                passed=record['status']=='success' and result['decision']==fixture[f'expected_decision_{variant}'] and result['trace']==fixture[f'expected_trace_{variant}']
                if fixture['id']=='x05' and passed:passed=result['action'].strip().upper()==('SUBTRACT_ONE' if variant=='a' else 'ADD_ONE')
                variants.append(dict(variant=variant,status=record['status'],passed=passed,result=result,expectedDecision=fixture[f'expected_decision_{variant}'],expectedTrace=fixture[f'expected_trace_{variant}'],source=artifact(target/'calls'/f'{fixture["id"]}-{variant}'/'record.json')))
            diagnostics.append(dict(id=fixture['id'],title=fixture['title'],variants=variants,pairPassed=all(v['passed'] for v in variants)))
    n=agree['candidate_actions'];pairs=agree['grouping_pairs']
    positive_pair_count=agree['same_group_j1']+agree['same_group_j2']
    agreement=dict(counts=dict(agree),rates={k:agree[k]/n if n else None for k in ('constraint_valid_agree','feasible_agree','actionable_agree','bank_newness_agree','qualified_agree')},
                   pairwiseMechanismGroupingAgreement=agree['grouping_agree']/pairs if pairs else None,
                   positiveMechanismLinkAgreement=2*agree['same_group_both']/positive_pair_count if positive_pair_count else None,
                   qnmMeanAbsoluteJudgeDifference=sum(abs(p['arms'][a]['judges']['j1']['qnm']-p['arms'][a]['judges']['j2']['qnm']) for p in per_problem for a in ARMS)/(len(per_problem)*4),
                   caveat='Within-block descriptive agreement; candidate pairs are correlated, and agreement is not truth or human validation.')
    ledger=[]
    for req in requests+judge_requests:
        directory=target/'calls'/req['id'];record=(judged if req['phase']=='judge' else records)[req['id']]
        ledger.append(dict(id=req['id'],phase=req['phase'],taskId=req['task_id'],model=req['model'],status=record['status'],attempts=len(record['attempts']),
                           sources=[artifact(p) for p in sorted(directory.iterdir()) if p.is_file()]))
    return dict(schemaVersion=1,study=manifest['study'],cohort=cohort,measurement='Model-judged qualified mechanisms absent from the finite independent reference bank.',
                complete=True,nTasks=len(per_problem),perProblem=per_problem,agreement=agreement,bankMatchContradictions=contradictions,
                usage=dict(usage),acquisitionLedger=ledger,diagnostics=diagnostics,diagnosticSummary=dict(pairs=len(diagnostics),passedPairs=sum(d['pairPassed'] for d in diagnostics)),
                provenance=dict(sourceCommit=manifest['source_commit'],frozenAt=manifest['frozen_at'],sourceHashes=manifest['source_sha256'],requestedGenerator=manifest['generator'],requestedJudges=manifest['judges'],returnedModelSnapshots=None,hardTokenCap=None,temperature=None,costUSD=None,
                                interpretation='Action-count and word-budget matched main arms, not token-matched; same-provider judges; no returned provider model snapshots.'),
                sources=[artifact(target/f) for f in ('manifest.json','judge-manifest.json','mask-map.json')]+[artifact(p) for p in source_paths.values()],
                globalBankMatchPolicy='Any nonnull match anywhere in a task/judge mechanism group makes that group non-new in every arm. Raw ratings remain unchanged.')


def analyze_dataset(dataset):
    proc=subprocess.run(['node',str(HERE/'analyze.mjs')],input=json.dumps(dataset),text=True,capture_output=True,check=True)
    inference=json.loads(proc.stdout)
    if dataset['cohort']=='development':
        inference['primary']['directionalEvidence']='not-applicable-development'
        inference['publicationStatus']='Development instrumentation check, excluded from main efficacy claims; inferential values are diagnostic only.'
    else:
        inference['publicationStatus']='Complete prespecified synthetic benchmark; interpret only within its stated scope.'
    return dict(dataset,analysis=inference)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort',choices=['main','development'],default='main')
    parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args()
    dataset=load_dataset(HERE/'runs'/args.cohort)
    if args.validate_only:
        print(json.dumps(dict(complete=True,cohort=args.cohort,nTasks=dataset['nTasks'],usage=dataset['usage'])))
        return
    result=analyze_dataset(dataset)
    targets=[HERE/'runs'/args.cohort/'results.json']
    if args.cohort=='main':targets += [HERE/'results.json',ROOT/'site/data/transfer-study.json']
    data=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    for target in targets:target.parent.mkdir(parents=True,exist_ok=True);target.write_text(data)
    print(json.dumps(dict(cohort=args.cohort,nTasks=result['nTasks'],primary=result['analysis']['primary'],outputs=[str(p) for p in targets])))


if __name__=='__main__':main()
