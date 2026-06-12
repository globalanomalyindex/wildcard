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
