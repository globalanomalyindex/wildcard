// Frozen task-level inference. All resampling operates on integer pass-count differences.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
export const VERSION='wildcard-working-solutions-analysis-v1';
export const BOOTSTRAP_ITERATIONS=100000, SIGNFLIP_ITERATIONS=1000000;
const DENOMINATOR=256, FAMILIES=['cache','queue','sync','ui'], ARMS=['D','R','X'];
export function stream(namespace){
  if(typeof namespace!=='string'||!namespace)throw new Error('Explicit nonempty RNG namespace required');
  let counter=0,buffer,offset=32;
  return ()=>{
    if(offset===32){buffer=createHash('sha256').update(`${namespace}\0${counter++}`).digest();offset=0;}
    const result=buffer.readUInt32BE(offset);offset+=4;return result;
  };
}
function pick(next,n){const limit=4294967296-4294967296%n;let value;do{value=next();}while(value>=limit);return value%n;}
function validateDifferences(values){
  if(!Array.isArray(values)||!values.length||values.length>32||values.some(x=>!Number.isSafeInteger(x)||Math.abs(x)>DENOMINATOR))throw new Error('Expected 1 to 32 integer case-count differences in [-256,256]');
}
function checkIterations(n){if(!Number.isSafeInteger(n)||n<100||n>1000000)throw new Error('Invalid iteration count');}
export function stratifiedBootstrap(rows,{seed,iterations=BOOTSTRAP_ITERATIONS}={}){
  validateDifferences(rows.map(r=>r.differenceCount));checkIterations(iterations);
  const groups=new Map();
  for(const row of rows){
    if(typeof row.family!=='string'||!row.family)throw new Error('Missing family');
    if(!groups.has(row.family))groups.set(row.family,[]);
    groups.get(row.family).push(row.differenceCount);
  }
  const entries=[...groups].sort(([a],[b])=>a<b?-1:a>b?1:0),next=stream(seed),samples=[];
  for(let b=0;b<iterations;b++){
    let sum=0;
    for(const [,values] of entries)for(let i=0;i<values.length;i++)sum+=values[pick(next,values.length)];
    samples.push(sum);
  }
  samples.sort((a,b)=>a-b);
  const denominator=rows.length*DENOMINATOR;
  return {meanDifference:rows.reduce((s,r)=>s+r.differenceCount,0)/denominator,
    ci95:[samples[Math.floor(.025*iterations)]/denominator,samples[Math.ceil(.975*iterations)-1]/denominator],
    iterations,seed,method:'paired-task-percentile-bootstrap-within-fixed-family-strata',
    percentileIndicesZeroBased:[Math.floor(.025*iterations),Math.ceil(.975*iterations)-1],
    familySizes:Object.fromEntries(entries.map(([family,values])=>[family,values.length])),integerDifferenceDenominator:DENOMINATOR};
}
export function signFlip(differences,{seed,iterations=SIGNFLIP_ITERATIONS}={}){
  validateDifferences(differences);checkIterations(iterations);
  const next=stream(seed),observed=Math.abs(differences.reduce((a,b)=>a+b,0));let extreme=0;
  for(let b=0;b<iterations;b++){
    const signs=next();let sum=0;
    for(let i=0;i<differences.length;i++)sum+=(signs>>>i&1)?differences[i]:-differences[i];
    if(Math.abs(sum)>=observed)extreme++;
  }
  return {p:(extreme+1)/(iterations+1),extremeCount:extreme,iterations,seed,
    method:'two-sided-paired-mean-sign-flip-monte-carlo-plus-one',comparison:'absolute integer count sum >= observed absolute integer count sum',
    observedAbsoluteCountSum:observed,integerDifferenceDenominator:DENOMINATOR};
}
export function analyze(data){
  const main=data.cohort==='main';
  if(!main&&!['development-1','development-2'].includes(data.cohort))throw new Error('Unknown cohort');
  if(!Array.isArray(data.perTask))throw new Error('Missing task rows');
  const rows=[...data.perTask].sort((a,b)=>a.taskId<b.taskId?-1:a.taskId>b.taskId?1:0);
  if(rows.length!==(main?32:8)||new Set(rows.map(r=>r.taskId)).size!==rows.length)throw new Error('Incomplete or duplicate task panel');
  for(const family of FAMILIES)if(rows.filter(r=>r.family===family).length!==(main?8:2))throw new Error('Incorrect family allocation');
  for(const row of rows){
    if(typeof row.taskId!=='string'||!row.taskId)throw new Error('Missing task identity');
    if(Object.keys(row.arms||{}).sort().join(',')!==ARMS.join(','))throw new Error('Every task requires exactly D, R, X');
    for(const arm of ARMS){const score=row.arms[arm];
      if(!Number.isSafeInteger(score.passCount)||score.passCount<0||score.passCount>DENOMINATOR||score.totalCases!==DENOMINATOR||score.fullSuite!==(score.passCount===DENOMINATOR))throw new Error('Invalid arm count or suite indicator');
    }
  }
  const summarize=rs=>Object.fromEntries(ARMS.map(arm=>[arm,{nTasks:rs.length,meanPassRate:rs.reduce((s,r)=>s+r.arms[arm].passCount,0)/(rs.length*DENOMINATOR),fullSuiteCount:rs.filter(r=>r.arms[arm].fullSuite).length,fullSuiteRate:rs.filter(r=>r.arms[arm].fullSuite).length/rs.length}]));
  const descriptive=summarize(rows);
  function contrast(id,x,y,inferential){
    const paired=rows.map(r=>({taskId:r.taskId,family:r.family,differenceCount:r.arms[x].passCount-r.arms[y].passCount}));
    const difference=paired.reduce((s,r)=>s+r.differenceCount,0)/(rows.length*DENOMINATOR);
    const bootstrap=inferential?stratifiedBootstrap(paired,{seed:`${VERSION}:bootstrap:${id}`}):null;
    const test=inferential?signFlip(paired.map(r=>r.differenceCount),{seed:`${VERSION}:signflip:${id}`}):null;
    return {id,armX:x,armY:y,nPairs:rows.length,meanX:descriptive[x].meanPassRate,meanY:descriptive[y].meanPassRate,difference,
      integerDifferenceDenominator:DENOMINATOR,nonzeroPairs:paired.filter(r=>r.differenceCount!==0).length,ci95:bootstrap?.ci95??null,bootstrap,test,perTask:paired,
      perFamily:Object.fromEntries(FAMILIES.map(f=>{const rs=paired.filter(r=>r.family===f);return [f,{nPairs:rs.length,difference:rs.reduce((s,r)=>s+r.differenceCount,0)/(rs.length*DENOMINATOR),descriptiveOnly:true}]}))};
  }
  const primary=main?contrast('R-D','R','D',true):null;
  if(primary){
    primary.positiveEvidence=primary.difference>0&&primary.ci95[0]>0&&primary.test.p<=.05;
    primary.practicalBenefit=primary.positiveEvidence&&primary.difference>=.10;
    primary.decision=primary.positiveEvidence?'positive-directional-evidence':'positive-benefit-not-established';
    primary.decisionRule='Positive mean, two-sided p <= .05, and 95% bootstrap lower endpoint > 0; practical-benefit gate additionally requires point difference >= .10. No equivalence or minimum-true-effect claim.';
  }
  const secondary=main?contrast('R-X','R','X',primary.positiveEvidence):null;
  if(secondary){secondary.inferentialGateOpen=primary.positiveEvidence;secondary.positiveEvidence=primary.positiveEvidence?secondary.difference>0&&secondary.ci95[0]>0&&secondary.test.p<=.05:null;}
  return {analysisVersion:VERSION,cohort:data.cohort,nTasks:rows.length,descriptive,perFamily:Object.fromEntries(FAMILIES.map(f=>[f,summarize(rows.filter(r=>r.family===f))])),primary,secondary,
    developmentGate:main?null:{dMean:descriptive.D.meanPassRate,floor:descriptive.D.meanPassRate<=.10,ceiling:descriptive.D.meanPassRate>=.95,readyForMain:descriptive.D.meanPassRate>.10&&descriptive.D.meanPassRate<.95,criterion:'Complete validated development evidence and direct mean strictly between .10 and .95. Outside-arm outcomes do not choose difficulty.'},
    prototypeReadiness:{benchmarkGateMet:main?descriptive.R.meanPassRate>=.95&&descriptive.R.fullSuiteCount>=24:null,criterion:'Main R mean >= .95 and at least 24 of 32 R programs pass the complete suite; a benchmark gate only, not production reliability or comparative benefit.'},
    estimand:'Equal-weight paired difference in per-task hidden-instance pass rate; each of four fixed regimes has 64 cases and each of 32 main tasks receives equal weight.',
    multiplicity:'Fixed sequence: inferential R-X is computed only after the primary R-D positive-evidence gate opens; no additional hypothesis family.',
    rng:{algorithm:'SHA-256 of UTF-8 namespace + NUL + decimal counter beginning 0; eight big-endian uint32 words per block. Bootstrap uses rejection-sampled unbiased indices; each sign-flip draw consumes one uint32 with task signs from least significant bit upward.',purpose:'Analysis resampling only, not provider decoding or hidden-case generation.',bootstrapIterations:BOOTSTRAP_ITERATIONS,signFlipIterations:SIGNFLIP_ITERATIONS},
    limitations:['Inference is conditional on these authored task families, fixed donor library and matching schedule.','Sign-flip inference assumes exchangeability of paired signs under the null; symmetry is not established by this small authored sample.','Calls and response limits are matched; realized tokens and unavailable decoding settings are not exactly matched.','A null result is not equivalence, and hidden cases do not increase the independent task count.']};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))console.log(JSON.stringify(analyze(JSON.parse(readFileSync(0,'utf8')))));
