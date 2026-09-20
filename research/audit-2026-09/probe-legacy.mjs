// Read-only diagnostic of the legacy CRC and Fisher–Yates code.
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {join} from 'node:path';
import {ROOT} from '../../scripts/verify-history.mjs';
import {seededShuffle} from '../../experiment/lib/seeded.mjs';
import {pickIndex} from '../../site/js/entropy.js';
const bytes=readFileSync(join(ROOT,'site/js/entropy.js'));
const blob=createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
if(blob!=='db9c16347c63edea904e7ee8b700f857a5597ef6')throw new Error('Legacy entropy source changed; run this probe against the pinned historical source.');
const permutations={};
for(const n of [3,4,8]){
  const seen=new Set();
  for(let i=0;i<100000;i++)seen.add(seededShuffle(Array.from({length:n},(_,j)=>j),'audit',String(i).padStart(6,'0')).join(','));
  permutations[n]={diagnosticSeeds:100000,seedByteLength:6,tag:'audit',uniquePermutations:seen.size};
}
const modeLensCounts=[Array(8).fill(0),Array(8).fill(0)],leaves=[new Set(),new Set()];
for(let i=0;i<100000;i++){
  const s=String(i).padStart(22,'0'),m=pickIndex('mode',s,2),l=pickIndex('lens',s,8);
  modeLensCounts[m][l]++;leaves[m].add(pickIndex(m?'concept':'domain',s,m?461:378));
}
const treatment=JSON.parse(readFileSync(join(ROOT,'experiment/v3/raw/manifest.json'),'utf8')).filter(x=>x.arm==='W');
console.log(JSON.stringify({analysisVersion:'legacy-probe-2026-09-v1',sourceGitBlob:blob,diagnosticSeeds:100000,fixedSeedByteLength:22,modeLensCounts,conditionalUniqueLeaves:leaves.map(s=>s.size),permutations,
  study3:{draws:treatment.length,modeLensParityCoupled:treatment.filter(r=>pickIndex('mode',r.seed,2)===pickIndex('lens',r.seed,8)%2).length},
  caveat:'These finite seed-bank diagnostics show legacy dependencies. They do not measure resulting output quality or establish actual grader exposure.'},null,2));
