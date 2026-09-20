"""Pure controller traces: executable behavior, not rendered or user-tested UX."""
import json
import math
from .common import cloned, rng_for, result, check_count, REGIMES

_COMMON=" Return one output per event. State is opaque JSON, initially null. Output objects have exactly the documented keys; object key order is irrelevant, array order is significant. IDs are nonempty ASCII strings. Values are JSON scalars unless stated otherwise. Numeric values and intermediate arithmetic are safe integers; integral JSON notations such as 1 and 1.0 denote the same number, while booleans are distinct. Strings contain Unicode scalar values without unpaired surrogates. Inputs have at most 48 events and eight simultaneous identities. Ordinary instances vary values; boundary instances emphasize empty/disabled/equality/no-op states; adversarial instances reorder callbacks and interleave edits; shift instances use longer traces/more identities within the same rules. These tasks test controller state/effects only, not visual quality, browser integration or screen-reader usability. "
_SPECS={
"u01":("Latest-request search controller",["identity","ordering","visibility","causality"],"config={} . Initially mounted=true,query='',current=null,loading=false,result=null,error=null. search={type:'search',id,query} while mounted cancels a loading current request (effect {type:'cancel',id}), sets the new query/current, loading=true,error=null and emits {type:'request',id,query}; prior result remains visible. Issued IDs are unique within an instance, queries may repeat. success={type:'success',id,result} or failure={type:'failure',id,error} only settles a mounted, loading, matching current request. Success replaces result and clears error; failure sets error and retains result. Both stop loading. cancel stops a loading request and emits its cancel effect, clears current and error, retaining query/result. dispose does the same cancellation then resets all data to initial values except mounted=false. mount resets to initial mounted state only when previously disposed. All other events while disposed are ignored. Output {mounted,query,current,loading,result,error,effects}; effects occur only on the current event, in cancel-before-request order. Late errors after success are ignored."),
"u02":("Scoped timeline state editing",["propagation","visibility","ordering","isolation"],"config={frames:[unique IDs],initial:object}. Maintain each frame's persistent patch, one-frame patch and optional full snapshot. edit={type:'edit',id,scope:'persistent'|'one',key,value} sets that patch field; snapshot={type:'snapshot',id,values:object} replaces that frame with a full snapshot and clears BOTH patches. insert={type:'insert',after:null|ID,id:new ID} inserts an empty frame at start when after=null, otherwise immediately after a known frame; missing after or duplicate new ID is ignored. Edits to unknown IDs are ignored. Expand in current frame order from initial: apply a frame's snapshot if present, then its persistent patch to the carried state; display a copy with its one-frame patch applied. Carry does NOT include the one-frame patch. A snapshot is the boundary of earlier persistent scope. Output {frames:[{id,values}]} in current order. Explicit 0 and null are stored values; object edits never delete fields. Insertions inherit the then-current preceding carried state."),
"u03":("Nested dialog focus lifecycle",["isolation","visibility","identity","reversibility"],"config={fallback:ID,elements:{ID:{present:boolean,enabled:boolean}}}; fallback is always present/enabled and cannot be changed. Initial focus=fallback, stack=[]. element={type:'element',id,present,enabled} replaces eligibility for a nonfallback element. open={type:'open',id,opener,focus} pushes a dialog if that dialog ID is absent from stack; focus goes to its requested focus element if eligible, otherwise fallback. close/complete={type:'close'|'complete',id} closes ONLY a matching top dialog, ignoring stale/lower-layer completions. Restore its opener if eligible, otherwise the new top dialog's requested focus if eligible, otherwise fallback. After an element change, if the current focus became ineligible choose the top requested focus if eligible, otherwise fallback. Output {stack:[dialog IDs],active:top ID or null,focus:element ID,inert:[all lower dialog IDs]}. Only the active layer is interactive by this abstract contract. Eligible means present AND enabled."),
"u04":("Acknowledged warning hysteresis",["thresholds","identity","ordering","visibility"],"config={low:integer,high:integer,dwell:positive integer},low<high. Initially lastTime=-1,normal enabled=true, invisible, no critical ID. observe={type:'observe',t:nonnegative integer,level:integer,critical:boolean,id:ID}. Observations with t<=lastTime are ignored; every newer observation advances lastTime. An unacknowledged critical observation immediately shows kind='critical' with its ID and resets normal counters, even when normal mode is disabled; it replaces any previous critical ID. An acknowledged critical ID is ignored apart from lastTime. While critical is visible, normal observations do not change it. Otherwise, when enabled, dwell consecutive newer normal observations level>=high turn an invisible warning on; dwell consecutive level<=low turn a visible normal warning off. Any other newer normal value resets that counter. High and low equality count. ack={type:'ack',id} permanently records the ID; if it matches visible critical, hide it and reset counters. mode={type:'mode',enabled:boolean} resets normal counters, and hides a normal warning only when disabled; it never hides a critical warning. Output {visible:boolean,kind:'normal'|'critical'|null,id:ID|null}, id is nonnull only for visible critical. No timer or future observations are available."),
"u05":("Stable keyboard list selection",["identity","ordering","visibility","fairness"],"config={options:[{id,disabled:boolean}]} with unique IDs. Initially active=first enabled ID, selected=null. options={type:'options',options:[...]} replaces the view: retain active if enabled and present, else first enabled; retain selected only if enabled and present, else null. key={type:'key',key:'ArrowDown'|'ArrowUp'|'Home'|'End'|'Enter'} moves active among enabled options, wrapping arrows. Home/End choose first/last; Enter selects active; an empty enabled list leaves both null. click={type:'click',id} sets active and selected only for an enabled present ID. Disabled options never become active or selected. Output {active:ID|null,selected:ID|null}. Reorder retains stable IDs, not indices."),
"u06":("Revision-owned optimistic form",["identity","causality","reversibility","visibility"],"config={fields:object}. Start revision=0,status='idle',pending={}. edit={type:'edit',set:object,remove:[keys]} applies removals then sets, increments revision even if no-op, and status=idle. submit={type:'submit',id,set:object,remove:[keys]} for an ID never previously submitted saves the pre-submit fields, applies the same patch, increments revision, records that revision, makes this ID current owner, and sets status=saving; repeated IDs are ignored. success={type:'success',id,fields:object} or failure={type:'failure',id} removes a known pending submission. It can change form fields/status ONLY if it is current owner AND its recorded revision equals current revision. Such success replaces fields with server fields, increments revision,status=saved; such failure restores its saved pre-submit fields, increments revision,status=error. Both clear current owner. Other known outcomes only remove pending; unknown/repeated outcomes are ignored. A newer user edit or submission protects newer values from old outcomes. Output {fields,revision,status,pending:[sorted unsettled IDs]}. Null is a real value, deletion uses remove."),
"u07":("Nested transactional undo history",["reversibility","isolation","retention","ordering"],"config={initial:object,limit:integer 1..4}. Events set={type:'set',key,value}, delete={type:'delete',key}, or {type:'begin'|'commit'|'cancel'|'undo'|'redo'}. Maintain document, bounded undo/redo histories and nested group stack. Begin saves the current document. Edits inside groups change the document without history entries. Commit closes the innermost group; only an outermost commit whose final document differs from its saved start records that start in undo and clears redo. Cancel restores and closes the innermost group's start, without recording history. A changed edit outside groups records its pre-edit document in undo and clears redo. No-op edits and empty/no-op groups preserve redo. Undo/redo during a group are ignored; otherwise move current document to the opposite history and restore the most recent source entry. Retain at most limit entries in each history, dropping oldest. Commit/cancel without a group and unavailable undo/redo are ignored. Output {document,canUndo:boolean,canRedo:boolean,depth:integer}; availability booleans are false while a group is open. Deep object equality ignores key order."),
"u08":("Stable range and multiselection",["identity","ordering","visibility","propagation"],"config={options:[{id,disabled:boolean}]} unique IDs; initially selected=[],anchor=null. view={type:'view',options:[...]} replaces ordered options, drops selected IDs absent or disabled, and clears an absent/disabled anchor. click={type:'click',id,shift:boolean,ctrl:boolean} ignores absent/disabled IDs. A plain click replaces selection with id and sets anchor=id. Ctrl without Shift toggles id and sets anchor=id. Shift uses the current valid anchor, or establishes clicked id as anchor if absent; select the inclusive range in the CURRENT view between anchor and id, skipping disabled options. Ctrl+Shift unions that range with existing selection; Shift alone replaces selection. A Shift operation preserves an existing anchor. Output {selected:[lexicographically sorted IDs],anchor:ID|null}. Selection cannot retain filtered-out IDs under this explicit policy."),
"dev-u01":("Bounded numeric stepper",["thresholds","visibility","conservation"],"config={min:integer,max:integer,value:integer},min<=value<=max. Events {type:'step',amount:integer} or {type:'set',value:integer}. Clamp the requested new value into [min,max]. Output {value,atMin:boolean,atMax:boolean}. This stateless-bound numeric controller has no asynchronous callbacks, selection or undo."),
"dev-u02":("Single-open disclosure set",["identity","visibility","isolation"],"config={ids:[unique IDs]}; initially open=null. Events {type:'toggle',id} toggle a known ID between open and closed, replacing any other open ID; {type:'close'} closes all. Unknown IDs are ignored. Output {open:ID|null,expanded:[open ID] or []}. There is no focus lifecycle, dialog stack or keyboard-navigation policy.")}
TASKS=[{"id":k,"family":"ui","split":"development" if k.startswith("dev-") else "main","title":v[0],"tags":v[1],"specification":v[2]+_COMMON} for k,v in _SPECS.items()]

def make_case(task_id,regime,seed):
    if task_id not in _SPECS or regime not in REGIMES:raise ValueError("unknown task or regime")
    r=rng_for(seed,["ui",task_id,regime]);config={}
    if task_id=="u01":
        events=[{"type":"search","id":"r1","query":"A"},{"type":"search","id":"r2","query":"B"},{"type":"success","id":"r1","result":"old"},{"type":"search","id":"r3","query":"A"},{"type":"failure","id":"r2","error":"old"},{"type":"success","id":"r3","result":r.randint(0,9)},{"type":"failure","id":"r3","error":"late"},{"type":"search","id":"r4","query":"C"},{"type":"dispose"},{"type":"success","id":"r4","result":"gone"},{"type":"mount"}]
        if regime=="boundary":events+=[{"type":"cancel"},{"type":"mount"}]
        if regime=="shift":events+=[{"type":"search","id":"r5","query":""},{"type":"failure","id":"r5","error":"failed"},{"type":"search","id":"r6","query":""},{"type":"cancel"},{"type":"success","id":"r6","result":"stale"}]
        if regime=="adversarial":events.insert(5,{"type":"success","id":"r2","result":"late B"})
    elif task_id=="u02":
        config={"frames":["a","b","c","d"],"initial":{"x":r.randint(1,5),"y":1}}
        events=[{"type":"edit","id":"b","scope":"persistent","key":"x","value":0},{"type":"edit","id":"c","scope":"one","key":"x","value":None},{"type":"snapshot","id":"d","values":{"x":8}},{"type":"edit","id":"a","scope":"persistent","key":"y","value":3},{"type":"insert","after":"b","id":"e"},{"type":"edit","id":"c","scope":"persistent","key":"z","value":2},{"type":"snapshot","id":"c","values":{"q":None}}]
        if regime=="boundary":events+=[{"type":"insert","after":None,"id":"first"},{"type":"insert","after":"missing","id":"bad"}]
        if regime=="shift":events+=[{"type":"insert","after":"e","id":"f"},{"type":"edit","id":"f","scope":"one","key":"x","value":7},{"type":"edit","id":"b","scope":"persistent","key":"x","value":9}]
        if regime=="adversarial":events.insert(3,{"type":"edit","id":"d","scope":"one","key":"x","value":99})
    elif task_id=="u03":
        config={"fallback":"root","elements":{k:{"present":True,"enabled":True} for k in ["root","button","field","inner"]}}
        events=[{"type":"open","id":"d1","opener":"button","focus":"field"},{"type":"open","id":"d2","opener":"field","focus":"inner"},{"type":"complete","id":"d1"},{"type":"element","id":"field","present":False,"enabled":True},{"type":"close","id":"d2"},{"type":"element","id":"button","present":True,"enabled":False},{"type":"close","id":"d1"}]
        if regime=="boundary":events+=[{"type":"close","id":"missing"},{"type":"element","id":"root","present":False,"enabled":False}]
        if regime=="shift":events+=[{"type":"open","id":"d3","opener":"root","focus":"inner"},{"type":"element","id":"inner","present":False,"enabled":False},{"type":"close","id":"d3"}]
        if regime=="adversarial":events.insert(2,{"type":"open","id":"d1","opener":"root","focus":"root"})
    elif task_id=="u04":
        config={"low":3,"high":7,"dwell":2 if regime!="shift" else 3};events=[]
        levels=[7,7,5,3,3,8,3,8]
        for i,level in enumerate(levels):events.append({"type":"observe","t":i,"level":level,"critical":False,"id":"n"+str(i)})
        events += [{"type":"mode","enabled":False},{"type":"observe","t":9,"level":0,"critical":True,"id":"critical"},{"type":"observe","t":8,"level":9,"critical":True,"id":"stale"},{"type":"ack","id":"critical"},{"type":"observe","t":10,"level":9,"critical":True,"id":"critical"},{"type":"mode","enabled":True}]
        if regime=="shift":events += [{"type":"observe","t":11+i,"level":7,"critical":False,"id":"x"+str(i)} for i in range(4)]
        if regime=="adversarial":events.insert(2,{"type":"observe","t":1,"level":0,"critical":False,"id":"same-time"})
        if regime=="boundary":events.append({"type":"ack","id":"future"})
    elif task_id=="u05":
        opts=[{"id":"a","disabled":False},{"id":"b","disabled":True},{"id":"c","disabled":False}];config={"options":opts}
        events=[{"type":"key","key":"ArrowDown"},{"type":"key","key":"Enter"},{"type":"options","options":list(reversed(opts))},{"type":"key","key":"ArrowDown"},{"type":"key","key":"Home"},{"type":"click","id":"b"},{"type":"options","options":[{"id":"c","disabled":True},{"id":"d","disabled":False}]},{"type":"key","key":"End"},{"type":"key","key":"Enter"}]
        if regime=="boundary":events += [{"type":"options","options":[]},{"type":"key","key":"Enter"},{"type":"key","key":"ArrowUp"}]
        if regime=="shift":events += [{"type":"options","options":[{"id":chr(97+i),"disabled":i%2==0} for i in range(7)]},{"type":"key","key":"ArrowUp"},{"type":"key","key":"Enter"}]
        if regime=="adversarial":events.insert(3,{"type":"options","options":[{"id":"c","disabled":True},{"id":"a","disabled":False}]})
    elif task_id=="u06":
        config={"fields":{"name":"old","count":r.randint(0,5)}}
        patch=lambda typ,ident=None,**fields:dict({"type":typ,"set":fields,"remove":[]},**({"id":ident} if ident else {}))
        events=[patch("submit","s1",name="one"),patch("edit",name="newer"),{"type":"failure","id":"s1"},patch("submit","s2",name="two"),patch("submit","s3",name="three"),{"type":"success","id":"s2","fields":{"name":"old server"}},{"type":"failure","id":"s3"},patch("submit","s4",name="four"),{"type":"success","id":"s4","fields":{"name":"server","count":None}},{"type":"failure","id":"s4"}]
        if regime=="boundary":events.insert(3,{"type":"edit","set":{"zero":0},"remove":["count"]})
        if regime=="shift":events += [patch("submit","s5",name="five"),{"type":"edit","set":{},"remove":["name"]},{"type":"success","id":"s5","fields":{"name":"resurrect"}}]
        if regime=="adversarial":events.insert(5,patch("submit","s2",name="duplicate"))
    elif task_id=="u07":
        config={"initial":{"x":0},"limit":1 if regime=="boundary" else 3}
        events=[{"type":"set","key":"x","value":1},{"type":"begin"},{"type":"set","key":"x","value":2},{"type":"begin"},{"type":"set","key":"y","value":3},{"type":"cancel"},{"type":"undo"},{"type":"commit"},{"type":"undo"},{"type":"redo"},{"type":"undo"},{"type":"set","key":"x","value":1},{"type":"redo"},{"type":"undo"},{"type":"set","key":"z","value":0},{"type":"redo"}]
        if regime=="shift":events += [{"type":"set","key":"x","value":i} for i in range(4,9)]+[{"type":"undo"}]*4
        if regime=="adversarial":events += [{"type":"begin"},{"type":"delete","key":"x"},{"type":"begin"},{"type":"set","key":"x","value":9},{"type":"commit"},{"type":"cancel"}]
    elif task_id=="u08":
        opts=[{"id":k,"disabled":k=="b"} for k in "abcd"];config={"options":opts}
        click=lambda k,s=False,c=False:{"type":"click","id":k,"shift":s,"ctrl":c}
        events=[click("a"),click("d",True),click("c",False,True),{"type":"view","options":list(reversed(opts))},click("a",True),{"type":"view","options":[{"id":"d","disabled":False},{"id":"e","disabled":False}]},click("e",True),click("d",True,True),click("d",False,True)]
        if regime=="boundary":events += [{"type":"view","options":[]},click("missing",True,True)]
        if regime=="shift":events += [{"type":"view","options":[{"id":k,"disabled":k=="f"} for k in "defgh"]},click("h",True,True)]
        if regime=="adversarial":events.insert(2,click("b",True,True))
    elif task_id=="dev-u01":
        config={"min":-2,"max":5,"value":r.randint(-2,5)}
        events=[{"type":"step","amount":1},{"type":"step","amount":99},{"type":"step","amount":-99},{"type":"set","value":0},{"type":"step","amount":0}]
    else:
        config={"ids":["a","b","c"]};events=[{"type":"toggle","id":"a"},{"type":"toggle","id":"b"},{"type":"toggle","id":"b"},{"type":"toggle","id":"unknown"},{"type":"toggle","id":"c"},{"type":"close"}]
    # Fixed contract, varied legal event ordering and state; no donor or arm
    # enters generation. Private seeds are not just new numeric constants.
    for j in range(8 if regime=="shift" else 4):
        if task_id=="u01":
            typ=r.choice(["success","failure","cancel","dispose","mount"]);extra={"type":typ}
            if typ in ("success","failure"):
                extra["id"]=r.choice(["r1","r2","r3","r4","r5","r6"]);extra["result" if typ=="success" else "error"]=r.choice([None,0,"noise"])
        elif task_id=="u02":extra={"type":"edit","id":r.choice(["a","b","c","d","e","f"]),"scope":r.choice(["one","persistent"]),"key":r.choice(["x","y","z"]),"value":r.choice([None,0,False,r.randint(1,8)])}
        elif task_id=="u03":
            if j%2:extra={"type":r.choice(["close","complete"]),"id":r.choice(["d1","d2","d3"])}
            else:extra={"type":"element","id":r.choice(["button","field","inner"]),"present":r.choice([True,False]),"enabled":r.choice([True,False])}
        elif task_id=="u04":
            if j%3==0:extra={"type":"mode","enabled":r.choice([True,False])}
            elif j%3==1:extra={"type":"ack","id":r.choice(["critical","future","n1"])}
            else:extra={"type":"observe","t":r.randint(0,24),"level":r.randint(0,10),"critical":r.random()<.3,"id":r.choice(["critical","future","n1"])}
        elif task_id=="u05":
            if j%3==0:extra={"type":"options","options":[{"id":k,"disabled":r.random()<.35} for k in r.sample(list("abcdefg"),r.randint(0,7))]}
            else:extra={"type":"key","key":r.choice(["Home","End","ArrowDown","ArrowUp","Enter"])}
        elif task_id=="u06":
            if j%2:extra={"type":r.choice(["failure","success"]),"id":r.choice(["s1","s2","s3","s4","s5"])};extra.update({"fields":{"name":"interleaved","zero":0}} if extra["type"]=="success" else {})
            else:extra={"type":"edit","set":{r.choice(["name","count","zero"]):r.choice([None,0,"edit"])},"remove":r.sample(["name","count"],r.randint(0,1))}
        elif task_id=="u07":
            typ=r.choice(["set","delete","begin","commit","cancel","undo","redo"]);extra={"type":typ}
            if typ in ("set","delete"):extra["key"]=r.choice(["x","y","z"])
            if typ=="set":extra["value"]=r.choice([None,0,False,r.randint(1,9)])
        elif task_id=="u08":
            if j%3==0:extra={"type":"view","options":[{"id":k,"disabled":r.random()<.25} for k in r.sample(list("abcdefg"),r.randint(0,7))]}
            else:extra={"type":"click","id":r.choice(list("abcdefg")),"shift":r.choice([True,False]),"ctrl":r.choice([True,False])}
        elif task_id=="dev-u01":extra={"type":"step","amount":r.randint(-10,10)}
        else:extra={"type":"toggle","id":r.choice(["a","b","c","unknown"])}
        events.insert(r.randrange(len(events)+1),extra)
    names={};reserved={"search","success","failure","cancel","dispose","mount","edit","snapshot","insert","persistent","one","element","open","close","complete","observe","ack","mode","options","key","click","ArrowDown","ArrowUp","Home","End","Enter","submit","set","delete","begin","commit","undo","redo","view","step","toggle"}
    def name(x):
        if x=="" or x in reserved:return x
        if x not in names:names[x]="v%06d"%r.randrange(1000000)+"_"+str(len(names))
        return names[x]
    def visit(x,user_map=False):
        if isinstance(x,str):return name(x)
        if isinstance(x,list):return [visit(y,user_map) for y in x]
        if isinstance(x,dict):
            return {(name(k) if user_map else k):({name(ident):visit(flags) for ident,flags in v.items()} if k=="elements" and not user_map else visit(v,user_map or k in ("initial","fields","values","set"))) for k,v in x.items()}
        return x
    return visit({"config":config,"events":cloned(events)})

def public_cases(task_id):return [{"id":"p"+str(i+1),**make_case(task_id,x,201+i)} for i,x in enumerate(REGIMES)]

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

def _equal(a,b):return _json_equal(a,b)
def reference(task_id,case):
    if task_id not in _SPECS:raise ValueError("unknown task")
    c=case["config"];outputs=[];s={}
    if task_id=="u01":s={"mounted":True,"query":"","current":None,"loading":False,"result":None,"error":None}
    if task_id=="u02":s={"frames":[{"id":k,"persistent":{},"one":{},"snapshot":None} for k in c["frames"]]}
    if task_id=="u03":s={"elements":cloned(c["elements"]),"stack":[],"focus":c["fallback"]}
    if task_id=="u04":s={"last":-1,"enabled":True,"visible":False,"kind":None,"id":None,"count":0,"acked":set()}
    if task_id=="u05":s={"options":cloned(c["options"]),"active":next((x["id"] for x in c["options"] if not x["disabled"]),None),"selected":None}
    if task_id=="u06":s={"fields":cloned(c["fields"]),"revision":0,"status":"idle","pending":{},"seen":set(),"owner":None}
    if task_id=="u07":s={"document":cloned(c["initial"]),"undo":[],"redo":[],"groups":[]}
    if task_id=="u08":s={"options":cloned(c["options"]),"selected":set(),"anchor":None}
    if task_id=="dev-u01":s={"value":c["value"]}
    if task_id=="dev-u02":s={"open":None}
    for e in case["events"]:
        typ=e["type"]
        if task_id=="u01":
            effects=[]
            if typ=="mount" and not s["mounted"]:s={"mounted":True,"query":"","current":None,"loading":False,"result":None,"error":None}
            elif s["mounted"]:
                if typ in ("search","cancel","dispose"):
                    if s["loading"]:effects.append({"type":"cancel","id":s["current"]})
                    if typ=="search":s.update(query=e["query"],current=e["id"],loading=True,error=None);effects.append({"type":"request","id":e["id"],"query":e["query"]})
                    elif typ=="cancel":s.update(current=None,loading=False,error=None)
                    else:s={"mounted":False,"query":"","current":None,"loading":False,"result":None,"error":None}
                elif typ in ("success","failure") and s["loading"] and s["current"]==e["id"]:
                    s["loading"]=False
                    if typ=="success":s.update(result=cloned(e["result"]),error=None)
                    else:s["error"]=e["error"]
            out={**s,"effects":effects}
        elif task_id=="u02":
            frame=next((x for x in s["frames"] if x["id"]==e.get("id")),None)
            if typ=="insert" and frame is None:
                idx=-1 if e["after"] is None else next((i for i,x in enumerate(s["frames"]) if x["id"]==e["after"]),None)
                if idx is not None:s["frames"].insert(idx+1,{"id":e["id"],"persistent":{},"one":{},"snapshot":None})
            elif frame is not None:
                if typ=="snapshot":frame.update(snapshot=cloned(e["values"]),persistent={},one={})
                elif typ=="edit":frame[e["scope"]][e["key"]]=cloned(e["value"])
            carry=cloned(c["initial"]);rows=[]
            for f in s["frames"]:
                if f["snapshot"] is not None:carry=cloned(f["snapshot"])
                carry.update(f["persistent"]);rows.append({"id":f["id"],"values":{**carry,**f["one"]}})
            out={"frames":rows}
        elif task_id=="u03":
            def eligible(k):return k in s["elements"] and s["elements"][k]["present"] and s["elements"][k]["enabled"]
            def fallback():return s["stack"][-1]["focus"] if s["stack"] and eligible(s["stack"][-1]["focus"]) else c["fallback"]
            if typ=="element":
                if e["id"]!=c["fallback"]:s["elements"][e["id"]]={"present":e["present"],"enabled":e["enabled"]}
                if not eligible(s["focus"]):s["focus"]=fallback()
            elif typ=="open" and all(x["id"]!=e["id"] for x in s["stack"]):s["stack"].append(cloned(e));s["focus"]=e["focus"] if eligible(e["focus"]) else c["fallback"]
            elif typ in ("close","complete") and s["stack"] and s["stack"][-1]["id"]==e["id"]:
                old=s["stack"].pop();s["focus"]=old["opener"] if eligible(old["opener"]) else fallback()
            ids=[x["id"] for x in s["stack"]];out={"stack":ids,"active":ids[-1] if ids else None,"focus":s["focus"],"inert":ids[:-1]}
        elif task_id=="u04":
            if typ=="ack":
                s["acked"].add(e["id"])
                if s["kind"]=="critical" and s["id"]==e["id"]:s.update(visible=False,kind=None,id=None,count=0)
            elif typ=="mode":
                s["enabled"]=e["enabled"];s["count"]=0
                if not e["enabled"] and s["kind"]=="normal":s.update(visible=False,kind=None,id=None)
            elif e["t"]>s["last"]:
                s["last"]=e["t"]
                if e["critical"]:
                    if e["id"] not in s["acked"]:s.update(visible=True,kind="critical",id=e["id"],count=0)
                elif s["kind"]!="critical" and s["enabled"]:
                    qualifying=e["level"]<=c["low"] if s["visible"] else e["level"]>=c["high"]
                    s["count"]=s["count"]+1 if qualifying else 0
                    if s["count"]>=c["dwell"]:
                        s["visible"]=not s["visible"];s["kind"]="normal" if s["visible"] else None;s["id"]=None;s["count"]=0
            out={k:s[k] for k in ("visible","kind","id")}
        elif task_id=="u05":
            if typ=="options":s["options"]=cloned(e["options"])
            enabled=[x["id"] for x in s["options"] if not x["disabled"]]
            if s["active"] not in enabled:s["active"]=enabled[0] if enabled else None
            if s["selected"] not in enabled:s["selected"]=None
            if typ=="click" and e["id"] in enabled:s.update(active=e["id"],selected=e["id"])
            elif typ=="key" and enabled:
                key=e["key"];idx=enabled.index(s["active"])
                if key=="Enter":s["selected"]=s["active"]
                elif key in ("Home","End"):s["active"]=enabled[0 if key=="Home" else -1]
                else:s["active"]=enabled[(idx+(1 if key=="ArrowDown" else -1))%len(enabled)]
            out={"active":s["active"],"selected":s["selected"]}
        elif task_id=="u06":
            if typ=="edit" or (typ=="submit" and e["id"] not in s["seen"]):
                before=cloned(s["fields"])
                for k in e["remove"]:s["fields"].pop(k,None)
                s["fields"].update(cloned(e["set"]));s["revision"]+=1
                if typ=="edit":s["status"]="idle"
                else:s["seen"].add(e["id"]);s["pending"][e["id"]]={"before":before,"revision":s["revision"]};s["owner"]=e["id"];s["status"]="saving"
            elif typ in ("success","failure") and e["id"] in s["pending"]:
                record=s["pending"].pop(e["id"])
                if s["owner"]==e["id"] and record["revision"]==s["revision"]:
                    s["fields"]=cloned(e["fields"] if typ=="success" else record["before"]);s["revision"]+=1;s["status"]="saved" if typ=="success" else "error";s["owner"]=None
            out={"fields":s["fields"],"revision":s["revision"],"status":s["status"],"pending":sorted(s["pending"])}
        elif task_id=="u07":
            def push(key,doc):s[key].append(cloned(doc));s[key]=s[key][-c["limit"]:]
            if typ=="begin":s["groups"].append(cloned(s["document"]))
            elif typ in ("commit","cancel") and s["groups"]:
                before=s["groups"].pop()
                if typ=="cancel":s["document"]=before
                elif not s["groups"] and not _equal(before,s["document"]):push("undo",before);s["redo"]=[]
            elif typ in ("undo","redo") and not s["groups"] and s[typ]:
                push("redo" if typ=="undo" else "undo",s["document"]);s["document"]=s[typ].pop()
            elif typ in ("set","delete"):
                before=cloned(s["document"])
                if typ=="set":s["document"][e["key"]]=cloned(e["value"])
                else:s["document"].pop(e["key"],None)
                if not s["groups"] and not _equal(before,s["document"]):push("undo",before);s["redo"]=[]
            out={"document":s["document"],"canUndo":bool(s["undo"]) and not s["groups"],"canRedo":bool(s["redo"]) and not s["groups"],"depth":len(s["groups"])}
        elif task_id=="u08":
            if typ=="view":s["options"]=cloned(e["options"])
            enabled=[x["id"] for x in s["options"] if not x["disabled"]];ids=[x["id"] for x in s["options"]]
            s["selected"]&=set(enabled)
            if s["anchor"] not in enabled:s["anchor"]=None
            if typ=="click" and e["id"] in enabled:
                k=e["id"]
                if e["shift"]:
                    if s["anchor"] is None:s["anchor"]=k
                    lo,hi=sorted([ids.index(s["anchor"]),ids.index(k)]);span=set(ids[lo:hi+1])&set(enabled)
                    s["selected"]=(s["selected"]|span) if e["ctrl"] else span
                elif e["ctrl"]:s["selected"]^={k};s["anchor"]=k
                else:s["selected"]={k};s["anchor"]=k
            out={"selected":sorted(s["selected"]),"anchor":s["anchor"]}
        elif task_id=="dev-u01":
            requested=s["value"]+e["amount"] if typ=="step" else e["value"];s["value"]=max(c["min"],min(c["max"],requested));out={"value":s["value"],"atMin":s["value"]==c["min"],"atMax":s["value"]==c["max"]}
        else:
            if typ=="close":s["open"]=None
            elif e["id"] in c["ids"]:s["open"]=None if s["open"]==e["id"] else e["id"]
            out={"open":s["open"],"expanded":[] if s["open"] is None else [s["open"]]}
        outputs.append(cloned(out))
    return outputs

def _audit(task,c,events):
    """Independent prefix reconstruction; no call into the executable model."""
    if task=="u01":
        mounted=True;query="";ticket=None;busy=False;shown=None;error=None;effects=[]
        for x in events:
            effects=[];t=x["type"]
            if not mounted:
                if t=="mount":mounted=True;query="";ticket=None;busy=False;shown=None;error=None
                continue
            if t=="search":
                if busy:effects.append({"type":"cancel","id":ticket})
                query=x["query"];ticket=x["id"];busy=True;error=None;effects.append({"type":"request","id":ticket,"query":query})
            if t in ("cancel","dispose"):
                if busy:effects.append({"type":"cancel","id":ticket})
                ticket=None;busy=False;error=None
                if t=="dispose":mounted=False;query="";shown=None
            if t in ("success","failure") and busy and x["id"]==ticket:
                busy=False
                if t=="success":shown=x["result"];error=None
                else:error=x["error"]
        return {"mounted":mounted,"query":query,"current":ticket,"loading":busy,"result":shown,"error":error,"effects":effects}
    if task=="u02":
        order=list(c["frames"]);changes={k:[] for k in order}
        for x in events:
            k=x["id"]
            if x["type"]=="insert":
                if k not in changes and (x["after"] is None or x["after"] in order):
                    order.insert(0 if x["after"] is None else order.index(x["after"])+1,k);changes[k]=[]
            elif k in changes:
                if x["type"]=="snapshot":changes[k]=[x]
                else:changes[k].append(x)
        rows=[];carry=cloned(c["initial"])
        for k in order:
            one={};persistent={}
            for edit in changes[k]:
                if edit["type"]=="snapshot":carry=cloned(edit["values"]);one={};persistent={}
                elif edit["scope"]=="one":one[edit["key"]]=edit["value"]
                else:persistent[edit["key"]]=edit["value"]
            carry={**carry,**persistent};rows.append({"id":k,"values":{**carry,**one}})
        return {"frames":rows}
    if task=="u03":
        allowed={k for k,v in c["elements"].items() if v["present"] and v["enabled"]};layers=[];focus=c["fallback"]
        for x in events:
            t=x["type"]
            if t=="element":
                if x["id"]!=c["fallback"]:
                    allowed.discard(x["id"])
                    if x["present"] and x["enabled"]:allowed.add(x["id"])
                if focus not in allowed:focus=layers[-1][2] if layers and layers[-1][2] in allowed else c["fallback"]
            if t=="open" and x["id"] not in [row[0] for row in layers]:
                layers.append((x["id"],x["opener"],x["focus"]));focus=x["focus"] if x["focus"] in allowed else c["fallback"]
            if t in ("close","complete") and layers and layers[-1][0]==x["id"]:
                _,opener,_=layers.pop();candidates=[opener]+([layers[-1][2]] if layers else [])+[c["fallback"]];focus=next(k for k in candidates if k in allowed)
        ids=[x[0] for x in layers]
        return {"stack":ids,"active":ids[-1] if ids else None,"focus":focus,"inert":ids[:-1]}
    if task=="u04":
        last=-1;enabled=True;kind=None;critical=None;acked=set();run=[]
        for x in events:
            t=x["type"]
            if t=="ack":
                acked.add(x["id"])
                if kind=="critical" and critical==x["id"]:kind=None;critical=None;run=[]
            elif t=="mode":
                enabled=x["enabled"];run=[]
                if not enabled and kind=="normal":kind=None
            elif x["t"]>last:
                last=x["t"]
                if x["critical"]:
                    if x["id"] not in acked:kind="critical";critical=x["id"];run=[]
                elif kind!="critical" and enabled:
                    qualifies=x["level"]>=c["high"] if kind is None else x["level"]<=c["low"]
                    run=run+[x["level"]] if qualifies else []
                    if len(run)==c["dwell"]:kind="normal" if kind is None else None;critical=None;run=[]
        return {"visible":kind is not None,"kind":kind,"id":critical}
    if task=="u05":
        available=[x["id"] for x in c["options"] if not x["disabled"]];active=available[0] if available else None;selected=None
        for x in events:
            if x["type"]=="options":
                available=[row["id"] for row in x["options"] if not row["disabled"]]
                active=active if active in available else available[0] if available else None
                if selected not in available:selected=None
            elif x["type"]=="click":
                if x["id"] in available:active=selected=x["id"]
            elif available:
                key=x["key"]
                if key=="Enter":selected=active
                elif key=="Home":active=available[0]
                elif key=="End":active=available[-1]
                else:
                    cycle=available+available+available;index=available.index(active)+len(available);active=cycle[index+(1 if key=="ArrowDown" else -1)]
        return {"active":active,"selected":selected}
    if task=="u06":
        fields=cloned(c["fields"]);rev=0;status="idle";submitted={};settled=set();owner=None
        for x in events:
            t=x["type"]
            if t=="edit" or t=="submit" and x["id"] not in submitted:
                previous=cloned(fields);fields={k:v for k,v in fields.items() if k not in x["remove"]};fields.update(x["set"]);rev+=1
                if t=="edit":status="idle"
                else:submitted[x["id"]]=(rev,previous);owner=x["id"];status="saving"
            elif t in ("success","failure") and x["id"] in submitted and x["id"] not in settled:
                k=x["id"];settled.add(k);submitted_rev,before=submitted[k]
                if owner==k and submitted_rev==rev:
                    fields=cloned(before if t=="failure" else x["fields"]);rev+=1;status="error" if t=="failure" else "saved";owner=None
        return {"fields":fields,"revision":rev,"status":status,"pending":sorted(set(submitted)-settled)}
    if task=="u07":
        doc=cloned(c["initial"]);past=[];future=[];starts=[]
        for x in events:
            t=x["type"];old=cloned(doc);record=False
            if t=="begin":starts.append(old)
            elif t=="cancel" and starts:doc=starts.pop()
            elif t=="commit" and starts:
                old=starts.pop();record=not starts and not _equal(old,doc)
            elif t in ("set","delete"):
                doc={k:v for k,v in doc.items() if k!=x["key"]}
                if t=="set":doc[x["key"]]=x["value"]
                record=not starts and not _equal(old,doc)
            elif t=="undo" and not starts and past:
                future=(future+[old])[-c["limit"]:];doc=past[-1];past=past[:-1]
            elif t=="redo" and not starts and future:
                past=(past+[old])[-c["limit"]:];doc=future[-1];future=future[:-1]
            if record:past=(past+[old])[-c["limit"]:];future=[]
        return {"document":doc,"canUndo":bool(past) and not starts,"canRedo":bool(future) and not starts,"depth":len(starts)}
    if task=="u08":
        view=[x["id"] for x in c["options"]];allowed={x["id"] for x in c["options"] if not x["disabled"]};selected=[];anchor=None
        for x in events:
            if x["type"]=="view":
                view=[y["id"] for y in x["options"]];allowed={y["id"] for y in x["options"] if not y["disabled"]};selected=[k for k in selected if k in allowed]
                if anchor not in allowed:anchor=None
            elif x["id"] in allowed:
                target=x["id"]
                if x["shift"]:
                    anchor=target if anchor is None else anchor;start=view.index(anchor);end=view.index(target)
                    span=[k for j,k in enumerate(view) if min(start,end)<=j<=max(start,end) and k in allowed]
                    selected=list(set(selected+span)) if x["ctrl"] else span
                else:
                    anchor=target
                    if not x["ctrl"]:selected=[target]
                    elif target in selected:selected.remove(target)
                    else:selected.append(target)
        return {"selected":sorted(selected),"anchor":anchor}
    if task=="dev-u01":
        value=c["value"]
        for x in events:
            value=value+x["amount"] if x["type"]=="step" else x["value"]
            if value<c["min"]:value=c["min"]
            if value>c["max"]:value=c["max"]
        return {"value":value,"atMin":value==c["min"],"atMax":value==c["max"]}
    opened=[]
    for x in events:
        if x["type"]=="close":opened=[]
        elif x["id"] in c["ids"]:opened=[] if opened==[x["id"]] else [x["id"]]
    return {"open":opened[0] if opened else None,"expanded":opened}

def check(task_id,case,outputs):
    errors=check_count(case,outputs)
    if errors:return result(errors)
    if task_id not in _SPECS:raise ValueError("unknown task")
    for i,actual in enumerate(outputs):
        expected=_audit(task_id,case["config"],case["events"][:i+1])
        if not _equal(actual,expected):errors.append("event_%d_contract"%i)
    return result(errors)

_FAULTS={
"u01":[("stale_result","result","invented"),("settlement_loading","loading",None),("missing_request_effect","effects",[{"type":"request","id":"invented","query":"bad"}])],
"u02":[("scope_propagation","frames",[]),("snapshot_boundary","frames",[{"id":"d","values":{"x":999}}]),("one_frame_leak","frames",None)],
"u03":[("lost_focus_restore","focus","invented"),("lower_layer_interactivity","inert",["invented"]),("stale_completion","active","invented")],
"u04":[("critical_suppression","visible",None),("acknowledged_reappearance","id","invented"),("normal_hysteresis","kind","invented")],
"u05":[("disabled_focus","active","b"),("disabled_selection","selected","b"),("identity_loss","active","invented")],
"u06":[("stale_rollback","fields",{"name":"invented"}),("wrong_revision_owner","revision",999),("lost_pending_submission","pending",["invented"])],
"u07":[("partial_group_undo","document",{"invented":1}),("history_availability","canUndo",None),("nested_group_boundary","depth",999)],
"u08":[("disabled_range_member","selected",["b"]),("removed_anchor","anchor","invented"),("lost_range","selected",None)],
"dev-u01":[("upper_bound","value",999),("lower_bound_flag","atMin",None),("upper_bound_flag","atMax",None)],
"dev-u02":[("unknown_disclosure","open","invented"),("two_open_panels","expanded",["a","b"]),("expansion_mismatch","expanded",None)]}
def fault_cases(task_id):
    case=public_cases(task_id)[0];good=reference(task_id,case);faults=[]
    for name,key,bad in _FAULTS[task_id]:
        altered=cloned(good);i=next((j for j,x in enumerate(altered) if not _equal(x[key],bad)),0);altered[i][key]=cloned(bad)
        faults.append({"name":name,"case":cloned(case),"outputs":altered})
    return faults

_JS_COMMON=r'''
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const put=(o,k,v)=>Object.defineProperty(o,k,{value:v,writable:true,enumerable:true,configurable:true});
const copy=x=>JSON.parse(JSON.stringify(x));
const canon=x=>x===null?'null':Array.isArray(x)?'['+x.map(canon).join(',')+']':typeof x==='object'?'{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canon(x[k])).join(',')+'}':JSON.stringify(x);
const eq=(a,b)=>canon(a)===canon(b);
const patch=(target,source)=>{for(const k of Object.keys(source))put(target,k,source[k]);};
'''
_JS={
"u01":r'''const initial=m=>({mounted:m,query:'',current:null,loading:false,result:null,error:null});if(!state)state=initial(true);let effects=[];const t=event.type;if(t==='mount'&&!state.mounted)state=initial(true);else if(state.mounted){if(['search','cancel','dispose'].includes(t)){if(state.loading)effects.push({type:'cancel',id:state.current});if(t==='search'){state.query=event.query;state.current=event.id;state.loading=true;state.error=null;effects.push({type:'request',id:event.id,query:event.query});}else if(t==='cancel'){state.current=null;state.loading=false;state.error=null;}else state=initial(false);}else if(['success','failure'].includes(t)&&state.loading&&state.current===event.id){state.loading=false;if(t==='success'){state.result=event.result;state.error=null;}else state.error=event.error;}}return {state,output:{...state,effects}};''',
"u02":r'''const empty=id=>({id,persistent:{},one:{},snapshot:null});if(!state)state={frames:config.frames.map(empty)};const f=state.frames.find(x=>x.id===event.id);if(event.type==='insert'&&!f){const index=event.after===null?-1:state.frames.findIndex(x=>x.id===event.after);if(event.after===null||index>=0)state.frames.splice(index+1,0,empty(event.id));}else if(f){if(event.type==='snapshot'){f.snapshot=event.values;f.persistent={};f.one={};}else if(event.type==='edit')put(f[event.scope],event.key,event.value);}let carry=copy(config.initial);const frames=[];for(const row of state.frames){if(row.snapshot!==null)carry=copy(row.snapshot);patch(carry,row.persistent);const values=copy(carry);patch(values,row.one);frames.push({id:row.id,values});}return {state,output:{frames}};''',
"u03":r'''if(!state)state={elements:config.elements,stack:[],focus:config.fallback};const eligible=k=>own(state.elements,k)&&state.elements[k].present&&state.elements[k].enabled;const fallback=()=>state.stack.length&&eligible(state.stack[state.stack.length-1].focus)?state.stack[state.stack.length-1].focus:config.fallback;if(event.type==='element'){if(event.id!==config.fallback)put(state.elements,event.id,{present:event.present,enabled:event.enabled});if(!eligible(state.focus))state.focus=fallback();}else if(event.type==='open'&&!state.stack.some(x=>x.id===event.id)){state.stack.push(event);state.focus=eligible(event.focus)?event.focus:config.fallback;}else if(['close','complete'].includes(event.type)&&state.stack.length&&state.stack[state.stack.length-1].id===event.id){const old=state.stack.pop();state.focus=eligible(old.opener)?old.opener:fallback();}const ids=state.stack.map(x=>x.id);return {state,output:{stack:ids,active:ids.length?ids[ids.length-1]:null,focus:state.focus,inert:ids.slice(0,-1)}};''',
"u04":r'''if(!state)state={last:-1,enabled:true,visible:false,kind:null,id:null,count:0,acked:{}};const hide=()=>{state.visible=false;state.kind=null;state.id=null;state.count=0;};if(event.type==='ack'){put(state.acked,event.id,true);if(state.kind==='critical'&&state.id===event.id)hide();}else if(event.type==='mode'){state.enabled=event.enabled;state.count=0;if(!event.enabled&&state.kind==='normal')hide();}else if(event.t>state.last){state.last=event.t;if(event.critical){if(!own(state.acked,event.id)){state.visible=true;state.kind='critical';state.id=event.id;state.count=0;}}else if(state.kind!=='critical'&&state.enabled){const qualifies=state.visible?event.level<=config.low:event.level>=config.high;state.count=qualifies?state.count+1:0;if(state.count>=config.dwell){state.visible=!state.visible;state.kind=state.visible?'normal':null;state.id=null;state.count=0;}}}return {state,output:{visible:state.visible,kind:state.kind,id:state.id}};''',
"u05":r'''if(!state){const first=config.options.find(x=>!x.disabled);state={options:config.options,active:first?first.id:null,selected:null};}if(event.type==='options')state.options=event.options;const enabled=state.options.filter(x=>!x.disabled).map(x=>x.id);if(!enabled.includes(state.active))state.active=enabled.length?enabled[0]:null;if(!enabled.includes(state.selected))state.selected=null;if(event.type==='click'&&enabled.includes(event.id))state.active=state.selected=event.id;else if(event.type==='key'&&enabled.length){const k=event.key,i=enabled.indexOf(state.active);if(k==='Enter')state.selected=state.active;else if(k==='Home')state.active=enabled[0];else if(k==='End')state.active=enabled[enabled.length-1];else state.active=enabled[(i+(k==='ArrowDown'?1:-1)+enabled.length)%enabled.length];}return {state,output:{active:state.active,selected:state.selected}};''',
"u06":r'''if(!state)state={fields:config.fields,revision:0,status:'idle',pending:{},seen:{},owner:null};const t=event.type;if(t==='edit'||(t==='submit'&&!own(state.seen,event.id))){const before=copy(state.fields);for(const k of event.remove)delete state.fields[k];patch(state.fields,event.set);state.revision++;if(t==='edit')state.status='idle';else{put(state.seen,event.id,true);put(state.pending,event.id,{before,revision:state.revision});state.owner=event.id;state.status='saving';}}else if(['success','failure'].includes(t)&&own(state.pending,event.id)){const row=state.pending[event.id];delete state.pending[event.id];if(state.owner===event.id&&row.revision===state.revision){state.fields=t==='success'?event.fields:row.before;state.revision++;state.status=t==='success'?'saved':'error';state.owner=null;}}return {state,output:{fields:state.fields,revision:state.revision,status:state.status,pending:Object.keys(state.pending).sort()}};''',
"u07":r'''if(!state)state={document:config.initial,undo:[],redo:[],groups:[]};const push=(k,d)=>{state[k].push(copy(d));state[k]=state[k].slice(-config.limit);};const t=event.type;if(t==='begin')state.groups.push(copy(state.document));else if(['commit','cancel'].includes(t)&&state.groups.length){const before=state.groups.pop();if(t==='cancel')state.document=before;else if(!state.groups.length&&!eq(before,state.document)){push('undo',before);state.redo=[];}}else if(['undo','redo'].includes(t)&&!state.groups.length&&state[t].length){push(t==='undo'?'redo':'undo',state.document);state.document=state[t].pop();}else if(t==='set'||t==='delete'){const before=copy(state.document);if(t==='set')put(state.document,event.key,event.value);else delete state.document[event.key];if(!state.groups.length&&!eq(before,state.document)){push('undo',before);state.redo=[];}}return {state,output:{document:state.document,canUndo:!!state.undo.length&&!state.groups.length,canRedo:!!state.redo.length&&!state.groups.length,depth:state.groups.length}};''',
"u08":r'''if(!state)state={options:config.options,selected:[],anchor:null};if(event.type==='view')state.options=event.options;const ids=state.options.map(x=>x.id),enabled=state.options.filter(x=>!x.disabled).map(x=>x.id);state.selected=state.selected.filter(k=>enabled.includes(k));if(!enabled.includes(state.anchor))state.anchor=null;if(event.type==='click'&&enabled.includes(event.id)){const k=event.id;if(event.shift){if(state.anchor===null)state.anchor=k;const a=ids.indexOf(state.anchor),b=ids.indexOf(k),span=ids.slice(Math.min(a,b),Math.max(a,b)+1).filter(x=>enabled.includes(x));state.selected=event.ctrl?[...new Set(state.selected.concat(span))]:span;}else if(event.ctrl){state.selected=state.selected.includes(k)?state.selected.filter(x=>x!==k):state.selected.concat(k);state.anchor=k;}else{state.selected=[k];state.anchor=k;}}state.selected.sort();return {state,output:{selected:state.selected,anchor:state.anchor}};''',
"dev-u01":r'''if(!state)state={value:config.value};state.value=Math.max(config.min,Math.min(config.max,event.type==='step'?state.value+event.amount:event.value));return {state,output:{value:state.value,atMin:state.value===config.min,atMax:state.value===config.max}};''',
"dev-u02":r'''if(!state)state={open:null};if(event.type==='close')state.open=null;else if(config.ids.includes(event.id))state.open=state.open===event.id?null:event.id;return {state,output:{open:state.open,expanded:state.open===null?[]:[state.open]}};'''}

def reference_source(task_id):return _JS_COMMON+"\nfunction solve({config,state,event}) {\n"+_JS[task_id]+"\n}\n"
