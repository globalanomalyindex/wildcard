// Post-hoc finite-bootstrap sensitivity, not a new confidence-interval method.
// Integer convolution evaluates every ordered resample, removing Monte Carlo error.
import {mean} from '../lib/stats.mjs';
export function exactBootstrap(differences,{scale=360}={}){
  mean(differences);
  const n=differences.length,total=n**n;
  if(n>12||!Number.isSafeInteger(total)||!Number.isSafeInteger(scale)||scale<1)throw new RangeError('Exact audit bootstrap supports at most 12 units and an explicit integer scale');
  const values=differences.map(d=>{const v=Math.round(d*scale);if(Math.abs(v/scale-d)>1e-10)throw new Error('Difference is not represented by exact audit scale');return v;});
  let counts=new Map([[0,1]]);
  for(let i=0;i<n;i++){
    const next=new Map();
    for(const [s,c]of counts)for(const v of values)next.set(s+v,(next.get(s+v)||0)+c);
    counts=next;
  }
  const sorted=[...counts].sort((a,b)=>a[0]-b[0]);
  if(sorted.reduce((s,[,c])=>s+c,0)!==total)throw new Error('Bootstrap mass conservation failure');
  function quantile(q){let cumulative=0;for(const [v,c]of sorted){cumulative+=c;if(cumulative>=q*total)return v/(scale*n);}throw new Error('Quantile failed');}
  return {mean:mean(differences),ci95:[quantile(.025),quantile(.975)],method:'exact-finite-paired-percentile-bootstrap',orderedResamples:total,scale,n};
}
