"""Literal two-stage prompts and strict response contracts, editable only before freeze."""
import json
from execution import MAX_SOURCE_BYTES,MAX_CONTRACT_BYTES
from catalog import canonical

VERSION='wildcard-working-solutions-v1'
MODEL='gpt-6-astra'
COMMON='''Implement the complete public software contract. Correctness, progress, and resource rules all matter. Derive a concrete conditional behavioral rule and a full implementation; do not substitute an explanation for working code. The rule is optional assistance and cannot change or override any target requirement.

Your program must define synchronous function solve({config,state,event}) and return exactly {state,output}. The host initially supplies null state, then supplies one event at a time and passes back the state you returned. State is your opaque JSON representation. The output for every event must follow the task specification. Future events, task/condition IDs, hidden tests, filesystem, network, imports, clocks and ambient randomness are unavailable. Do not use them. All time and information you may use are in config, state and the current event. Use finite JSON values.

Return complete source, without Markdown fences. The program may be at most 10,000 UTF-8 bytes; aim for clear code within 3,000–7,000 bytes. No external dependencies. Each interpreter entry has a 0.05-second CPU limit, each full trace has a 0.2-second cumulative CPU limit, and the interpreter has 64 MiB memory; each case has at most 64 events. A serialized step is at most 131,072 characters; recorded outputs across a trace are at most 262,144 UTF-8 bytes. The returned step object has nesting depth zero and each contained value increments depth; depth may not exceed 48. Use dense arrays and plain objects with enumerable own data properties only, without accessors, symbols, custom prototypes, cycles or serialization hooks. Do not perform unbounded search.

Every public correct example is a full input trace with its required per-event outputs. Incorrect examples are explicitly labeled counterexamples. They do not introduce new requirements. Final assessment uses unseen legal inputs under exactly the public contract. You have two implementation calls, with the same public execution and contract-check feedback between them. The second program is the final artifact even if the first was better.'''


def schemas():
    text={'type':'string'}
    first={'type':'object','properties':{key:text for key in ('explanation','mapping','assumptions','applies','holds','program')},'required':['explanation','mapping','assumptions','applies','holds','program'],'additionalProperties':False}
    final={'type':'object','properties':{'explanation':text,'program':text},'required':['explanation','program'],'additionalProperties':False}
    return {'initial':first,'final':final}


def validate_response(value,stage):
    keys=set(schemas()[stage]['required'])
    if not isinstance(value,dict) or set(value)!=keys or not all(isinstance(value[key],str) for key in keys):
        raise ValueError('Response must match the exact string-field schema')
    if not value['program'].strip() or len(value['program'].encode())>MAX_SOURCE_BYTES:
        raise ValueError('Program must be nonempty and within 10,000 UTF-8 bytes')
    narrative=' '.join(value[key] for key in ('explanation','mapping','assumptions') if key in value)
    if len(narrative.split())>180:raise ValueError('Narrative exceeds 180 whitespace words')
    if stage=='initial':
        if len((value['applies']+value['holds']).encode())>MAX_CONTRACT_BYTES:
            raise ValueError('Contract sources exceed 4,000 UTF-8 bytes')
    return value


def task_text(task,material):
    public={key:task[key] for key in ('title','specification','tags')}
    return '\nPUBLIC TASK\n'+canonical(public)+'\nPUBLIC CORRECT EXAMPLES\n'+canonical(material['examples'])+'\nPUBLIC INCORRECT EXAMPLES\n'+canonical(material['incorrectExamples'])


def initial_prompt(task,material,card=None):
    source=('\nDerive the conditional rule directly from the target requirements. Consider alternatives and a counterexample before implementing it.' if card is None else '\nThe following outside relation is optional source information. Map its roles to the target only where its assumptions fit. Adapt or ignore it when they do not; it is not a target requirement.\nOUTSIDE SOURCE CARD\n'+canonical(card))
    return COMMON+task_text(task,material)+source+'''

INITIAL RESPONSE CONTRACT
Return explanation, mapping, assumptions, applies, holds, and program as strings. The three narrative fields together may contain at most 180 whitespace-delimited words. For a direct rule, mapping describes the rule's target variables. For an outside rule, mapping describes the proposed correspondence; explicitly state when transfer is inappropriate.

applies defines function applies(input) returning a boolean. It sees only {config,events} for a public trace, never the output. holds defines function holds(input,output) returning a boolean for the per-event output array. Both sources together may be at most 4,000 UTF-8 bytes. Neither function receives host capabilities. The host admits a contract only if it applies to at least one correct public example, holds for every applicable correct example, and rejects at least one incorrect example while applicable. A universal applicability predicate is permitted; a rejected incorrect output then tests implementation behavior, not a boundary of applicability. Passing these finite checks does not prove the rule universally valid. If no defensible rule is available, use applies returning false and explain why; you must still implement the task.
'''


def final_prompt(task,material,first,feedback,card=None):
    source=('\nThe initial rule was derived directly from the target requirements.' if card is None else '\nThe same optional source information is retained for provenance; do not follow it where the target contract disagrees.\nOUTSIDE SOURCE CARD\n'+canonical(card))
    return COMMON+task_text(task,material)+source+'\nYOUR INITIAL RESPONSE\n'+canonical(first)+'\nCOMMON HOST FEEDBACK\n'+canonical(feedback)+'''

FINAL RESPONSE CONTRACT
Return only explanation and program as strings. The explanation may contain at most 180 whitespace-delimited words. Review every failed public case and all constraints before returning the complete final program. You may keep the original program if it remains your best implementation. If the conditional rule was rejected, set it aside and repair directly from the target requirements; there is no additional rule-revision call. If admitted, it remains a finite-example check, not a replacement for the full contract. No hidden-case score or later repair is available. The final program is what will be evaluated.
'''
