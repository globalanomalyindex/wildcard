"""Public material construction and deterministic relation selection.

Only public task tags enter the matcher. Expected hidden outputs never enter
selection, model prompts or contract admission.
"""
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FAMILIES=('queue','cache','sync','ui')
TAGS={'capacity','conservation','ordering','identity','isolation','recovery','retention','thresholds','fairness','causality','visibility','propagation','uncertainty','reversibility','aggregation','deadlines'}
MATCH_SEED='wildcard-working-solutions-matching-v1'
PUBLIC_EVENT_LIMIT=4  # Prospective development-revision.md; common to every arm.


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':'))


def digest(value): return hashlib.sha256(canonical(value).encode()).hexdigest()


def modules(): return [importlib.import_module('benchmark.'+name) for name in FAMILIES]


def all_tasks():
    tasks=[]
    for module in modules():
        for task in module.TASKS:
            required={'id','family','split','title','specification','tags'}
            if not required<=task.keys() or not set(task['tags'])<=TAGS:
                raise ValueError('Invalid public task metadata: '+str(task.get('id')))
            if task['family'] not in FAMILIES or task['split'] not in ('main','development'):
                raise ValueError('Invalid task family/split')
            tasks.append(task)
    if len({x['id'] for x in tasks})!=len(tasks):raise ValueError('Duplicate task IDs')
    return tasks


def owner(task_id):
    matches=[module for module in modules() if any(t['id']==task_id for t in module.TASKS)]
    if len(matches)!=1:raise ValueError('Expected exactly one task owner')
    return matches[0]


def cards():
    result=json.loads((HERE/'cards.json').read_text())['cards']
    if len(result)!=16 or len({x['id'] for x in result})!=16:raise ValueError('Expected 16 unique source cards')
    for card in result:
        if not set(card['tags'])<=TAGS:raise ValueError('Unknown card feature')
    return result


def match(task,bank):
    # IDs, titles, implementations and hidden tests are deliberately absent.
    features=sorted(set(task['tags']))
    rankings=[]
    for card in bank:
        overlap=sorted(set(features)&set(card['tags']))
        rankings.append({'cardId':card['id'],'overlap':overlap,'score':len(overlap),'tieBreak':digest([MATCH_SEED,features,card['id']])})
    rankings.sort(key=lambda row:(-row['score'],row['tieBreak']))
    if not rankings or rankings[0]['score']==0:raise ValueError('No structurally indexed relation')
    return {'publicFeatures':features,'selectedCardId':rankings[0]['cardId'],'rankings':rankings}


def assignments(tasks,bank):
    order=sorted(bank,key=lambda card:digest([MATCH_SEED,'shuffle',card['id']]))
    positions={card['id']:i for i,card in enumerate(order)}
    result=[]
    for task in tasks:
        decision=match(task,bank)
        selected=decision['selectedCardId']
        # Fixed half-bank cyclic displacement is a derangement of card identities.
        shuffled=order[(positions[selected]+len(order)//2)%len(order)]['id']
        result.append({'taskId':task['id'],'matchedCardId':selected,'shuffledCardId':shuffled,'selection':decision})
    return result


def _mutations(value,path=()):
    if isinstance(value,dict):
        for key in sorted(value):yield from _mutations(value[key],path+(key,))
    elif isinstance(value,list):
        for index,item in enumerate(value):yield from _mutations(item,path+(index,))
    elif type(value) is bool:yield path,not value
    elif type(value) in (int,float):yield path,value+1
    elif isinstance(value,str):yield path,value+'__changed'
    elif value is None:yield path,'__changed'


def _replace(value,path,replacement):
    result=deepcopy(value)
    if not path:return replacement
    cursor=result
    for part in path[:-1]:cursor=cursor[part]
    cursor[path[-1]]=replacement
    return result


def public_material(task_id,module=None):
    module=module or owner(task_id)
    cases=[{**case,'events':deepcopy(case['events'][:PUBLIC_EVENT_LIMIT])} for case in module.public_cases(task_id)]
    if len(cases)!=4 or [case['id'] for case in cases]!=['p1','p2','p3','p4']:
        raise ValueError('Exactly p1 through p4 are required')
    examples=[];foils=[]
    for case in cases:
        input_value={'config':case['config'],'events':case['events']}
        output=module.reference(task_id,case)
        if not module.check(task_id,case,output)['passed']:
            raise ValueError('Public oracle and independent checker disagree: '+task_id)
        example={'id':case['id'],'input':input_value,'output':output}
        examples.append(example)
        for path,replacement in _mutations(output):
            changed=_replace(output,path,replacement)
            if not module.check(task_id,case,changed)['passed']:
                foils.append({'id':case['id']+'-foil','input':input_value,'output':changed,'mutationPath':list(path)})
                break
    if len(foils)<2:raise ValueError('Need behavioral foils from at least two public examples: '+task_id)
    return {'examples':examples,'incorrectExamples':foils}
