"""Known-answer tests for strict executable-study scoring and inference."""
import copy
import contextlib
import io
import tempfile
from unittest.mock import patch
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import unittest

HERE=Path(__file__).resolve().parent

class AnalysisTests(unittest.TestCase):
    def module(self):
        path=HERE/'analysis.py'
        self.assertTrue(path.exists(),'The strict analysis implementation is required')
        spec=importlib.util.spec_from_file_location('working_analysis_test_target',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module

    def fixture(self):
        import run
        request={'id':'demo-R-final','taskId':'demo','arm':'R'}
        record={'status':'success','result':{'program':'unused recorded source'}}
        cases=[{'id':f'demo/{regime}/{i:02d}','taskId':'demo','regime':regime,'index':i,'input':{'config':{},'events':[{}]},'expected':[1]} for regime in run.REGIMES for i in range(64)]
        execution={'id':request['id'],'taskId':'demo','arm':'R','recordSHA256':run.digest(record),'cases':[{'caseId':c['id'],'regime':c['regime'],'status':'success','outputs':[1],'passed':True,'violations':[],'error':None} for c in cases]}
        def checker(task,case,output):
            passed=output in ([1],[2])
            return {'passed':passed,'violations':[] if passed else ['wrong output']}
        return request,record,cases,execution,checker

    def test_valid_alternative_uses_checker_not_reference_equality(self):
        request,record,cases,execution,checker=self.fixture()
        execution['cases'][0]['outputs']=[2]
        result=self.module().validate_execution(execution,request,record,cases,checker)
        self.assertEqual(result['passCount'],256)
        self.assertTrue(result['fullSuite'])
        self.assertEqual(result['exactExpectedMatches'],255)

    def test_missing_duplicate_mismatched_and_false_verdicts_are_rejected(self):
        request,record,cases,execution,checker=self.fixture()
        variants=[]
        changed=copy.deepcopy(execution);changed['cases'].pop();variants.append(changed)
        changed=copy.deepcopy(execution);changed['cases'][-1]=changed['cases'][0];variants.append(changed)
        changed=copy.deepcopy(execution);changed['cases'][0]['regime']='unknown';variants.append(changed)
        changed=copy.deepcopy(execution);changed['taskId']='different';variants.append(changed)
        changed=copy.deepcopy(execution);changed['recordSHA256']='bad';variants.append(changed)
        changed=copy.deepcopy(execution);changed['cases'][0]['outputs']=[99];variants.append(changed)
        changed=copy.deepcopy(execution);changed['cases'][0]['passed']=1;variants.append(changed)
        module=self.module()
        for changed in variants:
            with self.subTest(change=changed['cases'][0]):
                with self.assertRaises(ValueError):module.validate_execution(changed,request,record,cases,checker)

    def test_invalid_final_scores_zero_and_cannot_be_laundered_as_success(self):
        import run
        request,record,cases,execution,checker=self.fixture()
        record={'status':'validation_error','result':None,'error':'invalid artifact'}
        execution['recordSHA256']=run.digest(record)
        for case in execution['cases']:
            case.update(status='invalid_final',outputs=[],passed=False,violations=['invalid_final'],error='invalid artifact')
        module=self.module()
        self.assertEqual(module.validate_execution(execution,request,record,cases,checker)['passCount'],0)
        execution['cases'][0].update(status='success',outputs=[1],passed=True,violations=[])
        with self.assertRaises(ValueError):module.validate_execution(execution,request,record,cases,checker)

    def test_wrong_regime_allocation_fails_even_at_256_cases(self):
        request,record,cases,execution,checker=self.fixture()
        cases[-1]['regime']=cases[0]['regime']
        execution['cases'][-1]['regime']=cases[0]['regime']
        with self.assertRaises(ValueError):self.module().validate_execution(execution,request,record,cases,checker)

    def test_cost_counts_retries_and_does_not_add_component_tokens(self):
        records=[{'requestedModel':'alias','returnedModel':None,'status':'success','attempts':[{'elapsedSeconds':1.5,'usage':{'input_tokens':100,'cached_input_tokens':40,'output_tokens':20}},{'elapsedSeconds':2.5,'usage':{'input_tokens':80,'cached_input_tokens':0,'output_tokens':10,'reasoning_output_tokens':4}}]}, {'requestedModel':'alias','returnedModel':None,'status':'validation_error','attempts':[{'elapsedSeconds':1,'usage':None}]}]
        result=self.module().summarize_cost(records)
        self.assertEqual(result['logicalCalls'],2)
        self.assertEqual(result['attempts'],3)
        self.assertEqual(result['reportedUsageTotals']['input_tokens'],180)
        self.assertEqual(result['reportedUsageTotals']['output_tokens'],30)
        self.assertEqual(result['missingUsageAttemptCounts']['input_tokens'],1)
        self.assertEqual(result['missingUsageAttemptCounts']['reasoning_output_tokens'],2)
        self.assertEqual(result['summedAttemptLatencySeconds'],5)
        self.assertEqual(result['returnedModelUnknownCalls'],2)

    @contextlib.contextmanager
    def artifact_fixture(self,module):
        # Exercise real acquisition-artifact validators, without any model call.
        import run
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)/'study';base.mkdir()
            for name in run.SOURCE_NAMES:
                destination=base/name;destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(HERE/name,destination)
            seed=Path(directory)/'private-seed';seed.write_text('0'*64+'\n')
            with patch.object(run,'HERE',base),contextlib.redirect_stdout(io.StringIO()):
                run.prepare('development-1',seed)
                target=base/'runs'/'development-1';manifest=run.read(target/'manifest.json')
                def delivered_invalid(request):
                    destination=target/'calls'/request['id'];destination.mkdir(parents=True)
                    text='invalid-json'
                    events='\n'.join(json.dumps(x) for x in [{'type':'item.completed','item':{'type':'agent_message','text':text}},{'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':2}}])+'\n'
                    attempt={'number':1,'exitCode':0,'elapsedSeconds':1.0,'usage':{'input_tokens':10,'output_tokens':2},'completed':True,'toolViolation':False,'malformedEventLines':0,'eventsSHA256':run.sha(events.encode()),'stderrSHA256':run.sha(b'')}
                    (destination/'attempt-1.events.jsonl').write_text(events);(destination/'attempt-1.stderr.txt').write_text('');(destination/'response.txt').write_text(text)
                    run.write_new(destination/'attempt-1.json',attempt)
                    record={'id':request['id'],'requestSHA256':run.digest(request),'promptSHA256':request['promptSHA256'],'status':'validation_error','error':'invalid JSON','requestedModel':request['model'],'returnedModel':None,'attempts':[attempt],'result':None,'resultSHA256':None,'rawOutputSHA256':run.sha(text.encode())}
                    run.write_new(destination/'record.json',record)
                for request in manifest['requests']:delivered_invalid(request)
                run.make_final('development-1')
                finals=run.final_requests(target,manifest)
                for request in finals:delivered_invalid(request)
                run.seal('development-1');sealed=run.read(target/'final-program-seal.json')
                corpus=[]
                for task in manifest['tasks']:
                    implementation=module.owner(task['id'])
                    for regime in run.REGIMES:
                        for index in range(64):
                            case=implementation.make_case(task['id'],regime,run.digest(['0'*64,task['id'],regime,index]))
                            corpus.append({'id':f"{task['id']}/{regime}/{index:02d}",'taskId':task['id'],'regime':regime,'index':index,'input':case,'expected':implementation.reference(task['id'],case)})
                run.write_new(target/'hidden-corpus.json',{'seed':'0'*64,'seedSHA256':manifest['hiddenSeedSHA256'],'finalProgramSealSHA256':run.digest(sealed),'cases':corpus})
                for request in finals:
                    record=run.record_for(target,request)
                    cases=[{'caseId':c['id'],'regime':c['regime'],'status':'invalid_final','outputs':[],'error':'invalid JSON','passed':False,'violations':['invalid_final']} for c in corpus if c['taskId']==request['taskId']]
                    run.write_new(target/'execution'/f"{request['id']}.json",{'id':request['id'],'taskId':request['taskId'],'arm':request['arm'],'recordSHA256':run.digest(record),'cases':cases})
                yield target

    def test_complete_chain_rejects_missing_raw_and_corrupt_corpus_or_seal(self):
        module=self.module()
        with self.artifact_fixture(module) as target:
            data=module.load_dataset(target)
            self.assertEqual(len(data['perTask']),8)
            self.assertEqual(data['acquisition']['attempts'],48)
            self.assertEqual(data['acquisition']['reportedUsageTotals']['input_tokens'],480)
            self.assertTrue(all(row['arms']['R']['passCount']==0 for row in data['perTask']))
            execution=next((target/'execution').glob('*.json'))
            raw=next((target/'calls').glob('*/attempt-1.events.jsonl'))
            for path,mutate in [(execution,lambda value:value['cases'].pop()),(target/'hidden-corpus.json',lambda value:value['cases'][0]['input']['config'].update({'unexpected':1})),(target/'final-program-seal.json',lambda value:value.update({'manifestSHA256':'wrong'}))]:
                original=path.read_text();value=json.loads(original);mutate(value);path.write_text(json.dumps(value))
                with self.assertRaises(ValueError):module.load_dataset(target)
                path.write_text(original)
            original=raw.read_text();raw.unlink()
            with self.assertRaises((ValueError,FileNotFoundError)):module.load_dataset(target)
            raw.write_text(original)
            # A prospective source revision must dispatch to the old full snapshot.
            current=target.parent.parent/'js_worker.py';current.write_text(current.read_text()+'\n# new prospective version\n')
            import sys
            proc=subprocess.run([sys.executable,str(target.parent.parent/'analysis.py'),'--run-dir',str(target),'--validate-only'],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual(json.loads(proc.stdout),{'valid':True,'cohort':'development-1','tasks':8,'finalPrograms':24,'effectsComputed':False})

    def js(self,expression,value=None):
        path=HERE/'analyze.mjs'
        self.assertTrue(path.exists(),'The deterministic inference implementation is required')
        node=shutil.which('node')
        self.assertIsNotNone(node,'Node is required for the frozen statistics bridge')
        code='import * as m from '+json.dumps(path.as_uri())+';\n'+expression
        proc=subprocess.run([node,'--input-type=module','-e',code],input=json.dumps(value),text=True,capture_output=True)
        self.assertEqual(proc.returncode,0,proc.stderr)
        return json.loads(proc.stdout)

    def rows(self,d=128,r=128,x=128,split='main'):
        per_family=8 if split=='main' else 2
        return {'cohort':split,'perTask':[{'taskId':f'{family}-{i}','family':family,'arms':{arm:{'passCount':count,'totalCases':256,'fullSuite':count==256} for arm,count in [('D',d),('R',r),('X',x)]}} for family in ['queue','cache','sync','ui'] for i in range(per_family)]}

    def test_all_zero_effect_is_inconclusive_and_secondary_is_closed(self):
        result=self.js('import {readFileSync} from "node:fs"; console.log(JSON.stringify(m.analyze(JSON.parse(readFileSync(0,"utf8")))));',self.rows())
        self.assertEqual(result['primary']['difference'],0)
        self.assertEqual(result['primary']['ci95'],[0,0])
        self.assertEqual(result['primary']['test']['p'],1)
        self.assertFalse(result['primary']['positiveEvidence'])
        self.assertIsNone(result['secondary']['test'])
        self.assertFalse(result['secondary']['inferentialGateOpen'])

    def test_all_positive_effect_meets_statistical_and_practical_rules(self):
        result=self.js('import {readFileSync} from "node:fs"; console.log(JSON.stringify(m.analyze(JSON.parse(readFileSync(0,"utf8")))));',self.rows(d=0,r=256,x=0))
        self.assertEqual(result['primary']['difference'],1)
        self.assertEqual(result['primary']['ci95'],[1,1])
        self.assertTrue(result['primary']['positiveEvidence'])
        self.assertTrue(result['primary']['practicalBenefit'])
        self.assertTrue(result['secondary']['inferentialGateOpen'])
        self.assertTrue(result['prototypeReadiness']['benchmarkGateMet'])
        self.assertEqual(result['primary']['bootstrap']['iterations'],100000)
        self.assertEqual(result['primary']['test']['iterations'],1000000)
        self.assertEqual(result['primary']['test']['p'],(result['primary']['test']['extremeCount']+1)/1000001)

    def test_bootstrap_preserves_all_four_family_sizes(self):
        expression='const rows=[[-256,"a"],[-64,"b"],[64,"c"],[256,"d"]].flatMap(([differenceCount,family])=>Array.from({length:8},()=>({differenceCount,family}))); console.log(JSON.stringify(m.stratifiedBootstrap(rows,{seed:"test-strata",iterations:1000})));'
        first=self.js(expression)
        self.assertEqual(first,self.js(expression))
        self.assertEqual(first['ci95'],[0,0])
        self.assertEqual(first['familySizes'],{'a':8,'b':8,'c':8,'d':8})

    def test_development_is_descriptive_and_marks_baseline_extremes(self):
        result=self.js('import {readFileSync} from "node:fs"; console.log(JSON.stringify(m.analyze(JSON.parse(readFileSync(0,"utf8")))));',self.rows(d=0,r=256,split='development-1'))
        self.assertIsNone(result['primary'])
        self.assertTrue(result['developmentGate']['floor'])
        self.assertFalse(result['developmentGate']['ceiling'])
        self.assertIsNone(result['prototypeReadiness']['benchmarkGateMet'])

    def test_inference_refuses_missing_arm_and_wrong_family_counts(self):
        value=self.rows();value['perTask'][0]['arms'].pop('X')
        result=self.js('import {readFileSync} from "node:fs"; try{m.analyze(JSON.parse(readFileSync(0,"utf8")));console.log("false")}catch{console.log("true")}',value)
        self.assertTrue(result)
        value=self.rows();value['perTask'][0]['family']='cache'
        self.assertTrue(self.js('import {readFileSync} from "node:fs"; try{m.analyze(JSON.parse(readFileSync(0,"utf8")));console.log("false")}catch{console.log("true")}',value))

if __name__=='__main__':unittest.main()
