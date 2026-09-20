import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync,spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
const root=new URL('../',import.meta.url).pathname;
let api; try { api=await import('../plugin/lib/sampler-v2.mjs'); } catch(e) { if(e.code!=='ERR_MODULE_NOT_FOUND') throw e; }
const get=()=>{assert.ok(api,'the versioned sampler API is available');return api;};

test('default CLI returns a replayable v2 receipt rather than a legacy draw',()=>{
  const p=spawnSync('bash',['plugin/scripts/draw.sh','--seed','42','--json'],{cwd:root,encoding:'utf8'});
  assert.equal(p.status,0,p.stderr);
  const r=JSON.parse(p.stdout);assert.equal(r.sampler,'sha256-counter-v2');assert.equal(r.seed,'42');assert.match(r.corpusSha256,/^[a-f0-9]{64}$/);assert.ok(r.entryId);assert.ok(r.value);
});
test('seedless CLI succeeds on Bash 3.2 and emits a 256-bit issued seed receipt',()=>{
  const p=spawnSync('/bin/bash',['plugin/scripts/draw.sh'],{cwd:root,encoding:'utf8'});
  assert.equal(p.status,0,p.stderr);assert.match(p.stdout,/^mode=(specialist|concept)\n/);
  const receipt=JSON.parse(p.stderr.trim().replace(/^receipt=/,''));assert.match(receipt.seed,/^[0-9a-f]{64}$/);
});
test('missing runtime, unsupported overrides and seedless legacy replay fail explicitly',()=>{
  const p=spawnSync('/bin/bash',['plugin/scripts/draw.sh','--seed','42'],{cwd:root,encoding:'utf8',env:{...process.env,PATH:'/usr/bin:/bin'}});
  assert.notEqual(p.status,0);assert.match(p.stderr,/Node.js 22/);
  for(const args of [['--sampler','legacy-crc-v1'],['--seed','42','--file','unexpected'],['--sampler','unknown']])assert.notEqual(spawnSync('bash',['plugin/scripts/draw.sh',...args],{cwd:root,encoding:'utf8'}).status,0);
});
test('entropy acquisition propagates source failure instead of switching sources',()=>{
  get();const p=spawnSync(process.execPath,['--input-type=module','-e',`import {freshSeed} from './plugin/lib/sampler-v2.mjs';Object.defineProperty(globalThis,'crypto',{value:{getRandomValues(){throw new Error('entropy read failed')}}});try{freshSeed();process.exit(0)}catch(e){console.error(e.message);process.exit(7)}`],{cwd:root,encoding:'utf8'});
  assert.equal(p.status,7);assert.match(p.stderr,/entropy read failed/);
});
test('legacy source remains byte-identical and explicit replay matches historical seed 42',()=>{
  const bytes=readFileSync(root+'plugin/scripts/draw-legacy.sh');
  assert.equal(createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex'), '3ab14d6d28091bac5b6b0552e6037893478875b4');
  const a=execFileSync('bash',['plugin/scripts/draw-legacy.sh','--seed','42'],{cwd:root,encoding:'utf8'});
  const b=execFileSync('bash',['plugin/scripts/draw.sh','--sampler','legacy-crc-v1','--seed','42'],{cwd:root,encoding:'utf8'});assert.equal(a,b);
});
test('SHA-256 framing agrees with independently produced Python vector',async()=>{
  const {frameBytes}=get();
  const bytes=frameBytes('é:42','mode',0n);
  assert.equal(Buffer.from(bytes).toString('hex'),'77696c64636172642f73616d706c65722f763200000005c3a93a3432000000046d6f64650000000000000000');
  assert.equal(createHash('sha256').update(bytes).digest('hex'),'9cc2950944b2f2a09526c73ff9dcef09709f857b89b3da9255b970d7b592137c');
});
test('rejection drops the boundary and advances; failures never fall back',async()=>{
  const {uniformInt}=get();let words=[4294967295,4294967166,4294967165];
  assert.equal(await uniformInt(378,async()=>words.shift()),377);assert.equal(words.length,0);
  assert.equal(await uniformInt(2**32,async()=>4294967295),4294967295);
  assert.equal(await uniformInt(1,async()=>4294967295),0);
  await assert.rejects(uniformInt(378,async()=>{throw new Error('source failed');}),/source failed/);
  await assert.rejects(uniformInt(378,async()=>4294967295,{maxAttempts:3}),/exhausted/);
  for(const n of [0,-1,1.5,NaN,Infinity,2**32+1]) await assert.rejects(uniformInt(n,async()=>0),/integer/);
  await assert.rejects(uniformInt(2,async()=>undefined),/word/);
});
test('seed contract preserves exact text, rejects non-scalar or unbounded input, and shell copy quotes literally',()=>{
  const {validateSeed,shellQuote}=get();
  for(const seed of ['42',' leading space ','single\'quote','é','e\u0301','🪄','line\nbreak','$(printf unsafe);`printf unsafe`']){
    assert.equal(validateSeed(seed),seed);
    assert.equal(execFileSync('bash',['-c',`printf '%s' ${shellQuote(seed)}`],{encoding:'utf8'}),seed);
  }
  for(const seed of ['',null,42,'a\0b','\ud800','a'.repeat(1025),'🪄'.repeat(257)]) assert.throws(()=>validateSeed(seed),/seed/i);
  assert.equal(validateSeed('a'.repeat(1024)).length,1024);
});
test('wrapper treats option-shaped seed strings as literal values',()=>{
  for(const seed of ['--sampler','--sampler=legacy-crc-v1','--json']){
    const p=spawnSync('bash',['plugin/scripts/draw.sh','--seed',seed,'--json'],{cwd:root,encoding:'utf8'});
    assert.equal(p.status,0,p.stderr);assert.equal(JSON.parse(p.stdout).seed,seed);
  }
});
test('word stream consumes all digest words then advances its counter',async()=>{
  const {createWordStream}=get();const next=createWordStream('é:42','mode');
  const actual=[];for(let i=0;i<9;i++)actual.push(await next());
  assert.deepEqual(actual,[2629997833,1152578208,2502346559,4192005897,1889502587,2310265490,1438216407,3046249340,1032548442]);
  assert.equal(await createWordStream('é:42','mode')(),2629997833);
});
test('receipt validates version and corpus and handles forced mode without changing its stream',async()=>{
  const {drawV2,replayV2}=get();const a=await drawV2('42');
  assert.deepEqual(await replayV2(a),a);
  assert.equal((await drawV2('42',{mode:a.mode})).entryId,a.entryId);
  assert.equal((await drawV2('42',{mode:a.mode})).modeForced,true);
  await assert.rejects(drawV2('42',{mode:'other'}),/mode/);
  await assert.rejects(replayV2({...a,corpusSha256:'0'.repeat(64)}),/corpus/i);
  await assert.rejects(replayV2({...a,lens:'wrong'}),/receipt/i);
});
test('altered bundled corpus fails before a receipt can cite the old digest',async()=>{
  get();const temporary=mkdtempSync(join(tmpdir(),'wildcard-corrupt-'));
  try{
    writeFileSync(join(temporary,'sampler-v2.mjs'),readFileSync(root+'plugin/lib/sampler-v2.mjs'));
    writeFileSync(join(temporary,'corpus-v2.mjs'),readFileSync(root+'plugin/lib/corpus-v2.mjs','utf8').replace('abacus','changed-abacus'));
    const altered=await import(pathToFileURL(join(temporary,'sampler-v2.mjs')));
    await assert.rejects(altered.drawV2('42'),/corpus.*hash|corpus.*digest/i);
  }finally{rmSync(temporary,{recursive:true});}
});
test('fixed-length conditional support covers both pools and every lens',async()=>{
  const {drawV2}=get();
  for(const length of [6,10,22]){
    const coverage=[new Set(),new Set()],lenses=[new Set(),new Set()];
    for(let i=0;i<12000;i++){
      const r=await drawV2(String(i).padStart(length,'0')),m=r.mode==='concept'?1:0;
      coverage[m].add(r.entryId);lenses[m].add(r.lens);
    }
    assert.deepEqual(coverage.map(s=>s.size),[378,461],`conditional support at ${length} bytes`);
    assert.deepEqual(lenses.map(s=>s.size),[8,8],`conditional lenses at ${length} bytes`);
  }
});
test('browser artifact and plugin engine produce the same receipt and generator is current',async()=>{
  get();const browser=await import('../site/js/sampler-v2.js');
  for(const seed of ['42','single\'quote','é','🪄','7eb8abe05e8a13d2:p02:1'])assert.deepEqual(await browser.drawV2(seed),await api.drawV2(seed));
  const p=spawnSync(process.execPath,['plugin/scripts/build-corpus.mjs','--check'],{cwd:root,encoding:'utf8'});assert.equal(p.status,0,p.stderr);
});
