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
  const go = async path => { await page.goto(options.base+path); };
  const ready = () => page.waitForFunction(() => document.querySelector('#draw-copy') && !document.querySelector('#draw-copy').disabled);
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

  for (const [width,height] of [[1440,1024],[1280,720],[390,844],[320,800]]) {
    await page.setViewportSize({width,height});
    for (const view of ['landing','overview','methods','install','evidence','experiment']) {
      await go(view === 'landing' ? '/?seed=42&sampler=sha256-counter-v2' : '/case-study/#'+view);
      if (view === 'landing') await ready();
      const geometry = await page.evaluate(() => ({w:document.documentElement.scrollWidth, client:document.documentElement.clientWidth}));
      check(geometry.w <= geometry.client+1, view+' has no document overflow at '+width);
      if (width === 320) {
        await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
        const bottom = await page.locator(view === 'landing' ? '.readout' : '.case-footer').boundingBox();
        check(bottom && bottom.y >= -1 && bottom.y+bottom.height <= height+1, view+' final content reachable at320');
      }
      // WebKit screenshots inject <style>body {}</style> and create CSP warnings.
      // Keep its functional run capture-free so no CSP violation is exempted.
      if (options.browser !== 'webkit' && (view === 'landing' || view === 'overview')) {
        // Capture from the top after reachability checks. Otherwise a fixed
        // offscreen skip link can appear inside the full-page stitched image.
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.screenshot({path:options.output+'/'+view+'-'+width+'.png',fullPage:true});
      }
    }
  }
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
    check(study.complete && study.cohort === 'main' && study.nTasks === 32, 'actual main artifact is complete');
    for (const row of [study.perProblem[0], study.perProblem.at(-1)]) {
      await page.locator('#task-select').selectOption(row.taskId);
      check(await page.locator('#task-title').textContent() === row.task.title, 'actual task title '+row.taskId);
      for (const arm of ['S','R','LR','XR']) {
        await page.locator('#condition-left').selectOption(arm);
        check((await page.locator('#left-score').textContent()).startsWith(row.arms[arm].score.qnm.toFixed(1)+' QNM@4'), 'actual score adapter '+row.taskId+'/'+arm);
        if (row.arms[arm].actions.length) check(await page.locator('#left-actions>li').count() === row.arms[arm].actions.length, 'actual action coverage '+row.taskId+'/'+arm);
        else check((await page.locator('#left-actions').textContent()).includes(row.arms[arm].status), 'actual failure/abstention '+row.taskId+'/'+arm);
      }
      check(await page.locator('#bank-actions>li').count() === row.bank.actions.length, 'actual reference-bank coverage '+row.taskId);
    }
    await page.locator('.case-nav a[href="#evidence"]').click();
    check(!(await page.locator('#primary-result').textContent()).includes('p=0.0000'), 'positive p-value never rounded tozero');
    check(await page.locator('#primary-chart title').count() === 1, 'result chart has accessible explanation');
    studyStatus = 'actual complete main artifact adapters checked';
  } else {
    await go('/case-study/#experiment');
    await page.waitForFunction(() => document.querySelector('#experiment-loading').textContent.includes('could not be loaded'));
    check(await page.locator('#experiment-workbench').isHidden(), 'absent study shows explicit unavailable state');
  }
  check(errors.length === 0, 'no uncaught page errors: '+errors.join('; '));
  check(failedResources.length === 0, 'no unexpected failed assets: '+failedResources.join('; '));
  check(cspErrors.length === 0, 'CSP permits required assets: '+cspErrors.join('; '));
  const result = {passed:true,browser:options.browser,version:page.context().browser().version(),checks,study:studyStatus,
    screenshots:options.browser === 'webkit'?'omitted: Playwright screenshot injection conflicts with restrictive CSP':'landing and overview at four sizes',
    clipboard:nativeClipboard?'native Chromium clipboard read/write':'export-value shim; native OS clipboard not tested'};
  return result;
}
