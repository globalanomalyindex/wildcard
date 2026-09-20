import test from 'node:test';
import assert from 'node:assert/strict';
import {mean,pairedBootstrap,signedRank,signFlip,holm} from './stats.mjs';
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-12,`${a} != ${b}`);
test('all-positive exact signed-rank at 31/32 avoids old bitshift overflow',()=>{
  for(const n of [1,5,10,20,31,32,100])close(signedRank(Array(n).fill(1)).p,2/2**n);
  assert.equal(signedRank(Array(32).fill(1)).p,2/2**32);
});
test('signed-rank known tied/zero cases and historical rational fixtures',()=>{
  assert.equal(signedRank([0,0]).p,1);
  assert.equal(signedRank([1,-1,2,-2]).p,1);
  assert.equal(signedRank([1,2,3,4,5,0]).p,1/16);
  const novelty=[21,8,25,60,-15,9,51,57,-18,63].map(x=>x/36);
  assert.equal(signedRank(novelty).p,19/512);
  assert.equal(signFlip(novelty).p,17/512);
  const genuine=[-33,-31,-10,0,-36,0,3,15,-6,15].map(x=>x/36);
  assert.equal(signedRank(genuine).p,19/64);
  assert.equal(signedRank(genuine.map(x=>-x)).p,19/64);
});
test('signed-rank is independently checked by brute force across small tied fixtures',()=>{
  function brute(ds){
    ds=ds.filter(Boolean);if(!ds.length)return 1;
    const ranks=ds.map(d=>1+ds.filter(e=>Math.abs(e)<Math.abs(d)).length+(ds.filter(e=>Math.abs(e)===Math.abs(d)).length-1)/2);
    const total=ranks.reduce((a,b)=>a+b,0),positive=ranks.reduce((s,r,i)=>s+(ds[i]>0?r:0),0),obs=Math.min(positive,total-positive);
    let counts=[0];for(const r of ranks)counts=counts.flatMap(s=>[s,s+r]);
    return counts.filter(s=>Math.min(s,total-s)<=obs).length/counts.length;
  }
  for(let code=0;code<625;code++){
    let k=code;const ds=[];for(let i=0;i<4;i++){ds.push(k%5-2);k=Math.floor(k/5);}
    assert.equal(signedRank(ds).p,brute(ds));
  }
});
test('floating representations of rational ties are handled explicitly',()=>{
  const exact=[1,-1,2,-2,2];
  const drift=[1+1e-15,-1,2,-2+1e-15,2];
  assert.equal(signedRank(exact).p,signedRank(drift).p);
});
test('bootstrap uses declared paired units and deterministic seed',()=>{
  const a=pairedBootstrap([1,2,3],{seed:'fixture',iterations:1000});
  assert.deepEqual(a,pairedBootstrap([1,2,3],{seed:'fixture',iterations:1000}));
  assert.equal(a.n,3);assert.equal(a.mean,2);
  assert.deepEqual(pairedBootstrap([.5,.5],{seed:3}).ci95,[.5,.5]);
});
test('malformed inputs and unsupported work sizes fail explicitly',()=>{
  for(const bad of [[1,NaN],[Infinity],[null],['1'],null]){
    assert.throws(()=>mean(bad));assert.throws(()=>signedRank(bad));assert.throws(()=>pairedBootstrap(bad,{seed:1}));
  }
  assert.throws(()=>mean([]));assert.throws(()=>pairedBootstrap([1]));
  assert.throws(()=>pairedBootstrap([1],{seed:1,iterations:0}));
  assert.throws(()=>signedRank(Array(251).fill(1)));
  assert.throws(()=>signFlip(Array(21).fill(1)));
  assert.throws(()=>holm([1.1]));assert.throws(()=>signedRank([1],{tieTolerance:NaN}));
});
test('Holm adjustment returns original ordering and enforces monotonicity',()=>{
  const actual=holm([.04,.01,.03]);[.06,.03,.06].forEach((v,i)=>close(actual[i],v));
  assert.deepEqual(holm([]),[]);assert.deepEqual(holm([1,1]),[1,1]);
});
