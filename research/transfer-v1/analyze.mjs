// Frozen inferential bridge. Input consists of one judge-averaged score per task/arm.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {mean,signedRank,holm} from '../lib/stats.mjs';
export const ANALYSIS_VERSION='counterfactual-transfer-analysis-v1';
export const BOOTSTRAP_ITERATIONS=50000, SIGNFLIP_ITERATIONS=100000;
export function stream(namespace){
  if(typeof namespace!=='string'||!namespace)throw new Error('Analysis RNG requires an explicit nonempty namespace');
  let counter=0,buffer=null,offset=32;
  return ()=>{
    if(offset===32){buffer=createHash('sha256').update(`${namespace}\0${counter++}`).digest();offset=0;}
    const word=buffer.readUInt32BE(offset);offset+=4;return word;
  };
}
function pick(next,n){const limit=4294967296-4294967296%n;let word;do{word=next();}while(word>=limit);return word%n;}
export function stratifiedBootstrap(rows,{seed,iterations=BOOTSTRAP_ITERATIONS}={}){
  if(!Number.isSafeInteger(iterations)||iterations<100||iterations>1000000)throw new Error('Invalid bootstrap iteration count');
  if(!rows.length||rows.some(r=>typeof r.family!=='string'||!Number.isFinite(r.difference)))throw new Error('Expected finite paired differences with fixed family labels');
  const next=stream(seed),groups=new Map();
  for(const r of rows){if(!groups.has(r.family))groups.set(r.family,[]);groups.get(r.family).push(r.difference);}
  const strata=[...groups].sort(([a],[b])=>a<b?-1:a>b?1:0).map(([,values])=>values),samples=[];
  for(let b=0;b<iterations;b++){
    let sum=0;
    for(const values of strata)for(let i=0;i<values.length;i++)sum+=values[pick(next,values.length)];
    samples.push(sum/rows.length);
  }
  samples.sort((a,b)=>a-b);
  return {meanDifference:mean(rows.map(r=>r.difference)),ci95:[samples[Math.floor(.025*iterations)],samples[Math.ceil(.975*iterations)-1]],
    iterations,seed,method:'paired-task-percentile-bootstrap-within-fixed-family-strata',familySizes:Object.fromEntries([...groups].map(([k,v])=>[k,v.length]))};
}
export function monteCarloSignFlip(differences,{seed,iterations=SIGNFLIP_ITERATIONS}={}){
  if(!Number.isSafeInteger(iterations)||iterations<100||iterations>1000000)throw new Error('Invalid sign-flip iteration count');
  if(!differences.length||differences.some(v=>typeof v!=='number'||!Number.isFinite(v)))throw new Error('Expected nonempty finite paired differences');
  const next=stream(seed),observed=Math.abs(mean(differences));let extreme=0;
  for(let b=0;b<iterations;b++){
    let sum=0,word=0;
    for(let i=0;i<differences.length;i++){if(i%32===0)word=next();sum+=(word>>>(i%32)&1)?differences[i]:-differences[i];}
    if(Math.abs(sum/differences.length)>=observed-1e-12)extreme++;
  }
  return {p:(1+extreme)/(iterations+1),extremeCount:extreme,iterations,seed,method:'two-sided-paired-mean-sign-flip-monte-carlo-plus-one',tieTolerance:1e-12};
}
export function analyze(data){
  const rows=data.perProblem;
  if(!Array.isArray(rows)||!rows.length||new Set(rows.map(r=>r.taskId)).size!==rows.length)throw new Error('Task IDs must be nonempty and unique');
  for(const row of rows)for(const arm of ['S','R','LR','XR'])if(!Number.isFinite(row.arms?.[arm]?.score?.qnm)||row.arms[arm].score.qnm<0||row.arms[arm].score.qnm>4)throw new Error('Expected validated QNM@4 score for every assigned arm');
  function contrast(id,x,y){
    const paired=rows.map(r=>({taskId:r.taskId,family:r.task.family,difference:r.arms[x].score.qnm-r.arms[y].score.qnm}));
    const bootstrap=stratifiedBootstrap(paired,{seed:`wildcard-transfer-analysis-v1:bootstrap:${id}`});
    const test=monteCarloSignFlip(paired.map(r=>r.difference),{seed:`wildcard-transfer-analysis-v1:signflip:${id}`});
    const complete=rows.filter(r=>r.arms[x].status==='success'&&r.arms[y].status==='success');
    const families=[...new Set(rows.map(r=>r.task.family))].sort();
    return {id,metric:'QNM@4',armX:x,armY:y,nPairs:rows.length,meanX:mean(rows.map(r=>r.arms[x].score.qnm)),meanY:mean(rows.map(r=>r.arms[y].score.qnm)),
      difference:bootstrap.meanDifference,ci95:bootstrap.ci95,bootstrap,test,signedRankSensitivity:signedRank(paired.map(r=>r.difference)),perProblem:paired,
      judgeSpecific:Object.fromEntries(['j1','j2'].map(j=>[j,{difference:mean(rows.map(r=>r.arms[x].judges[j].qnm-r.arms[y].judges[j].qnm)),nPairs:rows.length}])),
      perFamily:Object.fromEntries(families.map(f=>[f,{difference:mean(paired.filter(r=>r.family===f).map(r=>r.difference)),nPairs:paired.filter(r=>r.family===f).length}])),
      successfulOnlySensitivity:{criterion:'Both contrasted main requests have success status; valid abstentions and failed acquisitions are excluded.',nPairs:complete.length,difference:complete.length?mean(complete.map(r=>r.arms[x].score.qnm-r.arms[y].score.qnm)):null,descriptiveOnly:true}};
  }
  const primary=contrast('LR-R','LR','R'),secondary=[contrast('R-S','R','S'),contrast('XR-LR','XR','LR')];
  const adjusted=holm(secondary.map(c=>c.test.p));secondary.forEach((c,i)=>c.holmAdjustedP=adjusted[i]);
  const directional=primary.test.p<=.05&&((primary.difference>0&&primary.ci95[0]>0)||(primary.difference<0&&primary.ci95[1]<0));
  primary.directionalEvidence=directional?(primary.difference>0?'positive':'negative'):'inconclusive';
  primary.decisionRule='Direction agrees, two-sided primary p ≤ .05, and the 95% interval excludes zero in that direction. No minimum practical benefit threshold.';
  const descriptive=Object.fromEntries(['S','R','LR','XR'].map(arm=>[arm,{
    nTasks:rows.length,means:Object.fromEntries(['qnm','qdm','qualified_actions','total_actions'].map(k=>[k,mean(rows.map(r=>r.arms[arm].score[k]))])),
    judgeMeans:Object.fromEntries(['j1','j2'].map(j=>[j,Object.fromEntries(['qnm','qdm'].map(k=>[k,mean(rows.map(r=>r.arms[arm].judges[j][k]))]))])),
    qdmCeilingSetsByJudge:Object.fromEntries(['j1','j2'].map(j=>[j,rows.filter(r=>r.arms[arm].judges[j].qdm===4).length]))
  }]));
  return {analysisVersion:ANALYSIS_VERSION,primary,secondary,descriptive,secondaryMultiplicity:'Holm across only the two specified secondary QNM contrasts; primary separate.',
    estimand:'Equal-weight mean of paired task QNM@4 differences after averaging the two required judge configurations within each task and arm.',
    bankSizeSensitivity:{status:'unexecuted',reason:'A single selected baseline_match ID cannot recover all matches against a restricted bank. Requires rejudging or complete annotations.'},
    rng:{algorithm:'SHA-256(namespace + NUL + decimal block counter), 8 big-endian u32 values per block; rejection-sampled bootstrap indices; consecutive bits of u32 words form sign vectors.',seedIsInferenceSeed:false}};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))console.log(JSON.stringify(analyze(JSON.parse(readFileSync(0,'utf8')))));
