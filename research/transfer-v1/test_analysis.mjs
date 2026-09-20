import test from 'node:test';
import assert from 'node:assert/strict';
import {stream,stratifiedBootstrap,monteCarloSignFlip,analyze} from './analyze.mjs';
test('separate deterministic SHA streams and correct one-unit strata preserve pairing',()=>{
  const a=stream('a'),b=stream('a'),c=stream('b');
  assert.deepEqual(Array.from({length:20},()=>a()),Array.from({length:20},()=>b()));
  assert.notEqual(a(),c());
  const result=stratifiedBootstrap([{family:'one',difference:2},{family:'two',difference:-1}],{seed:'fixture',iterations:100});
  assert.deepEqual(result.ci95,[.5,.5]);assert.equal(result.meanDifference,.5);
});
test('Monte Carlo sign flip includes ties, uses plus-one, and is reproducible',()=>{
  const zeros=monteCarloSignFlip(Array(32).fill(0),{seed:'zero',iterations:100});
  assert.equal(zeros.p,1);
  const first=monteCarloSignFlip(Array(32).fill(1),{seed:'positive',iterations:1000});
  assert.equal(first.p,(first.extremeCount+1)/1001);
  assert.deepEqual(first,monteCarloSignFlip(Array(32).fill(1),{seed:'positive',iterations:1000}));
});
test('all 32 paired tasks contribute and secondary family contains exactly two contrasts',()=>{
  const data={perProblem:Array.from({length:32},(_,i)=>({taskId:`t${i}`,task:{family:`f${Math.floor(i/8)}`},arms:Object.fromEntries(['S','R','LR','XR'].map((arm,j)=>[arm,{status:'success',score:{qnm:j,qdm:4,qualified_actions:4,total_actions:4},judges:{j1:{qnm:j,qdm:4},j2:{qnm:j,qdm:4}}}]))}))};
  const result=analyze(data);
  assert.equal(result.primary.nPairs,32);assert.equal(result.primary.difference,1);
  assert.deepEqual(result.primary.ci95,[1,1]);assert.equal(result.primary.directionalEvidence,'positive');
  assert.deepEqual(result.secondary.map(c=>c.id),['R-S','XR-LR']);
  assert.ok(result.secondary.every(c=>c.holmAdjustedP>=c.test.p));
});
