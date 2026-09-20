import {readFileSync,existsSync} from 'node:fs';
import {join} from 'node:path';
const METRICS=['genuineness','usefulness','novelty','nonDerailment'];
export const DESIGNS={study1:{path:'experiment',arms:['A','B','C'],replicates:3},study2:{path:'experiment/v2',arms:['v1','v2'],replicates:3},study3:{path:'experiment/v3',arms:['W','P'],replicates:3}};
export function validateRecords({selected,manifest,graders,arms,replicates=3},{mode='strict'}={}) {
  if(!['strict','legacy-available-case'].includes(mode))throw new Error('Use strict or explicitly named legacy-available-case mode');
  const problems=(Array.isArray(selected)?selected:selected.problems).map(p=>p.id),issues=[];
  const issue=(code,details)=>issues.push({code,...details});
  if(new Set(problems).size!==problems.length)issue('duplicate-problem',{});
  const expected=new Set(arms.flatMap(a=>problems.flatMap(p=>Array.from({length:replicates},(_,i)=>`${a}|${p}|${i+1}`))));
  const seenTuples=new Set(),outputs=new Set();
  for(const r of manifest){
    const tuple=`${r.arm}|${r.problemId}|${r.rep??r.run}`;
    if(!expected.has(tuple))issue('unknown-design-cell',{output:r.outId,tuple});
    if(seenTuples.has(tuple))issue('duplicate-design-cell',{output:r.outId,tuple});
    if(outputs.has(r.outId))issue('duplicate-output',{output:r.outId});
    if(typeof r.abstained!=='boolean')issue('invalid-manifest-abstention',{output:r.outId});
    seenTuples.add(tuple);outputs.add(r.outId);
  }
  for(const tuple of expected)if(!seenTuples.has(tuple))issue('missing-design-cell',{tuple});
  const graderIDs=new Set(),uniquePairs=new Set(),byGrader=[];
  let rows=0;
  for(const g of graders){
    const grader=g.grader??g.graderId;
    if(!['g1','g2','g3','g4'].includes(grader))issue('unknown-grader',{grader});
    if(graderIDs.has(grader))issue('duplicate-grader',{grader});
    graderIDs.add(grader);
    const seen=new Set();
    for(const r of g.grades){
      rows++;
      if(seen.has(r.id))issue('duplicate-rating',{grader,output:r.id});
      if(!outputs.has(r.id))issue('unknown-rating-output',{grader,output:r.id});
      seen.add(r.id);uniquePairs.add(`${grader}|${r.id}`);
      for(const metric of METRICS)if(!Number.isInteger(r[metric])||r[metric]<1||r[metric]>7)issue('invalid-rating',{grader,output:r.id,metric});
      for(const key of ['fabrication','abstained'])if(typeof r[key]!=='boolean')issue('invalid-boolean',{grader,output:r.id,key});
    }
    const missing=[...outputs].filter(id=>!seen.has(id)).sort();
    for(const output of missing)issue('missing-rating',{grader,output});
    byGrader.push({grader,rows:g.grades.length,uniqueOutputs:seen.size,missing});
  }
  for(const grader of ['g1','g2','g3','g4'])if(!graderIDs.has(grader))issue('missing-grader',{grader});
  const report={mode,confirmatoryEligible:issues.length===0,expectedOutputs:expected.size,observedOutputs:manifest.length,
    scheduledRatings:expected.size*4,observedRows:rows,uniqueGraderOutputPairs:uniquePairs.size,byGrader,issues};
  const permittedLegacy=new Set(['missing-rating','duplicate-rating']);
  if(issues.length && (mode==='strict'||issues.some(i=>!permittedLegacy.has(i.code)))){
    const error=new Error(`Historical validation failed: ${issues.map(i=>`${i.code}:${i.grader??''}:${i.output??''}`).join(', ')}`);
    error.report=report;throw error;
  }
  return report;
}
export function readStudy(root,id,{mode='strict'}={}){
  const design=DESIGNS[id];if(!design)throw new Error(`Unknown study ${id}`);
  const dir=join(root,design.path),read=file=>JSON.parse(readFileSync(join(dir,file),'utf8'));
  const selected=read('problems-selected.json'),manifest=read('raw/manifest.json'),graders=read('grades.json').graders;
  const validation=validateRecords({selected,manifest,graders,...design},{mode});
  for(const row of manifest)for(const stage of ['raw','normalized']){
    const path=join(dir,stage,`${row.id??row.outId}.md`);
    if(!existsSync(path))throw new Error(`Missing historical output ${path}`);
  }
  return {selected,manifest,graders,design,validation};
}
