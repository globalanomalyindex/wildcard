"""Execute candidate JavaScript in a bounded, host-free interpreter subprocess.

The worker receives inputs, never expected hidden answers. No Python callback,
module loader, filesystem, network, clock or ambient RNG is exposed to JavaScript.
This is a local research runner, not a general multi-tenant sandbox service.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
MAX_SOURCE_BYTES = 10_000
MAX_CONTRACT_BYTES = 4_000
MAX_REQUEST_BYTES = 16 * 1024 * 1024


def _worker(payload):
    encoded=json.dumps(payload,ensure_ascii=False,allow_nan=False)
    if len(encoded.encode())>MAX_REQUEST_BYTES:
        raise ValueError('Execution request too large')
    args=[sys.executable,'-I',str(HERE/'js_worker.py')]
    dependency_path=os.environ.get('WILDCARD_PYTHON_DEPS')
    if dependency_path: args.extend(['--dependencies',dependency_path])
    # Deliberately exclude user configuration, account variables and credentials.
    env={'PATH':os.defpath,'LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1'}
    proc=subprocess.run(args,input=encoded,text=True,capture_output=True,cwd=HERE,
                        env=env,timeout=180)
    if proc.returncode:
        raise RuntimeError('JavaScript worker failed: '+proc.stderr[-1500:])
    result=json.loads(proc.stdout)
    if 'workerError' in result:
        raise RuntimeError(result['workerError'])
    return result


def run_cases(source,cases):
    if not isinstance(source,str) or len(source.encode())>MAX_SOURCE_BYTES:
        raise ValueError('Program exceeds source contract')
    if not isinstance(cases,list) or not 1<=len(cases)<=256:
        raise ValueError('Expected 1 to 256 cases')
    for case in cases:
        if not isinstance(case.get('config'),dict) or not isinstance(case.get('events'),list) or len(case['events'])>64:
            raise ValueError('Invalid case interface or event limit')
    return _worker({'operation':'cases','source':source,'cases':cases})['cases']


def check_contract(when_source,property_source,correct,foils):
    if any(not isinstance(x,str) for x in (when_source,property_source)) or len((when_source+property_source).encode())>MAX_CONTRACT_BYTES:
        return {'admitted':False,'error':'contract_source_limit','applicableCorrect':0,'excludedCorrect':0,'rejectedFoils':0,'applicabilityBoundaryExercised':False,'correct':[],'foils':[]}
    correct_inputs={json.dumps(pair['input'],sort_keys=True,ensure_ascii=False,allow_nan=False) for pair in correct}
    identities=[pair['id'] for pair in correct+foils]
    if not 1<=len(correct)<=8 or not 1<=len(foils)<=8 or len(set(identities))!=len(identities):
        raise ValueError('Contract examples require bounded unique identities')
    if any(json.dumps(pair['input'],sort_keys=True,ensure_ascii=False,allow_nan=False) not in correct_inputs for pair in foils):
        raise ValueError('Every incorrect example must share a correct example input')
    return _worker({'operation':'contract','whenSource':when_source,'propertySource':property_source,'correct':correct,'foils':foils})
