// Versioned statistics for new work. Historical analyzers remain unchanged.
// Signed-rank p-values are exact conditional on observed tie-averaged ranks.
const finite = (values, name = 'values', allowEmpty = false) => {
  if (!Array.isArray(values) || (!allowEmpty && values.length === 0) ||
      values.some(x => typeof x !== 'number' || !Number.isFinite(x))) {
    throw new TypeError(`${name} must be ${allowEmpty ? 'an' : 'a nonempty'} array of finite numbers`);
  }
};
export function mean(values) {
  finite(values);
  // Divide first to avoid overflowing on a sum of individually finite values.
  return values.reduce((sum, value) => sum + value / values.length, 0);
}
function rngFromSeed(seed) {
  if (typeof seed !== 'string' && !Number.isSafeInteger(seed)) throw new TypeError('seed must be a string or safe integer');
  let state = 2166136261;
  for (const b of new TextEncoder().encode(String(seed))) state = Math.imul(state ^ b, 16777619) >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = Math.imul(state ^ (state >>> 15), state | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export function pairedBootstrap(differences, { seed, iterations = 10000 } = {}) {
  finite(differences, 'differences');
  if (seed === undefined) throw new TypeError('an explicit bootstrap seed is required');
  if (!Number.isSafeInteger(iterations) || iterations < 100 || iterations > 1000000) throw new RangeError('iterations must be an integer from 100 to 1000000');
  const random = rngFromSeed(seed), n = differences.length, samples = [];
  for (let b = 0; b < iterations; b++) {
    let value = 0;
    for (let i = 0; i < n; i++) value += differences[Math.floor(random() * n)] / n;
    samples.push(value);
  }
  samples.sort((a,b) => a-b);
  return { mean: mean(differences), ci95: [samples[Math.floor(.025*iterations)], samples[Math.ceil(.975*iterations)-1]], n,
    method: 'paired-problem-percentile-bootstrap', seed: String(seed), iterations,
    rng: 'fnv1a32-seeded-mulberry32-analysis-v1' };
}
export function signedRank(differences, { tieTolerance = 1e-12 } = {}) {
  finite(differences, 'differences', true);
  if (typeof tieTolerance !== 'number' || !Number.isFinite(tieTolerance) || tieTolerance < 0) throw new RangeError('tieTolerance must be a finite nonnegative number');
  const sorted = differences.filter(d => Math.abs(d) > tieTolerance).map(d => ({d,abs:Math.abs(d)})).sort((a,b)=>a.abs-b.abs);
  const n = sorted.length;
  if (n > 250) throw new RangeError('exact signed-rank is bounded to 250 nonzero differences');
  if (!n) return { n:0, wPlus:0, wMinus:0, p:1, rankBiserial:0, method:'exact-conditional-signed-rank-dp', tieTolerance };
  const ranks2=[];
  let plus2=0;
  for (let i=0;i<n;) {
    let j=i+1;
    while (j<n && sorted[j].abs-sorted[i].abs <= tieTolerance) j++;
    const rank2=i+1+j;
    for(let k=i;k<j;k++){ranks2.push(rank2);if(sorted[k].d>0)plus2+=rank2;}
    i=j;
  }
  const total2=ranks2.reduce((a,b)=>a+b,0), observed=Math.min(plus2,total2-plus2);
  let counts=new Map([[0,1n]]);
  for(const rank of ranks2){
    const next=new Map(counts);
    for(const [sum,count] of counts) next.set(sum+rank,(next.get(sum+rank)||0n)+count);
    counts=next;
  }
  let tail=0n;
  for(const [sum,count] of counts)if(Math.min(sum,total2-sum)<=observed)tail+=count;
  return {n,wPlus:plus2/2,wMinus:(total2-plus2)/2,p:Number(tail)/2**n,rankBiserial:(2*plus2-total2)/total2,
    method:'exact-conditional-signed-rank-dp',tieTolerance};
}
export function signFlip(differences, { tolerance = 1e-12 } = {}) {
  finite(differences, 'differences', true);
  if (typeof tolerance !== 'number' || !Number.isFinite(tolerance) || tolerance < 0) throw new RangeError('tolerance must be finite and nonnegative');
  if (differences.length>20) throw new RangeError('exact mean sign-flip enumeration is bounded to 20 paired differences');
  if (!differences.length)return {n:0,p:1,method:'exact-paired-mean-sign-flip'};
  const n=differences.length,scaled=differences.map(d=>d/n),obs=Math.abs(mean(differences));
  let count=0;
  function visit(i,sum){if(i===n){if(Math.abs(sum)>=obs-tolerance)count++;return;}visit(i+1,sum+scaled[i]);visit(i+1,sum-scaled[i]);}
  visit(0,0);
  return {n,p:count/2**n,method:'exact-paired-mean-sign-flip',tolerance};
}
export function holm(pvalues) {
  finite(pvalues, 'pvalues', true);
  if(pvalues.some(p=>p<0||p>1))throw new RangeError('pvalues must lie in [0, 1]');
  const sorted=pvalues.map((p,i)=>({p,i})).sort((a,b)=>a.p-b.p),out=Array(pvalues.length);
  let prior=0;
  sorted.forEach(({p,i},rank)=>{prior=Math.max(prior,Math.min(1,(sorted.length-rank)*p));out[i]=prior;});
  return out;
}
