import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from analysis import load_dataset, score_task, analyze_dataset
from prompts import generation_prompt, judge_prompt
from run import canonical, hash_json, stable_shuffle, schemas, SEED


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def rating(ident,group='g',match=None):
    return dict(id=ident,constraint_valid=True,feasible=True,actionable=True,baseline_match=match,mechanism_group=group,reason='Concrete valid intervention')


def fixture(root,failed=None,abstain_bank=False):
    source=root/'source';target=root/'run';source.mkdir();target.mkdir()
    tasks=[dict(id=f'd{i}',family=f'f{i}',title=f'Task {i}',brief='An offline process needs a visible action.',constraints=['No network'],success_criteria=['Observable success']) for i in (1,2)]
    cards=[dict(id=f'c{i}',label=f'Label {i}',relation=f'Relation {i}',boundary='Only local changes') for i in (1,2)]
    write(source/'tasks.json',{'development':tasks});write(source/'cards.json',{'cards':cards});write(source/'diagnostics.json',{'fixtures':[]})
    order=stable_shuffle(cards,'card-order');requests=[];assignments=[]
    for i,task in enumerate(tasks):
        card=order[i%2];wrong=order[(i+1)%2]
        assignments.append(dict(task_id=task['id'],card_id=card['id'],wrong_label_card_id=wrong['id']))
        for suffix,phase,arm,count in [('bank-1','bank','S',8),('bank-2','bank','S',8)]+[(a,'main',a,4) for a in ('S','R','LR','XR')]:
            prompt=generation_prompt(task,arm,card,wrong['label'],count=count)
            requests.append(dict(id=f'{task["id"]}-{suffix}',phase=phase,task_id=task['id'],arm=arm,count=count,model='gpt-6-astra',schema='generation',prompt=prompt,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest()))
    untagged=[{k:v for k,v in r.items() if k!='prompt_sha256'} for r in requests]
    scheduled=stable_shuffle(untagged,'development-acquisition');by_id={r['id']:r for r in requests};requests=[by_id[r['id']] for r in scheduled]
    manifest=dict(schema_version=1,study='counterfactual-transfer-v1',cohort='development',frozen_at='2026-09-20T00:00:00+00:00',source_commit='mock-only',source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()},tasks=tasks,assignments=assignments,requests=requests,generator='gpt-6-astra',judges=['gpt-6-astra','gpt-5.5'],schema_sha256={k:hash_json(v) for k,v in schemas().items()})
    write(target/'manifest.json',manifest)
    for name,schema in schemas().items():write(target/'schemas'/f'{name}.json',schema)
    def record(req,result,status='success'):
        directory=target/'calls'/req['id'];directory.mkdir(parents=True)
        raw=json.dumps(result);events='\n'.join([json.dumps({'type':'item.completed','item':{'type':'agent_message','text':raw}}),json.dumps({'type':'turn.completed','usage':{'input_tokens':100,'output_tokens':20}})])
        (directory/'attempt-1.events.jsonl').write_text(events);(directory/'attempt-1.stderr.txt').write_text('');(directory/'response.txt').write_text(raw)
        attempt=dict(number=1,exit_code=0,elapsed_seconds=1,usage={'input_tokens':100,'output_tokens':20},completed=True,tool_violation=False,events_sha256=hashlib.sha256(events.encode()).hexdigest(),stderr_sha256=hashlib.sha256(b'').hexdigest())
        hour={'bank':1,'main':3,'judge':5}[req['phase']]
        good=status in ('success','abstention')
        r=dict(schema_version=1,id=req['id'],request_sha256=hash_json(req),prompt_sha256=req['prompt_sha256'],status=status,error=None if good else 'Invalid schema',started_at=f'2026-09-20T0{hour}:00:00+00:00',finished_at=f'2026-09-20T0{hour+1}:00:00+00:00',requested_model=req['model'],returned_model=None,reasoning_effort='low',temperature=None,top_p=None,max_output_tokens=None,attempts=[attempt],result=result if good else None,result_sha256=hash_json(result) if good else None,raw_output_sha256=hashlib.sha256(raw.encode()).hexdigest())
        write(directory/'request.json',req);write(directory/'attempt-1.json',attempt);write(directory/'record.json',r)
        return r
    records={}
    for req in requests:
        action={k:f'{req["id"]} concrete {k}' for k in ('action','mechanism','implementation','check','risk')}
        result=dict(actions=[action],abstention_reason='')
        status='success'
        if req['id']==failed:result={'invalid':'schema'};status='validation_error'
        if abstain_bank and req['phase']=='bank':result=dict(actions=[],abstention_reason='No valid bank action');status='abstention'
        records[req['id']]=record(req,result,status)
    mappings=[];judgerequests=[]
    for task in tasks:
        bank=[];candidates=[];links=[]
        for req in [r for r in requests if r['task_id']==task['id']]:
            if records[req['id']]['status']=='validation_error':continue
            for i,action in enumerate(records[req['id']]['result']['actions']):
                ident=hashlib.sha256(canonical([SEED,'development',req['id'],i]).encode()).hexdigest()[:16]
                item=dict(id=ident,**action)
                if req['phase']=='bank':bank.append(item)
                else:candidates.append(item);links.append(dict(id=ident,request_id=req['id'],arm=req['arm'],action_index=i))
        candidates=stable_shuffle(candidates,f'development-{task["id"]}-candidates');bank=stable_shuffle(bank,f'development-{task["id"]}-bank')
        mappings.append(dict(task_id=task['id'],candidates=links,bank_ids=[b['id'] for b in bank]))
        for i,model in enumerate(manifest['judges'],1):
            prompt=judge_prompt(task,bank,candidates if i==1 else list(reversed(candidates)))
            req=dict(id=f'{task["id"]}-judge-{i}',phase='judge',task_id=task['id'],judge_id=f'j{i}',model=model,schema='judgment',prompt=prompt,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),candidate_ids=[c['id'] for c in candidates],bank_ids=[b['id'] for b in bank])
            judgerequests.append(req);record(req,{'ratings':[rating(c['id'],group=c['id']) for c in candidates]})
    write(target/'judge-manifest.json',dict(schema_version=1,source_manifest_sha256=hash_json(manifest),requests=stable_shuffle(judgerequests,'development-judge-order')));write(target/'mask-map.json',dict(schema_version=1,mappings=mappings))
    return target,source


class AnalysisTests(unittest.TestCase):
    def test_bank_match_propagates_across_arms_without_changing_raw_rows(self):
        rows=[rating('a','same','b1'),rating('b','same'),rating('c','other')]
        original=copy.deepcopy(rows)
        links=[dict(id='a',arm='S'),dict(id='b',arm='LR'),dict(id='c',arm='LR')]
        result=score_task(rows,links)
        self.assertEqual(rows,original)
        self.assertEqual(result['scores']['LR']['qnm'],1)
        self.assertEqual(result['scores']['LR']['qdm'],2)
        self.assertEqual(len(result['contradictions']),1)

    def test_complete_mock_records_pass_and_score_independent_units(self):
        with tempfile.TemporaryDirectory() as temporary:
            target,source=fixture(Path(temporary))
            data=load_dataset(target,source_root=source,expected_count=2)
            self.assertEqual(data['nTasks'],2)
            self.assertEqual(data['perProblem'][0]['arms']['LR']['score']['qnm'],1)
            self.assertEqual(data['usage']['bank']['logicalCalls'],4)
            self.assertEqual(data['agreement']['pairwiseMechanismGroupingAgreement'],1)
            result=analyze_dataset(data)
            self.assertEqual(result['analysis']['primary']['difference'],0)
            self.assertEqual(result['analysis']['primary']['test']['p'],1)
            self.assertEqual(result['analysis']['primary']['directionalEvidence'],'not-applicable-development')

    def test_failed_main_gets_zero_and_does_not_disappear(self):
        with tempfile.TemporaryDirectory() as temporary:
            target,source=fixture(Path(temporary),failed='d1-LR')
            data=load_dataset(target,source_root=source,expected_count=2)
            self.assertEqual(data['nTasks'],2)
            self.assertEqual(data['perProblem'][0]['arms']['LR']['score']['qnm'],0)
            self.assertEqual(data['perProblem'][0]['arms']['LR']['status'],'validation_error')

    def test_valid_empty_bank_is_retained_and_bank_failure_aborts(self):
        with tempfile.TemporaryDirectory() as temporary:
            target,source=fixture(Path(temporary),abstain_bank=True)
            data=load_dataset(target,source_root=source,expected_count=2)
            self.assertEqual(data['perProblem'][0]['bank']['realizedActions'],0)
        with tempfile.TemporaryDirectory() as temporary:
            target,source=fixture(Path(temporary),failed='d1-bank-1')
            with self.assertRaisesRegex(ValueError,'Invalid independent bank'):
                load_dataset(target,source_root=source,expected_count=2)

    def test_missing_judge_unknown_masks_and_tampered_raw_fail_closed(self):
        for defect in ('judge','mask','raw','events','source','unknown_call'):
            with self.subTest(defect=defect),tempfile.TemporaryDirectory() as temporary:
                target,source=fixture(Path(temporary))
                if defect=='judge':(target/'calls/d1-judge-1/record.json').unlink()
                elif defect=='mask':
                    doc=json.loads((target/'mask-map.json').read_text());doc['mappings'][0]['candidates'][0]['id']='unknown';write(target/'mask-map.json',doc)
                elif defect=='raw':(target/'calls/d1-LR/response.txt').write_text('{}')
                elif defect=='events':(target/'calls/d1-LR/attempt-1.events.jsonl').write_text('changed')
                elif defect=='source':(source/'cards.json').write_text('{}')
                else:(target/'calls/unscheduled').mkdir()
                with self.assertRaises((ValueError,FileNotFoundError)):
                    load_dataset(target,source_root=source,expected_count=2)


if __name__=='__main__':unittest.main()
