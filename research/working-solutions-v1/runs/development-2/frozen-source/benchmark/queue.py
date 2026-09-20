"""Scheduling contracts. No donor information participates in these task oracles."""
import json
import math
from fractions import Fraction
from .common import cloned, rng_for, result, check_count, REGIMES


def _integer_json(value):
    """JSON has numeric values, not separate integer/float spelling types."""
    if type(value) in (int, float):
        if abs(value)>9007199254740991 or not math.isfinite(value) or int(value)!=value:
            raise ValueError('Expected a finite safe integer JSON number')
        return int(value)
    if isinstance(value, list):return [_integer_json(x) for x in value]
    if isinstance(value, dict):return {k:_integer_json(v) for k,v in value.items()}
    return value

_COMMON = (' Implement pure solve({config,state,event})->{state,output}; initial state is null. '
           'Only the current event is available; each named event uses a type field, e.g. {type:"run"}. Inputs have at most eight single lowercase ASCII-letter identifiers, safe integer quantities and at most 48 events. '
           'Return exactly the documented output fields after every event; state representation is unrestricted JSON. '
           'All identifiers and numeric fields shown in event forms are present; quantities and all intermediate arithmetic are safe integers. '
           'Integral JSON number spellings such as 1 and 1.0 are equivalent; booleans remain distinct from numbers. '
           'Regimes vary event order and timing: ordinary uses moderate capacity, boundary tests equality/empty cases, '
           'adversarial repeats stale/conflicting events, and shift uses smaller capacities or larger costs/delays within the same semantics.')
_DEFS = [
('q01','Expiring bounded work queue','capacity conservation deadlines ordering',
 'Config capacity>=1. Start now=0 and empty jobs. Events: add{id,size>0,deadline>=0}, cancel{id}, advance{dt>=0}, run. Advance adds dt; before processing any other event remove jobs with deadline<=now (also remove immediately after advance). Add succeeds only if id is not currently queued, deadline>now and total size+size<=capacity; otherwise status=rejected. Accepted add status=accepted. Cancel removes current id with status=cancelled, absent id=missing. Run takes the job with smallest deadline, breaking ties by earlier accepted insertion, with status=ran; empty run status=empty. Advance status=advanced. IDs may be reused after removal. Output {status,ran:id_or_null,pending:[ids in insertion order],bytes:sum_size,now}. Expiry never counts as ran.'),
('q02','Weighted cyclic dispatch','fairness ordering capacity identity',
 'Config weights maps tenant IDs to positive integers. Build a fixed slot cycle by sorted tenant ID, repeating each tenant weight times. Start cursor=0 and empty per-tenant FIFO queues. Events add{tenant,id}, dispatch. Add rejects an id already pending in any tenant (status=duplicate); otherwise queues it (status=queued). Dispatch scans at most one cycle starting at cursor, takes the first nonempty tenant FIFO item, then sets cursor to the slot after that chosen slot modulo cycle length (status=sent). If all queues empty status=empty and cursor stays unchanged. Output {status,sent:id_or_null,queues:{every tenant:[pending IDs]},cursor}. Tenants always exist in config.'),
('q03','Age-bounded keyed batching','aggregation deadlines identity capacity',
 'Config limit>=1,delay>=1,required:boolean. Start time=0 and no pending keys. Events put{key,value}, cancel{key}, advance{dt>=0}, flush. Put stores/replaces the latest value for a key; replacement retains its first pending time. With required=true each put emits immediately and nothing is queued. Otherwise put flushes all pending keys when distinct-key count>=limit. Advance increases time and flushes all when any first pending age>=delay. Flush explicitly emits all; cancel silently removes only that key. Emission order is lexical key order. Output {emitted:[{key,value}],pending:[lexically sorted keys],now}. All emissions drain those keys. Values are safe integers.'),
('q04','Atomic staged resource ownership','isolation identity recovery ordering',
 'Config resources is a list of unique resource IDs. Events begin{id,resources}, prepare{id}, commit{id}, abort{id}; begin resource list is nonempty unique and drawn from config. Jobs are never reused once begun. Begin succeeds only for unseen id and all requested resources free, status=begun; otherwise blocked. Prepare changes active->prepared (prepared); any other phase=invalid. Commit only prepared jobs, releases all resources, records done (committed); otherwise invalid. Abort only active/prepared jobs, releases resources, records aborted (aborted); otherwise invalid. Output {status,held:{owned_resource:job_id},done:[sorted committed IDs]}. A blocked begin does not consume the ID; an aborted ID remains used.'),
('q05','Capacity interval reservations','capacity conservation ordering reversibility',
 'Config capacity>=1. Events reserve{id,start,end,units},cancel{id}. A reservation is valid only for a currently unused id, integers 0<=start<end and 1<=units<=capacity, and summed units<=capacity at every instant. Intervals are half-open [start,end). Successful reserve status=reserved; otherwise rejected without changing state. Cancel removes a current id with cancelled, else missing. Removed IDs may be reused. Output {status,active:[sorted reservation IDs],units:sum of units of active reservations (not peak occupancy)}. All endpoints are <=100.'),
('q06','Fractional rate credit accounting','capacity conservation identity ordering',
 'Config capacity>=1,rate>=1,denom>=1. Start credits=capacity,carry=0, no accepted reservation IDs. advance{dt>=0}: n=carry+dt*rate, credits=min(capacity,credits+floor(n/denom)),carry=n%denom,status=advanced. take{id,cost>0}: succeeds if id never accepted and cost<=credits, debits cost and records it (taken), else rejected. refund{id}: restores an accepted not-yet-refunded cost capped at capacity (refunded); unknown/already refunded=ignored. Refund never changes carry. IDs remain consumed after refund. Output {status,credits,carry}.'),
('q07','Bounded retry lifecycle','deadlines identity recovery ordering',
 'Config attempts>=1,delay>=1. Start now=0,phase=idle,id=null,attempt=0,due=null. start{id}: while pending/waiting status=busy; otherwise starts a new job attempt=1,phase=pending, emits {id,attempt:1}, status=started. IDs may be reused after terminal states. fail{id,attempt,after>=0}: only matching current pending attempt counts; if attempt>=attempts set phase=failed,due=null; else phase=waiting,due=now+max(delay,after); status=failed or waiting. success{id,attempt}: matching pending attempt sets succeeded,due=null,status=succeeded. cancel: active pending/waiting->cancelled,due=null,status=cancelled, otherwise ignored. advance{dt>=0}: add dt; if waiting and now>=due increment attempt once,phase=pending,due=null,emit current attempt; status=advanced. Every stale/nonmatching response status=ignored. Output {status,phase,id,attempt,due,now,send:[{id,attempt}]}.'),
('q08','Dependency completion propagation','causality propagation ordering recovery',
 'Config deps maps unique nodes to prerequisite-node lists and is a finite acyclic graph; IDs in deps always exist. Initially all nodes pending. Events poll,ok{id},fail{id}. A matching running node changes to done or failed; all other completion events are ignored. After each event, mark pending nodes blocked if any prerequisite is failed or blocked, transitively; then start every pending node whose prerequisites are all done, simultaneously in lexical order. Roots therefore start after the first event, not before it. Output {started:[newly started IDs in lexical order],states:{every node:pending|running|done|failed|blocked}}. No hidden cycle or undefined-node requirement exists.'),
('dev-q01','Development aging partial-service scheduler','fairness capacity ordering conservation',
 'Config capacity>=1,quantum>=1,ceiling>=1. Start now=0 and no jobs. add{id,work>=1,priority:0..ceiling} queues an unused pending ID if fewer than capacity jobs exist (queued), otherwise rejected. IDs may be reused after removal. Effective priority=min(ceiling,initial_priority+floor((now-arrival_time)/quantum)). advance{dt>=0} changes now (advanced); it never services jobs. run{budget>=0} selects highest effective priority, ties by earlier accepted insertion. Service ONLY that job by min(budget,remaining_work), output one served record; remove it exactly when remaining work reaches zero, otherwise retain its original arrival and insertion rank. Budget left after completion is discarded. Run status=served, or empty with no jobs. cancel{id} removes a pending job (cancelled), otherwise missing. Output {status,served:[{id,units,complete:boolean}],pending:[insertion-order IDs],remaining:{pending_id:work},priorities:{pending_id:effective_priority},now}. Non-run served=[]. No deadline expiry or automatic dispatch exists.'),
('dev-q02','Development fenced renewable lease','identity deadlines isolation recovery',
 'Config ttl>=1. Start now=0,owner=null,generation=0,expires=null. advance{dt>=0} first increases now. Before every operation, expire an active lease when expires<=now, clearing owner/expires but preserving generation. acquire{owner} succeeds only while vacant: increment generation, set owner and expires=now+ttl (acquired); otherwise busy even for the same owner. renew{owner,generation} only for matching active owner and generation resets expires=now+ttl (renewed); release{owner,generation} only for that same match clears owner/expires (released). Nonmatching/expired renew and release are ignored. Advance status=advanced. Output {status,owner:id_or_null,generation:latest_issued_generation,expires:time_or_null,now}. Generations never reset or get reused; release after expiry cannot release a new lease. Renew is replacement from current time, not extension from the old expiration.')]
TASKS=[dict(id=i,family='queue',split='development' if i.startswith('dev-') else 'main',title=t,tags=tags.split(),specification=spec+_COMMON) for i,t,tags,spec in _DEFS]
_IDS={t['id'] for t in TASKS}

_REGIME_NOTES={
'q01':'Boundary capacity=2; shift capacity=4 versus ordinary 7, sizes 2..6 instead of 1..5, deadline gaps 0..2 instead of 0..5, and clock steps 0..5 instead of 0..3.',
'q02':'Boundary weights are a:1,b:3,c:1; shift weights a:2,b:1,c:3 replace ordinary a:1,b:2,c:1, with eight job IDs and 70% add events instead of four IDs and 50%.',
'q03':'Boundary limit=2 versus ordinary 3; shift enables required delivery, disabling aggregation.',
'q04':'Shift reduces the resource universe from three to two, increasing shared-resource contention.',
'q05':'Boundary capacity=1; shift capacity=2 versus ordinary 3, starts 0..4 instead of 0..8, durations 1..6 instead of 0..4 and units 1..3 instead of 1..4, increasing overlap.',
'q06':'Boundary capacity=2; shift capacity=4,rate=3,denom=7 versus ordinary capacity=7,rate=2,denom=3, with clock steps 0..3 instead of 0..5 and costs 1..6 instead of 1..8.',
'q07':'Shift permits one attempt versus ordinary 3, requiring immediate terminal failure; timing still applies to other regimes.',
'q08':'Boundary uses independent roots; shift uses six nodes versus four with randomly sampled acyclic dependencies.',
'dev-q01':'Boundary uses capacity=1,quantum=1; ordinary capacity=3,quantum=3; shift capacity=2,quantum=2 with work up to 12 instead of 6 and clock gaps up to 6 instead of 3. Ceiling=3 throughout.',
'dev-q02':'Boundary ttl=1 versus ordinary 3; shift ttl=5 and clock gaps 0..7 instead of 0..3, mixing early renewal and expiry with stale generations.'}
for _task in TASKS:
    _task['specification'] += ' Generator regimes: '+_REGIME_NOTES[_task['id']]+' Adversarial traces add adjacent repeated events, capped at 48; those events obey the same contract.'



def make_case(task_id, regime, seed):
    if task_id not in _IDS or regime not in REGIMES: raise ValueError('unknown task/regime')
    r=rng_for(seed, 'queue/'+task_id+'/'+regime); n=12 if regime=='ordinary' else 20
    ids=list('abcdefgh') if task_id=='q02' and regime=='shift' else list('abcd'); small=regime in ('shift','boundary'); shifted=regime=='shift'
    if task_id=='q01':
        config={'capacity':4 if shifted else 2 if small else 7}; events=[{'type':'add','id':'a','size':1,'deadline':2},{'type':'add','id':'b','size':2,'deadline':2},{'type':'run'},{'type':'advance','dt':2}]
        now=2
        for _ in range(n):
            op=r.choice(['add','add','cancel','run','advance']); e={'type':op}
            if op=='add':e.update(id=r.choice(ids),size=r.randint(2,6) if shifted else r.randint(1,5),deadline=now+r.randint(0,2 if shifted else 5))
            if op=='cancel':e['id']=r.choice(ids)
            if op=='advance':e['dt']=r.randint(0,5 if shifted else 3);now+=e['dt']
            events.append(e)
    elif task_id=='q02':
        config={'weights':{'a':2,'b':1,'c':3} if shifted else {'a':1,'b':3 if small else 2,'c':1}};events=[{'type':'add','tenant':'b','id':'a'},{'type':'add','tenant':'b','id':'a'},{'type':'dispatch'}]
        for _ in range(n):events.append({'type':'dispatch'} if r.random()<(.3 if shifted else .5) else {'type':'add','tenant':r.choice('abc'),'id':r.choice(ids)})
    elif task_id=='q03':
        config={'limit':2 if small else 3,'delay':2,'required':regime=='shift'};events=[{'type':'put','key':'a','value':1},{'type':'advance','dt':1},{'type':'put','key':'a','value':2},{'type':'advance','dt':1}]
        for _ in range(n):
            op=r.choice(['put','put','cancel','advance','flush']);e={'type':op}
            if op=='put':e.update(key=r.choice(ids),value=r.randint(-3,8))
            if op=='cancel':e['key']=r.choice(ids)
            if op=='advance':e['dt']=r.randint(0,4)
            events.append(e)
    elif task_id=='q04':
        config={'resources':['x','y'] if regime=='shift' else ['x','y','z']};events=[{'type':'begin','id':'a','resources':['x','y']},{'type':'begin','id':'b','resources':['y']},{'type':'commit','id':'a'},{'type':'prepare','id':'a'},{'type':'commit','id':'a'},{'type':'begin','id':'b','resources':['y']}]
        for _ in range(n):
            op=r.choice(['begin','prepare','commit','abort']);e={'type':op,'id':r.choice(ids)}
            if op=='begin':e['resources']=r.sample(config['resources'],r.randint(1,len(config['resources'])))
            events.append(e)
    elif task_id=='q05':
        config={'capacity':2 if shifted else 1 if small else 3};events=[{'type':'reserve','id':'a','start':0,'end':2,'units':1},{'type':'reserve','id':'b','start':2,'end':4,'units':1},{'type':'reserve','id':'c','start':1,'end':3,'units':config['capacity']},{'type':'cancel','id':'a'}]
        for _ in range(n):
            if r.random()<.3:events.append({'type':'cancel','id':r.choice(ids)})
            else:
                start=r.randint(0,4 if shifted else 8);events.append({'type':'reserve','id':r.choice(ids),'start':start,'end':start+(r.randint(1,6) if shifted else r.randint(0,4)),'units':r.randint(1,3 if shifted else 4)})
    elif task_id=='q06':
        config={'capacity':4 if shifted else 2 if small else 7,'rate':3 if shifted else 2,'denom':7 if shifted else 3};events=[{'type':'take','id':'a','cost':2},{'type':'advance','dt':1},{'type':'advance','dt':1},{'type':'refund','id':'a'},{'type':'refund','id':'a'}]
        for _ in range(n):
            op=r.choice(['take','refund','advance']);e={'type':op}
            if op=='advance':e['dt']=r.randint(0,3 if shifted else 5)
            else:e['id']=r.choice(ids)
            if op=='take':e['cost']=r.randint(1,6 if shifted else 8)
            events.append(e)
    elif task_id=='q07':
        config={'attempts':1 if regime=='shift' else 3,'delay':2};events=[{'type':'start','id':'a'},{'type':'fail','id':'a','attempt':1,'after':3},{'type':'advance','dt':2},{'type':'advance','dt':1},{'type':'success','id':'a','attempt':1}]
        for _ in range(n):
            op=r.choice(['start','fail','success','cancel','advance']);e={'type':op}
            if op in ('start','fail','success'):e['id']=r.choice(ids)
            if op in ('fail','success'):e['attempt']=r.randint(1,3)
            if op=='fail':e['after']=r.randint(0,5)
            if op=='advance':e['dt']=r.randint(0,4)
            events.append(e)
    elif task_id=='q08':
        nodes=list('abcdef') if regime=='shift' else list('abcd');deps={k:r.sample(nodes[:i],r.randint(0,min(i,2))) for i,k in enumerate(nodes)}
        if regime=='boundary':deps={k:[] for k in nodes}
        config={'deps':deps};events=[{'type':'ok','id':nodes[0]},{'type':'poll'}]
        events += [{'type':r.choice(['ok','ok','fail','poll']), 'id':r.choice(nodes)} for _ in range(n)]
    elif task_id=='dev-q01':
        config={'capacity':2 if shifted else 1 if regime=='boundary' else 3,'quantum':2 if shifted else 1 if regime=='boundary' else 3,'ceiling':3}
        events=[{'type':'add','id':'a','work':3,'priority':0},{'type':'advance','dt':3*config['quantum']},{'type':'add','id':'b','work':1,'priority':3},{'type':'run','budget':2},{'type':'run','budget':2},{'type':'cancel','id':'b'},{'type':'add','id':'a','work':2,'priority':1},{'type':'run','budget':0},{'type':'run','budget':4}]
        for _ in range(24 if regime=='ordinary' else 34):
            op=r.choice(['add','add','advance','run','run','cancel']);e={'type':op}
            if op in ('add','cancel'):e['id']=r.choice(ids)
            if op=='add':e.update(work=r.randint(1,12 if shifted else 6),priority=r.randint(0,3))
            if op=='advance':e['dt']=r.randint(0,6 if shifted else 3)
            if op=='run':e['budget']=r.randint(0,5)
            events.append(e)
    else:
        config={'ttl':5 if shifted else 1 if regime=='boundary' else 3}
        events=[{'type':'acquire','owner':'a'},{'type':'advance','dt':config['ttl']},{'type':'renew','owner':'a','generation':1},{'type':'acquire','owner':'a'},{'type':'release','owner':'a','generation':1},{'type':'advance','dt':0},{'type':'renew','owner':'a','generation':2},{'type':'release','owner':'a','generation':2},{'type':'acquire','owner':'b'}]
        for _ in range(24 if regime=='ordinary' else 34):
            op=r.choice(['acquire','renew','release','advance']);e={'type':op}
            if op=='advance':e['dt']=r.randint(0,7 if shifted else 3)
            else:e['owner']=r.choice(ids)
            if op in ('renew','release'):e['generation']=r.randint(0,8)
            events.append(e)
    if regime=='adversarial':
        events=[cloned(e) for e in events for _ in range(2 if r.random()<.5 else 1)][:48]
    return {'config':config,'events':events}


def public_cases(task_id):
    return [dict(id='p'+str(i+1),**make_case(task_id,regime,101+i)) for i,regime in enumerate(REGIMES)]


def reference(task_id, case):
    """Imperative state-machine reference, distinct from the declarative checker below."""
    case=_integer_json(case)
    c=case['config']; out=[]; jobs={}; order=[]; now=0; cursor=0; credits=c.get('capacity',0);carry=0;refunds=set();held={};done=set(); used=0;remain=0
    phase='idle'; current=None;attempt=0;due=None;lease_owner=None;generation=0;expires=None
    if task_id=='q02':cycle=[k for k in sorted(c['weights']) for _ in range(c['weights'][k])];queues={k:[] for k in c['weights']}
    if task_id=='q08':states={k:'pending' for k in c['deps']}
    for e in case['events']:
        op=e['type'];status='ignored'
        if task_id=='q01':
            ran=None
            if op=='advance':now+=e['dt']
            for k in list(order):
                if jobs[k]['deadline']<=now:order.remove(k);del jobs[k]
            if op=='add':
                if e['id'] not in jobs and e['deadline']>now and sum(j['size'] for j in jobs.values())+e['size']<=c['capacity']:jobs[e['id']]=dict(e);order.append(e['id']);status='accepted'
                else:status='rejected'
            elif op=='cancel':
                status='cancelled' if e['id'] in jobs else 'missing'
                if e['id'] in jobs:del jobs[e['id']];order.remove(e['id'])
            elif op=='run':
                status='empty'
                if order:ran=min(order,key=lambda k:jobs[k]['deadline']);order.remove(ran);del jobs[ran];status='ran'
            else:status='advanced'
            value=dict(status=status,ran=ran,pending=order[:],bytes=sum(j['size'] for j in jobs.values()),now=now)
        elif task_id=='q02':
            sent=None
            if op=='add':
                status='duplicate' if any(e['id'] in q for q in queues.values()) else 'queued'
                if status=='queued':queues[e['tenant']].append(e['id'])
            else:
                status='empty'
                for offset in range(len(cycle)):
                    pos=(cursor+offset)%len(cycle);tenant=cycle[pos]
                    if queues[tenant]:sent=queues[tenant].pop(0);cursor=(pos+1)%len(cycle);status='sent';break
            value=dict(status=status,sent=sent,queues=cloned(queues),cursor=cursor)
        elif task_id=='q03':
            emitted=[]
            if op=='put':
                if c['required']:emitted=[dict(key=e['key'],value=e['value'])]
                else:jobs[e['key']]={'value':e['value'],'time':jobs.get(e['key'],{}).get('time',now)}
            elif op=='cancel':jobs.pop(e['key'],None)
            elif op=='advance':now+=e['dt']
            flush=(op=='flush' or (op=='put' and len(jobs)>=c['limit']) or (op=='advance' and any(now-j['time']>=c['delay'] for j in jobs.values())))
            if flush:emitted=[dict(key=k,value=jobs[k]['value']) for k in sorted(jobs)];jobs={}
            value=dict(emitted=emitted,pending=sorted(jobs),now=now)
        elif task_id=='q04':
            k=e['id']; status='invalid'
            if op=='begin':
                status='blocked'
                if k not in jobs and not any(x in held for x in e['resources']):
                    jobs[k]=dict(phase='active',resources=e['resources']);held.update({x:k for x in e['resources']});status='begun'
            elif op=='prepare' and jobs.get(k,{}).get('phase')=='active':jobs[k]['phase']='prepared';status='prepared'
            elif (op=='commit' and jobs.get(k,{}).get('phase')=='prepared') or (op=='abort' and jobs.get(k,{}).get('phase') in ('active','prepared')):
                for x in jobs[k]['resources']:del held[x]
                jobs[k]['phase']='done' if op=='commit' else 'aborted';status='committed' if op=='commit' else 'aborted'
                if op=='commit':done.add(k)
            value=dict(status=status,held=held.copy(),done=sorted(done))
        elif task_id=='q05':
            k=e['id']
            if op=='cancel':status='cancelled' if k in jobs else 'missing';jobs.pop(k,None)
            else:
                valid=k not in jobs and 0<=e['start']<e['end'] and 1<=e['units']<=c['capacity']
                points=[]
                for j in list(jobs.values())+[e]:points.extend([(j['start'],j['units']),(j['end'],-j['units'])])
                occupancy=0
                for t in sorted(set(p[0] for p in points)):
                    occupancy+=sum(delta for at,delta in points if at==t)
                    if occupancy>c['capacity']:valid=False
                status='reserved' if valid else 'rejected'
                if valid:jobs[k]=dict(e)
            value=dict(status=status,active=sorted(jobs),units=sum(j['units'] for j in jobs.values()))
        elif task_id=='q06':
            if op=='advance':n=carry+e['dt']*c['rate'];credits=min(c['capacity'],credits+n//c['denom']);carry=n%c['denom'];status='advanced'
            elif op=='take':
                status='rejected'
                if e['id'] not in jobs and e['cost']<=credits:credits-=e['cost'];jobs[e['id']]=e['cost'];status='taken'
            else:
                status='ignored'
                if e['id'] in jobs and e['id'] not in refunds:credits=min(c['capacity'],credits+jobs[e['id']]);refunds.add(e['id']);status='refunded'
            value=dict(status=status,credits=credits,carry=carry)
        elif task_id=='q07':
            send=[]
            if op=='start':
                status='busy'
                if phase not in ('pending','waiting'):current=e['id'];attempt=1;phase='pending';due=None;send=[dict(id=current,attempt=attempt)];status='started'
            elif op=='advance':
                now+=e['dt'];status='advanced'
                if phase=='waiting' and now>=due:attempt+=1;phase='pending';due=None;send=[dict(id=current,attempt=attempt)]
            elif op=='cancel' and phase in ('pending','waiting'):phase='cancelled';due=None;status='cancelled'
            elif op in ('success','fail') and phase=='pending' and current==e['id'] and attempt==e['attempt']:
                if op=='success':phase='succeeded';due=None
                elif attempt>=c['attempts']:phase='failed';due=None
                else:phase='waiting';due=now+max(c['delay'],e['after'])
                status=phase
            value=dict(status=status,phase=phase,id=current,attempt=attempt,due=due,now=now,send=send)
        elif task_id=='q08':
            if op in ('ok','fail') and states[e['id']]=='running':states[e['id']]='done' if op=='ok' else 'failed'
            changed=True
            while changed:
                changed=False
                for k,parents in c['deps'].items():
                    if states[k]=='pending' and any(states[p] in ('failed','blocked') for p in parents):states[k]='blocked';changed=True
            started=sorted(k for k,parents in c['deps'].items() if states[k]=='pending' and all(states[p]=='done' for p in parents))
            for k in started:states[k]='running'
            value=dict(started=started,states=states.copy())
        elif task_id=='dev-q01':
            served=[]
            def priority(k):return min(c['ceiling'],jobs[k]['priority']+(now-jobs[k]['time'])//c['quantum'])
            if op=='advance':now+=e['dt'];status='advanced'
            elif op=='add':
                status='rejected'
                if e['id'] not in jobs and len(jobs)<c['capacity']:
                    jobs[e['id']]={'remaining':e['work'],'priority':e['priority'],'time':now};order.append(e['id']);status='queued'
            elif op=='cancel':
                status='cancelled' if e['id'] in jobs else 'missing'
                if e['id'] in jobs:del jobs[e['id']];order.remove(e['id'])
            elif op=='run':
                status='empty'
                if order:
                    k=max(order,key=priority);units=min(e['budget'],jobs[k]['remaining']);jobs[k]['remaining']-=units;complete=jobs[k]['remaining']==0
                    served=[dict(id=k,units=units,complete=complete)];status='served'
                    if complete:del jobs[k];order.remove(k)
            value=dict(status=status,served=served,pending=order[:],remaining={k:jobs[k]['remaining'] for k in order},priorities={k:priority(k) for k in order},now=now)
        elif task_id=='dev-q02':
            if op=='advance':now+=e['dt']
            if lease_owner is not None and expires<=now:lease_owner=None;expires=None
            status='ignored'
            if op=='advance':status='advanced'
            elif op=='acquire':
                status='busy'
                if lease_owner is None:generation+=1;lease_owner=e['owner'];expires=now+c['ttl'];status='acquired'
            elif lease_owner is not None and (e['owner'],e['generation'])==(lease_owner,generation):
                if op=='renew':expires=now+c['ttl'];status='renewed'
                else:lease_owner=None;expires=None;status='released'
            value=dict(status=status,owner=lease_owner,generation=generation,expires=expires,now=now)
        else:raise ValueError(task_id)
        out.append(cloned(value))
    return out


def _audit(task_id, case):
    """Second formulation: account for public event histories, never invoke the reference.

    Data representations intentionally differ (tuples/sets/rational credit, discrete
    interval occupancy and ancestor closure) so reference bugs are not inherited.
    """
    case=_integer_json(case)
    c=case['config']; events=case['events']; t=0; rows=[]; entries=[]; known={}; finished=set(); leases={}; pos=0; amount=c.get('capacity',0);fraction=Fraction(0); refunded=set();remaining=0
    phase='idle'; job=None;count=0;wake=None;lease_history=[]
    if task_id=='q02':slots=sum(([k]*c['weights'][k] for k in sorted(c['weights'])),[])
    if task_id=='q08':
        running=set();success=set();failed=set()
        def ancestors(k):return set(c['deps'][k]).union(*(ancestors(p) for p in c['deps'][k])) if c['deps'][k] else set()
        closure={k:ancestors(k) for k in c['deps']}
    for i,e in enumerate(events):
        op=e['type']
        if task_id=='q01':
            t=sum(x['dt'] for x in events[:i+1] if x['type']=='advance');entries=[x for x in entries if x[3]>t]; ran=None
            if op=='add':
                ok=e['id'] not in [x[0] for x in entries] and e['deadline']>t and sum(x[2] for x in entries)+e['size']<=c['capacity'];status='accepted' if ok else 'rejected'
                if ok:entries.append((e['id'],i,e['size'],e['deadline']))
            elif op=='cancel':status='cancelled' if any(x[0]==e['id'] for x in entries) else 'missing';entries=[x for x in entries if x[0]!=e['id']]
            elif op=='run':
                status='empty'
                if entries:
                    take=sorted(entries,key=lambda x:(x[3],x[1]))[0];ran=take[0];entries.remove(take);status='ran'
            else:status='advanced'
            expected=dict(status=status,ran=ran,pending=[x[0] for x in entries],bytes=sum(x[2] for x in entries),now=t)
        elif task_id=='q02':
            sent=None
            if op=='add':
                exists=any(x[1]==e['id'] for x in entries);status='duplicate' if exists else 'queued'
                if not exists:entries.append((e['tenant'],e['id'],i))
            else:
                available=[((j-pos)%len(slots),j) for j,tenant in enumerate(slots) if any(x[0]==tenant for x in entries)]
                if available:
                    _,chosen=min(available);take=next(x for x in entries if x[0]==slots[chosen]);entries.remove(take);sent=take[1];pos=(chosen+1)%len(slots);status='sent'
                else:status='empty'
            expected=dict(status=status,sent=sent,queues={k:[x[1] for x in entries if x[0]==k] for k in c['weights']},cursor=pos)
        elif task_id=='q03':
            emitted=[]
            if op=='advance':t+=e['dt']
            if op=='cancel':entries=[x for x in entries if x[0]!=e['key']]
            if op=='put':
                if c['required']:emitted=[{'key':e['key'],'value':e['value']}]
                else:
                    old=next((x for x in entries if x[0]==e['key']),None);entries=[x for x in entries if x[0]!=e['key']]+[(e['key'],e['value'],old[2] if old else t)]
            trigger=op=='flush' or (op=='put' and len(entries)>=c['limit']) or (op=='advance' and entries and t-min(x[2] for x in entries)>=c['delay'])
            if trigger:emitted=[{'key':k,'value':v} for k,v,_ in sorted(entries)];entries=[]
            expected=dict(emitted=emitted,pending=sorted(x[0] for x in entries),now=t)
        elif task_id=='q04':
            k=e['id'];status='invalid'
            if op=='begin':
                active_resources=set().union(*(v[1] for v in leases.values() if v[0] in ('active','prepared')))
                ok=k not in leases and not active_resources.intersection(e['resources']);status='begun' if ok else 'blocked'
                if ok:leases[k]=('active',set(e['resources']))
            elif op=='prepare' and k in leases and leases[k][0]=='active':leases[k]=('prepared',leases[k][1]);status='prepared'
            elif op=='commit' and k in leases and leases[k][0]=='prepared':leases[k]=('done',leases[k][1]);status='committed'
            elif op=='abort' and k in leases and leases[k][0] in ('active','prepared'):leases[k]=('aborted',leases[k][1]);status='aborted'
            expected=dict(status=status,held={x:k for k,(p,resources) in leases.items() if p in ('active','prepared') for x in resources},done=sorted(k for k,v in leases.items() if v[0]=='done'))
        elif task_id=='q05':
            k=e['id']
            if op=='cancel':status='cancelled' if k in known else 'missing';known.pop(k,None)
            else:
                ok=k not in known and 0<=e['start']<e['end'] and 1<=e['units']<=c['capacity']
                if ok:
                    for tick in range(e['start'],e['end']):
                        if e['units']+sum(v[2] for v in known.values() if v[0]<=tick<v[1])>c['capacity']:ok=False;break
                status='reserved' if ok else 'rejected'
                if ok:known[k]=(e['start'],e['end'],e['units'])
            expected=dict(status=status,active=sorted(known),units=sum(v[2] for v in known.values()))
        elif task_id=='q06':
            if op=='advance':
                fraction+=Fraction(e['dt']*c['rate'],c['denom']);whole=int(fraction);fraction-=whole;amount=min(c['capacity'],amount+whole);status='advanced'
            elif op=='take':
                ok=e['id'] not in known and e['cost']<=amount;status='taken' if ok else 'rejected'
                if ok:known[e['id']]=e['cost'];amount-=e['cost']
            else:
                ok=e['id'] in known and e['id'] not in refunded;status='refunded' if ok else 'ignored'
                if ok:refunded.add(e['id']);amount=min(c['capacity'],amount+known[e['id']])
            expected=dict(status=status,credits=amount,carry=int(fraction*c['denom']))
        elif task_id=='q07':
            send=[];status='ignored'
            if op=='advance':
                t+=e['dt'];status='advanced'
                if phase=='waiting' and wake<=t:count+=1;phase='pending';wake=None;send=[{'id':job,'attempt':count}]
            elif op=='start':
                if phase in ('pending','waiting'):status='busy'
                else:job=e['id'];count=1;wake=None;phase='pending';status='started';send=[{'id':job,'attempt':1}]
            elif op=='cancel':
                if phase in ('pending','waiting'):phase='cancelled';wake=None;status='cancelled'
            elif phase=='pending' and (e.get('id'),e.get('attempt'))==(job,count):
                if op=='success':phase='succeeded';wake=None
                elif count==c['attempts']:phase='failed';wake=None
                else:phase='waiting';wake=t+max(c['delay'],e['after'])
                status=phase
            expected=dict(status=status,phase=phase,id=job,attempt=count,due=wake,now=t,send=send)
        elif task_id=='q08':
            if op in ('ok','fail') and e['id'] in running:
                running.remove(e['id']);(success if op=='ok' else failed).add(e['id'])
            blocked={k for k in c['deps'] if closure[k]&failed and k not in success|running|failed}
            new=sorted(k for k,p in c['deps'].items() if k not in running|success|failed|blocked and set(p)<=success)
            running.update(new)
            expected=dict(started=new,states={k:'done' if k in success else 'failed' if k in failed else 'running' if k in running else 'blocked' if k in blocked else 'pending' for k in c['deps']})
        elif task_id=='dev-q01':
            if op=='advance':t+=e['dt']
            served=[];status='advanced'
            if op=='add':
                ok=len(entries)<c['capacity'] and all(x[0]!=e['id'] for x in entries);status='queued' if ok else 'rejected'
                if ok:entries.append((e['id'],e['work'],e['priority'],t,i))
            elif op=='cancel':
                status='cancelled' if any(x[0]==e['id'] for x in entries) else 'missing';entries=[x for x in entries if x[0]!=e['id']]
            elif op=='run':
                status='empty'
                if entries:
                    chosen=sorted(entries,key=lambda x:(-min(c['ceiling'],x[2]+(t-x[3])//c['quantum']),x[4]))[0]
                    amount=min(e['budget'],chosen[1]);complete=amount==chosen[1];status='served';served=[dict(id=chosen[0],units=amount,complete=complete)]
                    entries=[(x[0],x[1]-amount,*x[2:]) if x is chosen else x for x in entries if x is not chosen or not complete]
            ordered=sorted(entries,key=lambda x:x[4])
            expected=dict(status=status,served=served,pending=[x[0] for x in ordered],remaining={x[0]:x[1] for x in ordered},priorities={x[0]:min(c['ceiling'],x[2]+(t-x[3])//c['quantum']) for x in ordered},now=t)
        elif task_id=='dev-q02':
            if op=='advance':t+=e['dt']
            live=bool(lease_history and lease_history[-1][2] and lease_history[-1][1]>t);status='ignored'
            if op=='acquire':
                status='busy' if live else 'acquired'
                if not live:lease_history.append((e['owner'],t+c['ttl'],True));live=True
            elif op=='advance':status='advanced'
            elif live and (e['owner'],e['generation'])==(lease_history[-1][0],len(lease_history)):
                if op=='renew':lease_history[-1]=(e['owner'],t+c['ttl'],True);status='renewed'
                else:lease_history[-1]=(*lease_history[-1][:2],False);live=False;status='released'
            expected=dict(status=status,owner=lease_history[-1][0] if live else None,generation=len(lease_history),expires=lease_history[-1][1] if live else None,now=t)
        else:raise ValueError(task_id)
        rows.append(expected)
    return rows


def check(task_id, case, outputs):
    errors=check_count(case,outputs)
    if errors:return result(errors)
    expected=_audit(task_id,case)
    for i,(want,got) in enumerate(zip(expected,outputs)):
        try: equal=json.dumps(want,sort_keys=True,allow_nan=False)==json.dumps(_integer_json(got),sort_keys=True,allow_nan=False)
        except (TypeError,ValueError):equal=False
        if not equal:errors.append('event_%d_contract'%i)
    return result(errors)

_JS = {
'q01':r'''let s=state||{now:0,jobs:[]},e=event,status='advanced',ran=null;if(e.type==='advance')s.now+=e.dt;s.jobs=s.jobs.filter(j=>j.deadline>s.now);if(e.type==='add'){if(!s.jobs.some(j=>j.id===e.id)&&e.deadline>s.now&&s.jobs.reduce((n,j)=>n+j.size,0)+e.size<=config.capacity){s.jobs.push({...e});status='accepted';}else status='rejected';}else if(e.type==='cancel'){status=s.jobs.some(j=>j.id===e.id)?'cancelled':'missing';s.jobs=s.jobs.filter(j=>j.id!==e.id);}else if(e.type==='run'){status='empty';if(s.jobs.length){let j=s.jobs.reduce((a,b)=>b.deadline<a.deadline?b:a);ran=j.id;s.jobs=s.jobs.filter(x=>x.id!==ran);status='ran';}}return {state:s,output:{status,ran,pending:s.jobs.map(j=>j.id),bytes:s.jobs.reduce((n,j)=>n+j.size,0),now:s.now}};''',
'q02':r'''let cycle=Object.keys(config.weights).sort().flatMap(k=>Array(config.weights[k]).fill(k));let s=state||{cursor:0,q:Object.fromEntries(Object.keys(config.weights).map(k=>[k,[]]))},e=event,status='empty',sent=null;if(e.type==='add'){status=Object.values(s.q).some(q=>q.includes(e.id))?'duplicate':'queued';if(status==='queued')s.q[e.tenant].push(e.id);}else for(let i=0;i<cycle.length;i++){let p=(s.cursor+i)%cycle.length,k=cycle[p];if(s.q[k].length){sent=s.q[k].shift();s.cursor=(p+1)%cycle.length;status='sent';break;}}return {state:s,output:{status,sent,queues:s.q,cursor:s.cursor}};''',
'q03':r'''let s=state||{now:0,q:{}},e=event,emitted=[];if(e.type==='advance')s.now+=e.dt;if(e.type==='put'){if(config.required)emitted=[{key:e.key,value:e.value}];else s.q[e.key]={value:e.value,time:s.q[e.key]?.time??s.now};}else if(e.type==='cancel')delete s.q[e.key];let keys=Object.keys(s.q);if(e.type==='flush'||(e.type==='put'&&keys.length>=config.limit)||(e.type==='advance'&&keys.some(k=>s.now-s.q[k].time>=config.delay))){emitted=keys.sort().map(k=>({key:k,value:s.q[k].value}));s.q={};}return {state:s,output:{emitted,pending:Object.keys(s.q).sort(),now:s.now}};''',
'q04':r'''let s=state||{jobs:{},held:{},done:[]},e=event,k=e.id,status='invalid';if(e.type==='begin'){status='blocked';if(!s.jobs[k]&&!e.resources.some(x=>Object.hasOwn(s.held,x))){s.jobs[k]={phase:'active',resources:e.resources};for(let x of e.resources)s.held[x]=k;status='begun';}}else if(e.type==='prepare'&&s.jobs[k]?.phase==='active'){s.jobs[k].phase='prepared';status='prepared';}else if((e.type==='commit'&&s.jobs[k]?.phase==='prepared')||(e.type==='abort'&&['active','prepared'].includes(s.jobs[k]?.phase))){for(let x of s.jobs[k].resources)delete s.held[x];s.jobs[k].phase=e.type==='commit'?'done':'aborted';status=e.type==='commit'?'committed':'aborted';if(e.type==='commit')s.done.push(k);}return {state:s,output:{status,held:s.held,done:s.done.slice().sort()}};''',
'q05':r'''let s=state||{items:{}},e=event,status;if(e.type==='cancel'){status=Object.hasOwn(s.items,e.id)?'cancelled':'missing';delete s.items[e.id];}else{let ok=!Object.hasOwn(s.items,e.id)&&e.start>=0&&e.end>e.start&&e.units>=1&&e.units<=config.capacity;for(let t=e.start;ok&&t<e.end;t++){let used=Object.values(s.items).filter(j=>j.start<=t&&t<j.end).reduce((n,j)=>n+j.units,0);if(used+e.units>config.capacity)ok=false;}status=ok?'reserved':'rejected';if(ok)s.items[e.id]={...e};}return {state:s,output:{status,active:Object.keys(s.items).sort(),units:Object.values(s.items).reduce((n,j)=>n+j.units,0)}};''',
'q06':r'''let s=state||{credits:config.capacity,carry:0,taken:{},refunded:[]},e=event,status;if(e.type==='advance'){let n=s.carry+e.dt*config.rate;s.credits=Math.min(config.capacity,s.credits+Math.floor(n/config.denom));s.carry=n%config.denom;status='advanced';}else if(e.type==='take'){status='rejected';if(!Object.hasOwn(s.taken,e.id)&&e.cost<=s.credits){s.taken[e.id]=e.cost;s.credits-=e.cost;status='taken';}}else{status='ignored';if(Object.hasOwn(s.taken,e.id)&&!s.refunded.includes(e.id)){s.credits=Math.min(config.capacity,s.credits+s.taken[e.id]);s.refunded.push(e.id);status='refunded';}}return {state:s,output:{status,credits:s.credits,carry:s.carry}};''',
'q07':r'''let s=state||{now:0,phase:'idle',id:null,attempt:0,due:null},e=event,status='ignored',send=[];if(e.type==='start'){status='busy';if(!['pending','waiting'].includes(s.phase)){s.id=e.id;s.attempt=1;s.phase='pending';s.due=null;send=[{id:s.id,attempt:1}];status='started';}}else if(e.type==='advance'){s.now+=e.dt;status='advanced';if(s.phase==='waiting'&&s.now>=s.due){s.attempt++;s.phase='pending';s.due=null;send=[{id:s.id,attempt:s.attempt}];}}else if(e.type==='cancel'&&['pending','waiting'].includes(s.phase)){s.phase='cancelled';s.due=null;status='cancelled';}else if(['success','fail'].includes(e.type)&&s.phase==='pending'&&s.id===e.id&&s.attempt===e.attempt){if(e.type==='success'){s.phase='succeeded';s.due=null;}else if(s.attempt>=config.attempts){s.phase='failed';s.due=null;}else{s.phase='waiting';s.due=s.now+Math.max(config.delay,e.after);}status=s.phase;}return {state:s,output:{status,phase:s.phase,id:s.id,attempt:s.attempt,due:s.due,now:s.now,send}};''',
'q08':r'''let s=state||{phases:Object.fromEntries(Object.keys(config.deps).map(k=>[k,'pending']))},e=event;if(['ok','fail'].includes(e.type)&&s.phases[e.id]==='running')s.phases[e.id]=e.type==='ok'?'done':'failed';let changed=true;while(changed){changed=false;for(let [k,ps]of Object.entries(config.deps))if(s.phases[k]==='pending'&&ps.some(p=>['failed','blocked'].includes(s.phases[p]))){s.phases[k]='blocked';changed=true;}}let started=Object.keys(config.deps).filter(k=>s.phases[k]==='pending'&&config.deps[k].every(p=>s.phases[p]==='done')).sort();for(let k of started)s.phases[k]='running';return {state:s,output:{started,states:s.phases}};''',
'dev-q01':r'''let s=state||{now:0,jobs:[]},e=event,served=[],status='advanced';const priority=j=>Math.min(config.ceiling,j.priority+Math.floor((s.now-j.time)/config.quantum));if(e.type==='advance')s.now+=e.dt;else if(e.type==='add'){status='rejected';if(s.jobs.length<config.capacity&&!s.jobs.some(j=>j.id===e.id)){s.jobs.push({id:e.id,remaining:e.work,priority:e.priority,time:s.now});status='queued';}}else if(e.type==='cancel'){status=s.jobs.some(j=>j.id===e.id)?'cancelled':'missing';s.jobs=s.jobs.filter(j=>j.id!==e.id);}else if(e.type==='run'){status='empty';if(s.jobs.length){const j=s.jobs.reduce((a,b)=>priority(b)>priority(a)?b:a),units=Math.min(e.budget,j.remaining);j.remaining-=units;const complete=j.remaining===0;served=[{id:j.id,units,complete}];status='served';if(complete)s.jobs=s.jobs.filter(x=>x!==j);}}return {state:s,output:{status,served,pending:s.jobs.map(j=>j.id),remaining:Object.fromEntries(s.jobs.map(j=>[j.id,j.remaining])),priorities:Object.fromEntries(s.jobs.map(j=>[j.id,priority(j)])),now:s.now}};''',
'dev-q02':r'''let s=state||{now:0,owner:null,generation:0,expires:null},e=event,status='ignored';if(e.type==='advance')s.now+=e.dt;if(s.owner!==null&&s.expires<=s.now){s.owner=null;s.expires=null;}if(e.type==='advance')status='advanced';else if(e.type==='acquire'){status='busy';if(s.owner===null){s.generation++;s.owner=e.owner;s.expires=s.now+config.ttl;status='acquired';}}else if(s.owner!==null&&s.owner===e.owner&&s.generation===e.generation){if(e.type==='renew'){s.expires=s.now+config.ttl;status='renewed';}else{s.owner=null;s.expires=null;status='released';}}return {state:s,output:{status,owner:s.owner,generation:s.generation,expires:s.expires,now:s.now}};'''
}

def reference_source(task_id):return 'function solve({config,state,event}) {\n'+_JS[task_id]+'\n}'

def fault_cases(task_id):
    """Semantically plausible wrong outputs at concrete contract boundaries."""
    case=public_cases(task_id)[0]
    if task_id=='q08':
        case={'config':{'deps':{'a':[],'b':['a'],'c':['b']}},'events':[{'type':'poll'},{'type':'ok','id':'b'},{'type':'fail','id':'a'},{'type':'poll'}]}
    edits={
      'q01':[('capacity_accounting_omits_second_job',1,'bytes',1),('equal_deadline_lifo',2,'ran','b'),('expiry_equality_retains_job',3,'pending',['b'])],
      'q02':[('duplicate_admitted',1,'status','queued'),('weighted_cursor_reset',2,'cursor',0),('dispatched_job_not_removed',2,'queues',{'a':[],'b':['a'],'c':[]})],
      'q03':[('replacement_resets_maximum_age',3,'emitted',[]),('flush_retains_pending_key',3,'pending',['a']),('replacement_keeps_old_value',3,'emitted',[{'key':'a','value':1}])],
      'q04':[('conflicting_begin_acquires_resource',1,'held',{'x':'a','y':'b'}),('commit_without_prepare',2,'done',['a']),('commit_leaks_resource',4,'held',{'x':'a','y':'a'})],
      'q05':[('closed_interval_rejects_adjacent',1,'status','rejected'),('overlap_exceeds_capacity',2,'status','reserved'),('cancel_keeps_reservation',3,'active',['a','b'])],
      'q06':[('fractional_carry_discarded',1,'carry',0),('refill_rounds_up',1,'credits',6),('duplicate_refund_accepted',4,'status','refunded')],
      'q07':[('retry_ignores_delay_floor',2,'send',[{'id':'a','attempt':2}]),('retry_does_not_advance_attempt',3,'attempt',1),('stale_success_wins',4,'phase','succeeded')],
      'q08':[('dependent_starts_before_prerequisite',0,'started',['a','b']),('failure_not_transitive',2,'states',{'a':'failed','b':'blocked','c':'pending'}),('terminal_node_restarts',3,'started',['a'])],
      'dev-q01':[('aging_does_not_promote',1,'priorities',{'a':0}),('partial_service_removes_job',3,'pending',['b']),('remaining_budget_spills_to_second_job',4,'pending',[])],
      'dev-q02':[('expiry_equality_keeps_owner',1,'owner','a'),('generation_reused',3,'generation',1),('stale_release_releases_new_lease',4,'owner',None)]
    }[task_id]
    correct=reference(task_id,case);faults=[]
    for name,index,field,value in edits:
        outputs=cloned(correct);outputs[index][field]=cloned(value)
        faults.append(dict(name=name,case=cloned(case),outputs=outputs))
    return faults
