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
