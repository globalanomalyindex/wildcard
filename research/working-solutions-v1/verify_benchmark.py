#!/usr/bin/env python3
"""Pre-acquisition reference/checker/engine audit on public validation seeds."""
import argparse
import hashlib
import json
from pathlib import Path
from catalog import all_tasks,assignments,cards,digest,owner,public_material
from execution import run_cases
from benchmark.common import REGIMES

HERE=Path(__file__).resolve().parent

def verify(count=64):
    tasks=all_tasks()
    if len(tasks)!=40 or len([t for t in tasks if t['split']=='main'])!=32:raise ValueError('Expected 32 main plus 8 development tasks')
    if len({t['specification'] for t in tasks})!=40:raise ValueError('Duplicate contracts')
    assignments(tasks,cards())
    rows=[]
    for task in tasks:
        module=owner(task['id']);source=module.reference_source(task['id']);material=public_material(task['id'])
        if len(source.encode())>10000:raise ValueError('Reference source limit')
        faults=module.fault_cases(task['id'])
        if len(faults)<3 or len({fault['name'] for fault in faults})!=len(faults):raise ValueError('Three distinct named faults are required')
        for fault in faults:
            if module.check(task['id'],fault['case'],fault['outputs'])['passed']:raise ValueError('Fault escaped: '+task['id']+'/'+fault['name'])
        public=[example['input'] for example in material['examples']]
        actual=run_cases(source,public)
        for case,result in zip(public,actual):
            if result['status']!='success' or not module.check(task['id'],case,result['outputs'])['passed']:raise ValueError('JS public reference failure '+task['id'])
        row={'taskId':task['id'],'family':task['family'],'split':task['split'],'publicFixtures':len(public),'publicFoils':len(material['incorrectExamples']),'namedFaultsRejected':[fault['name'] for fault in faults],'referenceSourceUTF8Bytes':len(source.encode()),'regimes':{}}
        for regime in REGIMES:
            cases=[module.make_case(task['id'],regime,'preflight-v1/'+str(index)) for index in range(count)]
            actual=run_cases(source,cases)
            events=0
            for case,result in zip(cases,actual):
                expected=module.reference(task['id'],case)
                if len(case['events'])>64 or not module.check(task['id'],case,expected)['passed']:raise ValueError('Python oracle failure '+task['id'])
                if result['status']!='success' or not module.check(task['id'],case,result['outputs'])['passed']:raise ValueError('JS reference failure '+task['id']+'/'+regime+': '+str(result))
                if digest(result['outputs'])!=digest(expected):raise ValueError('Reference disagreement '+task['id'])
                events+=len(case['events'])
            row['regimes'][regime]={'traces':count,'distinctInputs':len({digest(case) for case in cases}),'events':events,'corpusSHA256':digest(cases)}
        rows.append(row);print(task['id'],'verified',flush=True)
    return {'schemaVersion':1,'kind':'pre-acquisition instrumentation validation, not model evidence','validationSeedNamespace':'preflight-v1','casesPerRegime':count,'tasks':rows,'totalTraces':sum(4+sum(r['traces'] for r in row['regimes'].values()) for row in rows),'generatorAndOracleSourceSHA256':{path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted((HERE/'benchmark').glob('*.py'))},'limitations':['Separately formulated reference and checker are AI-authored and may share errors; cross-author review and explicit boundary cases complement agreement checks.','Known bad-output rejection does not exhaust all possible incorrect programs.','These public validation seeds are separate from the private final study seed.']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cases',type=int,default=64);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=verify(args.cases);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
