// Same probe for pinned CLI Chromium/Firefox and pinned stable WebKit.
// Recorded data is tested without execution of any generated program.
async (page) => {
  const options = __WORKING_OPTIONS__;
  const checks = [], failures = [], pageErrors = [], resourceErrors = [], consoleErrors = [], cspErrors = [];
  const check = (ok, label) => { (ok ? checks : failures).push(label); };
  const labels = {D:'direct rule',R:'matched outside relation',X:'shuffled outside relation'};
  page.setDefaultTimeout(10000); page.setDefaultNavigationTimeout(15000);
  page.on('pageerror', e => pageErrors.push(e.message));
  page.on('requestfailed', r => resourceErrors.push(r.url()+': '+r.failure()?.errorText));
  page.on('response', r => { if (r.status() >= 400) resourceErrors.push(r.url()+': '+r.status()); });
  page.on('console', m => { if (m.type()==='error') consoleErrors.push(m.text()); if (/content security policy|refused to/i.test(m.text())) cspErrors.push(m.text()); });
  await page.addInitScript(() => {
    window.__workingURLWrites = 0;
    const replace = history.replaceState;
    history.replaceState = function(...args) { window.__workingURLWrites++; return replace.apply(this,args); };
    window.__workingCSP = [];
    document.addEventListener('securitypolicyviolation', e => window.__workingCSP.push(e.violatedDirective));
  });
  const ready = async (target=page, id=null) => target.waitForFunction(id => {
    const bench=document.querySelector('#working-workbench'), selected=document.querySelector('#working-task');
    return bench && !bench.hidden && (!id || selected.value===id);
  }, id);
  const selection = target => target.evaluate(() => {
    const q=new URL(location.href).searchParams;
    return Object.fromEntries(['task','arm','case','event'].map(k=>[k,q.get(k)]));
  });
  await page.goto(options.base+'/working-solutions/'); await ready();
  const study = await page.evaluate(async () => (await fetch('../data/working-solutions.json')).json());
  check(study.tasks.length===study.nTasks && study.tasks.length>0, 'actual summary task count is complete');
  check(await page.locator('#working-task option').count()===study.tasks.length, 'every actual task is selectable');
  check(await page.locator('#working-verdict').textContent()===study.verdict && await page.locator('#working-limit').textContent()===study.limit, 'actual cohort verdict and limitation bind exactly');
  await page.locator('.skip-link').focus();await page.keyboard.press('Enter');
  check(await page.evaluate(()=>document.activeElement?.id==='working-content'),'skip link moves keyboard focus into main content');
  if(options.focusOnly) return {passed:failures.length===0,browser:options.browser,version:page.context().browser().version(),cohort:study.cohort,traceChoices:0,eventObservations:0,checks,failures,pageErrors,resourceErrors,consoleErrors,cspErrors,robustness:[],scope:'focused skip-link regression only'};
  const archives = await page.evaluate(async tasks => Object.fromEntries(await Promise.all(tasks.map(async task => [task.id,await (await fetch('../data/working-solutions/'+encodeURIComponent(task.id)+'.json')).json()]))), study.tasks);
  let traceChoices=0, eventObservations=0;
  for (const summary of study.tasks) {
    const archive=archives[summary.id];
    check(archive.task.id===summary.id && archive.traces.length===256, summary.id+' archive identity and 256 traces');
    await page.locator('#working-task').selectOption(summary.id); await ready(page,summary.id);
    for (const arm of ['R','X']) {
      await page.locator('#working-arm').selectOption(arm);
      const bound=await page.evaluate(({archive,arm,labels}) => {
        const task=archive.task, card=arm==='R'?task.matchedCard:task.shuffledCard;
        const articles=[...document.querySelectorAll('#working-rules article')];
        const programs=[...document.querySelectorAll('#working-programs details')];
        const path=p=>'https://github.com/globalanomalyindex/wildcard/blob/main/'+p.split('/').map(encodeURIComponent).join('/');
        return document.querySelector('#working-task-title').textContent===task.title &&
          document.querySelector('#working-spec').textContent===task.specification &&
          document.querySelector('#working-card h3').textContent===card.label &&
          document.querySelector('#working-card > p:nth-of-type(2)').textContent===card.relation &&
          JSON.stringify([...document.querySelectorAll('#working-card .card-source')].map(a=>a.href))===JSON.stringify(card.sources.map(s=>s.url)) &&
          ['D',arm].every((key,i)=>articles[i].querySelector('h3').textContent===labels[key] &&
            articles[i].querySelector('.rule-badge').textContent===(task.arms[key].feedback.contract.admitted?'rule admitted on public examples':'rule not admitted on public examples') &&
            programs[i].querySelector('pre').textContent===(task.arms[key].final?.program||'No valid final program.') &&
            programs[i].querySelector('a').href===path(task.arms[key].sourcePath)) &&
          document.querySelector('#working-task-score').textContent.includes('direct '+task.arms.D.passCount+'/256') &&
          document.querySelector('#working-task-score').textContent.includes(labels[arm]+' '+task.arms[arm].passCount+'/256');
      }, {archive,arm,labels});
      check(bound, summary.id+'/'+arm+' relation, rule, program, source and score bindings');
      try {
        const observed=await page.evaluate(({archive,arm,labels}) => {
          const $=id=>document.getElementById(id), pretty=v=>JSON.stringify(v,null,2);
          let events=0;
          const assert=(ok,where)=>{if(!ok)throw new Error(archive.task.id+'/'+arm+'/'+where);};
          assert($('working-case').options.length===256,'trace options');
          for(let i=0;i<256;i++) {
            const trace=archive.traces[i], count=trace.input.events.length;
            $('working-case').value=String(i);$('working-case').dispatchEvent(new Event('change',{bubbles:true}));
            assert($('working-case').selectedOptions[0].textContent===`${trace.regime} · ${trace.index+1} · direct ${trace.arms.D.passed?'pass':'fail'} / outside ${trace.arms[arm].passed?'pass':'fail'}`,i+'/label');
            for(const at of [...new Set([0,Math.floor(count/2),count-1])]) {
              $('event-position').value=String(at);$('event-position').dispatchEvent(new Event('input',{bubbles:true}));
              assert($('event-input').textContent===pretty(trace.input.events[at]),i+'/'+at+'/input');
              assert($('event-expected').textContent===pretty(trace.expected[at]),i+'/'+at+'/expected');
              assert($('event-count').textContent===`${at+1} / ${count}`,i+'/'+at+'/position');
              assert($('event-previous').disabled===(at===0)&&$('event-next').disabled===(at===count-1),i+'/'+at+'/navigation bounds');
              for(const [side,key] of [['direct','D'],['relation',arm]]) {
                const result=trace.arms[key], rows=Array.isArray(result.outputs)?result.outputs:[];
                const expected=at<rows.length?pretty(rows[at]):'No recorded output for this event. '+(result.error||result.status);
                assert($('event-'+side).textContent===expected,i+'/'+at+'/'+key+'/recorded output');
                assert($('trace-'+side+'-status').textContent===(result.passed?'whole trace passed':'whole trace failed'),i+'/'+key+'/status');
              }
              assert($('trace-relation-title').textContent===labels[arm],i+'/arm title');events++;
            }
          }
          return {choices:256,events};
        }, {archive,arm,labels});
        traceChoices+=observed.choices;eventObservations+=observed.events;
        check(true,summary.id+'/'+arm+' all 256 choices and first/middle/last events match recorded data');
      } catch (error) { check(false,error.message); }
      const differences=archive.traces.flatMap((trace,i)=>trace.arms.D.passed!==trace.arms[arm].passed?[i]:[]);
      check(await page.locator('#working-difference').isDisabled()===!differences.length,summary.id+'/'+arm+' difference control availability');
      if(differences.length){await page.locator('#working-difference').click();check(await page.locator('#working-case').inputValue()===String(differences[0])&&await page.locator('#event-position').inputValue()==='0',summary.id+'/'+arm+' next difference selects actual discordant trace');}
      await page.locator('#working-case').selectOption('0');
      await page.locator('#event-next').click();
      check(await page.locator('#event-position').inputValue()==='1',summary.id+'/'+arm+' next event');
      await page.locator('#event-previous').click();
      check(await page.locator('#event-position').inputValue()==='0',summary.id+'/'+arm+' previous event');
      await page.locator('#event-position').focus();await page.keyboard.press('ArrowRight');
      check(await page.locator('#event-position').inputValue()==='1',summary.id+'/'+arm+' range keyboard navigation');
    }
  }
  const last=study.tasks.at(-1).id, first=study.tasks[0].id;
  await page.evaluate(({ids,last})=>{
    const change=(id,value,type='change')=>{const e=document.getElementById(id);e.value=value;e.dispatchEvent(new Event(type,{bubbles:true}));};
    window.__workingURLWrites=0;
    for(let i=0;i<180;i++){change('working-task',ids[i%ids.length]);change('working-arm',i%2?'R':'X');change('working-case',String(i%256));change('event-position',String(i%3),'input');}
    change('working-task',last);change('working-arm','X');change('working-case','255');change('event-position','2','input');
  },{ids:study.tasks.map(t=>t.id),last});
  await page.waitForFunction(last=>{const q=new URL(location.href).searchParams;return q.get('task')===last&&q.get('arm')==='X'&&q.get('case')==='255'&&q.get('event')==='2';},last);
  check(await page.evaluate(()=>window.__workingURLWrites)<=2,'rapid selections coalesce URL writes to the final task/arm/trace/event');
  const roundtrip=page.url();await page.reload();await ready(page,last);
  check(JSON.stringify(await selection(page))===JSON.stringify({task:last,arm:'X',case:'255',event:'2'})&&await page.locator('#working-arm').inputValue()==='X'&&await page.locator('#working-case').inputValue()==='255'&&await page.locator('#event-position').inputValue()==='2','URL roundtrip restores visible selection');
  check(page.url()===roundtrip,'roundtrip URL remains stable');
  for(const width of [1440,390,320]) {
    await page.setViewportSize({width,height:width===1440?1024:844});
    check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'no document overflow at '+width);
    for(const selector of ['#working-task','#working-arm','#working-case','#working-difference','#event-position','#event-previous','#event-next']) {
      const box=await page.locator(selector).boundingBox();
      check(box&&box.width>0&&box.x>=-1&&box.x+box.width<=width+1,selector+' visible horizontal bounds at '+width);
    }
    await page.locator('#working-programs details').first().locator('summary').click();
    check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'expanded program scroll stays local at '+width);
    await page.locator('#working-programs details').first().locator('summary').click();
    await page.locator('.case-footer').scrollIntoViewIfNeeded();
    check(await page.locator('.case-footer').evaluate(el=>{const r=el.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight+1;}),'footer reachable at '+width);
    if(options.browser!=='webkit'){await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:options.output+'/working-'+width+'.png',fullPage:true});}
  }
  // Separate pages use explicitly labelled fault-injection fixtures only for
  // error rendering; they are never counted as recorded study observations.
  const robustness=[];
  const isolated=async(name,routeSetup,assertions)=>{
    const p=await page.context().newPage(), errors=[], unexpected=[];
    p.on('pageerror',e=>errors.push(e.message));
    p.on('response',r=>{if(r.status()>=400&&!r.url().includes('/data/working-solutions'))unexpected.push(r.url());});
    try {await routeSetup(p);await p.goto(options.base+'/working-solutions/?task='+encodeURIComponent(first));await assertions(p);check(errors.length===0&&unexpected.length===0,name+' has no uncaught error or unrelated failed asset');robustness.push(name);}
    catch(error){check(false,name+': '+error.message);}finally{await p.close();}
  };
  await isolated('null and partial recorded outputs',async p=>{
    const fixture=JSON.parse(JSON.stringify(archives[first]));
    for(const arm of ['D','R','X']) Object.assign(fixture.traces[0].arms[arm],{passed:false,status:'runtime_error',error:'injected robustness fixture',violations:['runtime_error']});
    fixture.traces[0].arms.D.outputs=null;fixture.traces[0].arms.R.outputs=fixture.traces[0].arms.R.outputs.slice(0,1);fixture.traces[0].arms.X.outputs=[null];
    await p.route('**/data/working-solutions/'+first+'.json',route=>route.fulfill({json:fixture}));
  },async p=>{
    await ready(p,first);check((await p.locator('#event-direct').textContent()).includes('No recorded output for this event.'),'null output array shows runtime fallback');
    await p.locator('#event-next').click();check((await p.locator('#event-relation').textContent()).includes('No recorded output for this event.'),'partial output array shows fallback after its last event');
    await p.locator('#event-previous').click();await p.locator('#working-arm').selectOption('X');check(await p.locator('#event-relation').textContent()==='null','recorded null value is displayed as null');
  });
  await isolated('summary fetch inaccessible',async p=>p.route('**/data/working-solutions.json',route=>route.abort('failed')),async p=>{
    await p.waitForFunction(()=>document.querySelector('#working-verdict').textContent.includes('could not be loaded'));
    check(await p.locator('#working-workbench').isHidden()&&await p.locator('#working-loading').isVisible(),'summary failure shows repository fallback and hides workbench');
  });
  await isolated('archive HTTP error',async p=>p.route('**/data/working-solutions/'+first+'.json',route=>route.fulfill({status:503,body:'injected unavailable archive'})),async p=>{
    await p.waitForFunction(()=>document.querySelector('#working-loading').textContent.includes('could not be loaded'));
    check(await p.locator('#working-workbench').isHidden(),'archive failure cannot leave stale results visible');
  });
  cspErrors.push(...await page.evaluate(()=>window.__workingCSP));
  check(pageErrors.length===0,'zero JavaScript errors for actual data');check(resourceErrors.length===0,'zero failed requests or HTTP errors for actual data');
  check(consoleErrors.length===0,'zero console errors for actual data');check(cspErrors.length===0,'zero CSP failures for actual data');
  return {passed:failures.length===0,browser:options.browser,version:page.context().browser().version(),cohort:study.cohort,tasks:study.tasks.map(t=>t.id),traceChoices,eventObservations,checks,failures,pageErrors,resourceErrors,consoleErrors,cspErrors,robustness,limits:['Fault-injection pages test rendering only and are separate from recorded observations.','No generated model program runs in this probe.','Automated layout/keyboard checks do not replace screen-reader testing.']};
}
