const $=id=>document.getElementById(id);
const el=(tag,text,cls)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;};
const pretty=value=>JSON.stringify(value,null,2);
const github=path=>'https://github.com/globalanomalyindex/wildcard/blob/main/'+path.split('/').map(encodeURIComponent).join('/');
const labels={D:'direct rule',R:'matched outside relation',X:'shuffled outside relation'};
let study,task,traces=[],caseIndex=0,eventIndex=0,loadVersion=0,urlTimer;
const cache=new Map();
const query=new URL(location.href).searchParams;
function saveSelection(){clearTimeout(urlTimer);urlTimer=setTimeout(()=>{const url=new URL(location.href);for(const [key,value] of Object.entries({task:task.id,arm:$('working-arm').value,case:String(caseIndex),event:String(eventIndex)}))url.searchParams.set(key,value);history.replaceState(null,'',url);},150);}
function details(title,text){const wrapper=el('details');wrapper.append(el('summary',title),el('p',text));return wrapper;}
function cardView(card){
  const view=$('working-card');view.replaceChildren(el('p','the supplied outside relation','eyebrow'),el('h3',card.label),el('p',card.relation));
  const boundary=details('assumptions, boundary & source',card.boundary);
  const assumptions=el('ul');for(const item of card.assumptions)assumptions.append(el('li',item));boundary.append(assumptions,el('p',card.source_fact));
  for(const source of card.sources){const link=el('a',source.title+' ↗','card-source');const url=new URL(source.url);if(url.protocol==='https:'||url.protocol==='http:')link.href=url.href;boundary.append(link);}
  view.append(boundary);
}
function ruleView(arm){
  const record=task.arms[arm],view=el('article');view.append(el('h3',labels[arm]),el('span',record.feedback.contract.admitted?'rule admitted on public examples':'rule not admitted on public examples','rule-badge'));
  const first=record.initial;
  if(first){view.append(el('p',first.mapping),details('model’s stated assumptions',first.assumptions));const source=el('details');source.append(el('summary','inspect the proposed rule'));const code=el('pre');code.textContent=first.applies+'\n\n'+first.holds;source.append(code);view.append(source);}
  else view.append(el('p','The initial response did not meet the response contract. The common second call was still available.'));
  const checks=record.feedback.publicExecution,passed=checks.filter(row=>row.passed).length;
  view.append(el('p',(checks.length?`${passed}/${checks.length} public traces passed before repair.`:'Public execution was skipped after the invalid initial response.')+' The second program is the scored artifact.','method-note'));
  const report=el('details');report.append(el('summary','inspect the complete public feedback'));const data=el('pre',pretty(record.feedback));report.append(data);view.append(report);return view;
}
function programView(arm){
  const record=task.arms[arm],view=el('details');view.append(el('summary',labels[arm]+': final implementation'));
  view.append(el('p',record.final?.explanation || 'Final response failed validation; every hidden case scores zero.'));
  const source=el('pre',record.final?.program || 'No valid final program.');view.append(source);
  const link=el('a','open the raw final response ↗','mono-link');link.href=github(record.sourcePath);view.append(link);return view;
}
function statusLabel(result){return result.passed?'whole trace passed':'whole trace failed';}
function renderEvent(){
  const trace=traces[caseIndex],arm=$('working-arm').value;
  const count=trace.input.events.length;eventIndex=Math.max(0,Math.min(eventIndex,count-1));
  $('event-position').max=String(Math.max(0,count-1));$('event-position').value=String(eventIndex);$('event-count').textContent=`${eventIndex+1} / ${count}`;
  $('event-previous').disabled=eventIndex===0;$('event-next').disabled=eventIndex===count-1;
  $('event-input').textContent=pretty(trace.input.events[eventIndex]);$('event-expected').textContent=pretty(trace.expected[eventIndex]);
  for(const [side,key] of [['direct','D'],['relation',arm]]){
    const result=trace.arms[key],outputs=Array.isArray(result.outputs)?result.outputs:[];$('trace-'+side+'-status').textContent=statusLabel(result);
    $('event-'+side).textContent=eventIndex<outputs.length?pretty(outputs[eventIndex]):'No recorded output for this event. '+(result.error || result.status);
  }
  $('trace-relation-title').textContent=labels[arm];
  const failures=[['D',trace.arms.D],[arm,trace.arms[arm]]].filter(([,result])=>!result.passed).map(([key,result])=>labels[key]+': '+result.violations.join(', '));
  $('trace-status').textContent=`${trace.regime} · trace ${trace.index+1}. `+(failures.length?failures.join(' · '):'Both programs passed every required output in this trace.');
  saveSelection();
}
function renderCaseOptions(){
  const arm=$('working-arm').value;
  $('working-case').replaceChildren(...traces.map((trace,index)=>{const option=el('option',`${trace.regime} · ${trace.index+1} · direct ${trace.arms.D.passed?'pass':'fail'} / outside ${trace.arms[arm].passed?'pass':'fail'}`);option.value=String(index);return option;}));
  $('working-case').value=String(caseIndex);
  $('working-difference').disabled=!traces.some(trace=>trace.arms.D.passed!==trace.arms[arm].passed);
}
function renderComparison(){
  const arm=$('working-arm').value;
  cardView(arm==='R'?task.matchedCard:task.shuffledCard);
  $('working-rules').replaceChildren(ruleView('D'),ruleView(arm));$('working-programs').replaceChildren(programView('D'),programView(arm));
  $('working-task-score').textContent=`All 256 withheld traces: direct ${task.arms.D.passCount}/256 · ${labels[arm]} ${task.arms[arm].passCount}/256. One task block; differences here are descriptive.`;
  renderCaseOptions();renderEvent();
}
async function chooseTask(id,initial=false){
  const version=++loadVersion;const selected=study.tasks.find(row=>row.id===id)||study.tasks[0];
  $('working-loading').hidden=false;$('working-loading').textContent='loading recorded traces…';$('working-workbench').hidden=true;
  try{
    if(!cache.has(selected.id)){const response=await fetch('../data/working-solutions/'+encodeURIComponent(selected.id)+'.json');if(!response.ok)throw new Error('Trace archive unavailable');cache.set(selected.id,await response.json());}
    if(version!==loadVersion)return;
    const document=cache.get(selected.id);task=document.task;traces=document.traces;
    if(task.id!==selected.id||traces.length!==256)throw new Error('Trace archive failed its identity check');
    caseIndex=initial&&/^\d+$/.test(query.get('case')||'')?Math.min(Number(query.get('case')),traces.length-1):0;
    eventIndex=initial&&/^\d+$/.test(query.get('event')||'')?Number(query.get('event')):0;
    $('working-task').value=task.id;$('working-family').textContent=task.family+' · '+study.cohortLabel;$('working-task-title').textContent=task.title;$('working-spec').textContent=task.specification;
    renderComparison();$('working-loading').hidden=true;$('working-workbench').hidden=false;
  }catch(error){if(version!==loadVersion)return;$('working-loading').textContent='The trace archive could not be loaded. The complete study records remain available in the repository.';$('working-workbench').hidden=true;}
}
$('working-task').addEventListener('change',()=>chooseTask($('working-task').value));
$('working-arm').addEventListener('change',()=>{if(task)renderComparison();});
$('working-case').addEventListener('change',()=>{caseIndex=Number($('working-case').value);eventIndex=0;renderEvent();});
$('event-position').addEventListener('input',()=>{eventIndex=Number($('event-position').value);renderEvent();});
$('event-previous').addEventListener('click',()=>{eventIndex--;renderEvent();});$('event-next').addEventListener('click',()=>{eventIndex++;renderEvent();});
$('working-difference').addEventListener('click',()=>{const arm=$('working-arm').value;for(let offset=1;offset<=traces.length;offset++){const candidate=(caseIndex+offset)%traces.length;if(traces[candidate].arms.D.passed!==traces[candidate].arms[arm].passed){caseIndex=candidate;eventIndex=0;$('working-case').value=String(candidate);renderEvent();break;}}});
try{
  const response=await fetch('../data/working-solutions.json');if(!response.ok)throw new Error('Study unavailable');study=await response.json();
  $('result-title').textContent=study.title;$('working-verdict').textContent=study.verdict;$('working-limit').textContent=study.limit;
  $('working-numbers').replaceChildren(...study.metrics.map(metric=>{const item=el('div');item.append(el('b',metric.value),el('span',metric.label));return item;}));
  $('working-task').replaceChildren(...study.tasks.map(task=>{const option=el('option',task.family+' · '+task.title);option.value=task.id;return option;}));
  if(['R','X'].includes(query.get('arm')))$('working-arm').value=query.get('arm');
  if(study.tasks.length)await chooseTask(query.get('task'),true);else $('working-loading').textContent='No completed execution records are available for this study.';
}catch(error){$('working-verdict').textContent='The evidence summary could not be loaded.';$('working-loading').textContent='Read the complete protocol and recorded artifacts in the repository.';}
