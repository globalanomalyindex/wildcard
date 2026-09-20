"""Private process entry point for the no-host-binding QuickJS interpreter."""
import argparse
import json
import resource
import sys
import time

parser=argparse.ArgumentParser()
parser.add_argument('--dependencies')
args=parser.parse_args()
if args.dependencies: sys.path.insert(0,args.dependencies)
import _quickjs as quickjs

# Hard process bounds supplement the engine's per-entry CPU/memory/stack limits.
resource.setrlimit(resource.RLIMIT_CPU,(120,120))
resource.setrlimit(resource.RLIMIT_FSIZE,(0,0))
resource.setrlimit(resource.RLIMIT_CORE,(0,0))

SETUP = r'''
globalThis.Date=undefined;
globalThis.performance=undefined;
globalThis.Atomics=undefined;
globalThis.SharedArrayBuffer=undefined;
Math.random=function(){throw new Error("ambient randomness is unavailable");};
Object.freeze(Math);
'''
BRIDGE = r'''
(function(){
  const primitive=JSON.stringify, namesOf=Object.getOwnPropertyNames,
        descriptor=Object.getOwnPropertyDescriptor, symbolsOf=Object.getOwnPropertySymbols,
        isArray=Array.isArray, finite=Number.isFinite, proto=Object.getPrototypeOf;
  const objectProto=Object.prototype;
  function data(x,key){
    const d=descriptor(x,key);
    if(!d || !descriptor(d,"value"))throw new Error("JSON accessors are unavailable");
    if(!d.enumerable && !(isArray(x) && key==="length"))throw new Error("nonenumerable JSON property");
    return d.value;
  }
  function encode(x,seen,depth){
    if(depth>48)throw new Error("JSON nesting limit");
    if(x===null || typeof x==="boolean" || typeof x==="string")return primitive(x);
    if(typeof x==="number"){if(!finite(x))throw new Error("nonfinite JSON number");return primitive(x);}
    if(typeof x!=="object")throw new Error("non-JSON value");
    for(let i=0;i<seen.length;i++)if(seen[i]===x)throw new Error("cyclic JSON value");
    seen[seen.length]=x;
    if(symbolsOf(x).length)throw new Error("JSON symbol property");
    let text;
    const names=namesOf(x);
    if(isArray(x)){
      const length=data(x,"length");
      if(names.length!==length+1)throw new Error("non-JSON array properties or holes");
      text="[";
      for(let i=0;i<length;i++)text+=(i?",":"")+encode(data(x,primitive(i)),seen,depth+1);
      text+="]";
    }else{
      if(proto(x)!==objectProto && proto(x)!==null)throw new Error("non-JSON object");
      text="{";
      for(let i=0;i<names.length;i++)text+=(i?",":"")+primitive(names[i])+":"+encode(data(x,names[i]),seen,depth+1);
      text+="}";
    }
    seen.length-=1;
    if(text.length>131072)throw new Error("step output limit");
    return text;
  }
  return function(fn,input){
    const answer=fn(input);
    if(answer===null || typeof answer!=="object" || isArray(answer))throw new Error("step must return state and output");
    const names=namesOf(answer);
    if(names.length!==2 || !((names[0]==="output" && names[1]==="state") || (names[0]==="state" && names[1]==="output")))throw new Error("step must return exactly state and output");
    // Native stringification returns a flat transport string for the Python binding.
    return primitive(encode(answer,[],0));
  };
})()
'''


def context():
    ctx=quickjs.Context()
    ctx.set_memory_limit(64*1024*1024)
    ctx.set_max_stack_size(512*1024)
    ctx.set_time_limit(.05)
    ctx.eval(SETUP)
    return ctx


def execute_case(source,case):
    start=time.monotonic();cpu_start=time.process_time();outputs=[];output_bytes=0
    try:
        ctx=context();bridge=ctx.eval(BRIDGE)
        ctx.eval(source)
        fn=ctx.get('solve')
        if fn is None: raise ValueError('function solve is required')
        state=None
        for event in case['events']:
            # Only the current event enters the JavaScript realm.
            remaining=.2-(time.process_time()-cpu_start)
            if remaining<=0: raise ValueError('trace CPU limit')
            ctx.set_time_limit(min(.05,remaining))
            value=ctx.parse_json(json.dumps({'config':case['config'],'state':state,'event':event},ensure_ascii=False,allow_nan=False))
            answer=json.loads(json.loads(bridge(fn,value)))
            if not isinstance(answer,dict) or set(answer)!={'state','output'}:
                raise ValueError('invalid serialized step shape')
            state=answer['state']
            output_bytes+=len(json.dumps(answer['output'],ensure_ascii=False).encode())
            if output_bytes>262144: raise ValueError('trace output limit')
            outputs.append(answer['output'])
            if time.process_time()-cpu_start>.2: raise ValueError('trace CPU limit')
        return {'status':'success','outputs':outputs,'elapsedSeconds':round(time.monotonic()-start,6)}
    except (Exception,MemoryError) as error:
        return {'status':'runtime_error','outputs':outputs,'processedEvents':len(outputs),'error':str(error)[:1200],'elapsedSeconds':round(time.monotonic()-start,6)}


def contract_probe(when_source,property_source,pair):
    # New contexts for every observation prevent a previous output from becoming
    # implicit input to a later applicability predicate.
    ctx=context();ctx.eval(when_source)
    when=ctx.get('applies')
    if when is None: raise ValueError('function applies is required')
    input_value=ctx.parse_json(json.dumps(pair['input'],ensure_ascii=False,allow_nan=False))
    applicable=when(input_value)
    if type(applicable) is not bool: raise ValueError('applicability must return boolean')
    if not applicable: return {'id':pair['id'],'applies':False,'holds':None}
    other=context();other.eval(property_source)
    holds=other.get('holds')
    if holds is None: raise ValueError('function holds is required')
    value=holds(other.parse_json(json.dumps(pair['input'],ensure_ascii=False,allow_nan=False)),other.parse_json(json.dumps(pair['output'],ensure_ascii=False,allow_nan=False)))
    if type(value) is not bool: raise ValueError('property must return boolean')
    return {'id':pair['id'],'applies':True,'holds':value}


def gate(payload):
    good=[];bad=[];error=None
    try:
        for pair in payload['correct']:
            good.append(contract_probe(payload['whenSource'],payload['propertySource'],pair))
        for pair in payload['foils']:
            bad.append(contract_probe(payload['whenSource'],payload['propertySource'],pair))
    except (Exception,MemoryError) as failure:
        error=str(failure)[:1200]
    applicable=sum(x['applies'] for x in good)
    excluded=sum(not x['applies'] for x in good)
    rejected=sum(x['applies'] and not x['holds'] for x in bad)
    contradiction=any(x['applies'] and not x['holds'] for x in good)
    admitted=error is None and bool(good) and applicable>0 and rejected>0 and not contradiction
    return {'admitted':admitted,'error':error,'applicableCorrect':applicable,'excludedCorrect':excluded,'rejectedFoils':rejected,'applicabilityBoundaryExercised':excluded>0,'correct':good,'foils':bad}


def main():
    payload=json.load(sys.stdin)
    if payload['operation']=='cases':
        answer={'cases':[execute_case(payload['source'],case) for case in payload['cases']]}
    elif payload['operation']=='contract': answer=gate(payload)
    else: raise ValueError('Unknown worker operation')
    print(json.dumps(answer,ensure_ascii=False,allow_nan=False))

if __name__=='__main__':
    try:main()
    except Exception as failure:
        print(json.dumps({'workerError':str(failure)[:1500]}))
