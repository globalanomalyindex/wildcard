// Zero-dependency statistics for the experiment analysis. Small-N, ordinal-friendly,
// non-parametric: exactly what the pre-registration specifies. Each function is pure.

// Shannon entropy in bits over a histogram of counts.
export function shannonEntropy(counts) {
  const total = counts.reduce((a, b) => a + b, 0);
  let h = 0;
  for (const c of counts) {
    if (c === 0) continue;
    const p = c / total;
    h -= p * Math.log2(p);
  }
  return h;
}

// Cliff's delta: P(x > y) - P(x < y) over all cross-group pairs. Range [-1, 1].
export function cliffsDelta(xs, ys) {
  let gt = 0, lt = 0;
  for (const x of xs) for (const y of ys) {
    if (x > y) gt++;
    else if (x < y) lt++;
  }
  return (gt - lt) / (xs.length * ys.length);
}

// Average ranks with ties (1-based), shared by spearman and wilcoxon.
export function rankWithTies(arr) {
  const idx = arr.map((v, i) => ({ v, i })).sort((a, b) => a.v - b.v);
  const ranks = new Array(arr.length);
  let k = 0;
  while (k < idx.length) {
    let j = k;
    while (j + 1 < idx.length && idx[j + 1].v === idx[k].v) j++;
    const avg = (k + j + 2) / 2;
    for (let m = k; m <= j; m++) ranks[idx[m].i] = avg;
    k = j + 1;
  }
  return ranks;
}

// Spearman rank correlation (Pearson on tie-averaged ranks).
export function spearman(xs, ys) {
  const rx = rankWithTies(xs), ry = rankWithTies(ys);
  const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length;
  const mx = mean(rx), my = mean(ry);
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < xs.length; i++) {
    num += (rx[i] - mx) * (ry[i] - my);
    dx += (rx[i] - mx) ** 2;
    dy += (ry[i] - my) ** 2;
  }
  return num / Math.sqrt(dx * dy);
}

// Deterministic PRNG for the (seeded, pre-registered) bootstrap.
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Percentile bootstrap 95% CI of statFn over resamples (with replacement) of items.
export function bootstrapCI(items, statFn, iterations, rng) {
  const stats = [];
  for (let it = 0; it < iterations; it++) {
    const sample = Array.from({ length: items.length },
      () => items[Math.floor(rng() * items.length)]);
    stats.push(statFn(sample));
  }
  stats.sort((a, b) => a - b);
  return {
    lo: stats[Math.floor(0.025 * iterations)],
    hi: stats[Math.ceil(0.975 * iterations) - 1],
  };
}

// Exact two-sided Wilcoxon signed-rank test by full enumeration of the 2^n sign
// assignments (n after dropping zero diffs; n=10 -> 1024 cases, instant). Returns
// { wPlus, n, p }. Exact conditional on the observed tie-averaged ranks.
export function wilcoxonExact(diffs) {
  const nz = diffs.filter((d) => d !== 0);
  const n = nz.length;
  if (n === 0) return { wPlus: 0, n: 0, p: 1 };
  const ranks = rankWithTies(nz.map(Math.abs));
  let wPlus = 0;
  nz.forEach((d, i) => { if (d > 0) wPlus += ranks[i]; });
  const wMax = ranks.reduce((s, r) => s + r, 0);
  const wObs = Math.min(wPlus, wMax - wPlus);
  let count = 0;
  const total = 1 << n;
  for (let mask = 0; mask < total; mask++) {
    let w = 0;
    for (let b = 0; b < n; b++) if (mask & (1 << b)) w += ranks[b];
    if (Math.min(w, wMax - w) <= wObs + 1e-12) count++;
  }
  return { wPlus, n, p: count / total };
}

// Krippendorff's alpha with the ordinal difference metric (Krippendorff 2011).
// items: array per unit of the ratings it received (2+ raters; variable ok).
export function krippendorffAlphaOrdinal(items) {
  const values = [...new Set(items.flat())].sort((a, b) => a - b);
  const vi = new Map(values.map((v, i) => [v, i]));
  const V = values.length;
  const o = Array.from({ length: V }, () => new Array(V).fill(0));
  for (const ratings of items) {
    const m = ratings.length;
    if (m < 2) continue;
    for (let a = 0; a < m; a++) for (let b = 0; b < m; b++) {
      if (a === b) continue;
      o[vi.get(ratings[a])][vi.get(ratings[b])] += 1 / (m - 1);
    }
  }
  const nc = values.map((_, c) => o[c].reduce((s, x) => s + x, 0));
  const n = nc.reduce((s, x) => s + x, 0);
  const dist = (c, k) => {
    if (c === k) return 0;
    const [lo, hi] = c < k ? [c, k] : [k, c];
    let s = 0;
    for (let g = lo; g <= hi; g++) s += nc[g];
    s -= (nc[lo] + nc[hi]) / 2;
    return s * s;
  };
  let Do = 0, De = 0;
  for (let c = 0; c < V; c++) for (let k = 0; k < V; k++) {
    Do += o[c][k] * dist(c, k);
    De += nc[c] * nc[k] * dist(c, k);
  }
  Do /= n;
  De /= n * (n - 1);
  return 1 - Do / De;
}
