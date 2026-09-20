// Narrow fallback: CLI 0.1.21 bundles an alpha WebKit with a native-select CSP
// regression. Run the same probe through pinned stable Playwright 1.63.0, with no
// screenshot or CSP bypass during assertions. Both builds were probed separately.
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {readFileSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';
const [stableEntrypoint, optionsPath] = process.argv.slice(2);
const {webkit} = createRequire(pathToFileURL(stableEntrypoint))('playwright');
const options = JSON.parse(readFileSync(optionsPath, 'utf8'));
const source = readFileSync(new URL('./browser-regression.js', import.meta.url), 'utf8')
  .replace('__REGRESSION_OPTIONS__', JSON.stringify(options));
const probe = Function('return ('+source+')')();
const browser = await webkit.launch({headless:true});
try {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(options.base+'/?seed=42&sampler=sha256-counter-v2');
  writeFileSync(join(options.output, 'snapshot.yml'), await page.locator('body').ariaSnapshot());
  const result = await probe(page);
  result.transport = 'direct stable Playwright 1.63.0; CLI 0.1.21 alpha WebKit native-select CSP regression avoided';
  console.log(JSON.stringify(result));
} finally {
  await browser.close();
}
