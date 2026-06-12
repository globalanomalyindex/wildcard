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
