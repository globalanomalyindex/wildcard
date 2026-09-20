import test from 'node:test';
import assert from 'node:assert/strict';
import {readStudy,validateRecords} from './validate-history.mjs';
import {verifyHistory,ROOT} from '../../scripts/verify-history.mjs';
import {buildEvidence} from '../../scripts/build-evidence.mjs';
import {exactBootstrap} from './exact-bootstrap.mjs';
test('frozen research files retain exact pinned hashes',()=>assert.equal(verifyHistory().unchanged,true));
test('strict checks catch Study 2 duplicate/missing pair despite 240 rows',()=>{
  assert.throws(()=>readStudy(ROOT,'study2'),/duplicate-rating:g3:out-35/);
  const {validation:r}=readStudy(ROOT,'study2',{mode:'legacy-available-case'});
  assert.equal(r.observedRows,240);assert.equal(r.uniqueGraderOutputPairs,239);
  assert.deepEqual(r.issues.map(i=>[i.code,i.grader,i.output]),[['duplicate-rating','g3','out-35'],['missing-rating','g3','out-48']]);
});
test('strict Study 3 check reports both missing judgments; named legacy read remains possible',()=>{
  assert.throws(()=>readStudy(ROOT,'study3'),/missing-rating/);
  const {validation:r}=readStudy(ROOT,'study3',{mode:'legacy-available-case'});
  assert.equal(r.observedRows,238);assert.equal(r.scheduledRatings,240);assert.equal(r.confirmatoryEligible,false);
  assert.equal(readStudy(ROOT,'study1').validation.confirmatoryEligible,true);
});
test('invalid rating values are never allowed by legacy mode',()=>{
  const data=readStudy(ROOT,'study3',{mode:'legacy-available-case'});
  data.graders[0].grades[0].novelty=NaN;
  assert.throws(()=>validateRecords({...data,...data.design},{mode:'legacy-available-case'}),/invalid-rating/);
});
test('unknown identities, duplicate cells, and truthy booleans fail before analysis',()=>{
  for(const alter of [
    d=>{d.graders[0].grades[0].id='unknown';},
    d=>{d.graders[0].grades[0].fabrication='false';},
    d=>{d.manifest[0].rep=99;d.manifest[0].run=99;},
  ]){
    const data=readStudy(ROOT,'study3',{mode:'legacy-available-case'});alter(data);
    assert.throws(()=>validateRecords({...data,...data.design},{mode:'legacy-available-case'}));
  }
});
test('exact finite bootstrap matches full enumeration for small rational fixture',()=>{
  const ds=[-1,.5,2],ordered=[];
  for(const a of ds)for(const b of ds)for(const c of ds)ordered.push((a+b+c)/3);
  ordered.sort((a,b)=>a-b);
  const r=exactBootstrap(ds);
  assert.equal(r.orderedResamples,27);assert.deepEqual(r.ci95,[ordered[0],ordered[26]]);
  assert.throws(()=>exactBootstrap([Math.PI]));
});
test('generated evidence agrees with independent rational-arithmetic reanalysis',()=>{
  const e=buildEvidence();
  const nov=e.study3.recorded.novelty;
  assert.ok(Math.abs(nov.difference-.725)<1e-12);
  assert.equal(nov.signedRank.p,19/512);
  assert.deepEqual(nov.exactBootstrap.ci95,[.225,437/360]);
  assert.equal(e.study3.missingNoveltySensitivity.allMeetOriginalDecisionRule,true);
  const s=e.study3.missingNoveltySensitivity;
  assert.ok(Math.abs(s.differenceRange[0]-.675)<1e-12);assert.ok(Math.abs(s.differenceRange[1]-.775)<1e-12);
  assert.deepEqual(s.signedRankPRange,[11/512,30/512]);
  assert.equal(e.study3.fabrication.P.positiveFlags,6);assert.equal(e.study3.fabrication.P.outputsWithAnyFlag,2);
  assert.equal(e.study3.recorded.genuineness.signedRank.p,19/64);
});
