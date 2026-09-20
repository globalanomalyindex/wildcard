"""Cache/storage task contracts with separate reference and checker formulations."""
import json
import math
from .common import cloned, rng_for, result, check_count, REGIMES


def _integer_json(value):
    """Preserve boolean identity while canonicalizing integral JSON numbers."""
    if type(value) in (int, float):
        if abs(value)>9007199254740991 or not math.isfinite(value) or int(value)!=value:
            raise ValueError('Expected a finite safe integer JSON number')
        return int(value)
    if isinstance(value, list):return [_integer_json(x) for x in value]
    if isinstance(value, dict):return {k:_integer_json(v) for k,v in value.items()}
    return value

_COMMON=(' Implement pure solve({config,state,event})->{state,output}, initially state=null. '
 'Only the current event is supplied; every named event uses a type field, e.g. {type:"restore"}. Return exactly the stated output fields each step; opaque JSON state is not graded. '
 'All numeric inputs and intermediate arithmetic are safe integers; time deltas are nonnegative. Unless a task explicitly overrides this, keys, snapshot IDs, readers and graph nodes are single lowercase ASCII letters. '
 'Integral JSON number spellings such as 1 and 1.0 are equivalent; booleans remain distinct from numbers. '
 'At most eight identities and 48 events occur. Configurations and event fields shown below are present. '
 'Ordinary regimes use moderate storage and timing; boundary uses equality/empty states; adversarial repeats stale/conflicting events; '
 'shift uses smaller capacity, longer timing gaps or deeper dependency shapes, without changing these rules.')
_DEFS=[
('c01','Byte-budget expiring recency cache','capacity retention deadlines ordering',
 'Config capacity>=1. Start now=0 and empty entries. Events put{key,value,size>0,ttl>=0},get{key},advance{dt>=0}. Value is integer. Advance adds dt; delete entries with expiry<=now before handling other operations and after advance. A put with size>capacity does nothing, even if key exists; otherwise remove old key, and if ttl>0 evict oldest recency entries until the new entry fits, then insert it newest with expiry=now+ttl. ttl=0 simply removes that key. A successful get returns value and moves that entry newest; miss returns null. Put and advance value=null. Output {value,keys:[oldest-to-newest],bytes:sum_sizes,now}.'),
('c02','Single-flight stale refresh','identity deadlines causality visibility',
 'Config ttl>=1,stale>=0. Start now=0, empty cache/pending and next token=1. Events get{key},resolve{key,token,value},reject{key,token},invalidate{key},advance{dt>=0}. On get return cached value only if age<ttl+stale, else null. If no cache or age>=ttl and no pending for key, emit {key,token:next} and increment next. Cached data remains stored even after stale window. Matching resolve stores value at now and clears pending; matching reject only clears pending; unmatched response ignored. Invalidate clears cache and pending but never rewinds next token. Advance only changes now. Only get returns nonnull value; others return null. Output {value,fetch:[{key,token}],pending:[sorted pending keys],now}. Equality at ttl triggers refresh, equality at ttl+stale cannot return stale data.'),
('c03','Checksum-verified retained snapshots','recovery retention identity uncertainty',
 'Config keep>=1. Checksum(data)=sum((index+1)*integer_value) modulo 251 normalized to 0..250. Events save{id,data:[0..250],checksum:0..250},damage{id,index,value:0..250},drop{id},restore. Save replaces same ID and appends newest, retaining only the newest keep snapshots even if invalid. Damage updates an existing snapshot at valid index without updating checksum; missing snapshot/index does nothing. Drop removes that ID. Restore chooses the newest snapshot whose computed checksum equals its stored checksum, returns a copy of its data and chosen ID; if none, both null. Other operations return data=null,chosen=null. Output {data,chosen,retained:[oldest-to-newest IDs]}. Checksum validity is the complete declared integrity criterion, not cryptographic authenticity or guaranteed detection of every corruption.'),
('c04','Acknowledged replay-preserving compaction','retention ordering causality conservation',
 'Config readers is a nonempty list. Start sequence=0, empty log, each reader acknowledgment=0. Events set{key,value},ack{reader,seq},compact. Set increments sequence and appends {seq,key,value}. Ack succeeds only if old_ack<=seq<=current_sequence; otherwise unchanged. Compact watermark=min(reader acknowledgments): keep every log record above watermark, plus exactly the latest record at or below watermark for each key that has one. Preserve sequence order. Output {log:[retained sequence numbers],view:{key:latest value from all writes}} after each event. Compaction never changes visible values; unacknowledged records cannot be discarded. Values are integers.'),
('c05','Canonical typed query keys','identity ordering aggregation',
 'Config empty. Every event is encode{value}, where value is JSON null/boolean/safe integer/string/array/object, maximum depth 3; object keys are single lowercase ASCII letters. Output {key:canonical_JSON_string}. Canonical JSON has no insignificant spaces; recursively sort object keys lexically, preserve array order, encode strings and scalars exactly as ECMAScript JSON.stringify: quote and backslash escaped, backspace/form-feed/newline/carriage-return/tab use their short escapes, other U+0000..U+001F characters use lowercase four-digit Unicode escapes, and all other Unicode (including U+2028/U+2029) and slash remain literal. Emit null/true/false/numbers without added type coercion. Unicode string values are allowed; no lone surrogates, nonintegral numbers or negative zero occur. State is irrelevant. Distinctions between absent and null, numeric and string values, boolean and integer, or array order must remain distinguishable.'),
('c06','Dirty write-back residency','recovery retention identity capacity',
 'Config slots>=1. Start empty resident cache and durable map, per-key version counters=0. Events write{key,value},read{key},flush{key},ack{key,version},evict{key}. Cache recency is oldest->newest. To insert when full, evict the oldest CLEAN resident; if all dirty insertion fails. Write existing key always succeeds, increments its lifetime version, sets dirty=true and newest; insert write uses same rule, status=written or blocked. Read returns resident value and makes newest (hit); otherwise durable value (durable), must promote it CLEAN if space/clean eviction permits; if every resident is dirty, return the durable value without promotion, without changing lifetime version; absent=miss/null. Flush resident dirty key emits {key,version,value} without changing recency/dirty, status=flushed; otherwise ignored. Ack only for a currently resident dirty entry with version matching both current version AND a previously emitted flush for that key/version: persist current value, mark clean (persisted); otherwise ignored. Evict only clean resident (evicted), dirty=blocked, absent=missing. Other operations value=null. Output {status,value,flush:[records],cached:[oldest-to-newest keys],dirty:[sorted dirty keys],durable:{key:value}}. A stale acknowledgment cannot persist newer unflushed data.'),
('c07','Transitive dependency memo invalidation','causality propagation ordering retention',
 'Config deps is a finite DAG of existing nodes; values gives an integer for every leaf (empty dependency list). A nonleaf value is sum of its immediate dependency values; repeated dependencies are not present. Start empty memo. Events evaluate{node},set{node,value}. Set changes only a leaf; nonleaf set ignored. Successful set invalidates that leaf and every transitive dependent, even if value unchanged. Evaluate computes dependencies in their listed order, memoizes leaves and intermediate nodes, and returns the node value. Output {value:integer_or_null,computed:number of newly memoized nodes this event,valid:[sorted memoized node IDs]}. Set value=null and computed=0. Cached evaluate computed=0. No undefined nodes or cycles are supplied.'),
('c08','Sparse range completeness','identity uncertainty capacity conservation',
 'Config length>=1. Start all byte positions unknown. Events put{start,data:[0..255]},read{start,end},clear{start,end}. Put valid only if 0<=start and start+len(data)<=length and every overlapping known byte equals incoming byte; otherwise reject the ENTIRE put without changes. Empty in-range put allowed. Read/clear require 0<=start<=end<=length. Valid clear makes range unknown (cleared). Valid read returns status=complete and data list if every byte is known (empty range complete); otherwise status=incomplete,data=null,missing=maximal unknown half-open intervals in ascending order. Invalid operation status=invalid, data=null,missing=[]; valid put status=stored, other non-read data=null,missing=[]. Output {status,data,missing,known:count_known_positions}. Conflicting data must not silently replace known bytes.'),
('dev-c01','Development pinned FIFO invalidation','retention visibility capacity identity',
 'Config capacity>=1. Start empty residents. put{key,value:integer} replaces a live resident value without changing its FIFO position or pin count (stored); a tombstoned resident blocks replacement. New put evicts the oldest unpinned resident if full, or is blocked if all residents pinned; otherwise insert newest with pins=0 (stored). pin{key} increments pins for a live resident (pinned), otherwise ignored. unpin{key} decrements positive pins (released); if the last pin leaves a tombstone, remove that resident. Otherwise unpin ignored. invalidate{key} removes an unpinned resident or marks a pinned one tombstoned (invalidated); absent=missing. Tombstones still consume capacity and cannot be read or newly pinned. get{key} returns a live value (hit), else null (miss), without reordering. Output {status,value:integer_or_null,order:[resident FIFO keys including tombstones],pins:{resident_key:count},tombstones:[sorted tombstone keys]}. Only get returns nonnull value. Keys may be reused after removal. No recency promotion, persistence or flush acknowledgments exist.'),
('dev-c02','Development revision-guarded snapshot rollback','recovery identity retention isolation',
 'Config keep>=1,initial:integer. Start value=initial,revision=0, no snapshots and no used snapshot IDs. write{expect,value} changes value and increments revision exactly once iff expect=current revision (written), otherwise conflict. Even a same-value write increments. save{id} for an ID never saved stores immutable {value,revision}, appends newest, retaining only newest keep snapshots (saved); previously used ID=exists with no changes, even if evicted/dropped. rollback{id,expect} first checks expect=current revision (otherwise conflict); then requires a retained snapshot (otherwise missing); success restores its value and increments CURRENT revision once (rolled_back), never resets revision to the snapshot revision. Snapshots remain unchanged by rollback. drop{id} removes a retained snapshot (dropped), else missing; it never makes an ID reusable. Output {status,value,revision,snapshots:[retained IDs oldest-to-newest],saved:{retained_id:{value,revision}}}. There is no undo/redo stack, automatic snapshot creation or transactional group.')]
TASKS=[dict(id=i,family='cache',split='development' if i.startswith('dev-') else 'main',title=t,tags=tags.split(),specification=spec+_COMMON) for i,t,tags,spec in _DEFS]
_IDS={t['id'] for t in TASKS}

_REGIME_NOTES={
'c01':'Boundary byte capacity=2; shift capacity=4 versus ordinary 6, sizes 1..4 instead of 1..5, TTL 0..2 instead of 0..5 and clock steps 0..5 instead of 0..4.',
'c02':'Boundary ttl=2,stale=0; shift ttl=4,stale=2 versus ordinary ttl=2,stale=3, with clock gaps 0..7 instead of 0..5, retaining both fresh and stale behavior.',
'c03':'Boundary retains one snapshot; shift retains two versus ordinary three, with valid save checksums at 40% instead of 70%, stressing fallback and retention of invalid snapshots.',
'c04':'Shift uses four readers versus ordinary two, making independent acknowledgment lag more likely.',
'c05':'Shift permits nested values of depth three versus ordinary depth two; typed scalar distinctions remain required.',
'c06':'Boundary has one resident slot; shift has two versus ordinary three, with write events weighted 3/7 instead of 1/5 to increase dirty pressure; dirty entries cannot be evicted.',
'c07':'Boundary uses independent leaves; shift uses six DAG nodes versus four with randomly sampled acyclic dependencies.',
'c08':'Boundary buffer length=3; shift length=5 versus ordinary 8, with incoming lengths and read/clear lengths 0..6 instead of 0..4, increasing overlap and out-of-range pressure.',
'dev-c01':'Boundary capacity=1 versus ordinary 3; shift capacity=2 and eight identities instead of four, with more pin and invalidation events under admission pressure.',
'dev-c02':'Boundary keeps one snapshot versus ordinary 2; shift keeps three and uses eight snapshot IDs instead of four, with longer histories and stale expected revisions.'}
for _task in TASKS:
    _task['specification'] += ' Generator regimes: '+_REGIME_NOTES[_task['id']]+' Adversarial traces add adjacent repeated events, capped at 48; those events obey the same contract.'



def make_case(task_id,regime,seed):
    if task_id not in _IDS or regime not in REGIMES:raise ValueError('unknown task/regime')
    r=rng_for(seed,'cache/'+task_id+'/'+regime);n=12 if regime=='ordinary' else 20;keys=list('abcd');small=regime in ('boundary','shift');shifted=regime=='shift'
    if task_id=='c01':
        config={'capacity':4 if shifted else 2 if small else 6};events=[{'type':'put','key':'a','value':1,'size':1,'ttl':2},{'type':'get','key':'a'},{'type':'advance','dt':2},{'type':'get','key':'a'}]
        for _ in range(n):
            op=r.choice(['put','put','get','advance']);e={'type':op}
            if op!='advance':e['key']=r.choice(keys)
            if op=='put':e.update(value=r.randint(-5,9),size=r.randint(1,4 if shifted else 5),ttl=r.randint(0,2 if shifted else 5))
            if op=='advance':e['dt']=r.randint(0,5 if shifted else 4)
            events.append(e)
    elif task_id=='c02':
        config={'ttl':4 if shifted else 2,'stale':2 if shifted else 0 if small else 3};events=[{'type':'get','key':'a'},{'type':'get','key':'a'},{'type':'resolve','key':'a','token':1,'value':7},{'type':'advance','dt':2},{'type':'get','key':'a'},{'type':'invalidate','key':'a'},{'type':'resolve','key':'a','token':2,'value':9},{'type':'get','key':'a'}]
        for _ in range(n):
            op=r.choice(['get','get','resolve','reject','invalidate','advance']);e={'type':op}
            if op=='advance':e['dt']=r.randint(0,7 if shifted else 5)
            else:e['key']=r.choice(keys)
            if op in ('resolve','reject'):e['token']=r.randint(1,10)
            if op=='resolve':e['value']=r.randint(0,20)
            events.append(e)
    elif task_id=='c03':
        config={'keep':2 if shifted else 1 if small else 3};events=[{'type':'save','id':'a','data':[1,2],'checksum':5},{'type':'save','id':'b','data':[3,4],'checksum':11},{'type':'damage','id':'b','index':0,'value':8},{'type':'restore'}]
        for _ in range(n):
            op=r.choice(['save','restore','damage','drop']);e={'type':op}
            if op!='restore':e['id']=r.choice(keys)
            if op=='save':
                data=[r.randint(0,20) for _ in range(r.randint(0,4))];checksum=sum((i+1)*v for i,v in enumerate(data))%251;e.update(data=data,checksum=checksum if r.random()<(.4 if shifted else .7) else (checksum+1)%251)
            if op=='damage':e.update(index=r.randint(0,4),value=r.randint(0,20))
            events.append(e)
    elif task_id=='c04':
        config={'readers':['a','b','c','d'] if regime=='shift' else ['a','b']};events=[{'type':'set','key':'a','value':1},{'type':'set','key':'a','value':2},{'type':'ack','reader':'a','seq':2},{'type':'compact'},{'type':'ack','reader':'b','seq':2},{'type':'compact'}];seq=2
        for _ in range(n):
            op=r.choice(['set','set','ack','compact']);e={'type':op}
            if op=='set':e.update(key=r.choice(keys),value=r.randint(-5,9));seq+=1
            if op=='ack':e.update(reader=r.choice(config['readers']),seq=r.randint(0,seq+2))
            events.append(e)
    elif task_id=='c05':
        config={};events=[{'type':'encode','value':{'b':None,'a':1}},{'type':'encode','value':{'a':1,'b':None}},{'type':'encode','value':{'a':'1'}},{'type':'encode','value':[True,1,None]}]
        def value(depth):
            if depth<=0:return r.choice([None,True,False,r.randint(-5,20),'λ\n"','é','🙂'])
            kind=r.randrange(3)
            if kind==0:return [value(depth-1) for _ in range(r.randint(0,3))]
            if kind==1:return {k:value(depth-1) for k in r.sample(keys,r.randint(0,4))}
            return value(0)
        events += [{'type':'encode','value':value(3 if regime=='shift' else 2)} for _ in range(n)]
    elif task_id=='c06':
        config={'slots':2 if shifted else 1 if small else 3};events=[{'type':'write','key':'a','value':1},{'type':'ack','key':'a','version':1},{'type':'flush','key':'a'},{'type':'write','key':'a','value':2},{'type':'ack','key':'a','version':1},{'type':'flush','key':'a'},{'type':'ack','key':'a','version':2},{'type':'evict','key':'a'},{'type':'read','key':'a'}]
        for _ in range(n):
            op=r.choice(['write','write','write','read','flush','ack','evict'] if shifted else ['write','read','flush','ack','evict']);e={'type':op,'key':r.choice(keys)}
            if op=='write':e['value']=r.randint(-2,10)
            if op=='ack':e['version']=r.randint(1,5)
            events.append(e)
    elif task_id=='c07':
        nodes=list('abcdef') if regime=='shift' else list('abcd');deps={k:r.sample(nodes[:i],r.randint(0,min(i,2))) for i,k in enumerate(nodes)}
        if regime=='boundary':deps={k:[] for k in nodes}
        config={'deps':deps,'values':{k:r.randint(-3,5) for k,p in deps.items() if not p}};events=[{'type':'evaluate','node':nodes[-1]},{'type':'evaluate','node':nodes[-1]},{'type':'set','node':nodes[0],'value':2},{'type':'evaluate','node':nodes[-1]}]
        for _ in range(n):
            e={'type':r.choice(['evaluate','evaluate','set']),'node':r.choice(nodes)}
            if e['type']=='set':e['value']=r.randint(-3,5)
            events.append(e)
    elif task_id=='c08':
        config={'length':5 if shifted else 3 if small else 8};events=[{'type':'put','start':0,'data':[1,2]},{'type':'put','start':1,'data':[9]},{'type':'read','start':0,'end':3},{'type':'clear','start':1,'end':2},{'type':'read','start':0,'end':2}]
        for _ in range(n):
            op=r.choice(['put','read','clear']);start=r.randint(-1,config['length']);e={'type':op,'start':start}
            if op=='put':e['data']=[r.randint(0,3) for _ in range(r.randint(0,6 if shifted else 4))]
            else:e['end']=start+r.randint(0,6 if shifted else 4)
            events.append(e)
    elif task_id=='dev-c01':
        config={'capacity':2 if shifted else 1 if regime=='boundary' else 3}
        events=[{'type':'put','key':'a','value':1},{'type':'pin','key':'a'},{'type':'pin','key':'a'},{'type':'invalidate','key':'a'},{'type':'get','key':'a'},{'type':'put','key':'a','value':2},{'type':'unpin','key':'a'},{'type':'unpin','key':'a'},{'type':'put','key':'a','value':3}]
        for _ in range(24 if regime=='ordinary' else 34):
            op=r.choice(['put','pin','pin','unpin','invalidate','invalidate','get'] if shifted else ['put','put','pin','unpin','invalidate','get']);e={'type':op,'key':r.choice('abcdefgh' if shifted else 'abcd')}
            if op=='put':e['value']=r.randint(-2,9)
            events.append(e)
    else:
        config={'keep':3 if shifted else 1 if regime=='boundary' else 2,'initial':r.randint(-3,5)}
        events=[{'type':'save','id':'a'},{'type':'write','expect':0,'value':9},{'type':'rollback','id':'a','expect':0},{'type':'rollback','id':'a','expect':1},{'type':'save','id':'b'},{'type':'drop','id':'a'},{'type':'save','id':'a'},{'type':'write','expect':2,'value':0},{'type':'rollback','id':'b','expect':3}]
        for _ in range(24 if regime=='ordinary' else 34):
            op=r.choice(['write','save','save','rollback','drop']);e={'type':op}
            if op in ('save','rollback','drop'):e['id']=r.choice('abcdefgh' if shifted else 'abcd')
            if op in ('write','rollback'):e['expect']=r.randint(0,12)
            if op=='write':e['value']=r.randint(-5,12)
            events.append(e)
    if regime=='adversarial':
        events=[cloned(e) for e in events for _ in range(2 if r.random()<.5 else 1)][:48]
    return {'config':config,'events':events}


def public_cases(task_id):return [dict(id='p'+str(i+1),**make_case(task_id,regime,201+i)) for i,regime in enumerate(REGIMES)]


def reference(task_id,case):
    case=_integer_json(case)
    c=case['config']; out=[];now=0;store={};order=[];pending={};next_token=1;log=[];seq=0;versions={};flushed=set();durable={};memo={};hits=[]
    if task_id=='c04':acks={k:0 for k in c['readers']};view={}
    if task_id=='c07':values=c['values'].copy()
    if task_id=='c08':cells=[None]*c['length']
    if task_id=='dev-c02':snapshot_value=c['initial'];snapshot_revision=0;used_snapshots=set()
    for e in case['events']:
        op=e['type'];value=None
        if task_id=='c01':
            if op=='advance':now+=e['dt']
            for k in order[:]:
                if store[k]['expires']<=now:order.remove(k);del store[k]
            if op=='put' and e['size']<=c['capacity']:
                if e['key'] in store:order.remove(e['key']);del store[e['key']]
                if e['ttl']>0:
                    while sum(v['size'] for v in store.values())+e['size']>c['capacity']:del store[order.pop(0)]
                    store[e['key']]={'value':e['value'],'size':e['size'],'expires':now+e['ttl']};order.append(e['key'])
            elif op=='get' and e['key'] in store:value=store[e['key']]['value'];order.remove(e['key']);order.append(e['key'])
            row=dict(value=value,keys=order[:],bytes=sum(v['size'] for v in store.values()),now=now)
        elif task_id=='c02':
            fetch=[];k=e.get('key')
            if op=='advance':now+=e['dt']
            elif op=='get':
                age=now-store[k]['time'] if k in store else None
                if age is not None and age<c['ttl']+c['stale']:value=store[k]['value']
                if (age is None or age>=c['ttl']) and k not in pending:pending[k]=next_token;fetch=[dict(key=k,token=next_token)];next_token+=1
            elif op=='invalidate':store.pop(k,None);pending.pop(k,None)
            elif pending.get(k)==e['token']:
                del pending[k]
                if op=='resolve':store[k]={'value':e['value'],'time':now}
            row=dict(value=value,fetch=fetch,pending=sorted(pending),now=now)
        elif task_id=='c03':
            data=None;chosen=None;k=e.get('id')
            if op=='save':
                if k in store:order.remove(k)
                store[k]=dict(data=e['data'][:],checksum=e['checksum']);order.append(k)
                while len(order)>c['keep']:del store[order.pop(0)]
            elif op=='damage' and k in store and 0<=e['index']<len(store[k]['data']):store[k]['data'][e['index']]=e['value']
            elif op=='drop':
                if k in store:del store[k];order.remove(k)
            elif op=='restore':
                for candidate in reversed(order):
                    item=store[candidate]
                    if sum((i+1)*v for i,v in enumerate(item['data']))%251==item['checksum']:chosen=candidate;data=item['data'][:];break
            row=dict(data=data,chosen=chosen,retained=order[:])
        elif task_id=='c04':
            if op=='set':seq+=1;log.append(dict(seq=seq,key=e['key'],value=e['value']));view[e['key']]=e['value']
            elif op=='ack' and acks[e['reader']]<=e['seq']<=seq:acks[e['reader']]=e['seq']
            elif op=='compact':
                water=min(acks.values());latest={}
                for item in log:
                    if item['seq']<=water:latest[item['key']]=item['seq']
                log=[item for item in log if item['seq']>water or latest.get(item['key'])==item['seq']]
            row=dict(log=[item['seq'] for item in log],view=view.copy())
        elif task_id=='c05':row={'key':json.dumps(e['value'],sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)}
        elif task_id=='c06':
            k=e['key'];status='ignored';flush=[]
            def space():
                if len(store)<c['slots']:return True
                victim=next((x for x in order if not store[x]['dirty']),None)
                if victim is None:return False
                order.remove(victim);del store[victim];return True
            if op=='write':
                if k in store or space():
                    if k in order:order.remove(k)
                    versions[k]=versions.get(k,0)+1;store[k]=dict(value=e['value'],version=versions[k],dirty=True);order.append(k);status='written'
                else:status='blocked'
            elif op=='read':
                if k in store:value=store[k]['value'];order.remove(k);order.append(k);status='hit'
                elif k in durable:
                    value=durable[k];status='durable'
                    if space():store[k]=dict(value=value,version=versions[k],dirty=False);order.append(k)
                else:status='miss'
            elif op=='flush' and k in store and store[k]['dirty']:
                flush=[dict(key=k,version=store[k]['version'],value=store[k]['value'])];flushed.add((k,store[k]['version']));status='flushed'
            elif op=='ack' and k in store and store[k]['dirty'] and store[k]['version']==e['version'] and (k,e['version']) in flushed:durable[k]=store[k]['value'];store[k]['dirty']=False;status='persisted'
            elif op=='evict':
                status='missing' if k not in store else 'blocked' if store[k]['dirty'] else 'evicted'
                if status=='evicted':del store[k];order.remove(k)
            row=dict(status=status,value=value,flush=flush,cached=order[:],dirty=sorted(k for k,v in store.items() if v['dirty']),durable=durable.copy())
        elif task_id=='c07':
            computed=0;k=e['node']
            if op=='set' and not c['deps'][k]:
                values[k]=e['value'];bad={k};changed=True
                while changed:
                    changed=False
                    for node,parents in c['deps'].items():
                        if node not in bad and any(p in bad for p in parents):bad.add(node);changed=True
                for node in bad:memo.pop(node,None)
            elif op=='evaluate':
                def get(node):
                    nonlocal computed
                    if node not in memo:
                        memo[node]=sum(get(p) for p in c['deps'][node]) if c['deps'][node] else values[node];computed+=1
                    return memo[node]
                value=get(k)
            row=dict(value=value,computed=computed,valid=sorted(memo))
        elif task_id=='c08':
            start=e['start'];data=None;missing=[]
            if op=='put':
                ok=0<=start<=c['length'] and start+len(e['data'])<=c['length'] and all(cells[start+i] in (None,v) for i,v in enumerate(e['data']))
                status='stored' if ok else 'invalid'
                if ok:cells[start:start+len(e['data'])]=e['data']
            elif not 0<=start<=e['end']<=c['length']:status='invalid'
            elif op=='clear':cells[start:e['end']]=[None]*(e['end']-start);status='cleared'
            else:
                chunk=cells[start:e['end']]
                if None not in chunk:data=chunk[:];status='complete'
                else:
                    status='incomplete';i=start
                    while i<e['end']:
                        if cells[i] is not None:i+=1;continue
                        end=i+1
                        while end<e['end'] and cells[end] is None:end+=1
                        missing.append([i,end]);i=end
            row=dict(status=status,data=data,missing=missing,known=sum(v is not None for v in cells))
        elif task_id=='dev-c01':
            k=e['key'];status='ignored'
            if op=='put':
                status='blocked'
                if k in store:
                    if not store[k]['deleted']:store[k]['value']=e['value'];status='stored'
                else:
                    if len(store)>=c['capacity']:
                        victim=next((x for x in order if store[x]['pins']==0),None)
                        if victim is not None:del store[victim];order.remove(victim)
                    if len(store)<c['capacity']:store[k]={'value':e['value'],'pins':0,'deleted':False};order.append(k);status='stored'
            elif op=='pin' and k in store and not store[k]['deleted']:store[k]['pins']+=1;status='pinned'
            elif op=='unpin' and k in store and store[k]['pins']>0:
                store[k]['pins']-=1;status='released'
                if store[k]['pins']==0 and store[k]['deleted']:del store[k];order.remove(k)
            elif op=='invalidate':
                status='missing'
                if k in store:
                    status='invalidated'
                    if store[k]['pins']:store[k]['deleted']=True
                    else:del store[k];order.remove(k)
            elif op=='get':
                status='miss'
                if k in store and not store[k]['deleted']:value=store[k]['value'];status='hit'
            row=dict(status=status,value=value,order=order[:],pins={x:store[x]['pins'] for x in order},tombstones=sorted(x for x in order if store[x]['deleted']))
        elif task_id=='dev-c02':
            k=e.get('id')
            if op=='save':
                status='exists' if k in used_snapshots else 'saved'
                if status=='saved':
                    used_snapshots.add(k);store[k]={'value':snapshot_value,'revision':snapshot_revision};order.append(k)
                    if len(order)>c['keep']:del store[order.pop(0)]
            elif op=='drop':
                status='dropped' if k in store else 'missing'
                if k in store:del store[k];order.remove(k)
            elif e['expect']!=snapshot_revision:status='conflict'
            elif op=='rollback' and k not in store:status='missing'
            else:snapshot_value=e['value'] if op=='write' else store[k]['value'];snapshot_revision+=1;status='written' if op=='write' else 'rolled_back'
            row=dict(status=status,value=snapshot_value,revision=snapshot_revision,snapshots=order[:],saved=cloned(store))
        else:raise ValueError(task_id)
        out.append(cloned(row))
    return out


def _audit(task_id,case):
    """Alternative representations: timestamp ranks, append histories and closures.

    These checks share the published semantics, not the reference implementation.
    They inspect observable outputs only; opaque solution state is never trusted.
    """
    case=_integer_json(case)
    c=case['config'];rows=[];clock=0;entries=[];active=[];serial=0;history=[];allowed=set();durable={};version={};valid=set();observed=[]
    if task_id=='c04':acknowledged={k:0 for k in c['readers']};kept=set()
    if task_id=='c07':
        leaves=c['values'].copy();ancestors={}
        def ancestry(k):
            if k not in ancestors:ancestors[k]={k}.union(*(ancestry(p) for p in c['deps'][k]))
            return ancestors[k]
        for k in c['deps']:ancestry(k)
    if task_id in ('c08','dev-c01'):known={}
    for step,e in enumerate(case['events']):
        op=e['type'];value=None
        if task_id=='c01':
            if op=='advance':clock+=e['dt']
            # (key,value,size,expiration,last-touch-rank), no explicit recency queue.
            entries=[x for x in entries if x[3]>clock]
            if op=='put' and e['size']<=c['capacity']:
                entries=[x for x in entries if x[0]!=e['key']]
                if e['ttl']:
                    candidates=sorted(entries,key=lambda x:x[4],reverse=True);fitting=[];used=e['size']
                    # Evict the oldest prefix; all newer entries must fit together.
                    for x in candidates:
                        if used+x[2]<=c['capacity']:fitting.append(x);used+=x[2]
                        else:break
                    entries=fitting+[(e['key'],e['value'],e['size'],clock+e['ttl'],step)]
            elif op=='get':
                match=next((x for x in entries if x[0]==e['key']),None)
                if match:value=match[1];entries=[x for x in entries if x[0]!=e['key']]+[(*match[:4],step)]
            row=dict(value=value,keys=[x[0] for x in sorted(entries,key=lambda x:x[4])],bytes=sum(x[2] for x in entries),now=clock)
        elif task_id=='c02':
            # Completed values and live request tuples are distinct ledgers.
            k=e.get('key');fetch=[]
            if op=='advance':clock+=e['dt']
            elif op=='get':
                stored=next((x for x in entries if x[0]==k),None)
                if stored and clock<stored[2]+c['ttl']+c['stale']:value=stored[1]
                if (stored is None or clock>=stored[2]+c['ttl']) and not any(x[0]==k for x in active):
                    serial+=1;active.append((k,serial));fetch=[dict(key=k,token=serial)]
            elif op=='invalidate':entries=[x for x in entries if x[0]!=k];active=[x for x in active if x[0]!=k]
            elif (k,e['token']) in active:
                active.remove((k,e['token']))
                if op=='resolve':entries=[x for x in entries if x[0]!=k]+[(k,e['value'],clock)]
            row=dict(value=value,fetch=fetch,pending=sorted(x[0] for x in active),now=clock)
        elif task_id=='c03':
            k=e.get('id');data=None;chosen=None
            if op=='save':entries=([x for x in entries if x[0]!=k]+[(k,tuple(e['data']),e['checksum'])])[-c['keep']:]
            elif op=='drop':entries=[x for x in entries if x[0]!=k]
            elif op=='damage':
                entries=[(a,tuple(e['value'] if j==e['index'] else b for j,b in enumerate(v)),s) if a==k else (a,v,s) for a,v,s in entries]
            elif op=='restore':
                eligible=[]
                for a,v,s in entries:
                    residue=0
                    for multiplier,byte in zip(range(1,len(v)+1),v):residue=(residue+multiplier*byte)%251
                    if residue==s:eligible.append((a,v))
                if eligible:chosen=eligible[-1][0];data=list(eligible[-1][1])
            row=dict(data=data,chosen=chosen,retained=[x[0] for x in entries])
        elif task_id=='c04':
            if op=='set':history.append((e['key'],e['value']));kept.add(len(history))
            elif op=='ack':
                r=e['reader'];candidate=e['seq']
                if acknowledged[r]<=candidate<=len(history):acknowledged[r]=candidate
            elif op=='compact':
                w=min(acknowledged.values());obsolete=set()
                for i in kept:
                    if i<=w and any(j>i and j<=w and history[j-1][0]==history[i-1][0] for j in kept):obsolete.add(i)
                kept-=obsolete
            row=dict(log=sorted(kept),view={k:v for k,v in history})
        elif task_id=='c05':
            def canonical(v):
                if v is None:return 'null'
                if type(v) is bool:return 'true' if v else 'false'
                if type(v) is int:return str(v)
                if isinstance(v,str):return json.dumps(v,ensure_ascii=False)
                if isinstance(v,list):return '['+','.join(map(canonical,v))+']'
                return '{'+','.join(json.dumps(k)+':'+canonical(v[k]) for k in sorted(v))+'}'
            row={'key':canonical(e['value'])}
        elif task_id=='c06':
            # Resident tuples (key,value,version,dirty,touch), plus flush authority.
            k=e['key'];existing=next((x for x in entries if x[0]==k),None);status='ignored';flush=[]
            if op in ('write','read'):
                promote=op=='write' or existing is None and k in durable
                room=True
                if promote and existing is None and len(entries)==c['slots']:
                    clean=sorted((x for x in entries if not x[3]),key=lambda x:x[4])
                    room=bool(clean)
                    if room:entries.remove(clean[0])
                if op=='write':
                    status='written' if room else 'blocked'
                    if room:
                        version[k]=version.get(k,0)+1;entries=[x for x in entries if x[0]!=k]+[(k,e['value'],version[k],True,step)]
                elif existing:
                    value=existing[1];status='hit';entries=[x for x in entries if x[0]!=k]+[(*existing[:4],step)]
                elif k in durable:
                    value=durable[k];status='durable'
                    if room:entries.append((k,value,version[k],False,step))
                else:status='miss'
            elif op=='flush' and existing and existing[3]:
                flush=[dict(key=k,version=existing[2],value=existing[1])];allowed.add((k,existing[2]));status='flushed'
            elif op=='ack' and existing and existing[3] and existing[2]==e['version'] and (k,e['version']) in allowed:
                durable[k]=existing[1];entries=[(x[0],x[1],x[2],False,x[4]) if x[0]==k else x for x in entries];status='persisted'
            elif op=='evict':
                status='missing' if existing is None else 'blocked' if existing[3] else 'evicted'
                if status=='evicted':entries.remove(existing)
            row=dict(status=status,value=value,flush=flush,cached=[x[0] for x in sorted(entries,key=lambda x:x[4])],dirty=sorted(x[0] for x in entries if x[3]),durable=durable.copy())
        elif task_id=='c07':
            k=e['node'];computed=0
            if op=='set' and not c['deps'][k]:leaves[k]=e['value'];valid={x for x in valid if k not in ancestors[x]}
            elif op=='evaluate':
                computed=len(ancestors[k]-valid);valid|=ancestors[k]
                def total(node):return sum(total(p) for p in c['deps'][node]) if c['deps'][node] else leaves[node]
                value=total(k)
            row=dict(value=value,computed=computed,valid=sorted(valid))
        elif task_id=='c08':
            start=e['start'];data=None;missing=[]
            end=start+len(e['data']) if op=='put' else e['end'];legal=0<=start<=end<=c['length']
            if op=='put':
                incoming=dict(zip(range(start,end),e['data']))
                legal=legal and all(i not in known or known[i]==v for i,v in incoming.items())
                if legal:known.update(incoming)
                status='stored' if legal else 'invalid'
            elif not legal:status='invalid'
            elif op=='clear':
                known={i:v for i,v in known.items() if not start<=i<end};status='cleared'
            else:
                absent=[i for i in range(start,end) if i not in known];status='incomplete' if absent else 'complete'
                if absent:
                    first=last=absent[0]
                    for i in absent[1:]:
                        if i!=last+1:missing.append([first,last+1]);first=i
                        last=i
                    missing.append([first,last+1])
                else:data=[known[i] for i in range(start,end)]
            row=dict(status=status,data=data,missing=missing,known=len(known))
        elif task_id=='dev-c01':
            k=e['key'];found=next((x for x in entries if x[0]==k),None);status='ignored'
            # (key,value,pin-count,tombstone,first-insertion-rank); reads never rank.
            if op=='put':
                status='blocked'
                if found and not found[3]:entries=[(k,e['value'],*x[2:]) if x[0]==k else x for x in entries];status='stored'
                elif found is None:
                    free=sorted((x for x in entries if x[2]==0),key=lambda x:x[4])
                    if len(entries)==c['capacity'] and free:entries.remove(free[0])
                    if len(entries)<c['capacity']:entries.append((k,e['value'],0,False,step));status='stored'
            elif op=='pin' and found and not found[3]:entries=[(x[0],x[1],x[2]+1,x[3],x[4]) if x[0]==k else x for x in entries];status='pinned'
            elif op=='unpin' and found and found[2]>0:
                status='released';entries=[(x[0],x[1],x[2]-1,x[3],x[4]) if x[0]==k else x for x in entries if x[0]!=k or not (x[2]==1 and x[3])]
            elif op=='invalidate':
                status='invalidated' if found else 'missing'
                entries=[(x[0],x[1],x[2],True,x[4]) if x[0]==k else x for x in entries if x[0]!=k or x[2]>0]
            elif op=='get':
                status='hit' if found and not found[3] else 'miss'
                if status=='hit':value=found[1]
            ordered=sorted(entries,key=lambda x:x[4])
            row=dict(status=status,value=value,order=[x[0] for x in ordered],pins={x[0]:x[2] for x in entries},tombstones=sorted(x[0] for x in entries if x[3]))
        elif task_id=='dev-c02':
            current=history[-1] if history else c['initial'];k=e.get('id')
            if op=='save':
                status='exists' if k in allowed else 'saved'
                if status=='saved':allowed.add(k);entries=(entries+[(k,current,len(history))])[-c['keep']:]
            elif op=='drop':
                status='dropped' if any(x[0]==k for x in entries) else 'missing';entries=[x for x in entries if x[0]!=k]
            elif e['expect']!=len(history):status='conflict'
            elif op=='write':history.append(e['value']);status='written'
            else:
                saved=next((x for x in entries if x[0]==k),None);status='rolled_back' if saved else 'missing'
                if saved:history.append(saved[1])
            row=dict(status=status,value=history[-1] if history else c['initial'],revision=len(history),snapshots=[x[0] for x in entries],saved={x[0]:dict(value=x[1],revision=x[2]) for x in entries})
        else:raise ValueError(task_id)
        rows.append(cloned(row))
    return rows


def check(task_id,case,outputs):
    errors=check_count(case,outputs)
    if errors:return result(errors)
    expected=_audit(task_id,case)
    for i,(want,got) in enumerate(zip(expected,outputs)):
        try:
            # JSON textual types distinguish bool/int, null/missing, and reject NaN.
            equal=json.dumps(want,sort_keys=True,ensure_ascii=False,allow_nan=False)==json.dumps(_integer_json(got),sort_keys=True,ensure_ascii=False,allow_nan=False)
        except (TypeError,ValueError):equal=False
        if not equal:errors.append('event_'+str(i)+':output_contract')
    return result(errors)


_JS={
'c01':'''state ??= {now:0,items:{},order:[]}; const s=state,e=event,c=config; let value=null;
const drop=k=>{delete s.items[k];s.order=s.order.filter(x=>x!==k)};
if(e.type==='advance')s.now+=e.dt;for(const k of [...s.order])if(s.items[k].expires<=s.now)drop(k);
if(e.type==='put'&&e.size<=c.capacity){drop(e.key);if(e.ttl>0){while(s.order.reduce((a,k)=>a+s.items[k].size,0)+e.size>c.capacity)drop(s.order[0]);s.items[e.key]={value:e.value,size:e.size,expires:s.now+e.ttl};s.order.push(e.key)}}
else if(e.type==='get'&&s.items[e.key]){value=s.items[e.key].value;s.order=s.order.filter(k=>k!==e.key);s.order.push(e.key)}
return {state:s,output:{value,keys:[...s.order],bytes:s.order.reduce((a,k)=>a+s.items[k].size,0),now:s.now}};''',
'c02':'''state ??= {now:0,cache:{},pending:{},next:1};const s=state,e=event,k=e.key;let value=null,fetch=[];
if(e.type==='advance')s.now+=e.dt;else if(e.type==='get'){const item=s.cache[k],age=item?s.now-item.time:null;if(item&&age<config.ttl+config.stale)value=item.value;if((!item||age>=config.ttl)&&s.pending[k]===undefined){s.pending[k]=s.next++;fetch=[{key:k,token:s.pending[k]}]}}
else if(e.type==='invalidate'){delete s.cache[k];delete s.pending[k]}else if(s.pending[k]===e.token){delete s.pending[k];if(e.type==='resolve')s.cache[k]={value:e.value,time:s.now}}
return {state:s,output:{value,fetch,pending:Object.keys(s.pending).sort(),now:s.now}};''',
'c03':'''state ??= {items:{},order:[]};const s=state,e=event,k=e.id;let data=null,chosen=null;
const drop=k=>{delete s.items[k];s.order=s.order.filter(x=>x!==k)};
if(e.type==='save'){drop(k);s.items[k]={data:[...e.data],checksum:e.checksum};s.order.push(k);while(s.order.length>config.keep)drop(s.order[0])}
else if(e.type==='damage'){let v=s.items[k];if(v&&e.index>=0&&e.index<v.data.length)v.data[e.index]=e.value}
else if(e.type==='drop')drop(k);else if(e.type==='restore'){for(const id of [...s.order].reverse()){let v=s.items[id];if(v.data.reduce((a,b,i)=>(a+(i+1)*b)%251,0)===v.checksum){chosen=id;data=[...v.data];break}}}
return {state:s,output:{data,chosen,retained:[...s.order]}};''',
'c04':'''state ??= {seq:0,log:[],view:{},acks:Object.fromEntries(config.readers.map(k=>[k,0]))};const s=state,e=event;
if(e.type==='set'){s.seq++;s.log.push({seq:s.seq,key:e.key,value:e.value});s.view[e.key]=e.value}
else if(e.type==='ack'){if(e.seq>=s.acks[e.reader]&&e.seq<=s.seq)s.acks[e.reader]=e.seq}
else if(e.type==='compact'){const water=Math.min(...Object.values(s.acks)),latest={};for(const x of s.log)if(x.seq<=water)latest[x.key]=x.seq;s.log=s.log.filter(x=>x.seq>water||latest[x.key]===x.seq)}
return {state:s,output:{log:s.log.map(x=>x.seq),view:{...s.view}}};''',
'c05':'''function canonical(v){if(v===null||typeof v!=='object')return JSON.stringify(v);if(Array.isArray(v))return '['+v.map(canonical).join(',')+']';return '{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}'}
return {state:null,output:{key:canonical(event.value)}};''',
'c06':'''state ??= {items:{},order:[],durable:{},versions:{},flushed:{}};const s=state,e=event,k=e.key;let value=null,flush=[],status='ignored';
const has=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);const drop=k=>{delete s.items[k];s.order=s.order.filter(x=>x!==k)};const touch=k=>{s.order=s.order.filter(x=>x!==k);s.order.push(k)};
function space(){if(s.order.length<config.slots)return true;const victim=s.order.find(x=>!s.items[x].dirty);if(victim===undefined)return false;drop(victim);return true}
if(e.type==='write'){if(has(s.items,k)||space()){s.versions[k]=(s.versions[k]||0)+1;s.items[k]={value:e.value,version:s.versions[k],dirty:true};touch(k);status='written'}else status='blocked'}
else if(e.type==='read'){if(has(s.items,k)){value=s.items[k].value;status='hit';touch(k)}else if(has(s.durable,k)){value=s.durable[k];status='durable';if(space()){s.items[k]={value,version:s.versions[k],dirty:false};touch(k)}}else status='miss'}
else if(e.type==='flush'&&s.items[k]?.dirty){const x=s.items[k];flush=[{key:k,version:x.version,value:x.value}];s.flushed[k+':'+x.version]=true;status='flushed'}
else if(e.type==='ack'&&s.items[k]?.dirty&&s.items[k].version===e.version&&s.flushed[k+':'+e.version]){s.durable[k]=s.items[k].value;s.items[k].dirty=false;status='persisted'}
else if(e.type==='evict'){status=!has(s.items,k)?'missing':s.items[k].dirty?'blocked':'evicted';if(status==='evicted')drop(k)}
return {state:s,output:{status,value,flush,cached:[...s.order],dirty:Object.keys(s.items).filter(k=>s.items[k].dirty).sort(),durable:{...s.durable}}};''',
'c07':'''state ??= {values:{...config.values},memo:{}};const s=state,e=event,k=e.node;let value=null,computed=0;const has=k=>Object.prototype.hasOwnProperty.call(s.memo,k);
if(e.type==='set'&&!config.deps[k].length){s.values[k]=e.value;let bad=new Set([k]),changed=true;while(changed){changed=false;for(const [node,parents] of Object.entries(config.deps))if(!bad.has(node)&&parents.some(p=>bad.has(p))){bad.add(node);changed=true}}for(const node of bad)delete s.memo[node]}
else if(e.type==='evaluate'){function get(node){if(!has(node)){s.memo[node]=config.deps[node].length?config.deps[node].reduce((a,p)=>a+get(p),0):s.values[node];computed++}return s.memo[node]}value=get(k)}
return {state:s,output:{value,computed,valid:Object.keys(s.memo).sort()}};''',
'c08':'''state ??= {cells:Array(config.length).fill(null)};const s=state,e=event,a=e.start;let data=null,missing=[],status;const end=e.type==='put'?a+e.data.length:e.end;let legal=a>=0&&a<=end&&end<=config.length;
if(e.type==='put'){legal=legal&&e.data.every((v,i)=>s.cells[a+i]===null||s.cells[a+i]===v);status=legal?'stored':'invalid';if(legal)e.data.forEach((v,i)=>s.cells[a+i]=v)}
else if(!legal)status='invalid';else if(e.type==='clear'){for(let i=a;i<end;i++)s.cells[i]=null;status='cleared'}
else{const chunk=s.cells.slice(a,end);if(chunk.every(v=>v!==null)){data=chunk;status='complete'}else{status='incomplete';for(let i=a;i<end;){if(s.cells[i]!==null){i++;continue}let j=i+1;while(j<end&&s.cells[j]===null)j++;missing.push([i,j]);i=j}}}
return {state:s,output:{status,data,missing,known:s.cells.filter(v=>v!==null).length}};''',
'dev-c01':'''state ??= {items:{},order:[]};const s=state,e=event,k=e.key;let value=null,status='ignored';const drop=k=>{delete s.items[k];s.order=s.order.filter(x=>x!==k)};
if(e.type==='put'){status='blocked';if(s.items[k]){if(!s.items[k].deleted){s.items[k].value=e.value;status='stored'}}else{if(s.order.length>=config.capacity){const victim=s.order.find(x=>s.items[x].pins===0);if(victim!==undefined)drop(victim)}if(s.order.length<config.capacity){s.items[k]={value:e.value,pins:0,deleted:false};s.order.push(k);status='stored'}}}
else if(e.type==='pin'&&s.items[k]&&!s.items[k].deleted){s.items[k].pins++;status='pinned'}else if(e.type==='unpin'&&s.items[k]?.pins>0){s.items[k].pins--;status='released';if(s.items[k].pins===0&&s.items[k].deleted)drop(k)}
else if(e.type==='invalidate'){status=s.items[k]?'invalidated':'missing';if(s.items[k]){if(s.items[k].pins)s.items[k].deleted=true;else drop(k)}}else if(e.type==='get'){status=s.items[k]&&!s.items[k].deleted?'hit':'miss';if(status==='hit')value=s.items[k].value}
return {state:s,output:{status,value,order:[...s.order],pins:Object.fromEntries(s.order.map(x=>[x,s.items[x].pins])),tombstones:s.order.filter(x=>s.items[x].deleted).sort()}};''',
'dev-c02':'''state ??= {value:config.initial,revision:0,used:[],saved:{},order:[]};const s=state,e=event,k=e.id;let status;
if(e.type==='save'){status=s.used.includes(k)?'exists':'saved';if(status==='saved'){s.used.push(k);s.saved[k]={value:s.value,revision:s.revision};s.order.push(k);if(s.order.length>config.keep)delete s.saved[s.order.shift()]}}
else if(e.type==='drop'){status=s.saved[k]?'dropped':'missing';delete s.saved[k];s.order=s.order.filter(x=>x!==k)}else if(e.expect!==s.revision)status='conflict';else if(e.type==='rollback'&&!s.saved[k])status='missing';else{s.value=e.type==='write'?e.value:s.saved[k].value;s.revision++;status=e.type==='write'?'written':'rolled_back'}
return {state:s,output:{status,value:s.value,revision:s.revision,snapshots:[...s.order],saved:{...s.saved}}};'''
}


def reference_source(task_id):return 'function solve({config,state,event}) {\n'+_JS[task_id]+'\n}'


def fault_cases(task_id):
    """Observable semantic faults at concrete public boundaries, not empty programs."""
    case=public_cases(task_id)[0];correct=reference(task_id,case);faults=[]
    edits={
      'c01':[('read_does_not_return_value',1,'value',None),('expiry_equality_retains_entry',2,'keys',['a']),('bytes_ignore_inserted_size',0,'bytes',0)],
      'c02':[('duplicate_inflight_fetch',1,'fetch',[{'key':'a','token':2}]),('stale_reply_after_invalidation',6,'pending',['a']),('ttl_equality_skips_refresh',4,'fetch',[])],
      'c03':[('restore_chooses_corrupt_newest',3,'chosen','b'),('restore_returns_damaged_data',3,'data',[8,4]),('save_does_not_retain_snapshot',0,'retained',[])],
      'c04':[('drop_unacknowledged_history',3,'log',[2]),('compaction_keeps_obsolete_write',5,'log',[1,2]),('visible_value_regresses',1,'view',{'a':1})],
      'c05':[('object_key_order_not_canonical',0,'key','{"b":null,"a":1}'),('string_number_coercion',2,'key','{"a":1}'),('boolean_numeric_coercion',3,'key','[1,1,null]')],
      'c06':[('ack_without_flush_persists',1,'durable',{'a':1}),('stale_ack_cleans_new_write',4,'dirty',[]),('flush_omits_current_version',5,'flush',[{'key':'a','version':1,'value':2}])],
      'c07':[('memo_hit_recomputes',1,'computed',1),('evaluation_does_not_memoize',0,'valid',[]),('set_returns_a_value',2,'value',2)],
      'c08':[('conflicting_put_accepted',1,'status','stored'),('partial_read_marked_complete',2,'status','complete'),('clear_does_not_remove_byte',3,'known',2)],
      'dev-c01':[('invalidation_drops_pinned_resident',3,'order',[]),('tombstone_remains_readable',4,'value',1),('first_unpin_removes_tombstone',6,'order',[])],
      'dev-c02':[('stale_rollback_changes_value',2,'value',case['config'].get('initial')),('rollback_resets_revision',3,'revision',0),('dropped_snapshot_id_reused',6,'status','saved')]
    }[task_id]
    for name,index,field,value in edits:
        outputs=cloned(correct);outputs[index][field]=value;faults.append(dict(name=name,case=cloned(case),outputs=outputs))
    return faults
