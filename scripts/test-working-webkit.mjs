// Stable fallback for CLI 0.1.21's known native-select CSP regression.
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
const [entrypoint,optionsPath]=process.argv.slice(2);
const {webkit}=createRequire(pathToFileURL(entrypoint))('playwright');
const options=JSON.parse(readFileSync(optionsPath,'utf8'));
const source=readFileSync(new URL('./working-browser-regression.js',import.meta.url),'utf8').replace('__WORKING_OPTIONS__',JSON.stringify(options));
const browser=await webkit.launch({headless:true});
try {
  const context=await browser.newContext(),page=await context.newPage();
  await page.goto(options.base+'/working-solutions/');
  writeFileSync(join(options.output,'snapshot.yml'),await page.locator('body').ariaSnapshot());
  const result=await Function('return ('+source+')')()(page);
  result.transport='stable Playwright 1.63.0 WebKit; identical CLI-first probe';
  console.log(JSON.stringify(result));
} finally {await browser.close();}
