// Executed by the pinned Playwright CLI run-code command, not @playwright/test.
// Options are substituted as a JSON value by test-browser.py; no shell interpolation.
async (page) => {
  const options = __REGRESSION_OPTIONS__;
  const checks = [], errors = [], failedResources = [], cspErrors = [];
  const check = (condition, label) => { if (!condition) throw new Error(label); checks.push(label); };
  page.setDefaultTimeout(8000); page.setDefaultNavigationTimeout(12000);
  page.on('pageerror', error => errors.push(error.message));
  page.on('response', response => { if (response.status() >= 400 &&
    !(response.url().endsWith('/data/transfer-study.json') && !options.hasStudy)) failedResources.push(response.url()+': '+response.status()); });
  page.on('console', message => { if (/content security policy|refused to/i.test(message.text())) cspErrors.push(message.text()); });
  let nativeClipboard = options.browser === 'chromium';
  if (nativeClipboard) await page.context().grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.addInitScript(({ nativeClipboard }) => {
    window.__regressionIntervals = new Set();
    const set = window.setInterval, clear = window.clearInterval;
    window.setInterval = (...args) => { const id = set(...args); window.__regressionIntervals.add(id); return id; };
    window.clearInterval = id => { window.__regressionIntervals.delete(id); return clear(id); };
    // Firefox/WebKit do not expose Chromium's clipboard permission API. The shim
    // checks exactly what the UI exports, not native OS clipboard integration.
    if (!nativeClipboard) Object.defineProperty(navigator, 'clipboard', { configurable: true,
      value: { writeText: async value => { window.__regressionClipboard = value; } } });
  }, { nativeClipboard });
  const go = async path => {
    await page.goto(options.base+path);
    // Same-document hash navigation can resolve before the router runs,
    // particularly in Firefox. Wait for the requested view before probing it.
    if (path.startsWith('/case-study/')) await page.locator('#'+(path.split('#')[1]||'overview')).waitFor({state:'visible'});
  };
  const ready = () => page.waitForFunction(() => document.querySelector('#draw-copy') && !document.querySelector('#draw-copy').disabled);
  const studyReady = () => page.waitForFunction(() => !document.querySelector('#experiment-workbench').hidden);
  const expand = async summary => { if (!await summary.evaluate(el=>el.parentElement.open)) await summary.click(); };
  const receipt = () => page.locator('#receipt-text').textContent().then(JSON.parse);
  const urlSeed = () => page.evaluate(() => new URL(location.href).searchParams.get('seed'));
  const clipboard = () => page.evaluate(native => native ? navigator.clipboard.readText() : window.__regressionClipboard, nativeClipboard);
  const payload = '<img src="data:," onerror="window.__regressionInjected=1">';
  for (const motion of ['no-preference', 'reduce']) {
    await page.emulateMedia({ reducedMotion: motion });
    await go('/?seed='+encodeURIComponent(payload)+'&sampler=sha256-counter-v2'); await ready();
    const state = await page.evaluate(() => ({ injected: window.__regressionInjected,
      images: document.querySelectorAll('#draw-note img').length,
      seed: new URL(location.href).searchParams.get('seed'),
      disabled: document.querySelector('#draw-autoplay').disabled }));
    check(!state.injected && !state.images && (await receipt()).seed === payload && state.seed === payload,
      'hostile seed stays literal under '+motion);
    check(state.disabled === (motion === 'reduce'), 'autoplay respects '+motion);
  }
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await go('/?seed=42'); await ready();
  const legacy = await receipt();
  check(legacy.sampler === 'legacy-crc-v1' && legacy.value === 'frost' && legacy.lens === 'time-and-rhythm', 'unversioned seed replays legacy vector');
  await go('/?seed='+encodeURIComponent(options.seed)+'&sampler=sha256-counter-v2'); await ready();
  check(JSON.stringify(await receipt()) === JSON.stringify(options.expectedReceipt), 'browser receipt matches actual Node CLI receipt');
  check(await page.locator('#draw-autoplay').getAttribute('aria-pressed') === 'false', 'autoplay defaults off');
  await page.locator('#draw-autoplay').click(); await page.locator('#draw-copy').focus();
  check(await page.locator('#draw-autoplay').getAttribute('aria-pressed') === 'false', 'keyboard focus pauses autoplay');
  await page.locator('#draw-copy').click();
  const command = await clipboard();
  const quote = value => "'"+value.replaceAll("'", "'\"'\"'")+"'";
  check(command === 'bash plugin/scripts/draw.sh --sampler sha256-counter-v2 --seed '+quote(options.seed), 'copy command preserves one literal shell argument');
  await page.locator('#receipt-details summary').click(); await page.locator('#receipt-copy').click();
  check(await clipboard() === await page.locator('#receipt-text').textContent(), 'copied receipt equals visible receipt');
  await page.locator('#draw-share').click();
  check(await clipboard() === page.url() && await urlSeed() === options.seed, 'copied link owns the visible seed');
  await page.locator('#receipt-details summary').click();
  for (let i=0; i<4; i++) { await page.locator('#draw-next').click(); await ready(); }
  check(await page.evaluate(() => window.__regressionIntervals.size) === 0, 'decorative ASCII stays static across repeated redraws');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.waitForFunction(() => window.__regressionIntervals.size === 0);
  check(await page.evaluate(() => window.__regressionIntervals.size) === 0, 'reduced motion leaves no decorative timers');
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  check(await page.evaluate(() => window.__regressionIntervals.size) === 0, 'motion preference change does not start decorative animation');
  await page.locator('#draw-autoplay').click();
  const seedBefore = (await receipt()).seed;
  await page.waitForFunction(seed => JSON.parse(document.querySelector('#receipt-text').textContent).seed !== seed, seedBefore, {timeout:11000});
  const autoReceipt = await receipt();
  check(await urlSeed() === autoReceipt.seed && await page.locator('.seed-tag').textContent() === autoReceipt.sampler+' · '+autoReceipt.seed,
    'autoplay commits URL caption and receipt together');
  await page.locator('#receipt-details summary').click();
  await page.waitForFunction(() => document.querySelector('#draw-autoplay').getAttribute('aria-pressed') === 'false');
  check(true, 'opening receipt pauses autoplay');
  await go('/?seed='+('a'.repeat(1025))+'&sampler=sha256-counter-v2');
  await page.waitForFunction(() => document.querySelector('#draw-status').textContent.includes('1024'));
  check(await page.locator('#draw-copy').isDisabled() && (await urlSeed()).length === 1025, 'overlong seed rejected without truncation');
  const unavailable = await page.context().newPage(), entropyErrors = [];
  unavailable.on('pageerror', error => entropyErrors.push(error.message));
  await unavailable.addInitScript(() => { crypto.getRandomValues = () => { throw new Error('regression entropy unavailable'); }; });
  await unavailable.goto(options.base+'/');
  await unavailable.waitForFunction(() => document.querySelector('#draw-status').textContent.includes('regression entropy unavailable'));
  check(await unavailable.locator('#draw-copy').isDisabled() && await unavailable.locator('#draw-out').textContent() === 'no draw generated' && entropyErrors.length === 0,
    'entropy failure is visible and fails closed without an uncaught error');
  await unavailable.close();

  for (const [width,height] of [[1440,1024],[1280,720],[390,844],[320,800],[640,360],[320,180],[1280,500]]) {
    await page.setViewportSize({width,height});
    for (const view of ['landing','overview','methods','install','evidence','experiment']) {
      await go(view === 'landing' ? '/?seed=42&sampler=sha256-counter-v2' : '/case-study/#'+view);
      if (view === 'landing') await ready();
      else if (options.hasStudy) await studyReady();
      const geometry = await page.evaluate(() => ({w:document.documentElement.scrollWidth, client:document.documentElement.clientWidth}));
      check(geometry.w <= geometry.client+1, view+' has no document overflow at '+width);
      if (width === 320) {
        await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
        const bottom = await page.locator(view === 'landing' ? '.readout' : '.case-footer').boundingBox();
        check(bottom && bottom.y >= -1 && bottom.y+bottom.height <= height+1, view+' final content reachable at320');
      }
      // WebKit screenshots inject <style>body {}</style> and create CSP warnings.
      // Keep its functional run capture-free so no CSP violation is exempted.
      if (options.browser !== 'webkit' && height > 700 && (view === 'landing' || view === 'overview')) {
        // Capture from the top after reachability checks. Otherwise a fixed
        // offscreen skip link can appear inside the full-page stitched image.
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.screenshot({path:options.output+'/'+view+'-'+width+'.png',fullPage:true});
      }
    }
  }
  // Emulates user text-spacing overrides through existing CSSOM rules. This is
  // viewport reflow testing, not native browser zoom or screen-reader validation.
  for (const [width,height] of [[1280,720],[640,360],[320,180],[1280,500]]) {
    await page.setViewportSize({width,height});
    for (const view of ['landing','overview','methods','install','experiment']) {
      // A distinct query forces a fresh document so prior user-style rules do
      // not leak into another view or the later actual-dataset assertions.
      const query = '?spacing-qa='+width+'-'+height+'-'+view;
      await go(view === 'landing' ? '/'+query+'&seed=42&sampler=sha256-counter-v2' : '/case-study/'+query+'#'+view);
      if (view === 'landing') await ready();
      else if (options.hasStudy) await studyReady();
      await page.evaluate(() => {
        const sheet = [...document.styleSheets].find(s=>s.href?.includes('tokens.css'));
        sheet.insertRule('* {line-height:1.5 !important;letter-spacing:.12em !important;word-spacing:.16em !important}',sheet.cssRules.length);
        sheet.insertRule('p {margin-bottom:2em !important}',sheet.cssRules.length);
      });
      check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1), 'text spacing reflows '+view+' at'+width+'x'+height);
      if (view === 'landing') {
        check(await page.evaluate(() => document.querySelector('.lede').getBoundingClientRect().bottom <= document.querySelector('.demo').getBoundingClientRect().top+1), 'text spacing separates intro and draw at'+width+'x'+height);
        for (const selector of ['#draw-next','.fig:last-child a','.case-link a']) {
          const target = page.locator(selector); await target.scrollIntoViewIfNeeded();
          check(await target.evaluate(el => {
            const b=el.getBoundingClientRect(), x=Math.max(1,Math.min(innerWidth-1,b.x+b.width/2)), y=Math.max(1,Math.min(innerHeight-1,b.y+b.height/2));
            return b.width>0 && b.height>0 && el.contains(document.elementFromPoint(x,y));
          }), 'spaced landing target reachable '+selector+' at'+width+'x'+height);
        }
      } else {
        const link = page.locator('.case-nav a[href="#install"]'); await link.scrollIntoViewIfNeeded();
        const b = await link.boundingBox();
        check(b && b.x>=-1 && b.x+b.width<=width+1, 'spaced navigation scrolls locally at'+width+'x'+height+'/'+view);
      }
    }
  }
  await page.setViewportSize({width:320,height:800});
  await go('/case-study/#methods');
  await page.locator('.skip-link').focus(); await page.keyboard.press('Enter');
  check(await page.locator('#methods').isVisible() && await page.evaluate(() => document.activeElement.id) === 'methods-title', 'skip link preserves current section and focuses content');
  await page.locator('.case-nav a[href="#install"]').click();
  await page.waitForFunction(() => document.activeElement.id === 'install-title');
  check(await page.locator('#install').isVisible(), 'section navigation moves keyboard focus to new heading');
  const targetHeights = await page.locator('.case-nav a').evaluateAll(links => links.map(e => e.getBoundingClientRect().height));
  check(targetHeights.every(h=>h>=44), 'mobile case navigation has44px targets');
  let studyStatus = 'main artifact absent; empty state checked, no mock observations';
  if (options.hasStudy) {
    await go('/case-study/#experiment');
    await page.locator('#experiment-workbench').waitFor({state:'visible'});
    const study = await page.evaluate(async () => (await fetch('../data/transfer-study.json')).json());
    check(study.complete && study.cohort === 'main' && study.nTasks === 32 && study.perProblem.length === 32 && study.measurementPanel === 'remeasurement' && study.originalPrimaryStatus === 'halted', 'actual main artifact preserves the amended panel and original halt');
    const arms = ['S','R','LR','XR'];
    await page.evaluate(task=>{
      const replace=history.replaceState;
      window.__urlWrites=[];window.__restoreHistory=()=>{history.replaceState=replace;};
      history.replaceState=function(...args){window.__urlWrites.push(performance.now());return replace.apply(this,args);};
      const select=document.querySelector('#condition-left');
      for(let i=0;i<160;i++){select.value=i%2?'R':'S';select.dispatchEvent(new Event('change',{bubbles:true}));}
      select.value='XR';select.dispatchEvent(new Event('change',{bubbles:true}));
      const right=document.querySelector('#condition-right');right.value='S';right.dispatchEvent(new Event('change',{bubbles:true}));
      const tasks=document.querySelector('#task-select');tasks.value=task;tasks.dispatchEvent(new Event('change',{bubbles:true}));
      location.hash='methods';
    },study.perProblem.at(-1).taskId);
    check(await page.locator('#task-title').textContent() === study.perProblem.at(-1).task.title, 'rapid selections render the latest task immediately');
    await page.waitForFunction(task=>{const p=new URL(location.href).searchParams;return p.get('task')===task && p.get('left')==='XR' && p.get('right')==='S' && location.hash==='#methods';},study.perProblem.at(-1).taskId);
    check(await page.evaluate(()=>window.__urlWrites.length<=2), 'rapid selections coalesce history and preserve the current view');
    await page.evaluate(()=>window.__restoreHistory());
    await go('/case-study/#experiment');await studyReady();
    for (const row of study.perProblem) {
      await page.locator('#task-select').selectOption(row.taskId);
      check(await page.locator('#task-title').textContent() === row.task.title, 'actual task title '+row.taskId);
      check(await page.locator('#task-source-fact').textContent() === 'source fact: '+row.assignedCard.source_fact && await page.locator('#task-source-note').textContent() === row.assignedCard.source_note, 'source facts preserve recorded text '+row.taskId);
      for (const [index,arm] of arms.entries()) {
        await page.locator('#condition-left').selectOption(arm);
        const other = arms[(index+1)%arms.length];
        await page.locator('#condition-right').selectOption(other);
        const rendered = await page.evaluate(() => Object.fromEntries(['left','right'].map(side => [side,{
          score:document.querySelector('#'+side+'-score').textContent,
          titles:[...document.querySelectorAll('#'+side+'-actions>li>h3')].map(el=>el.textContent),
          text:document.querySelector('#'+side+'-actions').textContent
        }])));
        // The interface renders immediately and coalesces URL writes at 150ms.
        // Wait for real convergence rather than adding an arbitrary test delay.
        await page.waitForFunction(({task,arm,other})=>{const p=new URL(location.href).searchParams;return p.get('task')===task && p.get('left')===arm && p.get('right')===other;},{task:row.taskId,arm,other});
        check(true, 'comparison URL matches rendered selection '+row.taskId+'/'+arm);
        for (const [side,selected] of [['left',arm],['right',other]]) {
          const expected = row.arms[selected], actual = rendered[side];
          check(actual.score.startsWith(expected.score.qnm.toFixed(1)+' QNM@4'), 'actual score adapter '+row.taskId+'/'+selected+'/'+side);
          check(JSON.stringify(actual.titles) === JSON.stringify(expected.actions.map(action=>action.action)), 'exact action coverage '+row.taskId+'/'+selected+'/'+side);
          if (!expected.actions.length) check(actual.text.includes(expected.status), 'actual failure/abstention '+row.taskId+'/'+selected+'/'+side);
        }
      }
      check(await page.locator('#bank-actions>li').count() === row.bank.actions.length, 'actual reference-bank coverage '+row.taskId);
    }
    await page.locator('.case-nav a[href="#evidence"]').click();
    check(!(await page.locator('#primary-result').textContent()).includes('p=0.0000'), 'positive p-value never rounded tozero');
    check(await page.locator('#primary-chart title').count() === 1, 'result chart has accessible explanation');
    check((await page.locator('#primary-result').textContent()).includes('original primary halted'), 'result discloses original measurement halt');
    check(await page.locator('#brief-effects button').count() === study.nTasks, 'all task effects have an inspectable button');
    await page.locator('#brief-effects button').last().click();
    check(await page.locator('#task-select').inputValue() === study.perProblem.at(-1).taskId && await page.locator('#condition-left').inputValue() === 'R' && await page.locator('#condition-right').inputValue() === 'LR', 'task effect opens the matching named comparison');
    await page.locator('.case-nav a[href="#methods"]').click();
    check((await page.locator('#diagnostic-summary').textContent()).includes(study.diagnosticSummary.passedPairs+'/'+study.diagnosticSummary.pairs), 'diagnostic summary matches the exact contract count');
    await expand(page.locator('#diagnostic-summary'));
    check(await page.locator('#diagnostic-results>details').count() === study.diagnostics.length, 'all diagnostic pairs are inspectable');
    for (const [i,fixture] of study.diagnostics.entries()) {
      const detail=page.locator('#diagnostic-results>details').nth(i);
      await expand(detail.locator('summary'));
      const text=await detail.textContent();
      check(fixture.variants.every(v=>text.includes('expected trace: '+JSON.stringify(v.expectedTrace)) && text.includes('observed trace: '+JSON.stringify(v.result?.trace ?? null))), 'diagnostic expected and observed traces '+fixture.id);
    }
    // The longest recorded source explanation exercises expanded reading flow,
    // rather than assuming the initially selected brief has the largest content.
    const longest=study.perProblem.reduce((a,b)=>JSON.stringify(a.assignedCard).length>JSON.stringify(b.assignedCard).length?a:b);
    for (const width of [1440,320]) {
      await page.setViewportSize({width,height:width===320?800:1024});
      for (const view of ['evidence','methods','experiment']) {
        await go('/case-study/?task='+longest.taskId+'&left=R&right=LR#'+view); await studyReady();
        if (view === 'experiment') {
          await expand(page.locator('.relation-card summary'));
          await expand(page.locator('#left-actions>li>details>summary').first());
          await expand(page.locator('#right-actions>li>details>summary').first());
          check(await page.locator('#task-source-fact').isVisible() && await page.locator('#task-source-note').isVisible(), 'expanded source evidence is visible at'+width);
        } else if (view === 'methods') {
          await expand(page.locator('#diagnostic-summary'));
          await expand(page.locator('#diagnostic-results>details>summary').first());
        }
        check(await page.evaluate(() => document.documentElement.scrollWidth<=innerWidth+1), 'expanded actual '+view+' has no overflow at'+width);
        await page.locator('.case-footer').scrollIntoViewIfNeeded();
        check(await page.locator('.case-footer').evaluate(el=>{const b=el.getBoundingClientRect();return b.top>=-1 && b.bottom<=innerHeight+1;}), 'expanded actual '+view+' footer reachable at'+width);
        if (options.browser !== 'webkit') {
          await page.evaluate(()=>window.scrollTo(0,0));
          await page.screenshot({path:options.output+'/actual-'+view+'-'+width+'.png',fullPage:true});
        }
      }
    }
    studyStatus = 'all 32 actual tasks and four arms checked in both comparison columns';
  } else {
    await go('/case-study/#experiment');
    await page.waitForFunction(() => document.querySelector('#experiment-loading').textContent.includes('could not be loaded'));
    check(await page.locator('#experiment-workbench').isHidden(), 'absent study shows explicit unavailable state');
  }
  check(errors.length === 0, 'no uncaught page errors: '+errors.join('; '));
  check(failedResources.length === 0, 'no unexpected failed assets: '+failedResources.join('; '));
  check(cspErrors.length === 0, 'CSP permits required assets: '+cspErrors.join('; '));
  const result = {passed:true,browser:options.browser,version:page.context().browser().version(),checks,study:studyStatus,
    accessibility:'CSSOM text spacing and viewport reflow emulation; not native browser zoom or assistive-technology certification',
    screenshots:options.browser === 'webkit'?'omitted: Playwright screenshot injection conflicts with restrictive CSP':'landing and overview at four sizes; actual results, expanded methods and expanded comparison at desktop and mobile when data exists',
    clipboard:nativeClipboard?'native Chromium clipboard read/write':'export-value shim; native OS clipboard not tested'};
  return result;
}
