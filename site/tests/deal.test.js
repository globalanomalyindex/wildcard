import { test } from "node:test";
import assert from "node:assert/strict";
import { deal, CARDS } from "../js/deal.js";
import { V, H, rowSlots } from "../js/grid-cells.js";

const SEEDS = Array.from({ length: 200 }, (_, i) => `deal-${i}`);
const KIND = Object.fromEntries(CARDS.map((c) => [c.id, c.kind]));

test("measured grid constants are pinned (provenance with the alpha-scan)", () => {
  assert.deepEqual(V, [0.618, 0.764, 0.854]);
  assert.deepEqual(H, [0.382, 0.618, 0.764]);
  const wide = rowSlots(1, false);
  assert.equal(wide.length, 1);
  assert.equal(wide[0].x0, 0.618);
  const split = rowSlots(2, true);
  assert.deepEqual(split.map((s) => s.x0), [0.618, 0.764, 0.854]);
});

test("every card dealt exactly once, every seed", () => {
  for (const s of SEEDS) {
    const d = deal(s);
    const dealt = d.stacks.flat().sort();
    assert.deepEqual(dealt, CARDS.map((c) => c.id).sort(), `cards for ${s}`);
  }
});

test("demo card pinned alone to the row-1 wide slot", () => {
  for (const s of SEEDS) {
    const d = deal(s);
    assert.deepEqual(d.stacks[0], ["demo"], `demo stack for ${s}`);
    assert.equal(d.slots[0].row, 0);
    assert.equal(d.slots[0].wide, true);
  }
});

test("all cards in wide slots (sub-cells stay decorative); text needs tall rows; max stack 3", () => {
  for (const s of SEEDS) {
    const d = deal(s);
    d.slots.forEach((slot, i) => {
      assert.ok(d.stacks[i].length <= 3, `stack hoard for ${s}`);
      if (!slot.wide) assert.equal(d.stacks[i].length, 0, `card in sub-slot for ${s}`);
      for (const id of d.stacks[i]) {
        if (KIND[id] === "text") assert.ok(slot.y1 - slot.y0 >= 0.2, `text in short row for ${s}`);
      }
    });
  }
});

test("slots tile their rows: x-extents from measured cuts, no overlap", () => {
  for (const s of SEEDS.slice(0, 50)) {
    const d = deal(s);
    const byRow = new Map();
    for (const slot of d.slots) {
      assert.ok(slot.x0 >= 0.618 - 1e-9 && slot.x1 <= 1 + 1e-9, `zone bounds for ${s}`);
      const list = byRow.get(slot.row) || [];
      list.push(slot);
      byRow.set(slot.row, list);
    }
    for (const [, list] of byRow) {
      list.sort((a, b) => a.x0 - b.x0);
      assert.equal(list[0].x0, 0.618);
      assert.ok(Math.abs(list[list.length - 1].x1 - 1) < 1e-9);
      for (let i = 1; i < list.length; i++) assert.equal(list[i].x0, list[i - 1].x1);
    }
  }
});

test("deterministic in seed; varied across seeds; no fallback in a sweep", () => {
  for (const s of SEEDS.slice(0, 20)) assert.deepEqual(deal(s), deal(s));
  // The valid outcome space is ~40 signatures (5 text cards split 3+2 over the two tall
  // rows = 20 sets, times empty-row split variants). 25 sits far above collapse (a broken
  // CRC-counter stream measured 6) and safely below the ceiling, so it discriminates
  // without flaking.
  const shapes = new Set(SEEDS.map((s) => JSON.stringify(deal(s).stacks)));
  assert.ok(shapes.size >= 25, `only ${shapes.size}/200 distinct deals`);
  for (const s of SEEDS) assert.ok(!deal(s).fallback, `fallback hit for ${s}`);
});

test("the deterministic fallback itself satisfies the invariants", () => {
  const d = deal("anything", 0);
  assert.equal(d.fallback, true);
  assert.deepEqual(d.stacks.flat().sort(), CARDS.map((c) => c.id).sort());
  d.slots.forEach((slot, i) => {
    for (const id of d.stacks[i]) {
      if (KIND[id] === "text") assert.ok(slot.wide && slot.y1 - slot.y0 >= 0.2);
    }
    assert.ok(d.stacks[i].length <= 3);
  });
});
