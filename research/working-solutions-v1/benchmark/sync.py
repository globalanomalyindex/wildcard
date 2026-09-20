"""Finite synchronization contracts, separate executable and acceptance models.

No source-card or condition information enters this module. The acceptance model
below is a separate implementation and never calls the reference entry point.
"""
import json
import math
from .common import cloned, rng_for, result, check_count, REGIMES

_COMMON = " Return one JSON output per event; state is opaque JSON, initially null. Objects in outputs have exactly the documented keys; map keys are unordered, arrays are ordered. Sorted/lexicographic string order compares Unicode scalar values (code points), with a shorter prefix first. Numeric inputs/values and intermediate arithmetic are safe integers. Integral JSON number notations such as 1 and 1.0 denote the same number, while booleans are distinct. Strings contain Unicode scalar values (no unpaired surrogates). Decoded imported values outside these limits are invalid frames. There are at most 48 events. Unknown/invalid operations have the behavior below. Each instance starts fresh. Hidden ordinary cases vary legal values; boundary cases emphasize equality, empty data and duplicates; adversarial cases reorder and conflict; shift cases use longer traces and more identities within the same contract. "

_SPECS = {
"s01": ("Causal idempotent inbox", ["identity", "ordering", "causality", "conservation"], "config={} . Every event is {id:string,seq:positive integer,delta:integer}. The inbox starts value=0,next=1. First-seen IDs with a free sequence at or above next are recorded permanently for this instance. Reuse of an ID with exactly its original seq/delta is duplicate; changed reuse is conflict. A new ID at a sequence already reserved is conflict, and a new ID below next is stale. Otherwise status=accepted; immediately apply every consecutively available sequence beginning at next, adding its delta exactly once. Output {status,value,next,pending}, where pending is ascending unapplied sequence numbers. Deduplication covers the complete instance, including applied operations; there is no time-based cleanup."),
"s02": ("Tombstone-preserving replica merge", ["identity", "ordering", "recovery", "causality"], "config={} . Events {key:string,version:nonnegative integer,actor:ASCII string,deleted:boolean,value:ASCII string}. Retain the maximum event per key under the lexicographic tuple (version, deleted?1:0, actor, value). Deleted events must have value=''. Thus deletion wins a same-version write regardless of actor, and ties have a total public order. Output {visible,tombstones}: visible maps each live key to its value; tombstones is sorted deleted keys. An older write never resurrects a newer deletion; a higher-version write may replace it. Repeated and permuted deliveries must converge."),
"s03": ("Reconciliation with incomplete ancestry", ["identity", "causality", "uncertainty", "ordering"], "config={} . Start local head=null and an empty immutable record graph. Events {head:null|string,records:[{id:string,parent:null|string,value:integer}]}. IDs cannot parent themselves; supplied records form an acyclic graph. Merge records atomically: if any known or within-event ID disagrees in parent/value, reject the whole event with decision=conflict and keep graph/head. Otherwise add them, even when parents are missing. Walk parent links from local and remote head until null or an unknown ID. If heads equal, decision=same. If local head occurs in the known remote chain (including terminal null), set local head=remote head and decision=advance. Else if remote head occurs in the local chain, decision=ahead. Else if both walks reach null, decision=fork. Otherwise decision=unknown. Output {head,decision,missing}; missing is sorted distinct unknown terminal IDs from BOTH walks performed before any head advance. For rejected records compute missing from the unchanged graph and the requested remote head. No value or clock similarity establishes ancestry."),
"s04": ("Transactional UTF-8 line importer", ["isolation", "visibility", "aggregation", "recovery"], "config={maxBytes:integer 8..256}. Events are {type:'chunk',bytes:[integers 0..255]} or {type:'finish'}. Buffer bytes until LF byte 10; LF is not part of the frame or buffer limit. Each complete frame must be valid strict UTF-8 and JSON. Frames have exact schemas: {op:'begin',id:string}, {op:'put',key:string,value:JSON scalar}, {op:'commit',id:string}, {op:'abort'}. Begin is legal only with no open transaction; put only with an open transaction; commit only for its ID; abort is always legal. A transaction stages puts over current visible data and commit publishes all of them atomically. Any invalid frame increments errors once and abandons the open transaction. Once a line exceeds maxBytes, count one error, abandon the transaction, and discard bytes through its next LF without another error. Finish counts one error for a nonempty partial line (but no extra error for an already-overflowed line), then clears it; if a transaction is still open, count one further error and abandon it. Finish is not a permanent shutdown. Output {visible,open,buffered,errors}, open is ID or null and buffered counts retained frame bytes. Blank lines are invalid frames; escaped newlines in JSON strings are data."),
"s05": ("Offline escrow rights ledger", ["conservation", "identity", "isolation", "ordering"], "config={initial:nonnegative integer,grants:{transferId:positive integer}}. Start available=initial,spent=0. Events receive/send/spend have {type,id,amount:positive integer}; ack/cancel have {type,id}. Receive accepts only a listed grant with exactly its amount, adds rights once; matching repeat is duplicate, all other receives invalid. A send or spend with a fresh ID succeeds only if available>=amount, debits immediately, and is recorded permanently; insufficient attempts are not recorded. Matching recorded repeat is duplicate and changed amount is conflict. Spend increases spent. Send reserves an outgoing transfer pending until ack (permanently delivered) or cancel (refund once). Ack/cancel only changes a currently pending send; otherwise ignored. ID namespaces are separate for receives, sends and spends. Output {status,available,spent,pending,received}, sorted ID arrays. Status is accepted,duplicate,conflict,insufficient,invalid,or ignored. Delivery acknowledgment never refunds rights."),
"s06": ("Versioned delta handshake", ["ordering", "identity", "recovery", "causality"], "config={version:nonnegative integer,value:integer}. Events delta={type:'delta',base,version,delta}, snapshot={type:'snapshot',version,value}, ack={type:'ack',version}. Keep current version/value, acknowledged=-1 and a snapshot-request latch. A delta with base=current and version>base applies, clears the latch; any other delta with version<=current is ignored; any remaining delta emits {type:'snapshot',base:current} once while latched and leaves state unchanged. A snapshot with version>current replaces version/value and clears the latch; same-version same-value is ignored; same-version different-value requests a snapshot once; older snapshots are ignored. Ack sets acknowledged=current only when its version equals current; older/future acks are ignored. After version advances, previously acknowledged remains as a historical version. Output {version,value,acknowledged,effects}, where effects is the one request object or []. A request is rearmed only by a successfully applied newer delta or snapshot."),
"s07": ("Resumable verified chunk receiver", ["identity", "recovery", "conservation", "visibility"], "config={maxLength:integer 0..64}. Events begin={type:'begin',id,length}, chunk={type:'chunk',id,offset,bytes,checksum}, finish={type:'finish',id}. A legal begin length 0..maxLength starts a new active ID and clears bytes; repeating active ID with same length is ok and preserves bytes, different length is conflict and preserves bytes. Invalid length is invalid. A chunk/finish for another ID or no active transfer is ignored. Chunk checksum must equal sum(bytes)%251, bytes must be integers 0..255, offset a nonnegative integer, and offset+length<=declared length; otherwise invalid. Conflicting overlap rejects the ENTIRE chunk as conflict; matching overlap is allowed. Valid chunks fill known bytes, status=ok. Finish is incomplete unless every byte is known; otherwise complete and returns bytes, including [] for length zero. Output {status,id,received,data}, where id is active ID or null, received counts distinct known offsets, and data is full bytes ONLY on a complete finish, else null. Completed transfers remain active; future matching chunks/finishes are legal. No future trace is available."),
"s08": ("Three-way nested document merge", ["identity", "uncertainty", "reversibility", "propagation"], "config={} . Each event is an independent {base:object,local:object,remote:object}; JSON trees contain objects, arrays and scalars, depth<=3. Merge recursively. At a path, if local and remote are deeply equal (including both absent), choose that value. Else if local equals base choose remote; else if remote equals base choose local. Else if local and remote are objects and base is an object or absent, recursively merge the sorted union of their keys, treating absent base as {}. Otherwise retain base (omit if absent) and record the conflicting path as an array of keys. Arrays are atomic and absence differs from null. Output {merged,conflicts}, with conflicts in depth-first lexicographic key order. Root inputs are objects, so merged is an object. Delete/edit and scalar/object disagreements are explicit conflicts; equal concurrent edits are not."),
"dev-s01": ("Two-party token handshake", ["identity", "ordering", "visibility"], "config={} . Events {type:'offer',token:string}, {type:'accept',token:string}, or {type:'reset'}. Offer replaces pending token and clears connected; matching accept connects and clears pending; unmatched accepts do nothing; reset clears both. Output {pending:null|string,connected:null|string}. Repeated accept after connection has no effect. This is a two-party handshake, not an ordered operation inbox."),
"dev-s02": ("Atomic compare-and-swap register pair", ["isolation", "identity", "visibility"], "config={a:integer,b:integer}. Events {expect:[a,b],replace:[a,b]}. Replace both registers only if current pair exactly equals expect, otherwise retain both. Output {accepted:boolean,pair:[a,b]}. Each update is atomic; no merge, version routing, operation deduplication or partial update occurs.")}

TASKS = [{"id": k, "family": "sync", "split": "development" if k.startswith("dev-") else "main", "title": v[0], "tags": v[1], "specification": v[2] + _COMMON} for k, v in _SPECS.items()]

def _validate(task_id, regime):
    if task_id not in _SPECS or regime not in REGIMES:
        raise ValueError("unknown task or regime")

def _line(obj):
    return list((json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))

def make_case(task_id, regime, seed):
    _validate(task_id, regime)
    r = rng_for(seed, ["sync", task_id, regime])
    n = 6 if regime == "shift" else 4
    config = {}
    if task_id == "s01":
        ops = [{"id": "o"+str(i), "seq": i, "delta": r.randint(-4, 8)} for i in range(1,n+1)]
        events = [ops[1],ops[0],cloned(ops[1]),dict(ops[1],delta=99),{"id":"alias","seq":1,"delta":2}] + ops[2:]
        if regime == "adversarial": events = list(reversed(ops)) + [cloned(ops[0]),dict(ops[0],delta=99)]
    elif task_id == "s02":
        events=[]
        for i in range(n):
            key="k"+str(i%3)
            events.extend([{"key":key,"version":i,"actor":"a","deleted":False,"value":"v"+str(i)}, {"key":key,"version":i,"actor":"z","deleted":True,"value":""}])
        events += [dict(events[0]), {"key":"k0","version":0,"actor":"z","deleted":False,"value":"resurrect"}]
        if regime in ("adversarial","shift"): r.shuffle(events)
    elif task_id == "s03":
        a={"id":"a","parent":None,"value":r.randint(0,9)}; b={"id":"b","parent":"a","value":2}; c={"id":"c","parent":"a","value":3}
        events=[{"head":"b","records":[b]}, {"head":"b","records":[a]}, {"head":"a","records":[]}, {"head":"c","records":[c]}, {"head":"b","records":[dict(b,value=8)]}, {"head":"lost","records":[]}]
        if regime == "shift": events += [{"head":"d","records":[{"id":"d","parent":"b","value":4}]},{"head":"a","records":[]}]
        if regime == "boundary": events.insert(0,{"head":None,"records":[]})
    elif task_id == "s04":
        config={"maxBytes":96 if regime != "boundary" else 48}
        frames=[{"op":"begin","id":"t"},{"op":"put","key":"café","value":"α\nβ"},{"op":"commit","id":"t"}, {"op":"begin","id":"u"},{"op":"put","key":"x","value":0},{"op":"commit","id":"wrong"}]
        blob=sum((_line(x) for x in frames),[])+[255,10]+_line({"op":"begin","id":"v"})+_line({"op":"put","key":"z","value":None})
        if regime in ("adversarial","shift"): blob += [65]*(config["maxBytes"]+2)+[10]
        events=[]; pos=0
        while pos<len(blob):
            size=r.randint(10,28) if regime != "adversarial" else r.randint(6,16)
            events.append({"type":"chunk","bytes":blob[pos:pos+size]});pos+=size
        events += [{"type":"finish"}]
    elif task_id == "s05":
        config={"initial":r.randint(2,5),"grants":{"g":3,"h":2}}
        events=[{"type":"spend","id":"a","amount":2},{"type":"spend","id":"a","amount":2},{"type":"receive","id":"g","amount":3},{"type":"receive","id":"g","amount":3},{"type":"send","id":"s","amount":2},{"type":"cancel","id":"s"},{"type":"cancel","id":"s"},{"type":"send","id":"t","amount":2},{"type":"ack","id":"t"},{"type":"cancel","id":"t"},{"type":"spend","id":"a","amount":3},{"type":"receive","id":"h","amount":1}]
        if regime == "adversarial": events.insert(0,{"type":"ack","id":"t"})
        if regime == "shift": events += [{"type":"receive","id":"h","amount":2},{"type":"spend","id":"b","amount":30}]
    elif task_id == "s06":
        config={"version":0,"value":r.randint(-5,5)}
        events=[{"type":"delta","base":0,"version":1,"delta":2},{"type":"delta","base":0,"version":1,"delta":2},{"type":"delta","base":3,"version":4,"delta":7},{"type":"delta","base":3,"version":5,"delta":4},{"type":"ack","version":0},{"type":"snapshot","version":3,"value":10},{"type":"ack","version":3},{"type":"snapshot","version":3,"value":11},{"type":"snapshot","version":3,"value":12},{"type":"delta","base":3,"version":4,"delta":-1}]
        if regime == "shift": events += [{"type":"ack","version":9},{"type":"snapshot","version":9,"value":0},{"type":"ack","version":4}]
        if regime == "boundary": events.insert(0,{"type":"snapshot","version":0,"value":config["value"]})
    elif task_id == "s07":
        config={"maxLength":32}; data=[r.randrange(256) for _ in range(n)]
        chunk=lambda off,b:{"type":"chunk","id":"t","offset":off,"bytes":b,"checksum":sum(b)%251}
        events=[{"type":"begin","id":"t","length":n},chunk(0,data[:2]),{"type":"finish","id":"t"},chunk(1,data[1:]),chunk(0,data[:2]),chunk(0,[(data[0]+1)%256]),{"type":"finish","id":"t"},{"type":"begin","id":"t","length":n+1},{"type":"chunk","id":"t","offset":0,"bytes":[1],"checksum":2},{"type":"begin","id":"empty","length":0},{"type":"finish","id":"empty"}]
        if regime == "adversarial": events.insert(0,chunk(0,data[:2]))
    elif task_id == "s08":
        v=r.randint(1,9)
        events=[{"base":{"a":0,"b":0},"local":{"a":v,"b":0},"remote":{"a":0,"b":2}}, {"base":{"a":0},"local":{},"remote":{"a":1}}, {"base":{"a":None},"local":{"a":0},"remote":{"a":0}}, {"base":{"x":{"a":1,"b":2}},"local":{"x":{"a":3,"b":2}},"remote":{"x":{"a":1,"b":4}}}, {"base":{},"local":{"z":None},"remote":{"z":0}}, {"base":{"x":[1]},"local":{"x":[2]},"remote":{"x":[3]}}]
        if regime == "shift": events += [{"base":{"x":{"a":{"v":0}}},"local":{"x":0},"remote":{"x":{"a":{"v":1}}}},{"base":{},"local":{"x":{"a":1}},"remote":{"x":{"b":2}}}]
        if regime == "adversarial": r.shuffle(events)
    elif task_id == "dev-s01":
        events=[{"type":"offer","token":"a"},{"type":"accept","token":"b"},{"type":"accept","token":"a"},{"type":"accept","token":"a"},{"type":"offer","token":"b"},{"type":"reset"},{"type":"accept","token":"b"}]
        if regime == "shift": events += [{"type":"offer","token":str(seed)},{"type":"accept","token":str(seed)}]
    else:
        config={"a":r.randint(-3,3),"b":r.randint(-3,3)}; pair=[config["a"],config["b"]]
        events=[{"expect":pair,"replace":[1,2]},{"expect":pair,"replace":[7,8]},{"expect":[1,2],"replace":[3,4]},{"expect":[3,4],"replace":[3,4]},{"expect":[3,99],"replace":[8,8]}]
    # Seeded legal interleavings make private instances more than renumbered
    # copies of four public traces. Each source-independent oracle replays them.
    extras=[]
    count=8 if regime=="shift" else 4
    for j in range(count):
        if task_id=="s01":extra={"id":r.choice(["o1","o2","o3","o4","z"]),"seq":r.randint(1,n+2),"delta":r.randint(-5,5)}
        elif task_id=="s02":
            deleted=r.choice([False,True]);extra={"key":r.choice(["k0","k1","k2","extra"]),"version":r.randint(0,n+2),"actor":r.choice(["a","b","z"]),"deleted":deleted,"value":"" if deleted else str(r.randint(0,9))}
        elif task_id=="s03":extra={"head":r.choice([None,"a","b","c","lost"]),"records":[]}
        elif task_id=="s04":break # UTF-8 chunk boundaries and overflow are already seeded.
        elif task_id=="s05":
            typ=r.choice(["spend","send","receive","ack","cancel"]);extra={"type":typ,"id":r.choice(["a","s","t","g","h"])}
            if typ in ("spend","send","receive"):extra["amount"]=r.randint(1,6)
        elif task_id=="s06":
            typ=r.choice(["delta","snapshot","ack"]);extra={"type":typ,"version":r.randint(0,9)}
            if typ=="delta":extra.update(base=r.randint(0,8),delta=r.randint(-5,5))
            if typ=="snapshot":extra["value"]=r.randint(-5,10)
        elif task_id=="s07":
            typ=r.choice(["begin","chunk","finish"]);extra={"type":typ,"id":r.choice(["t","u","empty"])}
            if typ=="begin":extra["length"]=r.randint(0,n+1)
            if typ=="chunk":
                b=[r.randrange(256) for _ in range(r.randint(0,3))];extra.update(offset=r.randint(0,n+1),bytes=b,checksum=(sum(b)+(1 if r.random()<.25 else 0))%251)
        elif task_id=="s08":
            b={"x":{"a":r.choice([False,0,None,1]),"b":r.randint(0,4)},"y":r.randint(0,4)};l=cloned(b);rr=cloned(b)
            if j%3==0:l["x"]["a"]=r.choice([True,0,None,2]);rr["y"]=r.randint(5,9)
            elif j%3==1:l.pop("x");rr["x"]["b"]=r.randint(5,9)
            else:l["x"]=None;rr["x"]={"new":[r.randint(0,4)]}
            extra={"base":b,"local":l,"remote":rr}
        elif task_id=="dev-s01":
            extra={"type":r.choice(["offer","accept","reset"])}
            if extra["type"]!="reset":extra["token"]=r.choice(["a","b","c"])
        else:extra={"expect":[r.randint(-3,4),r.randint(-3,4)],"replace":[r.randint(-3,4),r.randint(-3,4)]}
        events.insert(r.randrange(len(events)+1),extra)
    case={"config":config,"events":cloned(events)}
    # Hide accidental semantic help in familiar IDs while keeping every actual
    # rule public. Actor order can change: its documented comparator still rules.
    if task_id!="s04":
        names={};reserved={"receive","send","spend","ack","cancel","delta","snapshot","begin","chunk","finish","offer","accept","reset"}
        def name(x):
            if x=="" or x in reserved:return x
            if x not in names:names[x]="v%06d"%r.randrange(1000000)+"_"+str(len(names))
            return names[x]
        def visit(x,user_map=False):
            if isinstance(x,str):return name(x)
            if isinstance(x,list):return [visit(y,user_map) for y in x]
            if isinstance(x,dict):return {(name(k) if user_map else k):visit(v,user_map or k in ("grants","base","local","remote")) for k,v in x.items()}
            return x
        case=visit(case)
    return case

def public_cases(task_id):
    return [{"id":"p"+str(i+1),**make_case(task_id,regime,101+i)} for i,regime in enumerate(REGIMES)]

def _walk(head, graph):
    chain=[]
    while head is not None and head in graph:
        chain.append(head);head=graph[head]["parent"]
    chain.append(head)
    return chain, None if head is None else head

_MISSING=object()
def _json_equal(a,b):
    """JSON typed equality: integral number notation is irrelevant, bool is not a number."""
    def number(x):
        return (type(x) is int and abs(x)<=9007199254740991 or
                type(x) is float and math.isfinite(x) and x.is_integer() and abs(x)<=9007199254740991)
    if a is None or b is None:return a is None and b is None
    if type(a) is bool or type(b) is bool:return type(a) is bool and type(b) is bool and a==b
    if type(a) in (int,float) or type(b) in (int,float):return number(a) and number(b) and a==b
    if type(a) is str or type(b) is str:return type(a) is str and type(b) is str and a==b
    if type(a) is list and type(b) is list:return len(a)==len(b) and all(_json_equal(x,y) for x,y in zip(a,b))
    if type(a) is dict and type(b) is dict:
        return (all(type(k) is str for k in a) and all(type(k) is str for k in b) and
                a.keys()==b.keys() and all(_json_equal(a[k],b[k]) for k in a))
    return False

def _merge_ref(base,left,right,path):
    eq=lambda a,b: a is b or (a is not _MISSING and b is not _MISSING and _json_equal(a,b))
    if eq(left,right): return left,[]
    if eq(left,base): return right,[]
    if eq(right,base): return left,[]
    if isinstance(left,dict) and isinstance(right,dict) and (base is _MISSING or isinstance(base,dict)):
        merged={}; conflicts=[]; b={} if base is _MISSING else base
        for key in sorted(set(left)|set(right)|set(b)):
            value,issues=_merge_ref(b.get(key,_MISSING),left.get(key,_MISSING),right.get(key,_MISSING),path+[key])
            if value is not _MISSING: merged[key]=value
            conflicts+=issues
        return merged,conflicts
    return base,[path]

def reference(task_id, case):
    if task_id not in _SPECS:raise ValueError("unknown task")
    c=case["config"];out=[];state={}
    if task_id == "s01": state={"seen":{},"slots":{},"next":1,"value":0}
    if task_id == "s03": state={"graph":{},"head":None}
    if task_id == "s04": state={"visible":{},"open":None,"staged":{},"buf":[],"drop":False,"errors":0}
    if task_id == "s05": state={"available":c["initial"],"spent":0,"spends":{},"sends":{},"received":set()}
    if task_id == "s06": state={"version":c["version"],"value":c["value"],"acknowledged":-1,"latch":False}
    if task_id == "s07": state={"id":None,"length":0,"bytes":{}}
    if task_id == "dev-s01": state={"pending":None,"connected":None}
    if task_id == "dev-s02": state={"pair":[c["a"],c["b"]]}
    for e in case["events"]:
        if task_id == "s01":
            ident=e["id"];seq=e["seq"]
            if ident in state["seen"]: status="duplicate" if state["seen"][ident]==e else "conflict"
            elif seq in state["slots"]: status="conflict"
            elif seq<state["next"]: status="stale"
            else:
                status="accepted";state["seen"][ident]=cloned(e);state["slots"][seq]=e["delta"]
                while state["next"] in state["slots"]:
                    state["value"]+=state["slots"].pop(state["next"]);state["next"]+=1
            value={"status":status,"value":state["value"],"next":state["next"],"pending":sorted(state["slots"])}
        elif task_id == "s02":
            key=e["key"];rank=lambda x:(x["version"],int(x["deleted"]),x["actor"],x["value"])
            if key not in state or rank(e)>rank(state[key]):state[key]=cloned(e)
            value={"visible":{k:x["value"] for k,x in state.items() if not x["deleted"]},"tombstones":sorted(k for k,x in state.items() if x["deleted"])}
        elif task_id == "s03":
            candidate=cloned(state["graph"]);conflict=False
            for rec in e["records"]:
                if rec["id"] in candidate and candidate[rec["id"]]!=rec:conflict=True
                else:candidate[rec["id"]]=cloned(rec)
            if not conflict:state["graph"]=candidate
            local,lost1=_walk(state["head"],state["graph"]);remote,lost2=_walk(e["head"],state["graph"])
            if conflict:decision="conflict"
            elif state["head"]==e["head"]:decision="same"
            elif state["head"] in remote:decision="advance";state["head"]=e["head"]
            elif e["head"] in local:decision="ahead"
            elif lost1 is None and lost2 is None:decision="fork"
            else:decision="unknown"
            value={"head":state["head"],"decision":decision,"missing":sorted(set(x for x in [lost1,lost2] if x is not None))}
        elif task_id == "s04":
            def fail():state.update(open=None,staged={});state["errors"]+=1
            if e["type"]=="finish":
                if state["buf"]:fail()
                state["buf"]=[];state["drop"]=False
                if state["open"] is not None:fail()
            else:
                for byte in e["bytes"]:
                    if state["drop"]:
                        if byte==10:state["drop"]=False
                        continue
                    if byte!=10:
                        state["buf"].append(byte)
                        if len(state["buf"])>c["maxBytes"]:state["buf"]=[];state["drop"]=True;fail()
                        continue
                    try:
                        f=json.loads(bytes(state["buf"]).decode("utf-8"),parse_constant=lambda _: (_ for _ in ()).throw(ValueError()));state["buf"]=[]
                        if not isinstance(f,dict):raise ValueError()
                        op=f.get("op")
                        text=lambda x:type(x) is str and all(not 0xD800<=ord(ch)<=0xDFFF for ch in x)
                        scalar=lambda x:x is None or type(x) is bool or type(x) in (int,float) and abs(x)<=9007199254740991 and (type(x) is int or x.is_integer()) or text(x)
                        if op=="begin" and set(f)=={"op","id"} and text(f["id"]) and state["open"] is None:state["open"]=f["id"];state["staged"]={}
                        elif op=="put" and set(f)=={"op","key","value"} and text(f["key"]) and scalar(f["value"]) and state["open"] is not None:state["staged"][f["key"]]=int(f["value"]) if type(f["value"]) is float else f["value"]
                        elif op=="commit" and set(f)=={"op","id"} and text(f["id"]) and state["open"]==f["id"]:state["visible"].update(state["staged"]);state.update(open=None,staged={})
                        elif op=="abort" and set(f)=={"op"}:state.update(open=None,staged={})
                        else:raise ValueError()
                    except (ValueError,UnicodeError,TypeError):state["buf"]=[];fail()
            value={k:state[k] for k in ("visible","open","errors")};value["buffered"]=len(state["buf"])
        elif task_id == "s05":
            typ=e["type"];ident=e["id"];status="ignored"
            if typ=="receive":
                if c["grants"].get(ident)!=e["amount"]:status="invalid"
                elif ident in state["received"]:status="duplicate"
                else:state["received"].add(ident);state["available"]+=e["amount"];status="accepted"
            elif typ in ("spend","send"):
                ledger=state["spends"] if typ=="spend" else state["sends"]
                if ident in ledger:status="duplicate" if ledger[ident]["amount"]==e["amount"] else "conflict"
                elif state["available"]<e["amount"]:status="insufficient"
                else:
                    state["available"]-=e["amount"];ledger[ident]={"amount":e["amount"],"status":"pending"};status="accepted"
                    if typ=="spend":state["spent"]+=e["amount"]
            elif ident in state["sends"] and state["sends"][ident]["status"]=="pending":
                state["sends"][ident]["status"]=typ;status="accepted"
                if typ=="cancel":state["available"]+=state["sends"][ident]["amount"]
            value={"status":status,"available":state["available"],"spent":state["spent"],"pending":sorted(k for k,v in state["sends"].items() if v["status"]=="pending"),"received":sorted(state["received"])}
        elif task_id == "s06":
            typ=e["type"];effects=[];request=False
            if typ=="delta":
                if e["base"]==state["version"] and e["version"]>e["base"]:state["version"]=e["version"];state["value"]+=e["delta"];state["latch"]=False
                elif e["version"]>state["version"]:request=True
            elif typ=="snapshot":
                if e["version"]>state["version"]:state["version"]=e["version"];state["value"]=e["value"];state["latch"]=False
                elif e["version"]==state["version"] and e["value"]!=state["value"]:request=True
            elif e["version"]==state["version"]:state["acknowledged"]=state["version"]
            if request and not state["latch"]:effects=[{"type":"snapshot","base":state["version"]}];state["latch"]=True
            value={k:state[k] for k in ("version","value","acknowledged")};value["effects"]=effects
        elif task_id == "s07":
            status="ignored";data=None;typ=e["type"]
            if typ=="begin":
                if type(e["length"]) is not int or not 0<=e["length"]<=c["maxLength"]:status="invalid"
                elif state["id"]==e["id"] and state["length"]!=e["length"]:status="conflict"
                else:
                    if state["id"]!=e["id"]:state={"id":e["id"],"length":e["length"],"bytes":{}}
                    status="ok"
            elif state["id"] is not None and state["id"]==e["id"]:
                if typ=="finish":
                    status="complete" if len(state["bytes"])==state["length"] else "incomplete"
                    if status=="complete":data=[state["bytes"][i] for i in range(state["length"])]
                else:
                    b=e["bytes"];off=e["offset"]
                    if type(off) is not int or off<0 or off+len(b)>state["length"] or any(type(x) is not int or not 0<=x<=255 for x in b) or sum(b)%251!=e["checksum"]:status="invalid"
                    elif any(off+i in state["bytes"] and state["bytes"][off+i]!=x for i,x in enumerate(b)):status="conflict"
                    else:state["bytes"].update({off+i:x for i,x in enumerate(b)});status="ok"
            value={"status":status,"id":state["id"],"received":len(state["bytes"]),"data":data}
        elif task_id == "s08":
            merged,conflicts=_merge_ref(e["base"],e["local"],e["remote"],[]);value={"merged":merged,"conflicts":conflicts}
        elif task_id == "dev-s01":
            if e["type"]=="offer":state={"pending":e["token"],"connected":None}
            elif e["type"]=="reset":state={"pending":None,"connected":None}
            elif state["pending"]==e["token"]:state={"pending":None,"connected":e["token"]}
            value=state
        else:
            accepted=state["pair"]==e["expect"]
            if accepted:state["pair"]=cloned(e["replace"])
            value={"accepted":accepted,"pair":state["pair"]}
        out.append(cloned(value))
    return out

def _audit(task, c, events):
    """Reconstruct the final observable prefix independently of reference()."""
    if task == "s01":
        identities={}; sequence={}; frontier=1;status="accepted"
        for x in events:
            token=(x["seq"],x["delta"])
            if x["id"] in identities:status="duplicate" if identities[x["id"]]==token else "conflict"
            elif x["seq"]>=frontier and x["seq"] in sequence:status="conflict"
            elif x["seq"]<frontier:status="stale"
            else:
                identities[x["id"]]=token;sequence[x["seq"]]=x["delta"];status="accepted"
                while frontier in sequence:frontier+=1
        return {"status":status,"value":sum(v for k,v in sequence.items() if k<frontier),"next":frontier,"pending":sorted(k for k in sequence if k>=frontier)}
    if task == "s02":
        visible={};dead=[]
        for key in sorted({x["key"] for x in events}):
            versions=[x for x in events if x["key"]==key]
            winner=sorted(versions,key=lambda x:[x["version"],1 if x["deleted"] else 0,x["actor"],x["value"]])[-1]
            if winner["deleted"]:dead.append(key)
            else:visible[key]=winner["value"]
        return {"visible":visible,"tombstones":dead}
    if task == "s03":
        records={};head=None
        for x in events:
            proposed={k:dict(v) for k,v in records.items()};bad=False
            for row in x["records"]:
                old=proposed.get(row["id"])
                if old is not None and (old["parent"],old["value"])!=(row["parent"],row["value"]):bad=True
                proposed[row["id"]]=row
            if not bad:records=proposed
            paths=[];missing=[]
            for start in [head,x["head"]]:
                path=[start]
                while path[-1] is not None and path[-1] in records:path.append(records[path[-1]]["parent"])
                if path[-1] is not None:missing.append(path[-1])
                paths.append(path)
            if bad:decision="conflict"
            elif head==x["head"]:decision="same"
            elif head in paths[1]:decision="advance";head=x["head"]
            elif x["head"] in paths[0]:decision="ahead"
            else:decision="unknown" if missing else "fork"
        return {"head":head,"decision":decision,"missing":sorted(set(missing))}
    if task == "s04":
        durable={};tx=None;writes={};line=bytearray();overflow=False;errors=0
        def invalidate():
            nonlocal tx,writes,errors
            tx=None;writes={};errors+=1
        for x in events:
            if x["type"]=="finish":
                if line:invalidate()
                line.clear();overflow=False
                if tx is not None:invalidate()
                continue
            for b in x["bytes"]:
                if b==10:
                    if overflow:overflow=False;continue
                    raw=bytes(line);line.clear()
                    try:
                        frame=json.loads(raw.decode("utf-8"),parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
                        keys=set(frame) if type(frame) is dict else set()
                        op=frame.get("op") if type(frame) is dict else None
                        def allowed_string(x):return isinstance(x,str) and not any(55296<=ord(ch)<57344 for ch in x)
                        val=frame.get("value") if type(frame) is dict else None
                        allowed_value=val is None or type(val) is bool or type(val) in (int,float) and -9007199254740991<=val<=9007199254740991 and (type(val) is int or val.is_integer()) or allowed_string(val)
                        valid=False
                        if op=="abort" and keys=={"op"}:tx=None;writes={};valid=True
                        if op=="begin" and keys=={"op","id"} and allowed_string(frame["id"]) and tx is None:tx=frame["id"];writes={};valid=True
                        if op=="put" and keys=={"op","key","value"} and allowed_string(frame["key"]) and allowed_value and tx is not None:writes[frame["key"]]=int(val) if type(val) is float else val;valid=True
                        if op=="commit" and keys=={"op","id"} and allowed_string(frame["id"]) and tx==frame["id"]:durable={**durable,**writes};tx=None;writes={};valid=True
                        if not valid:invalidate()
                    except (ValueError,UnicodeError,TypeError):invalidate()
                elif not overflow:
                    if len(line)==c["maxBytes"]:line.clear();overflow=True;invalidate()
                    else:line.append(b)
        return {"visible":durable,"open":tx,"buffered":len(line),"errors":errors}
    if task == "s05":
        grants=set();charges={};transfers={};finalized={};status="ignored"
        for x in events:
            typ=x["type"];ident=x["id"]
            credit=c["initial"]+sum(c["grants"][i] for i in grants)-sum(charges.values())-sum(v for k,v in transfers.items() if finalized.get(k)!="cancel")
            if typ=="receive":
                status="invalid" if ident not in c["grants"] or x["amount"]!=c["grants"][ident] else "duplicate" if ident in grants else "accepted"
                if status=="accepted":grants.add(ident)
            elif typ in ("send","spend"):
                book=transfers if typ=="send" else charges
                status=("duplicate" if book[ident]==x["amount"] else "conflict") if ident in book else "insufficient" if x["amount"]>credit else "accepted"
                if status=="accepted":book[ident]=x["amount"]
            else:
                status="accepted" if ident in transfers and ident not in finalized else "ignored"
                if status=="accepted":finalized[ident]=typ
        return {"status":status,"available":c["initial"]+sum(c["grants"][i] for i in grants)-sum(charges.values())-sum(v for k,v in transfers.items() if finalized.get(k)!="cancel"),"spent":sum(charges.values()),"pending":sorted(set(transfers)-set(finalized)),"received":sorted(grants)}
    if task == "s06":
        current=(c["version"],c["value"]);ack=-1;requested=None;effects=[]
        for x in events:
            effects=[];v,val=current;need=False;typ=x["type"]
            if typ=="ack":
                if x["version"]==v:ack=v
            elif typ=="snapshot":
                if x["version"]>v:current=(x["version"],x["value"]);requested=None
                elif x["version"]==v and x["value"]!=val:need=True
            elif x["base"]==v and x["version"]>v:current=(x["version"],val+x["delta"]);requested=None
            elif x["version"]>v:need=True
            if need and requested is None:requested=v;effects=[{"type":"snapshot","base":v}]
        return {"version":current[0],"value":current[1],"acknowledged":ack,"effects":effects}
    if task == "s07":
        ident=None;cells=[];status="ignored";data=None
        for x in events:
            data=None;status="ignored"
            if x["type"]=="begin":
                length=x["length"]
                if type(length) is not int or length<0 or length>c["maxLength"]:status="invalid"
                elif ident==x["id"] and length!=len(cells):status="conflict"
                else:
                    if ident!=x["id"]:ident=x["id"];cells=[None]*length
                    status="ok"
            elif ident is not None and x["id"]==ident:
                if x["type"]=="finish":
                    status="incomplete" if None in cells else "complete"
                    if status=="complete":data=list(cells)
                else:
                    off=x["offset"];blob=x["bytes"]
                    good=type(off) is int and 0<=off<=len(cells) and off+len(blob)<=len(cells) and all(type(b) is int and 0<=b<256 for b in blob)
                    if not good or sum(blob)%251!=x["checksum"]:status="invalid"
                    elif any(cells[off+j] is not None and cells[off+j]!=b for j,b in enumerate(blob)):status="conflict"
                    else:cells[off:off+len(blob)]=blob;status="ok"
        return {"status":status,"id":ident,"received":sum(b is not None for b in cells),"data":data}
    if task == "s08":
        x=events[-1];conflicts=[]
        # Tagged optional values avoid relying on the reference's missing sentinel.
        def equal(a,b):return a[0]==b[0] and (not a[0] or _json_equal(a[1],b[1]))
        def visit(b,l,r,path):
            choices=[(equal(l,r),l),(equal(b,l),r),(equal(b,r),l)]
            for match,val in choices:
                if match:return val
            if l[0] and r[0] and type(l[1]) is dict and type(r[1]) is dict and (not b[0] or type(b[1]) is dict):
                origin=b[1] if b[0] else {};merged={}
                for key in sorted(set(origin)|set(l[1])|set(r[1])):
                    optional=lambda d:(key in d,d.get(key))
                    found,value=visit(optional(origin),optional(l[1]),optional(r[1]),path+[key])
                    if found:merged[key]=value
                return True,merged
            conflicts.append(path);return b
        return {"merged":visit((True,x["base"]),(True,x["local"]),(True,x["remote"]),[])[1],"conflicts":conflicts}
    if task == "dev-s01":
        pending=None;connected=None
        for x in events:
            if x["type"]=="reset":pending=connected=None
            elif x["type"]=="offer":pending=x["token"];connected=None
            elif x["token"]==pending:connected=pending;pending=None
        return {"pending":pending,"connected":connected}
    pair=[c["a"],c["b"]];accepted=False
    for x in events:
        accepted=all(a==b for a,b in zip(pair,x["expect"]))
        if accepted:pair=list(x["replace"])
    return {"accepted":accepted,"pair":pair}

def check(task_id, case, outputs):
    errors=check_count(case,outputs)
    if errors:return result(errors)
    if task_id not in _SPECS:raise ValueError("unknown task")
    for i,actual in enumerate(outputs):
        expected=_audit(task_id,case["config"],case["events"][:i+1])
        if not _json_equal(actual,expected):errors.append("event_%d_contract"%i)
    return result(errors)

_FAULTS={
"s01":[("double_application","value",999),("causal_frontier","next",999),("pending_conservation","pending",[999])],
"s02":[("stale_resurrection","visible",{"invented":"x"}),("lost_tombstone","tombstones",["invented"]),("value_fabrication","visible",{"k0":"wrong"})],
"s03":[("invented_alignment","head","invented"),("ambiguity_erasure","decision","advance"),("missing_ancestry","missing",["invented"])],
"s04":[("partial_visibility","visible",{"invented":1}),("abandoned_transaction","open","invented"),("lost_parse_failure","errors",999)],
"s05":[("rights_creation","available",999),("double_spend","spent",999),("lost_transfer","pending",["invented"])],
"s06":[("wrong_base_apply","value",999),("stale_ack","acknowledged",999),("duplicate_request","effects",[{"type":"snapshot","base":999}])],
"s07":[("premature_finalize","data",[999]),("overlap_double_count","received",999),("transfer_identity","id","invented")],
"s08":[("lost_disjoint_edit","merged",{"invented":1}),("hidden_conflict","conflicts",[["invented"]]),("absence_null_collapse","merged",None)],
"dev-s01":[("wrong_token_accept","connected","invented"),("lost_offer","pending","invented"),("non_atomic_reset","connected",999)],
"dev-s02":[("partial_swap","pair",[999,0]),("false_acceptance","accepted",None),("lost_pair","pair",[])]}

def fault_cases(task_id):
    case=public_cases(task_id)[0];correct=reference(task_id,case);out=[]
    for name,key,bad in _FAULTS[task_id]:
        changed=cloned(correct)
        index=next((i for i,x in enumerate(changed) if x[key]!=bad),0)
        changed[index][key]=cloned(bad)
        out.append({"name":name,"case":cloned(case),"outputs":changed})
    return out

_JS_COMMON=r'''
const lex=(a,b)=>{const x=Array.from(a),y=Array.from(b);for(let i=0;i<Math.min(x.length,y.length);i++){const d=x[i].codePointAt(0)-y[i].codePointAt(0);if(d)return d;}return x.length-y.length;};
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const put=(o,k,v)=>Object.defineProperty(o,k,{value:v,writable:true,enumerable:true,configurable:true});
const canon=x=>x===undefined?'!absent':x===null?'null':Array.isArray(x)?'['+x.map(canon).join(',')+']':typeof x==='object'?'{'+Object.keys(x).sort(lex).map(k=>JSON.stringify(k)+':'+canon(x[k])).join(',')+'}':JSON.stringify(x);
const eq=(a,b)=>canon(a)===canon(b);
'''

_JS={
"s01":r'''if(!state)state={seen:{},slots:{},next:1,value:0};let status;const k=event.id,q=event.seq;
if(own(state.seen,k))status=eq(state.seen[k],event)?'duplicate':'conflict';else if(own(state.slots,q))status='conflict';else if(q<state.next)status='stale';else{status='accepted';put(state.seen,k,event);put(state.slots,q,event.delta);while(own(state.slots,state.next)){state.value+=state.slots[state.next];delete state.slots[state.next++];}}
return {state,output:{status,value:state.value,next:state.next,pending:Object.keys(state.slots).map(Number).sort((a,b)=>a-b)}};''',
"s02":r'''if(!state)state={};const rank=x=>[x.version,x.deleted?1:0,x.actor,x.value];let newer=!own(state,event.key);if(!newer){const a=rank(event),b=rank(state[event.key]);for(let i=0;i<4;i++){if(a[i]!==b[i]){newer=a[i]>b[i];break;}}}if(newer)put(state,event.key,event);const visible={},tombstones=[];for(const k of Object.keys(state).sort(lex)){if(state[k].deleted)tombstones.push(k);else put(visible,k,state[k].value);}return {state,output:{visible,tombstones}};''',
"s03":r'''if(!state)state={graph:{},head:null};const g=JSON.parse(JSON.stringify(state.graph));let bad=false;for(const r of event.records){if(own(g,r.id)&&!eq(g[r.id],r))bad=true;else put(g,r.id,r);}if(!bad)state.graph=g;const walk=h=>{const p=[];while(h!==null&&own(state.graph,h)){p.push(h);h=state.graph[h].parent;}p.push(h);return p;};const a=walk(state.head),b=walk(event.head);const missing=[...new Set([a[a.length-1],b[b.length-1]].filter(x=>x!==null))].sort(lex);let decision;if(bad)decision='conflict';else if(state.head===event.head)decision='same';else if(b.includes(state.head)){decision='advance';state.head=event.head;}else if(a.includes(event.head))decision='ahead';else decision=missing.length?'unknown':'fork';return {state,output:{head:state.head,decision,missing}};''',
"s04":r'''if(!state)state={visible:{},open:null,staged:{},buf:[],drop:false,errors:0};const fail=()=>{state.open=null;state.staged={};state.errors++;};
const utf8=bs=>{let s='';for(let i=0;i<bs.length;){let b=bs[i++],cp,n,min;if(b<128){cp=b;n=0;min=0;}else if(b>=194&&b<=223){cp=b&31;n=1;min=128;}else if(b>=224&&b<=239){cp=b&15;n=2;min=2048;}else if(b>=240&&b<=244){cp=b&7;n=3;min=65536;}else throw Error('utf8');for(let j=0;j<n;j++){if(i>=bs.length||bs[i]<128||bs[i]>191)throw Error('utf8');cp=cp*64+(bs[i++]&63);}if(cp<min||cp>1114111||(cp>=55296&&cp<=57343))throw Error('utf8');s+=String.fromCodePoint(cp);}return s;};
const text=x=>typeof x==='string'&&Array.from(x).every(ch=>{const n=ch.codePointAt(0);return n<55296||n>57343;});const scalar=x=>x===null||typeof x==='boolean'||Number.isSafeInteger(x)||text(x);const frame=()=>{try{const f=JSON.parse(utf8(state.buf));state.buf=[];if(!f||Array.isArray(f)||typeof f!=='object')throw Error();const keys=Object.keys(f).sort(lex).join(',');if(f.op==='begin'&&keys==='id,op'&&text(f.id)&&state.open===null){state.open=f.id;state.staged={};}else if(f.op==='put'&&keys==='key,op,value'&&text(f.key)&&scalar(f.value)&&state.open!==null)put(state.staged,f.key,f.value);else if(f.op==='commit'&&keys==='id,op'&&text(f.id)&&state.open===f.id){for(const k of Object.keys(state.staged))put(state.visible,k,state.staged[k]);state.open=null;state.staged={};}else if(f.op==='abort'&&keys==='op'){state.open=null;state.staged={};}else throw Error();}catch(e){state.buf=[];fail();}};
if(event.type==='finish'){if(state.buf.length)fail();state.buf=[];state.drop=false;if(state.open!==null)fail();}else for(const b of event.bytes){if(state.drop){if(b===10)state.drop=false;continue;}if(b===10)frame();else{state.buf.push(b);if(state.buf.length>config.maxBytes){state.buf=[];state.drop=true;fail();}}}return {state,output:{visible:state.visible,open:state.open,buffered:state.buf.length,errors:state.errors}};''',
"s05":r'''if(!state)state={available:config.initial,spent:0,spends:{},sends:{},received:{}};const t=event.type,k=event.id;let status='ignored';if(t==='receive'){if(!own(config.grants,k)||config.grants[k]!==event.amount)status='invalid';else if(own(state.received,k))status='duplicate';else{put(state.received,k,true);state.available+=event.amount;status='accepted';}}else if(t==='spend'||t==='send'){const book=t==='spend'?state.spends:state.sends;if(own(book,k))status=book[k].amount===event.amount?'duplicate':'conflict';else if(state.available<event.amount)status='insufficient';else{put(book,k,{amount:event.amount,status:'pending'});state.available-=event.amount;if(t==='spend')state.spent+=event.amount;status='accepted';}}else if(own(state.sends,k)&&state.sends[k].status==='pending'){state.sends[k].status=t;status='accepted';if(t==='cancel')state.available+=state.sends[k].amount;}return {state,output:{status,available:state.available,spent:state.spent,pending:Object.keys(state.sends).filter(k=>state.sends[k].status==='pending').sort(lex),received:Object.keys(state.received).sort(lex)}};''',
"s06":r'''if(!state)state={version:config.version,value:config.value,acknowledged:-1,latch:false};let need=false,effects=[];if(event.type==='delta'){if(event.base===state.version&&event.version>event.base){state.version=event.version;state.value+=event.delta;state.latch=false;}else if(event.version>state.version)need=true;}else if(event.type==='snapshot'){if(event.version>state.version){state.version=event.version;state.value=event.value;state.latch=false;}else if(event.version===state.version&&event.value!==state.value)need=true;}else if(event.version===state.version)state.acknowledged=state.version;if(need&&!state.latch){effects=[{type:'snapshot',base:state.version}];state.latch=true;}return {state,output:{version:state.version,value:state.value,acknowledged:state.acknowledged,effects}};''',
"s07":r'''if(!state)state={id:null,length:0,bytes:{}};let status='ignored',data=null;if(event.type==='begin'){if(!Number.isInteger(event.length)||event.length<0||event.length>config.maxLength)status='invalid';else if(state.id===event.id&&state.length!==event.length)status='conflict';else{if(state.id!==event.id)state={id:event.id,length:event.length,bytes:{}};status='ok';}}else if(state.id!==null&&state.id===event.id){if(event.type==='finish'){status=Object.keys(state.bytes).length===state.length?'complete':'incomplete';if(status==='complete')data=Array.from({length:state.length},(_,i)=>state.bytes[i]);}else{const b=event.bytes,o=event.offset;if(!Number.isInteger(o)||o<0||o+b.length>state.length||b.some(x=>!Number.isInteger(x)||x<0||x>255)||b.reduce((a,x)=>a+x,0)%251!==event.checksum)status='invalid';else if(b.some((x,i)=>own(state.bytes,o+i)&&state.bytes[o+i]!==x))status='conflict';else{b.forEach((x,i)=>put(state.bytes,o+i,x));status='ok';}}}return {state,output:{status,id:state.id,received:Object.keys(state.bytes).length,data}};''',
"s08":r'''const conflicts=[];const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);const merge=(b,l,r,p)=>{if(eq(l,r))return l;if(eq(l,b))return r;if(eq(r,b))return l;if(obj(l)&&obj(r)&&(b===undefined||obj(b))){const out={},base=b||{};for(const k of [...new Set([...Object.keys(base),...Object.keys(l),...Object.keys(r)])].sort(lex)){const value=merge(own(base,k)?base[k]:undefined,own(l,k)?l[k]:undefined,own(r,k)?r[k]:undefined,p.concat(k));if(value!==undefined)put(out,k,value);}return out;}conflicts.push(p);return b;};return {state:null,output:{merged:merge(event.base,event.local,event.remote,[]),conflicts}};''',
"dev-s01":r'''if(!state)state={pending:null,connected:null};if(event.type==='offer')state={pending:event.token,connected:null};else if(event.type==='reset')state={pending:null,connected:null};else if(state.pending===event.token)state={pending:null,connected:event.token};return {state,output:state};''',
"dev-s02":r'''if(!state)state={pair:[config.a,config.b]};const accepted=eq(state.pair,event.expect);if(accepted)state.pair=event.replace;return {state,output:{accepted,pair:state.pair}};'''}

def reference_source(task_id):
    return _JS_COMMON+"\nfunction solve({config,state,event}) {\n"+_JS[task_id]+"\n}\n"
