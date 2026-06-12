# Wildcard Experiment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the pre-registered, blind, three-arm experiment from `docs/superpowers/specs/2026-06-12-wildcard-experiment-design.md`, then fold the measured results into the case study, skill, and site.

**Architecture:** Pure, tested libraries first (seeded derivation + statistics), then the pre-registration freeze (master seed M committed before any data), then phased Workflow fan-outs (blind pool -> collection -> normalization -> blind panel), with raw data quarantined in an OS temp dir outside the repo until grading completes. Analysis is a zero-dependency node script over frozen committed artifacts, CI-gated. Subjects pinned to fable-5, graders pinned to opus-4-8.

**Tech Stack:** node 26 (node:test, ES modules, zero dependencies), bash, the repo's existing cksum entropy module (`site/js/entropy.js`), the Workflow tool for fan-out.

**Branch:** `experiment` (already created; spec committed).

**Working agreements (apply to every task):**
- No em dashes or en dashes in any prose file. Use " - ", commas, colons.
- Site-rendered copy and case-study/colophon prose is all-lowercase.
- Every commit ends with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- `<ABS>` below means the absolute repo root `/Users/chrisfiore/Documents/Claude/Projects/wildcard`.
- Values written `{like.this}` in templates are data slots filled from `experiment/results.json` at execution time. They are data dependence, not plan placeholders.

**File structure created by this plan:**

```
experiment/
  lib/seeded.mjs            derived-seed selection + shuffle (reuses site/js/entropy.js)
  lib/stats.mjs             entropy, cliff's delta, bootstrap CI, exact wilcoxon,
                            krippendorff alpha (ordinal), spearman, mulberry32
  tests/seeded.test.js
  tests/stats.test.js
  tests/analyze.test.js
  tests/fixtures/tiny/      minimal synthetic dataset for the analyze smoke test
  preregistration.md        hypotheses, prompts verbatim, rubric, master seed M, analysis plan
  problems-pool.json        blind-authored pool (committed before selection)
  problems-selected.json    the 10 drawn problems + derivation
  raw/                      90 transcripts + manifest.json (committed at freeze, after grading)
  normalized/               90 anonymized outputs + idmap.json (committed at freeze)
  h1/selfpicks.json         200 self-picks + canonical labels + adjacency
  h1/externals.json         200 matched external draws + adjacency
  grades.json               4 graders x 90 + blinding-check guesses
  human-anchor.json         the user's blind gradings (15 outputs)
  results.json              machine-readable analysis output
  results.md                generated report
scripts/analyze_experiment.mjs
docs/methods-colophon.md
```

---

### Task 1: Seeded derivation library

**Files:**
- Create: `experiment/lib/seeded.mjs`
- Test: `experiment/tests/seeded.test.js`

- [ ] **Step 1: Write the failing test**

```js
// experiment/tests/seeded.test.js
import test from "node:test";
import assert from "node:assert/strict";
import { selectDistinct, seededShuffle } from "../lib/seeded.mjs";

test("selectDistinct returns the requested count of distinct in-range indices", () => {
  const idx = selectDistinct("problems", "testM", 50, 10);
  assert.equal(idx.length, 10);
  assert.equal(new Set(idx).size, 10);
  for (const i of idx) assert.ok(i >= 0 && i < 50);
});

test("selectDistinct is deterministic for a given seed and differs across seeds", () => {
  const a = selectDistinct("problems", "testM", 50, 10);
  const b = selectDistinct("problems", "testM", 50, 10);
  const c = selectDistinct("problems", "otherM", 50, 10);
  assert.deepEqual(a, b);
  assert.notDeepEqual(a, c);
});

test("seededShuffle is a deterministic permutation and does not mutate input", () => {
  const arr = ["a", "b", "c", "d", "e", "f", "g"];
  const s1 = seededShuffle(arr, "ids", "testM");
  const s2 = seededShuffle(arr, "ids", "testM");
  assert.deepEqual(s1, s2);
  assert.deepEqual([...s1].sort(), [...arr].sort());
  assert.deepEqual(arr, ["a", "b", "c", "d", "e", "f", "g"]);
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node --test experiment/tests/seeded.test.js`
Expected: FAIL (cannot find module `../lib/seeded.mjs`)

- [ ] **Step 3: Write the implementation**

```js
// experiment/lib/seeded.mjs
// Derived-seed utilities for the experiment. Every random choice in the study derives
// from the master seed M (drawn from /dev/urandom at pre-registration, committed before
// any data existed) through the SAME parity-tested cksum stream the draw uses.
// Honest note (disclosed in the pre-registration): seeded picks are cksum % n, the
// parity path, not the rejection-sampled entropy path; modulo bias over a 2^32 hash is
// < 1.2e-8 for n <= 1000, negligible at this scale.
import { pickIndex } from "../../site/js/entropy.js";

// count distinct indices in [0, poolSize), derived from `${tag}:${i}` streams of M.
export function selectDistinct(tag, masterSeed, poolSize, count) {
  if (count > poolSize) throw new Error("count exceeds pool");
  const chosen = [];
  for (let i = 0; chosen.length < count; i++) {
    const idx = pickIndex(`${tag}:${i}`, masterSeed, poolSize);
    if (!chosen.includes(idx)) chosen.push(idx);
  }
  return chosen;
}

// Fisher-Yates with each swap index drawn from its own derived stream. Pure: returns a copy.
export function seededShuffle(arr, tag, masterSeed) {
  const out = arr.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = pickIndex(`${tag}:${i}`, masterSeed, i + 1);
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `node --test experiment/tests/seeded.test.js`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add experiment/lib/seeded.mjs experiment/tests/seeded.test.js
git commit -m "feat(experiment): seeded derivation lib (selectDistinct, seededShuffle) over the parity-tested cksum stream

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Statistics library, part 1 (entropy, cliff's delta, spearman, PRNG, bootstrap)

**Files:**
- Create: `experiment/lib/stats.mjs`
- Test: `experiment/tests/stats.test.js`

- [ ] **Step 1: Write the failing tests**

```js
// experiment/tests/stats.test.js
import test from "node:test";
import assert from "node:assert/strict";
import {
  shannonEntropy, cliffsDelta, spearman, mulberry32, bootstrapCI,
} from "../lib/stats.mjs";

const close = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) < eps, `${a} !~ ${b}`);

test("shannonEntropy: uniform 2 -> 1 bit, single mass -> 0, uniform 4 -> 2 bits", () => {
  close(shannonEntropy([10, 10]), 1);
  close(shannonEntropy([20]), 0);
  close(shannonEntropy([5, 5, 5, 5]), 2);
});

test("cliffsDelta: full separation -> 1, identical distributions -> 0, reversed -> -1", () => {
  close(cliffsDelta([2, 2, 2], [1, 1, 1]), 1);
  close(cliffsDelta([1, 2], [1, 2]), 0);
  close(cliffsDelta([1, 1], [2, 2]), -1);
});

test("spearman: perfect monotone -> 1, perfect inverse -> -1, handles ties", () => {
  close(spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1);
  close(spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1);
  const r = spearman([1, 1, 2, 3], [2, 2, 4, 6]);
  close(r, 1); // tied ranks on both sides, still perfectly monotone
});

test("mulberry32: deterministic stream in [0,1)", () => {
  const a = mulberry32(42), b = mulberry32(42), c = mulberry32(43);
  const seqA = [a(), a(), a()], seqB = [b(), b(), b()];
  assert.deepEqual(seqA, seqB);
  assert.notDeepEqual(seqA, [c(), c(), c()]);
  for (const v of seqA) assert.ok(v >= 0 && v < 1);
});

test("bootstrapCI: deterministic for a seeded rng, ordered, brackets the point estimate", () => {
  const pairs = [1, 2, 3, 4, 5];
  const mean = (xs) => xs.reduce((s, v) => s + v, 0) / xs.length;
  const r1 = bootstrapCI(pairs, mean, 2000, mulberry32(7));
  const r2 = bootstrapCI(pairs, mean, 2000, mulberry32(7));
  assert.deepEqual(r1, r2);
  assert.ok(r1.lo <= mean(pairs) && mean(pairs) <= r1.hi);
  assert.ok(r1.lo >= 1 && r1.hi <= 5);
});
```

- [ ] **Step 2: Run to verify failure**

Run: `node --test experiment/tests/stats.test.js`
Expected: FAIL (cannot find module `../lib/stats.mjs`)

- [ ] **Step 3: Write the implementation**

```js
// experiment/lib/stats.mjs
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
```

- [ ] **Step 4: Run to verify pass**

Run: `node --test experiment/tests/stats.test.js`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add experiment/lib/stats.mjs experiment/tests/stats.test.js
git commit -m "feat(experiment): stats lib part 1 (entropy, cliff's delta, spearman, seeded bootstrap)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Statistics library, part 2 (exact Wilcoxon, Krippendorff's alpha ordinal)

**Files:**
- Modify: `experiment/lib/stats.mjs` (append)
- Modify: `experiment/tests/stats.test.js` (append)

- [ ] **Step 1: Append the failing tests**

```js
// append to experiment/tests/stats.test.js
import { wilcoxonExact, krippendorffAlphaOrdinal } from "../lib/stats.mjs";

test("wilcoxonExact: all-positive diffs n=5 -> two-sided p = 2/32", () => {
  const r = wilcoxonExact([1, 2, 3, 4, 5]);
  assert.equal(r.n, 5);
  close(r.p, 2 / 32);
});

test("wilcoxonExact: drops zero diffs and is symmetric in sign", () => {
  const a = wilcoxonExact([0, 1, 2, 3, 4, 5]);
  assert.equal(a.n, 5);
  close(a.p, 2 / 32);
  const b = wilcoxonExact([-1, -2, -3, -4, -5]);
  close(b.p, 2 / 32);
});

test("wilcoxonExact: balanced diffs are not significant", () => {
  const r = wilcoxonExact([1, -1, 2, -2, 3, -3]);
  assert.ok(r.p > 0.5);
});

test("krippendorffAlphaOrdinal: perfect agreement -> 1", () => {
  close(krippendorffAlphaOrdinal([[1, 1], [5, 5], [3, 3], [7, 7]]), 1);
});

test("krippendorffAlphaOrdinal: hand-derived binary fixture -> 4/9", () => {
  // items [[1,1],[2,2],[1,2]]; coincidence: o11=2, o22=2, o12=o21=1; n1=n2=3, n=6.
  // ordinal d(1,2)^2 = (n1+n2 - (n1+n2)/2)^2 = 3^2 = 9.
  // Do = (1/6)(1*9 + 1*9) = 3.  De = (1/(6*5))(3*3*9*2) = 5.4.  alpha = 1 - 3/5.4 = 4/9.
  close(krippendorffAlphaOrdinal([[1, 1], [2, 2], [1, 2]]), 4 / 9, 1e-12);
});

test("krippendorffAlphaOrdinal: near disagreement hurts less than far (the ordinal property)", () => {
  const near = krippendorffAlphaOrdinal([[1, 2], [2, 1], [1, 1], [2, 2], [4, 4], [7, 7]]);
  const far = krippendorffAlphaOrdinal([[1, 7], [7, 1], [1, 1], [2, 2], [4, 4], [7, 7]]);
  assert.ok(near > far, `${near} should exceed ${far}`);
});
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `node --test experiment/tests/stats.test.js`
Expected: FAIL (wilcoxonExact is not exported)

- [ ] **Step 3: Append the implementation**

```js
// append to experiment/lib/stats.mjs

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
```

- [ ] **Step 4: Run to verify pass**

Run: `node --test experiment/tests/stats.test.js`
Expected: PASS (11 tests)

- [ ] **Step 5: Commit**

```bash
git add experiment/lib/stats.mjs experiment/tests/stats.test.js
git commit -m "feat(experiment): stats lib part 2 (exact wilcoxon by enumeration, krippendorff alpha ordinal)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Wire experiment tests into the CI gate

**Files:**
- Modify: `tests/run_all.sh:14` (insert before the final if)

- [ ] **Step 1: Add the suite line**

In `tests/run_all.sh`, after the `== diversity (real map) ==` line and before the final `if`, insert
(explicit glob - node 26 rejects a bare directory path to `--test`):

```bash
echo "== experiment libs =="; node --test "$ROOT"/experiment/tests/*.test.js || fail=1
```

- [ ] **Step 2: Run the full suite**

Run: `bash tests/run_all.sh`
Expected: ends `ALL GREEN`, with a `== experiment libs ==` section showing 14 passing tests (11 stats + 3 seeded).

- [ ] **Step 3: Commit**

```bash
git add tests/run_all.sh
git commit -m "test: CI gate runs the experiment library suites

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4b: Skill creative-posture refresh (MUST land before the Task 5 freeze)

The skill gains the conviction search posture (become it, think from it not about it; search
from the premise a connection exists; abstention is an earned terminus, not a reflex) while the
structure-mapping accept-test stays exactly as strict. This ships to the skill regardless of the
experiment; doing it now means the study tests the version users get. Arms A and B read SKILL.md
live, so both inherit it; A vs B still isolates only the draw source.

**Files:**
- Modify: `plugin/SKILL.md`
- Modify: `plugin/references/connecting.md`

- [ ] **Step 1: SKILL.md - add the posture to step 3 (inhabit)**

Replace:

```
**3. Inhabit the wildcard (branch on `mode`).**
```

with:

```
**3. Inhabit the wildcard (branch on `mode`).** Do not study the draw from the outside -
*become* it. You know a thing by thinking *from* it, not *about* it, and that inhabiting is
the conditioning that does the seeding; so reason from inside the wildcard, not at arm's length.
```

- [ ] **Step 2: SKILL.md - reframe the close of step 4 (search vs offer)**

Replace:

```
Both branches end in the *same* two places: genuine connections, or honest abstention. If little
maps, abstain gracefully - that is the skill working, not failing. Refinement never licenses a
connection the bar would reject.
```

with:

```
**Search from conviction; offer with rigor.** Do not open by asking whether a connection exists
- that question is an out, and it makes you bail at the first non-obvious turn. Work from the
premise that a structure is there to be uncovered, and let that conviction drive the search deep
(spread further, refine the loose strand one step more). What you *present*, though, is still
governed by the structure-mapping bar: offer only what genuinely maps. Conviction fuels the dig;
the bar governs the gold. Abstention remains - never fabricate - but it is the rare, earned
terminus of a wholehearted search that still found no isomorphism, not a reflex you reach for
early. Refinement never licenses a connection the bar would reject.
```

- [ ] **Step 3: SKILL.md - guard the no-fabrication guarantee against misreading**

Replace:

```
- **No fabrication.** Only genuine structural matches; abstention is honorable. You are never
  rewarded for hitting a count.
```

with:

```
- **No fabrication.** Only genuine structural matches; abstention is honorable. You are never
  rewarded for hitting a count. Mind the division of labor: you *search* from the conviction
  that a connection is there to uncover (this drives depth), but you *offer* only what passes
  the structure-mapping bar (this keeps you honest). Conviction is a search posture, never a
  license to assert a connection that does not hold.
```

- [ ] **Step 4: SKILL.md - tie the mechanism to its older statement (why specificity matters)**

Replace:

```
In concept mode the same logic runs through the concept's precise relational properties rather
than a person: it is the *specificity* of the conditioning, persona or property, that does the
seeding.
```

with:

```
In concept mode the same logic runs through the concept's precise relational properties rather
than a person: it is the *specificity* of the conditioning, persona or property, that does the
seeding. This mechanism is older than the model: you know a thing, as Goddard put it, by
*becoming* it - by thinking *from* it, not *about* it. Inhabiting the wildcard rather than
analyzing it is exactly the difference between shifting the conditioning to a coherent distant
region and merely adding noise.
```

- [ ] **Step 5: connecting.md - conviction in the cast (intro)**

Replace:

```
Think
of it as a web you spin out from the concept: most strands catch nothing and are swept away, and
you offer only the few that hold weight.
```

with:

```
Think
of it as a web you spin out from the concept, from the conviction that a strand will hold - that
is what makes you cast widely and dig rather than bail. Most strands still catch nothing and are
swept away; you offer only the few that genuinely hold weight.
```

- [ ] **Step 6: connecting.md - earned abstention (terminus)**

Replace:

```
A wide cast that yields nothing is the skill working: you say so plainly (see the
graceful-abstention shape in structure-mapping.md) and hand over the one true fragment you found, or
none.
```

with:

```
A wide cast that, after a wholehearted search, still yields nothing is the skill working and not
a reflex reached for early: you say so plainly (see the graceful-abstention shape in
structure-mapping.md) and hand over the one true fragment you found, or none.
```

- [ ] **Step 7: Verify and commit**

Run: `grep -nP '[\x{2013}\x{2014}]' plugin/SKILL.md plugin/references/connecting.md || echo clean`
Expected: `clean`.
Run: `bash plugin/scripts/draw.sh --seed 1` (sanity: skill scripts untouched, still draws).

```bash
git add plugin/SKILL.md plugin/references/connecting.md
git commit -m "feat(skill): conviction search posture (become it, think from it) with the honesty bar unchanged; earned abstention

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Pre-registration freeze (the heart of the study)

**Files:**
- Create: `experiment/preregistration.md`

This document must be committed BEFORE the problem pool, any transcript, or any grade exists. It contains the master seed, all prompts verbatim, the rubric verbatim, and the analysis plan. The executor drafts it from the template below, draws M, fills it in, and commits.

- [ ] **Step 1: Draw the master seed M**

Run: `M=$(od -An -N8 -tx8 /dev/urandom | tr -d ' '); echo "$M"`
Expected: a 16-hex-char string, e.g. `9f3a1c0b2e4d5a67`. Record it; it goes in the document and in every later derivation.

- [ ] **Step 2: Write `experiment/preregistration.md`**

Write the document with exactly these sections and contents (prose may be lightly edited for flow, but hypotheses, endpoints, derivations, prompts, rubric anchors, and bands are verbatim and binding):

````markdown
# pre-registration: wildcard three-arm experiment

frozen at commit time; the git timestamp of this file's first commit is the freeze.
nothing below changes after data collection begins. master seed M = `<M-HEX>` was drawn
from /dev/urandom at freeze time, before any problem pool, transcript, or grade existed.

## hypotheses

- **H1 (divergence):** asked to self-select "a random unrelated expert or concept" for a
  problem, the subject model's picks are far less diverse than a uniform external draw
  (lower distinct-count and entropy, higher top-pick share), and disproportionately
  adjacent to the problem's surface vocabulary.
- **H2 (quality):** outputs produced under the external draw (arm B) are at least as
  structurally genuine as outputs produced under self-selection (arm A). primary
  endpoint: the structural-genuineness rubric item, arm B vs arm A, paired by problem.
  direction is two-sided; we pre-commit to publishing whatever lands, including a null
  or a result against arm B.

## design constants

subject model: claude-fable-5 (all arms, all self-picks). grader model: claude-opus-4-8.
arms A/B/C as specified in the design spec. 10 problems, 3 runs per problem per arm,
K=20 self-picks per problem, K=20 matched external draws per problem, 4 graders, all 90
outputs graded by all 4.

## derivations from M (all via the repo's parity-tested cksum stream)

- problem selection: indices `pickIndex("problems:" + i, M, poolSize)` for i = 0, 1, ...
  skipping repeats, until 10 distinct (experiment/lib/seeded.mjs selectDistinct).
- arm B draw seeds: `M:draw:<problem-id>:r<run>` passed to draw.sh --seed.
- matched external H1 draws: seeds `M:h1ext:<problem-id>:<k>`, k = 1..20.
- opaque output ids: seededShuffle of the 90 manifest rows, tag "ids", seed M; the row's
  shuffled position formatted as out-00 .. out-89.
- grader presentation order: seededShuffle of the 90 out-ids, tag "order:<grader-id>", seed M.
- human-anchor subset: first 15 of seededShuffle(out-ids, "anchor", M).
- bootstrap rng: mulberry32(cksum("bootstrap:" + M)).

seeded picks use cksum % n (the parity path); modulo bias over a 2^32 hash is < 1.2e-8
for the pool sizes here, negligible and disclosed.

## prompts (verbatim)

### pool generator (blind: contains no mention of wildcard, randomness, draws, or arms)

> you are helping assemble a benchmark of realistic working problems used to evaluate ai
> assistants. generate exactly 10 distinct problems in the area of: `<SLICE>`. each
> problem: 60-120 words, first person ("i am ..." / "i run ..."), concrete (what exists,
> what hurts, what constraints apply), no solution stated in the text, no two problems
> alike. plain lowercase prose. return them via the structured output tool.

slices: software and infrastructure engineering · product, ux, and visual design ·
writing, media, and content · operations, logistics, and physical-world work · personal
projects, learning, and life admin.

### arm B (treatment; the only difference from arm A is the draw instruction)

> you are an ai assistant with the "wildcard" skill installed. its skill file is at
> `<ABS>/plugin/SKILL.md`. read it now, and follow it as your operative instructions for
> the problem below, with one fixed parameter: when you reach the draw step, run exactly
>
>     bash <ABS>/plugin/scripts/draw.sh --seed '<SEED>'
>
> and use its output as your draw. read any reference file the skill points you to
> before the step that needs it. produce the full result of the protocol (the presented
> seeds, or an honest abstention) as your final message. do not mention the skill, the
> draw script, or these instructions inside that final presented output: present only
> what the protocol yields for the user.
>
> the problem:
> `<PROBLEM>`

### arm A (self-pick control)

identical to arm B, with the draw instruction replaced by:

>     when you reach the draw step, do not run any script; instead choose yourself a
>     random wildcard from a completely unrelated field, or an unrelated concept (state
>     it on one line, e.g. "domain=..." or "concept=..."), and use that as your draw.

### arm C (plain baseline)

> you are an ai assistant. a user brings you the problem below. brainstorm 2 to 4
> creative angles or connections from outside the problem's usual frame that could help
> them. present each one briefly: what you noticed, how it connects, and what they might
> try. keep them optional in tone. produce the angles as your final message.
>
> the problem:
> `<PROBLEM>`

### self-pick probe (H1)

> consider this problem: `<PROBLEM>`
>
> name one expert from a completely unrelated field, or one unrelated concept, that
> could seed a fresh perspective on it. reply with only the field/expert or concept name
> on a single line. nothing else.

### normalizer

> read the file `<RAW_FILE>`. rewrite its content into exactly this template, preserving
> the substance, removing any persona introduction, self-description, process narration,
> draw or mode markers, and any mention of how the angles were obtained:
>
>     ## angles
>     - <what was noticed> -> <how it maps onto the problem> -> <the suggestion or provocation>
>
> one bullet per offered angle, in the original order. if the content is an honest
> abstention (no connections offered), render instead:
>
>     ## angles
>     - (abstained: <one-line reason>)
>
> do not add content, do not improve content, do not editorialize. write the result to
> `<OUT_FILE>` with the Write tool, and return it via the structured output tool with
> abstained set accordingly.

### grader (one instance per grader; receives all 90 items in its seeded order)

> you are grading anonymized brainstorm outputs, one per item below. each was produced
> for the stated problem. grade each item independently on four scales (integers 1-7)
> plus two booleans. do not compare items to each other; grade each against the anchors.
>
> structural genuineness: 1 = connections are noun-rhymes or vocabulary overlap only;
> 4 = at least one relation genuinely parallels the problem but the mapping is partial
> or fuzzy; 7 = at least one connection maps a system of relations onto the problem with
> a transferable method, failure mode, or constraint.
>
> usefulness: 1 = nothing a practitioner could act on; 4 = one angle would plausibly
> prompt a re-think; 7 = a practitioner would plausibly act on at least one angle within
> a week.
>
> novelty: 1 = angles restate the problem's obvious neighborhood; 4 = at least one angle
> comes from an adjacent-but-different domain; 7 = at least one angle comes from a
> genuinely distant domain and still fits.
>
> non-derailment: 1 = the output reframes or substitutes the user's question, or grades
> their approach as wrong; 4 = mostly additive with one prescriptive slip; 7 = fully
> additive and optional in tone.
>
> fabrication (boolean): true if any angle asserts a mechanism or fact that is false or
> invented (judge the claim itself, not the analogy's looseness).
>
> abstained (boolean): true if the item offers no connections (an abstention notice).
> for abstained items, still fill the four scales with your judgment of the abstention's
> presentation (they are excluded from quality analysis; flags are what matter).
>
> return all grades via the structured output tool.

### blinding checker

> each item below was produced by one of three procedures: (A) the model followed a
> connection-finding protocol and chose its own "unrelated expert or concept" to connect
> from; (B) the model followed the same protocol but the expert or concept was drawn for
> it by an external randomizer; (C) the model freely brainstormed angles with no
> protocol. you are told nothing else. for each item, guess A, B, or C. return guesses
> via the structured output tool.

### canonicalizer (H1 self-picks)

> below are free-text answers naming "an expert from an unrelated field, or an unrelated
> concept". map each to a short canonical lowercase label naming the field or concept
> (e.g. "a marine biologist studying coral" -> "marine biology"; "the concept of
> compound interest" -> "compound interest"). the same field or concept must always get
> the same label. return labels via the structured output tool.

### adjacency judge (H1)

> for each (problem, pick) pair below: would a layperson reading the problem see the
> pick as related to the problem's domain or vocabulary (sharing its field, its tools,
> or its obvious imagery)? answer true (adjacent) or false (unrelated) for each. return
> judgments via the structured output tool.

## analysis plan (binding)

- aggregation: per output, mean across the 4 graders per rubric item; per problem x arm,
  mean across the 3 runs (abstained outputs excluded from quality means; missing cells,
  if any agent call failed twice, are excluded and counted in the report).
- primary: structural genuineness, B vs A: 10 paired per-problem values; exact wilcoxon
  signed-rank (enumeration); cliff's delta on the two 10-value groups; paired bootstrap
  95% CI on delta (10000 resamples of problem indices, rng mulberry32(cksum("bootstrap:"+M))).
- interpretation bands, pre-committed: CI excludes 0 in B's favor = superiority; CI
  spans 0 = no detected difference, reported as exactly that; CI excludes 0 against B =
  inferiority, reported plainly. nothing outside this plan is confirmatory; anything
  else we compute is labelled exploratory.
- secondary (exploratory): other rubric items B vs A; B vs C; A vs C; fabrication rates
  per arm at every flag threshold (>=1 to 4 of 4 graders); abstention rates per arm
  (descriptive; abstaining is the skill working, not a failure).
- H1 (descriptive, no significance theater): per problem distinct-count, entropy (bits),
  top-pick share for the 20 self-picks vs the 20 matched external draws; pooled top-10
  share across all 200 self-picks; adjacency rate self-picks vs external draws.
- reliability: krippendorff's alpha (ordinal) per rubric item across the 4 graders.
- human anchor: spearman between the user's blind scores and the panel means, per rubric
  item over the 15 anchored outputs, and pooled over all 60 (15 x 4) pairs.
- blinding check: guess accuracy vs chance (1/3); reported with the result and factored
  into the limitations discussion if materially above chance.

## blinding architecture (what "blind" means mechanically)

raw transcripts and the id map live in an os temp directory outside the repository until
grading completes; graders receive only anonymized normalized text inline, in their own
seeded order, in fresh contexts, with no channel to the arms, the raw files, each other,
or this document. the pool generator's prompt contains no mention of the hypothesis. the
freeze commit of this file predates all data; M predates the pool, so neither problem
selection nor any draw could be steered toward a result.
````

- [ ] **Step 3: Dash check**

Run: `grep -nP '[\x{2013}\x{2014}]' experiment/preregistration.md || echo clean`
Expected: `clean`

- [ ] **Step 4: Commit (this commit IS the freeze)**

```bash
git add experiment/preregistration.md
git commit -m "experiment: pre-registration freeze (hypotheses, prompts, rubric, master seed, analysis plan)

Committed before any problem pool, transcript, or grade exists.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: Blind problem pool + selection

**Files:**
- Create: `experiment/problems-pool.json`
- Create: `experiment/problems-selected.json`

- [ ] **Step 1: Run the pool workflow**

Invoke the Workflow tool with this script (generators are fable, blind per the prereg prompt):

```js
export const meta = {
  name: 'wildcard-exp-pool',
  description: 'Generate the blind problem pool (5 slices x 10 problems)',
  phases: [{ title: 'Generate', detail: 'five blind generators, one per slice' }],
}
const SLICES = [
  'software and infrastructure engineering',
  'product, ux, and visual design',
  'writing, media, and content',
  'operations, logistics, and physical-world work',
  'personal projects, learning, and life admin',
]
const SCHEMA = {
  type: 'object', required: ['problems'],
  properties: { problems: { type: 'array', minItems: 10, maxItems: 10,
    items: { type: 'object', required: ['text'],
      properties: { text: { type: 'string' } } } } },
}
phase('Generate')
const results = await parallel(SLICES.map((slice, i) => () => agent(
  'you are helping assemble a benchmark of realistic working problems used to evaluate ai assistants. ' +
  `generate exactly 10 distinct problems in the area of: ${slice}. each problem: 60-120 words, ` +
  'first person ("i am ..." / "i run ..."), concrete (what exists, what hurts, what constraints apply), ' +
  'no solution stated in the text, no two problems alike. plain lowercase prose. ' +
  'return them via the structured output tool.',
  { label: `pool:${i}`, model: 'fable', schema: SCHEMA },
)))
return { slices: SLICES, pools: results }
```

- [ ] **Step 2: Validate and write the pool**

From the workflow result, build `experiment/problems-pool.json`. Validate: 50 problems, each 60-120 words (`text.split(/\s+/).length`), all distinct. If a generator returned null or under-length items, re-run that slice once. Shape:

```json
{
  "generatedBy": "claude-fable-5, blind generator prompt per preregistration.md",
  "problems": [
    { "id": "p00", "slice": "software and infrastructure engineering", "text": "..." }
  ]
}
```

Ids are `p00`..`p49` in slice order then generator order (assigned before selection, so selection indexes a committed, ordered pool).

- [ ] **Step 3: Commit the pool (before selection)**

```bash
git add experiment/problems-pool.json
git commit -m "experiment: blind-authored problem pool (50 problems, 5 slices)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Select 10 by derivation and commit**

Run a small node one-liner (M from the prereg):

```js
// node --input-type=module -e "..."
import { selectDistinct } from './experiment/lib/seeded.mjs';
import { readFileSync, writeFileSync } from 'node:fs';
const M = '<M-HEX>';
const pool = JSON.parse(readFileSync('experiment/problems-pool.json', 'utf8')).problems;
const idx = selectDistinct('problems', M, pool.length, 10);
writeFileSync('experiment/problems-selected.json', JSON.stringify({
  masterSeed: M,
  derivation: 'pickIndex("problems:"+i, M, 50), skipping repeats, first 10 distinct',
  indices: idx,
  problems: idx.map((i) => pool[i]),
}, null, 2) + '\n');
```

```bash
git add experiment/problems-selected.json
git commit -m "experiment: entropy-derived selection of 10 problems (seed M, auditable)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: Collection (90 protocol passes + 200 self-picks + matched external draws)

**Files:**
- Created OUTSIDE the repo this task: `$STAGE/raw/<arm>-<pid>-r<run>.md` (90 transcripts)
- Created in repo at Task 9 freeze, not now.

- [ ] **Step 1: Create the quarantine staging dir**

Run: `STAGE=$(mktemp -d /tmp/wildcard-exp.XXXXXX) && mkdir -p "$STAGE/raw" "$STAGE/normalized" && echo "$STAGE"`
Record `$STAGE`. Raw data stays here, outside the repo, until grading completes (the blinding architecture in the prereg).

- [ ] **Step 2: Generate the matched external draws (no agents, pure shell)**

```bash
: > /tmp/wildcard-exp-externals.tsv
while read -r pid; do
  for k in $(seq 1 20); do
    out=$(bash plugin/scripts/draw.sh --seed "M:h1ext:${pid}:${k}")
    mode=$(echo "$out" | sed -n 's/^mode=//p')
    pick=$(echo "$out" | sed -nE 's/^(domain|concept)=//p')
    printf '%s\t%s\t%s\t%s\n' "$pid" "$k" "$mode" "$pick" >> /tmp/wildcard-exp-externals.tsv
  done
done < <(node -e "JSON.parse(require('fs').readFileSync('experiment/problems-selected.json','utf8')).problems.forEach(p=>console.log(p.id))")
wc -l /tmp/wildcard-exp-externals.tsv
```

(Replace `M:` with the real master seed value, i.e. seeds like `9f3a...:h1ext:p07:3`.)
Expected: 200 lines.

- [ ] **Step 3: Run the collection workflow**

Invoke Workflow with `args = { stage, master, problems, armA, armB, armC, selfpickPrompt }` where the arm templates and self-pick prompt are the prereg texts verbatim (with `<ABS>` already substituted) and `problems` is the selected 10. Script:

```js
export const meta = {
  name: 'wildcard-exp-collect',
  description: 'Collect 90 protocol passes (A/B/C) and 200 self-picks, fresh contexts',
  phases: [
    { title: 'Protocol', detail: '10 problems x 3 arms x 3 runs, subjects fable-5' },
    { title: 'Selfpicks', detail: 'K=20 per problem, fable-5' },
  ],
}
const { stage, master, problems, armA, armB, armC, selfpickPrompt } = args
const TEMPLATES = { A: armA, B: armB, C: armC }
const OUT_SCHEMA = {
  type: 'object', required: ['written', 'abstained', 'drawLine'],
  properties: { written: { type: 'boolean' }, abstained: { type: 'boolean' },
    drawLine: { type: ['string', 'null'] } },
}
const jobs = []
for (const p of problems) for (const arm of ['A', 'B', 'C'])
  for (let r = 1; r <= 3; r++) jobs.push({ p, arm, r })
async function runJob(j) {
  const id = `${j.arm}-${j.p.id}-r${j.r}`
  const prompt = TEMPLATES[j.arm]
    .replaceAll('<PROBLEM>', j.p.text)
    .replaceAll('<SEED>', `${master}:draw:${j.p.id}:r${j.r}`)
    + `\n\nfinally: write your complete final message verbatim to ${stage}/raw/${id}.md`
    + ' using the Write tool. then return structured output: written=true once the file'
    + ' is written; abstained=true only if your final message is an honest abstention'
    + ' rather than offered connections; drawLine = the draw you used (its mode and'
    + ' domain/concept lines joined with " | "), or null if your arm had no draw step.'
  let res = await agent(prompt, { label: id, phase: 'Protocol', model: 'fable', schema: OUT_SCHEMA })
  if (!res || !res.written) {
    log(`retrying ${id}`)
    res = await agent(prompt, { label: `${id}:retry`, phase: 'Protocol', model: 'fable', schema: OUT_SCHEMA })
  }
  return { id, arm: j.arm, problemId: j.p.id, run: j.r,
    abstained: res ? res.abstained : null, drawLine: res ? res.drawLine : null,
    ok: !!(res && res.written) }
}
phase('Protocol')
const manifest = await parallel(jobs.map((j) => () => runJob(j)))
phase('Selfpicks')
const PICK_SCHEMA = { type: 'object', required: ['pick'], properties: { pick: { type: 'string' } } }
const pickJobs = []
for (const p of problems) for (let k = 1; k <= 20; k++) pickJobs.push({ p, k })
const selfpicks = await parallel(pickJobs.map(({ p, k }) => () =>
  agent(selfpickPrompt.replaceAll('<PROBLEM>', p.text),
    { label: `pick:${p.id}:${k}`, phase: 'Selfpicks', model: 'fable', schema: PICK_SCHEMA })
    .then((r) => ({ problemId: p.id, k, pick: r ? r.pick.trim() : null }))))
const missing = manifest.filter((m) => !m.ok).map((m) => m.id)
if (missing.length) log(`MISSING after retry: ${missing.join(', ')}`)
return { manifest, selfpicks, missing }
```

- [ ] **Step 4: Verify the staging dir**

Run: `ls "$STAGE/raw" | wc -l && for f in "$STAGE"/raw/*.md; do [ -s "$f" ] || echo "EMPTY: $f"; done`
Expected: 90 (or 90 minus reported missing), no EMPTY lines. Hold the returned `manifest` and `selfpicks` for Tasks 8-9 (also stash them: `$STAGE/manifest.json`, `$STAGE/selfpicks.json`).

No commit this task: raw data is quarantined until the Task 9 freeze.

---

### Task 8: Normalization, opaque ids, blinding check, canonicalization, adjacency

**Files:**
- Created OUTSIDE repo: `$STAGE/normalized/<out-id>.md` (90), `$STAGE/idmap.json`, `$STAGE/checks.json`

- [ ] **Step 1: Assign opaque ids (inline node)**

```js
import { seededShuffle } from './experiment/lib/seeded.mjs';
import { readFileSync, writeFileSync } from 'node:fs';
const M = '<M-HEX>'; const STAGE = '<STAGE>';
const manifest = JSON.parse(readFileSync(`${STAGE}/manifest.json`, 'utf8'));
const shuffled = seededShuffle(manifest.map((m) => m.id), 'ids', M);
const idmap = {};
shuffled.forEach((rawId, pos) => { idmap[`out-${String(pos).padStart(2, '0')}`] = rawId; });
writeFileSync(`${STAGE}/idmap.json`, JSON.stringify(idmap, null, 2));
```

- [ ] **Step 2: Run the normalization + checks workflow**

Invoke Workflow with `args = { stage, items, normTemplate, blindPrompt, canonItems, adjItems }`:
`items` = `[{ outId, rawId }]` from the idmap; `normTemplate`, `blindPrompt` verbatim from the prereg; `canonItems` = the 200 self-picks `[{ k, raw }]`; `adjItems` = 400 rows `[{ k, problemText, pick }]` (200 self-picks + 200 externals, in that order, k = 0..399).

```js
export const meta = {
  name: 'wildcard-exp-norm',
  description: 'Normalize 90 outputs, blinding check, canonicalize + adjacency for H1',
  phases: [
    { title: 'Normalize', detail: 'one normalizer per output' },
    { title: 'Checks', detail: 'blinding check, canonicalizer, adjacency judges' },
  ],
}
const { stage, items, normTemplate, blindPrompt, canonItems, adjItems } = args
const NORM_SCHEMA = { type: 'object', required: ['text', 'abstained'],
  properties: { text: { type: 'string' }, abstained: { type: 'boolean' } } }
phase('Normalize')
const normalized = await parallel(items.map((it) => () => agent(
  normTemplate
    .replaceAll('<RAW_FILE>', `${stage}/raw/${it.rawId}.md`)
    .replaceAll('<OUT_FILE>', `${stage}/normalized/${it.outId}.md`),
  { label: `norm:${it.outId}`, phase: 'Normalize', schema: NORM_SCHEMA },
).then((r) => ({ outId: it.outId, text: r ? r.text : null, abstained: r ? r.abstained : null }))))
phase('Checks')
const okNorm = normalized.filter((n) => n.text)
const GUESS_SCHEMA = { type: 'object', required: ['guesses'], properties: {
  guesses: { type: 'array', items: { type: 'object', required: ['id', 'arm'],
    properties: { id: { type: 'string' }, arm: { enum: ['A', 'B', 'C'] } } } } } }
const CANON_SCHEMA = { type: 'object', required: ['labels'], properties: {
  labels: { type: 'array', items: { type: 'object', required: ['k', 'canonical'],
    properties: { k: { type: 'integer' }, canonical: { type: 'string' } } } } } }
const ADJ_SCHEMA = { type: 'object', required: ['judgments'], properties: {
  judgments: { type: 'array', items: { type: 'object', required: ['k', 'adjacent'],
    properties: { k: { type: 'integer' }, adjacent: { type: 'boolean' } } } } } }
const blindItems = okNorm.map((n) => `### ${n.outId}\n${n.text}`).join('\n\n')
const adjBatches = []
for (let i = 0; i < adjItems.length; i += 100) adjBatches.push(adjItems.slice(i, i + 100))
const [blind, canon, ...adj] = await parallel([
  () => agent(`${blindPrompt}\n\n${blindItems}`, { label: 'blinding-check', phase: 'Checks', schema: GUESS_SCHEMA }),
  () => agent(
    'below are free-text answers naming "an expert from an unrelated field, or an unrelated concept". ' +
    'map each to a short canonical lowercase label naming the field or concept (e.g. "a marine biologist ' +
    'studying coral" -> "marine biology"; "the concept of compound interest" -> "compound interest"). ' +
    'the same field or concept must always get the same label. return labels via the structured output tool.\n\n' +
    canonItems.map((c) => `${c.k}. ${c.raw}`).join('\n'),
    { label: 'canonicalize', phase: 'Checks', schema: CANON_SCHEMA }),
  ...adjBatches.map((batch, bi) => () => agent(
    'for each (problem, pick) pair below: would a layperson reading the problem see the pick as related ' +
    'to the problem\'s domain or vocabulary (sharing its field, its tools, or its obvious imagery)? ' +
    'answer true (adjacent) or false (unrelated) for each. return judgments via the structured output tool.\n\n' +
    batch.map((a) => `${a.k}. problem: ${a.problemText}\n   pick: ${a.pick}`).join('\n\n'),
    { label: `adjacency:${bi}`, phase: 'Checks', schema: ADJ_SCHEMA })),
])
return { normalized, blind, canon, adjacency: adj.filter(Boolean).flatMap((a) => a.judgments) }
```

- [ ] **Step 3: Stash the check results**

Write the workflow's return value to `$STAGE/checks.json`. Verify: 90 normalized files exist in `$STAGE/normalized/`, blinding guesses cover all out-ids, 200 canonical labels, 400 adjacency judgments. Re-run any missing batch once.

No commit this task (still quarantined).

---

### Task 9: Blind panel, then the freeze (everything enters the repo at once)

**Files:**
- Create: `experiment/raw/` (90 transcripts + `manifest.json`)
- Create: `experiment/normalized/` (90 files + `idmap.json`)
- Create: `experiment/grades.json`, `experiment/h1/selfpicks.json`, `experiment/h1/externals.json`

- [ ] **Step 1: Build the four grader prompts (inline node)**

For each grader g1..g4: order = `seededShuffle(outIds, "order:" + graderId, M)`; prompt = the prereg grader rubric text, then for each out-id in that order:

```
### <out-id>
problem: <problem text for that output's problem>
<normalized text>
```

(The problem text reveals nothing about the arm; graders need it to judge mapping quality.)

- [ ] **Step 2: Run the grading workflow**

```js
export const meta = {
  name: 'wildcard-exp-grade',
  description: 'Blind panel: 4 independent opus graders x 90 anonymized outputs',
  phases: [{ title: 'Grade', detail: 'fresh contexts, seeded orders, no arm labels', model: 'opus' }],
}
const { graders } = args  // [{ graderId, prompt }]
const SCHEMA = { type: 'object', required: ['grades'], properties: {
  grades: { type: 'array', items: { type: 'object',
    required: ['id', 'genuineness', 'usefulness', 'novelty', 'nonDerailment', 'fabrication', 'abstained'],
    properties: {
      id: { type: 'string' },
      genuineness: { type: 'integer', minimum: 1, maximum: 7 },
      usefulness: { type: 'integer', minimum: 1, maximum: 7 },
      novelty: { type: 'integer', minimum: 1, maximum: 7 },
      nonDerailment: { type: 'integer', minimum: 1, maximum: 7 },
      fabrication: { type: 'boolean' }, abstained: { type: 'boolean' } } } } } }
phase('Grade')
return await parallel(graders.map((g) => () =>
  agent(g.prompt, { label: `grader:${g.graderId}`, phase: 'Grade', model: 'opus', schema: SCHEMA })
    .then((r) => ({ graderId: g.graderId, grades: r ? r.grades : null }))))
```

Validate: each grader returned 90 grades covering every out-id; re-run a failed grader once with a fresh call.

- [ ] **Step 3: Draw-fidelity integrity check**

Before freezing, verify every arm-B transcript used its pre-registered draw: for each of the 30 B rows, run `bash plugin/scripts/draw.sh --seed '<M>:draw:<pid>:r<run>'` and check the pick appears in that transcript's `drawLine` (and in the raw file). Report: `30/30 fidelity` expected. Any mismatch is reported in results.md, not silently fixed.

- [ ] **Step 4: The freeze: move quarantined data into the repo and commit everything**

```bash
mkdir -p experiment/raw experiment/normalized experiment/h1
cp "$STAGE"/raw/*.md experiment/raw/
cp "$STAGE"/normalized/*.md experiment/normalized/
cp "$STAGE/idmap.json" experiment/normalized/idmap.json
# manifest.json: the collection manifest joined with outIds and normalizer abstained flags
# grades.json: { graders: [...4 grader results...], blinding: [...guesses...] }
# h1/selfpicks.json: [{ problemId, k, raw, canonical, adjacent }]
# h1/externals.json: [{ problemId, k, mode, pick, adjacent }]
git add experiment/raw experiment/normalized experiment/grades.json experiment/h1
git commit -m "experiment: data freeze - 90 transcripts, anonymized outputs, 4x90 blind grades, h1 picks (raw data entered the repo only after grading completed)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 10: Human anchor (requires the user, ~15 minutes)

**Files:**
- Create: `experiment/human-anchor.json`

- [ ] **Step 1: Build the anchor sheet**

Anchor out-ids = first 15 of `seededShuffle(outIds, "anchor", M)`. Present to the user in chat: for each, the problem text + the normalized output + the four 1-7 scales and the fabrication flag, with the same rubric anchors verbatim from the prereg. No arm information exists in what they see.

- [ ] **Step 2: Collect and commit**

Parse the user's scores into:

```json
[{ "outId": "out-17", "genuineness": 5, "usefulness": 4, "novelty": 6, "nonDerailment": 7, "fabrication": false }]
```

```bash
git add experiment/human-anchor.json
git commit -m "experiment: human anchor - 15 outputs blind-graded by the user

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 11: Analysis runner + smoke test + results

**Files:**
- Create: `scripts/analyze_experiment.mjs`
- Create: `experiment/tests/analyze.test.js`, `experiment/tests/fixtures/tiny/` (synthetic dataset)
- Create (generated): `experiment/results.json`, `experiment/results.md`

- [ ] **Step 1: Write the failing smoke test**

```js
// experiment/tests/analyze.test.js
import test from "node:test";
import assert from "node:assert/strict";
import { analyze } from "../../scripts/analyze_experiment.mjs";

test("analyze produces the pre-registered result fields from a tiny fixture", () => {
  const r = analyze(new URL("./fixtures/tiny/", import.meta.url).pathname);
  assert.ok(r.h1.perProblem.length >= 1);
  assert.ok(typeof r.h1.pooledTopShare === "number");
  assert.ok(typeof r.h2.primary.delta === "number");
  assert.ok(typeof r.h2.primary.p === "number");
  assert.ok(r.h2.primary.ci.lo <= r.h2.primary.ci.hi);
  assert.ok(typeof r.reliability.genuineness === "number");
  assert.ok(typeof r.blinding.accuracy === "number");
  assert.ok(["superiority", "no detected difference", "inferiority"].includes(r.h2.primary.band));
});
```

- [ ] **Step 2: Build the tiny fixture**

`experiment/tests/fixtures/tiny/` mirrors the real artifact shapes at minimum size: 2 problems, 3 arms x 1 run (6 outputs), 2 graders, K=3 self-picks and externals per problem, a 2-output human anchor, synthetic values chosen by hand (any consistent values; the test asserts shape and band membership, not specific numbers). Files: `problems-selected.json`, `raw/manifest.json`, `grades.json`, `h1/selfpicks.json`, `h1/externals.json`, `human-anchor.json`, plus a `config.json` `{ "masterSeed": "fixtureM" }`.

- [ ] **Step 3: Run to verify failure, then write the runner**

Run: `node --test experiment/tests/analyze.test.js` - expected FAIL (module not found).

```js
// scripts/analyze_experiment.mjs
// Offline analysis over the frozen experiment artifacts. Pure: analyze(dir) -> results
// object; the CLI entry writes results.json and results.md. Implements exactly the
// pre-registered plan in experiment/preregistration.md - nothing more is confirmatory.
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import {
  shannonEntropy, cliffsDelta, bootstrapCI, mulberry32, wilcoxonExact,
  krippendorffAlphaOrdinal, spearman,
} from "../experiment/lib/stats.mjs";
import { cksum } from "../site/js/entropy.js";

const ITEMS = ["genuineness", "usefulness", "novelty", "nonDerailment"];
const read = (dir, f) => JSON.parse(readFileSync(join(dir, f), "utf8"));

function histogram(labels) {
  const m = new Map();
  for (const l of labels) m.set(l, (m.get(l) || 0) + 1);
  return [...m.values()].sort((a, b) => b - a);
}

export function analyze(dir) {
  const selected = read(dir, "problems-selected.json");
  const M = selected.masterSeed ?? read(dir, "config.json").masterSeed;
  const problems = selected.problems.map((p) => p.id);
  const manifest = read(dir, "raw/manifest.json");
  const gradesDoc = read(dir, "grades.json");
  const selfpicks = read(dir, "h1/selfpicks.json");
  const externals = read(dir, "h1/externals.json");
  const anchor = existsSync(join(dir, "human-anchor.json")) ? read(dir, "human-anchor.json") : [];

  // ---- H1: divergence ----
  const perProblem = problems.map((pid) => {
    const self = selfpicks.filter((s) => s.problemId === pid && s.canonical);
    const ext = externals.filter((e) => e.problemId === pid);
    const sh = histogram(self.map((s) => s.canonical));
    const eh = histogram(ext.map((e) => e.pick));
    return {
      problemId: pid,
      self: { k: self.length, distinct: sh.length, entropy: shannonEntropy(sh),
        top1Share: sh.length ? sh[0] / self.length : 0 },
      external: { k: ext.length, distinct: eh.length, entropy: shannonEntropy(eh),
        top1Share: eh.length ? eh[0] / ext.length : 0 },
    };
  });
  const pooled = histogram(selfpicks.filter((s) => s.canonical).map((s) => s.canonical));
  const pooledTopShare = pooled.slice(0, 10).reduce((a, b) => a + b, 0) /
    Math.max(1, pooled.reduce((a, b) => a + b, 0));
  const adjRate = (rows) => rows.length
    ? rows.filter((r) => r.adjacent === true).length / rows.length : 0;
  const h1 = {
    perProblem, pooledDistinct: pooled.length, pooledTopShare,
    selfAdjacency: adjRate(selfpicks), externalAdjacency: adjRate(externals),
    meanSelfEntropy: perProblem.reduce((s, p) => s + p.self.entropy, 0) / perProblem.length,
    meanExternalEntropy: perProblem.reduce((s, p) => s + p.external.entropy, 0) / perProblem.length,
  };

  // ---- H2: quality ----
  // per output: mean across graders per item; abstained excluded from quality means.
  const byOut = new Map();
  for (const g of gradesDoc.graders) {
    if (!g.grades) continue;
    for (const gr of g.grades) {
      if (!byOut.has(gr.id)) byOut.set(gr.id, []);
      byOut.get(gr.id).push(gr);
    }
  }
  const rowFor = new Map(manifest.map((m) => [m.outId, m]));
  const outMeans = [];
  for (const [outId, gs] of byOut) {
    const row = rowFor.get(outId);
    if (!row) continue;
    const abstained = row.abstained === true;
    const fabFlags = gs.filter((g) => g.fabrication).length;
    const means = Object.fromEntries(ITEMS.map((it) =>
      [it, gs.reduce((s, g) => s + g[it], 0) / gs.length]));
    outMeans.push({ outId, arm: row.arm, problemId: row.problemId, abstained, fabFlags,
      nGraders: gs.length, ...means });
  }
  const cell = (arm, pid, it) => {
    const rows = outMeans.filter((o) => o.arm === arm && o.problemId === pid && !o.abstained);
    return rows.length ? rows.reduce((s, r) => s + r[it], 0) / rows.length : null;
  };
  const contrast = (armX, armY, it) => {
    const pairs = problems
      .map((pid) => [cell(armX, pid, it), cell(armY, pid, it)])
      .filter(([x, y]) => x !== null && y !== null);
    const xs = pairs.map((p) => p[0]), ys = pairs.map((p) => p[1]);
    const delta = cliffsDelta(xs, ys);
    const rng = mulberry32(cksum("bootstrap:" + M));
    const ci = bootstrapCI(pairs, (sample) =>
      cliffsDelta(sample.map((p) => p[0]), sample.map((p) => p[1])), 10000, rng);
    const w = wilcoxonExact(pairs.map(([x, y]) => x - y));
    const band = ci.lo > 0 ? "superiority" : ci.hi < 0 ? "inferiority" : "no detected difference";
    return { item: it, nPairs: pairs.length, meanX: mean(xs), meanY: mean(ys),
      delta, ci, p: w.p, band };
  };
  const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length;
  const primary = contrast("B", "A", "genuineness");
  const secondary = [];
  for (const it of ITEMS) for (const [x, y] of [["B", "A"], ["B", "C"], ["A", "C"]]) {
    if (it === "genuineness" && x === "B" && y === "A") continue;
    secondary.push({ contrast: `${x} vs ${y}`, ...contrast(x, y, it) });
  }
  const fabrication = {}; const abstention = {};
  for (const arm of ["A", "B", "C"]) {
    const rows = outMeans.filter((o) => o.arm === arm);
    fabrication[arm] = Object.fromEntries([1, 2, 3, 4].map((t) =>
      [`>=${t}`, rows.filter((r) => r.fabFlags >= t).length]));
    abstention[arm] = rows.filter((r) => r.abstained).length;
  }

  // ---- reliability, anchor, blinding ----
  const reliability = Object.fromEntries(ITEMS.map((it) => [it,
    krippendorffAlphaOrdinal([...byOut.values()]
      .filter((gs) => gs.length >= 2).map((gs) => gs.map((g) => g[it])))]));
  let anchorStats = null;
  if (anchor.length >= 3) {
    const perItem = Object.fromEntries(ITEMS.map((it) => {
      const pairs = anchor
        .map((h) => [h[it], outMeans.find((o) => o.outId === h.outId)?.[it]])
        .filter(([, p]) => p !== undefined);
      return [it, spearman(pairs.map((p) => p[0]), pairs.map((p) => p[1]))];
    }));
    const all = anchor.flatMap((h) => ITEMS
      .map((it) => [h[it], outMeans.find((o) => o.outId === h.outId)?.[it]])
      .filter(([, p]) => p !== undefined));
    anchorStats = { perItem, pooled: spearman(all.map((p) => p[0]), all.map((p) => p[1])),
      n: anchor.length };
  }
  const guesses = gradesDoc.blinding?.guesses ?? gradesDoc.blinding ?? [];
  const correct = guesses.filter((g) => rowFor.get(g.id)?.arm === g.arm).length;
  const blinding = { n: guesses.length, correct,
    accuracy: guesses.length ? correct / guesses.length : 0, chance: 1 / 3 };

  const missing = manifest.filter((m) => m.ok === false).map((m) => m.outId ?? m.id);
  return { h1, h2: { primary, secondary, fabrication, abstention }, reliability,
    anchor: anchorStats, blinding, missing, counts: { outputs: outMeans.length } };
}

// ---- CLI: node scripts/analyze_experiment.mjs [dir] ----
if (process.argv[1] && import.meta.url.endsWith(process.argv[1].split("/").pop())) {
  const dir = process.argv[2] ?? "experiment";
  const r = analyze(dir);
  writeFileSync(join(dir, "results.json"), JSON.stringify(r, null, 2) + "\n");
  const f = (x, d = 2) => (typeof x === "number" ? x.toFixed(d) : String(x));
  const md = [];
  md.push("# results (generated by scripts/analyze_experiment.mjs - do not edit)\n");
  md.push("## h1: divergence\n");
  md.push("| problem | self distinct/20 | self entropy | self top1 | ext distinct/20 | ext entropy |");
  md.push("|---|---|---|---|---|---|");
  for (const p of r.h1.perProblem)
    md.push(`| ${p.problemId} | ${p.self.distinct} | ${f(p.self.entropy)} | ${f(p.self.top1Share)} | ${p.external.distinct} | ${f(p.external.entropy)} |`);
  md.push("");
  md.push(`mean entropy: self ${f(r.h1.meanSelfEntropy)} bits vs external ${f(r.h1.meanExternalEntropy)} bits.`);
  md.push(`pooled self-picks: ${r.h1.pooledDistinct} distinct labels over all problems; top-10 labels cover ${f(r.h1.pooledTopShare * 100, 1)}%.`);
  md.push(`adjacency to the problem: self ${f(r.h1.selfAdjacency * 100, 1)}% vs external ${f(r.h1.externalAdjacency * 100, 1)}%.\n`);
  md.push("## h2: quality (primary: structural genuineness, B vs A)\n");
  const pr = r.h2.primary;
  md.push(`mean B ${f(pr.meanX)} vs mean A ${f(pr.meanY)}; cliff's delta ${f(pr.delta)} (95% ci ${f(pr.ci.lo)} to ${f(pr.ci.hi)}); exact wilcoxon p = ${f(pr.p, 4)}; pre-registered band: **${pr.band}** (n pairs = ${pr.nPairs}).\n`);
  md.push("### secondary (exploratory)\n");
  md.push("| contrast | item | mean X | mean Y | delta | 95% ci | p |");
  md.push("|---|---|---|---|---|---|---|");
  for (const s of r.h2.secondary)
    md.push(`| ${s.contrast} | ${s.item} | ${f(s.meanX)} | ${f(s.meanY)} | ${f(s.delta)} | ${f(s.ci.lo)} to ${f(s.ci.hi)} | ${f(s.p, 4)} |`);
  md.push("");
  md.push(`fabrication flags per arm (output counts at grader-flag thresholds): ${JSON.stringify(r.h2.fabrication)}`);
  md.push(`abstentions per arm: ${JSON.stringify(r.h2.abstention)}\n`);
  md.push("## reliability and checks\n");
  md.push(`krippendorff alpha (ordinal): ${ITEMS.map((it) => `${it} ${f(r.reliability[it])}`).join(", ")}.`);
  if (r.anchor) md.push(`human anchor (n=${r.anchor.n}): pooled spearman ${f(r.anchor.pooled)}; per item ${ITEMS.map((it) => `${it} ${f(r.anchor.perItem[it])}`).join(", ")}.`);
  md.push(`blinding check: ${r.blinding.correct}/${r.blinding.n} (${f(r.blinding.accuracy * 100, 1)}%) vs chance 33.3%.`);
  md.push(`missing cells: ${r.missing.length ? r.missing.join(", ") : "none"}.`);
  writeFileSync(join(dir, "results.md"), md.join("\n") + "\n");
  console.log("wrote results.json + results.md");
}
```

- [ ] **Step 4: Run tests, then the real analysis**

Run: `node --test experiment/tests/analyze.test.js` - expected PASS.
Run: `bash tests/run_all.sh` - expected ALL GREEN.
Run: `node scripts/analyze_experiment.mjs experiment` - expected `wrote results.json + results.md`.

- [ ] **Step 5: Commit**

```bash
git add scripts/analyze_experiment.mjs experiment/tests/ experiment/results.json experiment/results.md
git commit -m "feat(experiment): pre-registered analysis runner + fixture smoke test + generated results

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 12: Methods colophon + case study rewrite (markdown and html mirror)

**Files:**
- Create: `docs/methods-colophon.md`
- Modify: `docs/case-study.md` (replace the "does it actually work? a blind a/b test" section)
- Modify: `site/case-study/index.html` (mirror the same changes)

- [ ] **Step 1: Write `docs/methods-colophon.md`**

All-lowercase prose, no dashes. Structure (slots from results.json):

```markdown
# how this study was run (and why the pipeline earns trust)

## the claim
blinding and isolation in this study are enforced by architecture, not by promise. [...]

## the stack, truthfully
designed and orchestrated by claude (opus 4.8 with 1m context, and fable 5, across
sessions); subjects pinned to claude-fable-5; the four blind graders pinned to
claude-opus-4-8 (a different model family from the subjects, reducing self-preference);
fan-out via a deterministic workflow orchestrator. [...]

## what the architecture guarantees
- the problem author never saw the hypothesis: its prompt is committed verbatim [...]
- the master seed M was committed before any data existed [...]
- raw transcripts and the id map were quarantined in an os temp directory outside the
  repository until grading completed; graders received only anonymized text [...]
- each grader ran in a fresh context, in its own seeded order, with no channel to the
  arms, the raw data, the other graders, or the pre-registration [...]
- every transcript, grade, and seed is committed: the chain of custody is a git history.
- scale: {counts.outputs} outputs, {4x90} independent blind gradings, run in parallel;
  a solo human evaluation cannot deliver this rater redundancy, and the human anchor
  (n={anchor.n}, pooled spearman {anchor.pooled}) keeps the panel honest.

## what it does not guarantee (honest residuals)
llm graders; same-vendor models; n=10 problems; blinding measured not assumed (the
blinding check scored {blinding.accuracy}); see the case study's limitations.
```

- [ ] **Step 2: Rewrite the case study section**

In `docs/case-study.md`, replace the section `## does it actually work? a blind a/b test` (keep its content as a new subsection `### the original illustrative walkthrough (n=1, kept for honesty)` at the end of the new section). New section skeleton, slots from results.json:

The section opens with the epigraph (verbatim, attributed, original capitalization preserved as
cited data - the standing quote exception to the all-lowercase rule), then one lowercase line
tying it to the mechanism: knowing a thing by *becoming* it, thinking *from* it not *about* it,
is persona-conditioning stated in 1952; inhabiting the wildcard vs analyzing it is conditioning
vs noise, and the conviction posture (assume the connection, uncover it) is how the model thinks
from the draw. Epigraph block, exactly:

```markdown
> You know a thing mentally by looking at it from the outside, by comparing it with other
> things, by analyzing it and defining it [by thinking of it]; whereas you can know a thing
> spiritually only by becoming it, [only by thinking from it]. You must be the thing itself and
> not merely talk about it or look at it. You must be like the moth in search of his idol, the
> flame, who spurred with true desire, plunging at once into the sacred fire, folded his wings
> within, till he became one color and one substance with the flame. He only knew the flame who
> in it burned, and only he could tell who ne'er to tell returned [Farid ud-Din Attar].
>
> - Neville Goddard, The Power of Awareness (1952), pp. 24-25
```

```markdown
## does it actually work? a pre-registered, blind, three-arm study

[methods paragraph: arms, only-the-draw-varies, blind pool + entropy selection, master
seed committed before data, quarantine blinding, 4 opus graders + human anchor.
pointer: experiment/preregistration.md]

[h1 paragraph: asked to pick its own wildcard 20 times per problem, the model produced
{h1.meanSelfEntropy} bits of entropy against the external draw's {h1.meanExternalEntropy};
{h1.pooledTopShare}% of all 200 self-picks were its top ten favorites;
{h1.selfAdjacency}% were adjacent to the problem vs {h1.externalAdjacency}% for the draw.]

[h2 paragraph: primary endpoint result with delta, ci, exact p, and the pre-registered
band verbatim. if null: said plainly. fabrication and abstention rates per arm.]

[reliability paragraph: alpha per item, human anchor spearman, blinding-check accuracy.]

[limitations additions: llm graders bounded by the anchor; same vendor; n=10.]
```

- [ ] **Step 3: Mirror into `site/case-study/index.html`**

Same content adapted to the existing html idiom (h2 + p + ul + pre), preserving the all-lowercase voice and `<strong>` highlights for the measured numbers.

- [ ] **Step 4: Dash + lowercase verification**

Run: `grep -rnP '[\x{2013}\x{2014}]' docs/methods-colophon.md docs/case-study.md site/case-study/index.html || echo clean`
Expected: `clean`. Re-run the browser textContent uppercase scan on the case-study page during Task 14's smoke.

- [ ] **Step 5: Commit**

```bash
git add docs/methods-colophon.md docs/case-study.md site/case-study/index.html
git commit -m "docs: methods colophon + case study rewritten around the pre-registered study

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 13: Skill + figures + run-note updates

**Files:**
- Modify: `plugin/SKILL.md` (step 2 paragraph)
- Modify: `site/js/figures.js` (replace the small-n a/b figure, add the study figure)
- Modify: `site/tests/run-note.md` (append v9 entry)

- [ ] **Step 1: Fold the measured numbers into SKILL.md**

In the step 2 paragraph, after "it is a poor RNG over its own distribution.", insert (slots from results.json, rounded):

```
(measured: across 10 problems x 20 self-picks each, the model averaged {h1.meanSelfEntropy}
bits of pick-entropy against the external draw's {h1.meanExternalEntropy}, and {pct}% of
its picks were surface-adjacent to the problem vs {pct}% for the draw - see
experiment/results.md in the repo.)
```

- [ ] **Step 2: Update the figures panel**

In `site/js/figures.js`, replace the `expert selection · blind a/b · single session` figure with (slots filled, all-lowercase):

```js
{
  k: "self-pick vs external draw · pre-registered study",
  v: "across <b>10</b> problems x <b>20</b> self-picks each, the model's own \"random unrelated expert\" averaged <b>{x.x}</b> bits of entropy against the draw's <b>{x.x}</b>; <b>{nn}%</b> of self-picks were surface-adjacent to the problem vs <b>{nn}%</b> for the draw. quality, blind-graded by 4 independent graders with a human anchor: {one-line primary result with band}.",
  cmd: "regenerate: node scripts/analyze_experiment.mjs",
},
```

- [ ] **Step 3: Append the v9 run-note entry**

Summarize: the study design, the freeze discipline, suites green, browser smoke, the headline numbers, and parity unaffected.

- [ ] **Step 4: Verify and commit**

Run: `bash tests/run_all.sh && (cd site && node --test)` - expected green.
Run: `grep -rnP '[\x{2013}\x{2014}]' plugin/SKILL.md site/js/figures.js || echo clean` - expected clean.

```bash
git add plugin/SKILL.md site/js/figures.js site/tests/run-note.md
git commit -m "feat: measured divergence numbers in the skill + study figures on the site

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 14: Full verification, merge, deploy, live checks

**Files:** none new.

- [ ] **Step 1: Full local gates**

Run: `bash tests/run_all.sh` (ALL GREEN) and `cd site && node --test` (all pass), then `cd ..`.

- [ ] **Step 2: Browser smoke**

Serve `site/` locally; check index and case-study at 1440x900 and 380x820: study section renders, figures updated, no horizontal overflow, console clean, uppercase scan of rendered prose = 0 (pre/code excluded), demo cycles with both modes.

- [ ] **Step 3: Merge and push**

```bash
git checkout main
git merge --no-ff experiment -m "Merge branch 'experiment': pre-registered, blind, three-arm study of the wildcard mechanism

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git push origin main
```

- [ ] **Step 4: Watch the gated deploy and verify live**

`gh run watch <id> --exit-status`. Then on the live URL: the case-study study section is present, figures updated, and live parity still 6/6 (fetch deployed entropy.js + domains.js, compare against draw.sh for seeds 1, 42, 7, wildcard, review-101, 999).

- [ ] **Step 5: Update memory**

Update `wildcard-v2-concepts.md` (or a new memory file) with: experiment shipped, headline numbers, and any follow-ups.

---

## Execution notes

- Tasks 1-4b are pure local work. Task 4b (skill posture) MUST precede Task 5 so the freeze
  and the whole study are defined against the shipped skill. Task 5's commit is the freeze and
  MUST precede Tasks 6-9.
- Tasks 6-9 are Workflow fan-outs with inline orchestration between them; raw data stays
  in `$STAGE` (outside the repo) until Task 9's freeze commit.
- Task 10 pauses for the user (~15 minutes of blind grading).
- If H2 lands null or unfavorable, Tasks 12-13 report it exactly per the pre-registered
  bands; the colophon and case study do not soften it.
- Model pins: subjects and pool generators `model: 'fable'`; graders `model: 'opus'`;
  support agents (normalizer, canonicalizer, adjacency, blinding checker) inherit the
  session model.
