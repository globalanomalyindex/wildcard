#!/usr/bin/env python3
"""Public-only contract workflow. This does not generate or score hidden cases."""
import argparse
import json
from catalog import all_tasks,assignments,cards,owner,public_material
from execution import run_cases
from prompts import initial_prompt,final_prompt,validate_response
from run import feedback_for,source_card


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prompt','feedback','repair-prompt','check-final'])
    parser.add_argument('--task',required=True)
    parser.add_argument('--arm',choices=['D','R','X'],default='R')
    parser.add_argument('--response',help='Local JSON response file for the relevant phase')
    args=parser.parse_args()
    matches=[task for task in all_tasks() if task['id']==args.task]
    if len(matches)!=1:parser.error('Unknown task; inspect the benchmark catalog')
    task=matches[0];material=public_material(task['id']);bank=cards();assignment=assignments([task],bank)[0];card=source_card(assignment,args.arm,bank)
    if args.command=='prompt':print(initial_prompt(task,material,card));return
    if not args.response:parser.error('--response is required for this command')
    with open(args.response) as file:response=json.load(file)
    stage='final' if args.command=='check-final' else 'initial';validate_response(response,stage)
    if stage=='initial':
        feedback=feedback_for(task,material,{'status':'success','result':response})
        if args.command=='feedback':print(json.dumps(feedback,ensure_ascii=False,indent=2))
        else:print(final_prompt(task,material,response,feedback,card))
    else:
        cases=[example['input'] for example in material['examples']];executions=run_cases(response['program'],cases);module=owner(task['id']);verdicts=[]
        for example,case,result in zip(material['examples'],cases,executions):
            verdict=module.check(task['id'],case,result['outputs']) if result['status']=='success' else {'passed':False,'violations':['runtime_error']}
            verdicts.append({'id':example['id'],**result,**verdict})
        print(json.dumps({'scope':'Four public examples only; no claim about hidden tests or production behavior.','task':task['id'],'cases':verdicts},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
