#!/usr/bin/env python3
"""Independent calibration count audit; no imports from the study analyzer.

This complements (does not replace) its strict provenance and checker replay.
"""
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
STUDY=ROOT/'research/working-solutions-v1'
def read(p):return json.loads(p.read_text())
def main():
    report={'scope':'Independent recount of stored execution verdicts, panel sizes, development gates and published summary values. The primary analyzer separately validates raw provenance and rechecks outputs.','cohorts':{}}
    for cohort in ('development-1','development-2','main'):
        if cohort=='main' and not (STUDY/'runs/main/results.json').exists(): continue
        path=STUDY/'runs'/cohort;r=read(path/'results.json');m=read(path/'manifest.json')
        n=32 if cohort=='main' else 8
        assert r['nTasks']==n and len(m['tasks'])==n
        if cohort!='main': assert r['primary'] is None and r['secondary'] is None
        result={}
        for arm in ('D','R','X'):
            rows=[]
            for task in m['tasks']:
                e=read(path/'execution'/f'{task["id"]}-{arm}-final.json')
                assert len(e['cases'])==256 and len({c['caseId'] for c in e['cases']})==256
                assert {regime:sum(c['regime']==regime for c in e['cases']) for regime in ('ordinary','boundary','adversarial','shift')}==dict.fromkeys(('ordinary','boundary','adversarial','shift'),64)
                count=sum(c['passed'] for c in e['cases']);rows.append(count)
                expected=next(t for t in r['perTask'] if t['taskId']==task['id'])['arms'][arm]
                assert expected['passCount']==count
            mean=sum(rows)/(n*256);full=sum(n==256 for n in rows)
            assert r['descriptive'][arm]['meanPassRate']==mean and r['descriptive'][arm]['fullSuiteCount']==full
            result[arm]={'passed':sum(rows),'total':n*256,'mean':mean,'fullSuites':full}
        calls=list((path/'calls').glob('*/record.json'));assert len(calls)==n*6
        statuses=dict(Counter(read(p)['status'] for p in calls)); assert statuses==r['acquisition']['statuses']
        d=result['D']['mean']
        if cohort!='main':
            gate=r['developmentGate'];assert gate['floor']==(d<=.1) and gate['ceiling']==(d>=.95) and gate['readyForMain']==(.1<d<.95)
        else:
            assert r['primary']['difference']==result['R']['mean']-d
        report['cohorts'][cohort]={'arms':result,'deliveredResponses':len(calls),'statuses':statuses,'readyForMain':r.get('developmentGate'),'resultsFileSHA256':hashlib.sha256((path/'results.json').read_bytes()).hexdigest()}
    report['passed']=True
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
