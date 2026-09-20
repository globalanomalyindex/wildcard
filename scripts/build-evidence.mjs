// Generate public evidence from immutable history. Never writes to experiment/**.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {ROOT,verifyHistory} from './verify-history.mjs';
import {readStudy} from '../research/audit-2026-09/validate-history.mjs';
import {mean,signedRank,signFlip} from '../research/lib/stats.mjs';
import {exactBootstrap} from '../research/audit-2026-09/exact-bootstrap.mjs';
const METRICS=['genuineness','usefulness','novelty','nonDerailment'];
const SOURCE='04ff0a546d4e55038fa75881ec245662ac5765e9';
const hash=(root,path)=>createHash('sha256').update(readFileSync(join(root,path))).digest('hex');
function aggregate(study,{deduplicate=false,fill={},keepGraders=null}={}){
  const out=new Map(study.manifest.map(m=>[m.outId,{...m,rows:[]}]));
  for(const g of study.graders){
    const grader=g.grader??g.graderId;if(keepGraders&&!keepGraders.includes(grader))continue;
    const seen=new Set();
    for(const r of g.grades){if(deduplicate&&seen.has(r.id))continue;seen.add(r.id);out.get(r.id).rows.push({...r,grader});}
  }
  const problems=(Array.isArray(study.selected)?study.selected:study.selected.problems).map(p=>p.id);
  function cell(arm,pid,metric){
    return mean([...out.values()].filter(o=>o.arm===arm&&o.problemId===pid&&!o.abstained).map(o=>{
      const values=o.rows.map(r=>r[metric]);
      if(Object.hasOwn(fill,o.outId)){
        const value=typeof fill[o.outId]==='number'?(metric==='novelty'?fill[o.outId]:undefined):fill[o.outId][metric];
        if(value!==undefined)values.push(value);
      }
      return mean(values);
    }));
  }
  return {out,problems,cell};
}
function contrasts(study,arms,options={}){
  const {cell,problems}=aggregate(study,options);
  return Object.fromEntries(METRICS.map(metric=>{
    const values=problems.map(problemId=>({problemId,x:cell(arms[0],problemId,metric),y:cell(arms[1],problemId,metric)}));
    const differences=values.map(v=>v.x-v.y);
    return [metric,{meanX:mean(values.map(v=>v.x)),meanY:mean(values.map(v=>v.y)),difference:mean(differences),nProblems:problems.length,
      signedRank:signedRank(differences),signFlip:signFlip(differences),exactBootstrap:exactBootstrap(differences),perProblem:values.map((v,i)=>({...v,difference:differences[i]}))}];
  }));
}
export function buildEvidence(root=ROOT){
  const history=verifyHistory(root);if(!history.unchanged)throw new Error('Historical data changed; evidence build refused');
  const studies=Object.fromEntries(['study1','study2','study3'].map(id=>[id,readStudy(root,id,{mode:'legacy-available-case'})]));
  const read=path=>JSON.parse(readFileSync(join(root,path),'utf8'));
  const frozen={study1:read('experiment/results.json'),study2:read('experiment/v2/results.json'),study3:read('experiment/v3/results.json')};
  const v3=contrasts(studies.study3,['W','P']);
  const {out,problems}=aggregate(studies.study3);
  const flags=Object.fromEntries(['W','P'].map(arm=>{
    const outputs=[...out.values()].filter(o=>o.arm===arm),rows=outputs.flatMap(o=>o.rows);
    const flagged=outputs.filter(o=>o.rows.some(r=>r.fabrication)).map(o=>({outputId:o.outId,flags:o.rows.filter(r=>r.fabrication).length,judgments:o.rows.length,graders:o.rows.filter(r=>r.fabrication).map(r=>r.grader)}));
    return [arm,{judgments:rows.length,positiveFlags:rows.filter(r=>r.fabrication).length,outputs:outputs.length,outputsWithAnyFlag:flagged.length,unanimouslyFlaggedOutputs:flagged.filter(o=>o.flags===o.judgments).length,flagged,adjudicatedErrors:null}];
  }));
  const sensitivity=[];
  for(let a=1;a<=7;a++)for(let b=1;b<=7;b++){
    const fill={'P-p48-r3':a,'P-p47-r2':b},r=contrasts(studies.study3,['W','P'],{fill}).novelty;
    sensitivity.push({hypotheticalMissingRatings:fill,difference:r.difference,ci95:r.exactBootstrap.ci95,p:r.signedRank.p,originalDecisionRuleMet:r.difference>=.3&&r.exactBootstrap.ci95[0]>0});
  }
  const range=f=>[Math.min(...sensitivity.map(f)),Math.max(...sensitivity.map(f))];
  const leaveOneGraderOut=Object.fromEntries(['g1','g2','g3','g4'].map(omit=>{
    const r=contrasts(studies.study3,['W','P'],{keepGraders:['g1','g2','g3','g4'].filter(g=>g!==omit)}).novelty;
    return [omit,{difference:r.difference,ci95:r.exactBootstrap.ci95,p:r.signedRank.p}];
  }));
  const v2dedup=contrasts(studies.study2,['v2','v1'],{deduplicate:true});
  const v2MissingGenuineness=Array.from({length:7},(_,i)=>{
    const r=contrasts(studies.study2,['v2','v1'],{deduplicate:true,fill:{'out-48':{genuineness:i+1}}}).genuineness;
    return {hypotheticalMissingGenuineness:i+1,difference:r.difference,ci95:r.exactBootstrap.ci95,p:r.signedRank.p,originalPointPredictionMet:r.difference>=.5};
  });
  const lensNames=['failure-modes','materials','time-and-rhythm','constraints-and-limits','energy-and-flow','structure-and-form','measurement','signals-and-noise'];
  const treatment=studies.study3.manifest.filter(o=>o.arm==='W');
  const coupled=treatment.filter(o=>Number(o.mode==='concept')===lensNames.indexOf(o.lens)%2).length;
  const source=(path,pointer)=>({path,sha256:hash(root,path),jsonPointer:pointer,sourceCommit:SOURCE});
  const claim=(id,statement,value,unit,denominator,sourceRecords,caveat,extra={})=>({id,statement,value,unit,denominator,sources:sourceRecords,caveat,verifiedAt:'2026-09-20',...extra});
  const claims=[
    claim('s3-novelty-difference','The recorded Wildcard treatment averaged 0.725 points higher in judged novelty than the specified plain prompt.',v3.novelty.difference,'points on a 1–7 judge scale',{problems:10,outputs:60,observedRatings:238,scheduledRatings:240},[source('experiment/v3/results.json','/results/novelty'),source('experiment/v3/grades.json','/graders')],'Available-case historical result; same-vendor model judges; limited to the recorded treatment and task pool.',{primary:true,interval:{method:'original 10000-resample paired percentile bootstrap',ci95:frozen.study3.results.novelty.ci95},p:frozen.study3.results.novelty.p}),
    claim('s3-decision-rule','Study 3 met its original rule: a novelty point estimate of at least +0.30 and a 95% interval excluding zero.',true,'original decision rule',{problems:10},[source('experiment/v3/preregistration.md',null),source('experiment/v3/results.json','/predictionMet')],'The interval does not establish a minimum +0.30 effect with 95% confidence; historical completeness is not met.'),
    claim('s3-missing-ratings','Study 3 contains 238 of 240 scheduled judgments.',238,'observed grader-output judgments',{scheduledJudgments:240},[source('experiment/v3/grades.json','/graders')],'Two judgments are absent: g4/P-p48-r3 and g3/P-p47-r2; no scores were recovered or invented.'),
    claim('s3-fabrication-flags','Six plain-arm fabrication flags concerned two outputs; Wildcard had zero flagged outputs.',flags,'judge flags and unique outputs',{W:{judgments:120,outputs:30},P:{judgments:118,outputs:30}},[source('experiment/v3/grades.json','/graders')],'Flags are model judgments, not independently adjudicated factual errors. Zero flags do not prove zero errors.'),
    claim('s3-usefulness','Judged usefulness was 0.233 points lower with Wildcard.',v3.usefulness.difference,'points on a 1–7 judge scale',{problems:10},[source('experiment/v3/results.json','/results/usefulness')],'Exploratory; percentile bootstrap CI is negative while the different signed-rank test gives p=0.140625. Non-significance does not establish equality.',{primary:false,interval:{method:'original paired percentile bootstrap',ci95:frozen.study3.results.usefulness.ci95},p:frozen.study3.results.usefulness.p}),
    claim('s2-duplicate-rating','Study 2 has 240 stored grading rows but 239 unique grader-output pairs.',239,'unique grader-output pairs',{scheduled:240,storedRows:240},[source('experiment/v2/grades.json','/graders/2')],'New audit finding: g3/out-35 is duplicated identically and g3/out-48 is missing. The intended identity of the repeated row is unknown.'),
    claim('s3-mode-lens-coupling','All 30 recorded Study 3 treatment draws couple the mode to lens-index parity.',coupled,'recorded treatment draws',{treatmentDraws:30},[source('experiment/v3/raw/manifest.json',null)],'The historical effect belongs to this legacy sampler. The direction of bias relative to an independent sampler is unknown.'),
  ];
  return {schemaVersion:1,analysisVersion:'historical-audit-2026-09-v1',verifiedAt:'2026-09-20',sourceCommit:SOURCE,status:'historical replay and explicitly post-hoc reanalysis; no new model or human data',historyIntegrity:history,
    validation:Object.fromEntries(Object.entries(studies).map(([id,s])=>[id,s.validation])),frozenResults:frozen,
    study3:{nProblems:10,nOutputs:60,observedRatings:238,scheduledRatings:240,primaryEndpoint:'novelty',recorded:v3,fabrication:flags,
      originalDecisionRule:{minimumPointEstimate:.3,ciMustExcludeZero:true,pThresholdUsed:false,met:frozen.study3.predictionMet},
      missingNoveltySensitivity:{status:'hypothetical exhaustive sensitivity; no source scores changed',scenarios:49,allMeetOriginalDecisionRule:sensitivity.every(s=>s.originalDecisionRuleMet),differenceRange:range(s=>s.difference),ciLowerRange:range(s=>s.ci95[0]),ciUpperRange:range(s=>s.ci95[1]),signedRankPRange:range(s=>s.p),details:sensitivity},
      leaveOneGraderOut,modeLensCoupling:{coupled,total:treatment.length}},
    study2:{deduplicatedAvailableCase:v2dedup,missingGenuinenessSensitivity:v2MissingGenuineness,policy:'Remove the repeated g3/out-35 record once; retain g3/out-48 as missing; this is sensitivity, not repair of original data.'},
    corrections:[{id:'study2-duplicate-missing',status:'newly verified',statement:'240 rows conceal one duplicate and one missing Study 2 judgment.'},{id:'study3-genuineness-ties',status:'verified',originalP:frozen.study3.results.genuineness.p,correctedConditionalP:v3.genuineness.signedRank.p,statement:'Floating-point representations split mathematically tied ranks. Rational-equivalent tie handling changes genuineness p from .3125 to .296875; novelty p is unchanged.'},{id:'confidence-rule',statement:'The original rule uses a point-estimate threshold and CI exclusion of zero. It does not require the lower bound to exceed .30.'}],
    provenance:{requestedModels:read('experiment/v3/config.json'),returnedModels:null,requestResponseEnvelopes:null,graderPrompts:null,graderOrderReceipts:null,judgingIndependence:'Four labeled grader runs of the same requested model; independent human experts or cross-vendor replication not established.',registration:'Commit e387745 precedes collection-artifact commit 406af96. Independent timing of actual model execution is not established by Git chronology alone.'},claims};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const result=buildEvidence();
  const json=JSON.stringify(result,null,2)+'\n';
  const files=[['site/data/evidence.json',json],['site/js/evidence-data.js','// Generated by scripts/build-evidence.mjs. Do not edit by hand.\nexport const evidence = '+JSON.stringify(result,null,2)+';\nexport default evidence;\n'],['research/audit-2026-09/evidence.json',json]];
  const check=process.argv.includes('--check');
  for(const [path,data]of files){
    if(check){if(readFileSync(join(ROOT,path),'utf8')!==data)throw new Error(`Generated evidence is stale: ${path}`);}
    else{mkdirSync(join(ROOT,path,'..'),{recursive:true});writeFileSync(join(ROOT,path),data);}
  }
  console.log(JSON.stringify({generated:!check,checked:check,claims:result.claims.length,historicalFilesUnchanged:result.historyIntegrity.checkedFiles,study2UniqueJudgments:result.validation.study2.uniqueGraderOutputPairs,study3Judgments:result.validation.study3.observedRows}));
}
