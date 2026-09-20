import historical from './evidence-data.js';
import {createSelectionUrlCommitter} from './selection-url.js';

const $ = id => document.getElementById(id);
const views = ['overview','experiment','evidence','methods','install'];
let activeView = 'overview';
function navigate(event) {
  const requested = location.hash.slice(1) || 'overview';
  const current = requested === 'case-content' ? activeView : requested === 'about' ? 'install' : views.includes(requested) ? requested : 'overview';
  activeView = current;
  for (const id of views) $(id).hidden = id !== current;
  for (const link of document.querySelectorAll('.case-nav a')) {
    if (link.hash === '#'+current) link.setAttribute('aria-current','page');
    else link.removeAttribute('aria-current');
  }
  if (requested === 'about') $('about').scrollIntoView();
  else window.scrollTo(0,0);
  if (event) {
    const heading = (requested === 'about' ? $('about') : $(current)).querySelector('h1,h2');
    if (heading) { heading.tabIndex = -1; heading.focus({preventScroll:true}); }
  }
}
document.querySelector('.skip-link').addEventListener('click', event => {
  event.preventDefault();
  const heading = $(activeView).querySelector('h1');
  heading.tabIndex = -1;
  heading.focus();
});
addEventListener('hashchange', navigate);
navigate();

const old = historical.frozenResults.study3.results.novelty;
$('historical-novelty').textContent = `the recorded configuration scored +${old.diff.toFixed(3)} points in judged novelty on ${old.nPairs} problems (original 95% interval ${old.ci95[0].toFixed(3)} to ${old.ci95[1].toFixed(3)}). higher usefulness or genuineness was not established. the result belongs to the legacy sampler and incomplete rating matrix.`;

const node = (tag, text, cls) => { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (cls) el.className = cls; return el; };
const signed = (n, digits=3) => (n>0?'+':'')+n.toFixed(digits);
const pValue = p => p < .0001 ? '<0.0001' : '='+p.toFixed(4);
const github = path => 'https://github.com/globalanomalyindex/wildcard/blob/main/'+path.split('/').map(encodeURIComponent).join('/');
let study, index = 0;
const commitSelectionUrl = createSelectionUrlCommitter();

function renderAction(action) {
  const item = node('li');
  item.append(node('h3',action.action),node('p',action.mechanism));
  const details = node('details'); details.append(node('summary','implementation, check & evaluation'));
  const list = node('dl');
  for (const [label,key] of [['implementation','implementation'],['observable check','check'],['risk / limit','risk']]) list.append(node('dt',label),node('dd',action[key]));
  details.append(list);
  for (const judge of ['j1','j2']) {
    const rating = action.ratings[judge];
    const qualified = rating.constraint_valid && rating.feasible && rating.actionable;
    const matched = action.globallyBankMatched[judge];
    const description = `${judge} · ${qualified?'qualified':'not qualified'} · ${matched?'mechanism found in baseline bank':'no baseline match recorded'}`;
    const report = node('div',undefined,'rating-note');
    report.append(node('p',description),node('p',rating.reason));
    report.append(node('p',`mechanism group: ${rating.mechanism_group}. direct bank reference: ${rating.baseline_match ?? 'none'}.`));
    if (matched && rating.baseline_match === null) report.append(node('p','another candidate in this judge’s same mechanism group matches the bank, so the group is counted as non-new throughout this brief.'));
    details.append(report);
  }
  item.append(details); return item;
}
function renderCondition(side, row) {
  const arm = $('condition-'+side).value;
  const record = row.arms[arm];
  let cue = 'no outside cue';
  if (arm === 'R') cue = 'the donor name is omitted from the prompt.';
  if (arm === 'LR') cue = `donor name: ${row.assignedCard.label}`;
  if (arm === 'XR') cue = `experimental mismatch: ${row.mismatchLabel}. this name deliberately does not identify the supplied relation.`;
  $(side+'-cue').textContent = cue;
  const score = record.score;
  $(side+'-score').textContent = `${score.qnm.toFixed(1)} QNM@4 · ${score.qdm.toFixed(1)} qualified mechanisms · average of two judges`;
  const actions = $(side+'-actions'); actions.replaceChildren();
  if (record.actions.length) for (const action of record.actions) actions.append(renderAction(action));
  else actions.append(node('li',`no actions recorded. status: ${record.status}. ${record.error || 'a valid abstention contributes zero mechanisms.'}`));
  const source = record.sources.find(s=>s.path.endsWith('/response.txt')) || record.sources.find(s=>s.path.endsWith('/record.json')) || record.sources[0];
  $(side+'-source').href = github(source.path);
}
function renderTask() {
  const row = study.perProblem[index], task = row.task;
  $('task-select').value = row.taskId;
  $('task-count').textContent = `${index+1} / ${study.perProblem.length}`;
  $('task-family').textContent = task.family.replaceAll('_',' ');
  $('task-title').textContent = task.title;
  $('task-brief').textContent = task.brief;
  $('task-constraints').replaceChildren(...[...task.constraints,...(task.success_criteria || []).map(v=>'success check: '+v)].map(v=>node('li',v)));
  $('task-relation').textContent = row.assignedCard.relation;
  $('task-boundary').textContent = row.assignedCard.boundary;
  $('task-source-fact').textContent = 'source fact: '+row.assignedCard.source_fact;
  $('task-source-note').textContent = row.assignedCard.source_note;
  $('task-sources').replaceChildren(...row.assignedCard.source_urls.map((url,i)=>{
    const a=node('a',`source ${i+1}: ${new URL(url).hostname}`);a.href=url;return a;
  }));
  $('bank-summary').textContent = `inspect the independent reference bank · ${row.bank.realizedActions} actions`;
  $('bank-actions').replaceChildren(...row.bank.actions.map(action=>{
    const item=node('li');item.append(node('h3',action.action),node('p',action.mechanism));
    const details=node('details');details.append(node('summary','implementation, check & risk'),node('p','reference id: '+action.id));
    for (const key of ['implementation','check','risk']) details.append(node('p',key+': '+action[key]));
    item.append(details);return item;
  }));
  $('bank-sources').replaceChildren(...row.bank.requests.map((request,i)=>{
    const source=request.sources.find(s=>s.path.endsWith('/response.txt'));
    const a=node('a',`bank response ${i+1} ↗`,'mono-link');a.href=github(source.path);return a;
  }), ...Object.entries(row.judgeSources).map(([judge,sources])=>{
    const a=node('a',`${judge} complete evaluation ↗`,'mono-link');a.href=github(sources.find(s=>s.path.endsWith('/response.txt')).path);return a;
  }));
  renderCondition('left',row);renderCondition('right',row);
  commitSelectionUrl({task:row.taskId,left:$('condition-left').value,right:$('condition-right').value});
}
function chart(primary) {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 520 146');svg.setAttribute('role','img');
  const title=document.createElementNS(ns,'title');title.textContent=`Named minus unnamed relation: ${signed(primary.difference)} QNM@4; 95% interval ${signed(primary.ci95[0])} to ${signed(primary.ci95[1])}.`;svg.append(title);
  const max=Math.max(.5,Math.ceil(Math.max(Math.abs(primary.ci95[0]),Math.abs(primary.ci95[1]))*2)/2), x=v=>50+(v+max)/(2*max)*420;
  const el=(tag,attrs)=>{const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);svg.append(e);return e;};
  el('line',{x1:50,x2:470,y1:82,y2:82,stroke:'#1e1e1e','stroke-width':1});
  el('line',{x1:x(0),x2:x(0),y1:25,y2:100,stroke:'#1e1e1e','stroke-dasharray':'3 4','stroke-width':1});
  el('line',{x1:x(primary.ci95[0]),x2:x(primary.ci95[1]),y1:54,y2:54,stroke:'#1e1e1e','stroke-width':3});
  for (const v of primary.ci95) el('line',{x1:x(v),x2:x(v),y1:46,y2:62,stroke:'#1e1e1e','stroke-width':2});
  el('circle',{cx:x(primary.difference),cy:54,r:7,fill:'#eb8853',stroke:'#1e1e1e','stroke-width':2});
  for (const v of [-max,0,max]) { const t=el('text',{x:x(v),y:107,'text-anchor':'middle','font-size':12,'font-family':'monospace',fill:'#1e1e1e'});t.textContent=v===0?'0':signed(v,1); }
  const l=el('text',{x:50,y:137,'font-size':11,'font-family':'monospace',fill:'#1e1e1e'});l.textContent='fewer new mechanisms';
  const r=el('text',{x:470,y:137,'text-anchor':'end','font-size':11,'font-family':'monospace',fill:'#1e1e1e'});r.textContent='more new mechanisms';
  $('primary-chart').replaceChildren(svg);
}
function renderResults() {
  const p=study.analysis.primary;
  const verdict=p.directionalEvidence==='positive'?'the named relation produced more baseline-relative new mechanisms.':p.directionalEvidence==='negative'?'the named relation produced fewer baseline-relative new mechanisms.':'the study did not resolve an advantage from naming the donor.';
  const result=$('primary-result'); result.replaceChildren(node('p',verdict));
  result.append(node('p','amended measurement: the original primary halted after an invalid judge block. all 64 blocks were remeasured under a published instrument correction.','result-details'));
  result.append(node('p',`${signed(p.difference)} QNM@4 · 95% interval [${signed(p.ci95[0])}, ${signed(p.ci95[1])}] · paired mean sign-flip p${pValue(p.test.p)}`,'result-details'));
  result.append(node('p',`named relation: ${p.meanX.toFixed(3)} · relation only: ${p.meanY.toFixed(3)}. ${study.nTasks} paired briefs. a null result is not evidence of equivalence.`,'result-details'));
  chart(p);
  const table=node('table');table.append(node('caption','all four conditions · mean mechanisms per set of up to four actions'));
  const head=node('thead'),tr=node('tr');for(const title of ['condition','QNM@4','QDM@4','valid sets']){const th=node('th',title);th.scope='col';tr.append(th);}head.append(tr);table.append(head);
  const body=node('tbody');for(const arm of ['S','R','LR','XR']){const row=node('tr'),th=node('th',arm);th.scope='row';const valid=study.perProblem.filter(r=>['success','abstention'].includes(r.arms[arm].status)).length;row.append(th,node('td',study.analysis.descriptive[arm].means.qnm.toFixed(3)),node('td',study.analysis.descriptive[arm].means.qdm.toFixed(3)),node('td',`${valid}/${study.nTasks}`));body.append(row);}table.append(body);result.append(table);
  result.append(node('p','invalid generation responses score zero in the main estimate. valid sets include explicit abstentions; they are not a quality guarantee.','result-details'));
  const effects=$('brief-effects');effects.replaceChildren(node('h2','every brief. the same comparison.'),node('p','named relation minus relation only, in QNM@4. each value averages the two judges. select a brief to inspect its actions; individual differences are descriptive.'));
  const groups=node('div',undefined,'brief-families');
  for (const family of [...new Set(study.perProblem.map(r=>r.task.family))]) {
    const group=node('section');group.append(node('h3',family.replaceAll('_',' ')));
    const list=node('div',undefined,'brief-list');
    for (const row of study.perProblem.filter(r=>r.task.family===family)) {
      const difference=row.arms.LR.score.qnm-row.arms.R.score.qnm;
      const button=node('button');button.type='button';button.append(node('span',row.taskId),node('span',signed(difference,1)));
      button.setAttribute('aria-label',`${row.task.title}: named minus unnamed ${signed(difference,1)} QNM. Inspect this brief.`);
      button.addEventListener('click',()=>{index=study.perProblem.indexOf(row);$('condition-left').value='R';$('condition-right').value='LR';renderTask();location.hash='experiment';});
      list.append(button);
    }
    group.append(list);groups.append(group);
  }
  effects.append(groups);effects.hidden=false;
  $('diagnostic-summary').textContent = `separate counterfactual checks · ${study.diagnosticSummary.passedPairs}/${study.diagnosticSummary.pairs} pairs passed the exact contract`;
  $('diagnostic-results').replaceChildren(...study.diagnostics.map(fixture=>{
    const details=node('details');details.append(node('summary',`${fixture.id} · ${fixture.title} · ${fixture.pairPassed?'pass':'exact-match failure'}`));
    for (const variant of fixture.variants) {
      details.append(node('h3',`variant ${variant.variant} · ${variant.passed?'pass':'exact-match failure'}`));
      details.append(node('p',`expected decision: ${variant.expectedDecision}. expected trace: ${JSON.stringify(variant.expectedTrace)}`));
      details.append(node('p',`observed decision: ${variant.result?.decision ?? variant.status}. observed trace: ${JSON.stringify(variant.result?.trace ?? null)}`));
      if (variant.result) details.append(node('p',variant.result.action),node('p',variant.result.explanation));
      const link=node('a','open recorded diagnostic ↗','mono-link');link.href=github(variant.source.path);details.append(link);
    }
    return details;
  }));
  $('diagnostic-inspector').hidden=false;
}
async function loadStudy() {
  try {
    const response = await fetch('../data/transfer-study.json');
    if (!response.ok) throw new Error('study artifact unavailable');
    const value=await response.json();
    if (!value.complete || value.cohort!=='main' || value.nTasks!==32 || value.perProblem.length!==32 || value.measurementPanel!=='remeasurement' || value.originalPrimaryStatus!=='halted') throw new Error('study artifact is incomplete');
    study=value;
    for (const row of study.perProblem) {const option=node('option',`${row.taskId} · ${row.task.title}`);option.value=row.taskId;$('task-select').append(option);}
    const params=new URLSearchParams(location.search);
    const requested=study.perProblem.findIndex(r=>r.taskId===params.get('task'));if(requested>=0)index=requested;
    for(const side of ['left','right'])if(['S','R','LR','XR'].includes(params.get(side)))$('condition-'+side).value=params.get(side);
    $('task-select').addEventListener('change',()=>{index=study.perProblem.findIndex(r=>r.taskId===$('task-select').value);renderTask();});
    $('task-previous').addEventListener('click',()=>{index=(index+study.perProblem.length-1)%study.perProblem.length;renderTask();});
    $('task-next').addEventListener('click',()=>{index=(index+1)%study.perProblem.length;renderTask();});
    for(const side of ['left','right'])$('condition-'+side).addEventListener('change',renderTask);
    renderTask();renderResults();$('experiment-loading').hidden=true;$('experiment-workbench').hidden=false;
  } catch(error) {
    $('experiment-loading').replaceChildren(node('span','the recorded data could not be loaded. '));
    const a=node('a','open the complete study in the repository ↗');a.href='https://github.com/globalanomalyindex/wildcard/tree/main/research/transfer-v1';$('experiment-loading').append(a);
    $('primary-result').replaceChildren(node('p','the result artifact could not be loaded. use the source link below to inspect the analysis.'));
  }
}
loadStudy();
