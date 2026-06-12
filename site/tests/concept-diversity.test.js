import { test } from "node:test";
import assert from "node:assert/strict";
import { CONCEPTS } from "../js/domains.js";
import { pickIndex } from "../js/entropy.js";

test("the concept pool spreads widely (no clustering)", () => {
  const counts = new Map();
  for (let i = 0; i < 200; i++) {
    const c = CONCEPTS[pickIndex("concept", `cd-${i}`, CONCEPTS.length)];
    counts.set(c, (counts.get(c) || 0) + 1);
  }
  assert.ok(counts.size >= 90, `only ${counts.size} distinct in 200`);
  assert.ok(Math.max(...counts.values()) <= 8, "a concept dominates");
});
