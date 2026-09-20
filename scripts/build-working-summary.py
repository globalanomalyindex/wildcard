#!/usr/bin/env python3
"""Build the recorded product viewer only from validated execution artifacts."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
STUDY=ROOT/'research'/'working-solutions-v1'
SITE=ROOT/'site'/'data'

def read(path):return json.loads(path.read_text())
def encode(value):return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n'
def percent(value):return f'{value*100:.1f}%'
def signed(value):return f'{value*100:+.1f}'

def build(cohort):
    target=STUDY/'runs'/cohort
    subprocess.run([sys.executable,str(STUDY/'analysis.py'),'--cohort',cohort,'--check'],check=True)
    manifest=read(target/'manifest.json');results=read(target/'results.json');corpus=read(target/'hidden-corpus.json')['cases']
    scores={row['taskId']:row for row in results['perTask']};assignments={row['taskId']:row for row in manifest['assignments']};cards={card['id']:card for card in manifest['cards']}
    summary={'schemaVersion':1,'cohort':cohort,'cohortLabel':'main study' if cohort=='main' else 'development calibration','nTasks':results['nTasks'],'sourcePath':str((target/'results.json').relative_to(ROOT)),'tasks':[],'metrics':[{'value':percent(results['descriptive']['D']['meanPassRate']),'label':'direct · mean trace pass rate'},{'value':percent(results['descriptive']['R']['meanPassRate']),'label':'matched outside · mean trace pass rate'},{'value':str(results['nTasks']),'label':'task blocks · 256 traces each'}]}
    if cohort=='main':
        primary=results['primary'];summary['title']='the main study'
        summary['verdict']='Outside relations improved working solutions on this benchmark.' if primary['positiveEvidence'] else 'This study did not establish an advantage for outside relations.'
        summary['limit']=f"Matched outside minus direct: {signed(primary['difference'])} percentage points; 95% interval [{signed(primary['ci95'][0])}, {signed(primary['ci95'][1])}]; paired sign-flip p={primary['test']['p']:.5g}. Thirty-two authored task blocks. This does not establish production reliability."
    else:
        gate=results['developmentGate'];summary['title']='development calibration'
        summary['verdict']='The calibration passed its difficulty gate.' if gate['readyForMain'] else 'The calibration blocked a confirmatory main test.'
        summary['limit']='These are eight development tasks. Outside-arm scores are descriptive; this is not a confirmatory test of the hypothesis. '+('Direct solving was at the predefined ceiling.' if gate['ceiling'] else 'Direct solving was at the predefined floor.' if gate['floor'] else 'Main-study results must be reported separately.')
    files={}
    for task in sorted(manifest['tasks'],key=lambda row:row['id']):
        identity=task['id'];selection=assignments[identity]
        summary['tasks'].append({key:task[key] for key in ('id','title','family')})
        expanded={**task,'matchedCard':cards[selection['matchedCardId']],'shuffledCard':cards[selection['shuffledCardId']],'arms':{}}
        executions={}
        for arm in ('D','R','X'):
            initial=read(target/'calls'/f'{identity}-{arm}-initial'/'record.json');final=read(target/'calls'/f'{identity}-{arm}-final'/'record.json');feedback=read(target/'feedback'/f'{identity}-{arm}.json')['feedback']
            expanded['arms'][arm]={'passCount':scores[identity]['arms'][arm]['passCount'],'initial':initial['result'],'final':final['result'],'feedback':feedback,'sourcePath':str((target/'calls'/f'{identity}-{arm}-final'/'response.txt').relative_to(ROOT))}
            executions[arm]={case['caseId']:case for case in read(target/'execution'/f'{identity}-{arm}-final.json')['cases']}
        traces=[]
        for case in [case for case in corpus if case['taskId']==identity]:
            traces.append({'id':case['id'],'regime':case['regime'],'index':case['index'],'input':case['input'],'expected':case['expected'],'arms':{arm:{key:executions[arm][case['id']][key] for key in ('passed','status','outputs','violations','error')} for arm in ('D','R','X')}})
        files[SITE/'working-solutions'/f'{identity}.json']=encode({'schemaVersion':1,'task':expanded,'traces':traces})
    files[SITE/'working-solutions.json']=encode(summary)
    return files

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cohort',choices=['main','development-1','development-2'],required=True);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    files=build(args.cohort)
    for path,content in files.items():
        if args.check:
            if not path.exists() or path.read_text()!=content:raise ValueError('Stale generated viewer artifact: '+str(path))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
    actual=set((SITE/'working-solutions').glob('*.json'));expected={path for path in files if path.parent.name=='working-solutions'}
    extra=actual-expected
    if extra:raise ValueError('Unexpected old task artifacts; review before removing: '+', '.join(map(str,sorted(extra))))
    print(('Verified' if args.check else 'Built')+f' {len(files)} recorded viewer artifacts from {args.cohort}.')

if __name__=='__main__':main()
