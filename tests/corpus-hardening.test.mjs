import {test} from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtempSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const root=new URL('../',import.meta.url).pathname;
const run=(script,args)=>spawnSync('bash',[root+'plugin/scripts/'+script,...args],{encoding:'utf8',env:{...process.env,WILDCARD_MIN_CONCEPTS:'4'}});
test('screen reports missing input without touching an existing rejection log',()=>{
 const d=mkdtempSync(join(tmpdir(),'wc-screen-'));try{const log=join(d,'log');writeFileSync(log,'keep me');const r=run('screen_concepts.sh',[join(d,'missing'),log]);assert.notEqual(r.status,0);assert.equal(readFileSync(log,'utf8'),'keep me');}finally{rmSync(d,{recursive:true});}
});
test('screen rejects source/log alias without data loss and keeps final unterminated line',()=>{
 const d=mkdtempSync(join(tmpdir(),'wc-screen-'));try{const raw=join(d,'raw'),log=join(d,'log');writeFileSync(raw,'tides');assert.notEqual(run('screen_concepts.sh',[raw,raw]).status,0);assert.equal(readFileSync(raw,'utf8'),'tides');const r=run('screen_concepts.sh',[raw,log]);assert.equal(r.status,0,r.stderr);assert.equal(r.stdout,'tides\n');}finally{rmSync(d,{recursive:true});}
});
test('final audit applies all source-screen rule families and rejects empty facets',()=>{
 const d=mkdtempSync(join(tmpdir(),'wc-audit-'));try{const p=join(d,'corpus');writeFileSync(p,'Apple Inc. | everyday | matter\nActor | natural | life\nHistory of Earth | scientific | earth\ntides | abstract | \n');const r=run('audit_concepts.sh',[p]);assert.notEqual(r.status,0);assert.match(r.stdout+r.stderr,/ip|person|meta|facet/);}finally{rmSync(d,{recursive:true});}
});
test('final audit rejects normalized duplicates and control characters',()=>{
 const d=mkdtempSync(join(tmpdir(),'wc-audit-'));try{const p=join(d,'corpus');writeFileSync(p,'tides | everyday | matter\nTIDES | natural | earth\nabacus | scientific | math\nspiral\t | abstract | structure\n');const r=run('audit_concepts.sh',[p]);assert.notEqual(r.status,0);assert.match(r.stdout+r.stderr,/duplicate|control/);}finally{rmSync(d,{recursive:true});}
});
