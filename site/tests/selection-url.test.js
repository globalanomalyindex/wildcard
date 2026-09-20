import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createSelectionUrlCommitter} from '../js/selection-url.js';

function environment() {
  const callbacks=[], writes=[];
  const browser={location:{href:'https://example.test/case-study/?other=kept#experiment'},
    history:{replaceState(_state,_title,url){writes.push(String(url));browser.location.href=String(url);}},
    setTimeout(callback,delay){callbacks.push({callback,delay});return callbacks.length;}};
  return {browser,callbacks,writes,flush(){callbacks.shift().callback();}};
}

test('rapid selections coalesce, preserving the latest task and both arms',()=>{
  const e=environment(), commit=createSelectionUrlCommitter(e.browser);
  for(let i=0;i<320;i++) commit({task:'task-'+i,left:i%2?'R':'S',right:'LR'});
  assert.equal(e.writes.length,0);
  assert.equal(e.callbacks.length,1);
  assert.equal(e.callbacks[0].delay,150);
  e.flush();
  assert.equal(e.writes.length,1);
  const url=new URL(e.writes[0]);
  assert.equal(url.searchParams.get('task'),'task-319');
  assert.equal(url.searchParams.get('left'),'R');
  assert.equal(url.searchParams.get('right'),'LR');
  assert.equal(url.searchParams.get('other'),'kept');
});

test('trailing selection reads the current view and later bursts still commit',()=>{
  const e=environment(), commit=createSelectionUrlCommitter(e.browser);
  commit({task:'one',left:'R',right:'LR'});
  e.browser.location.href='https://example.test/case-study/?other=changed#methods';
  e.flush();
  assert.equal(new URL(e.writes[0]).hash,'#methods');
  assert.equal(new URL(e.writes[0]).searchParams.get('other'),'changed');
  commit({task:'two',left:'XR',right:'S'});e.flush();
  assert.equal(e.writes.length,2);
  assert.equal(new URL(e.writes[1]).searchParams.get('task'),'two');
});
