import { test } from "node:test";
import assert from "node:assert/strict";
import { plan } from "../js/phi-grid.js";
import { MANIFEST, RATIOS } from "../js/manifest.js";

const SEEDS = Array.from({ length: 120 }, (_, i) => `seed-${i}`);
const ALLOWED = new Set([...RATIOS, 1]);

function contentCells(tree) {
  return tree.bands.flatMap((b) => b.cells).filter((c) => c.section);
}

test("reading order of content cells equals manifest order, every seed", () => {
  for (const s of SEEDS) {
    const tree = plan(s, "desktop", MANIFEST);
    const ids = contentCells(tree).map((c) => c.section);
    assert.deepEqual(ids, MANIFEST.map((m) => m.id), `order for ${s}`);
  }
});

test("closure: band heights sum to 1 and each band's widths sum to 1", () => {
  for (const s of SEEDS) {
    const tree = plan(s, "desktop", MANIFEST);
    const hsum = tree.bands.reduce((a, b) => a + b.hFrac, 0);
    assert.ok(Math.abs(hsum - 1) < 1e-9, `hsum ${hsum} for ${s}`);
    for (const band of tree.bands) {
      const wsum = band.cells.reduce((a, c) => a + c.wFrac, 0);
      assert.ok(Math.abs(wsum - 1) < 1e-9, `wsum for ${s}`);
    }
  }
});

test("ratios: every cell width is an allowed ratio (or full width)", () => {
  for (const s of SEEDS) {
    const tree = plan(s, "desktop", MANIFEST);
    for (const band of tree.bands) {
      for (const cell of band.cells) {
        const near = [...ALLOWED].some((r) => Math.abs(cell.wFrac - r) < 1e-9);
        assert.ok(near, `wFrac ${cell.wFrac} not an allowed ratio for ${s}`);
      }
    }
  }
});

test("determinism: same seed gives the identical tree", () => {
  for (const s of SEEDS.slice(0, 20)) {
    assert.deepEqual(plan(s, "desktop", MANIFEST), plan(s, "desktop", MANIFEST));
  }
});

test("variety: different seeds give different trees (at least 80% distinct)", () => {
  const shapes = new Set(SEEDS.map((s) => JSON.stringify(plan(s, "desktop", MANIFEST).bands)));
  assert.ok(shapes.size >= SEEDS.length * 0.8, `only ${shapes.size}/${SEEDS.length} distinct layouts`);
});

test("fit: every text/compact content cell meets its minColFrac", () => {
  const byId = Object.fromEntries(MANIFEST.map((m) => [m.id, m]));
  for (const s of SEEDS) {
    const tree = plan(s, "desktop", MANIFEST);
    for (const band of tree.bands) {
      for (const cell of band.cells) {
        if (!cell.section) continue;
        const spec = byId[cell.section];
        if (spec.kind === "image") continue;
        assert.ok(cell.wFrac + 1e-9 >= spec.minColFrac, `${cell.section} too narrow (${cell.wFrac}) for ${s}`);
      }
    }
  }
});

test("bounded emptiness: between 2 and 5 empty cells, never two stacked empty bands", () => {
  for (const s of SEEDS) {
    const tree = plan(s, "desktop", MANIFEST);
    const empty = tree.bands.flatMap((b) => b.cells).filter((c) => c.empty).length;
    assert.ok(empty >= 2 && empty <= 5, `empty=${empty} for ${s}`);
    const isEmptyBand = (b) => b.cells.length === 1 && b.cells[0].empty;
    for (let k = 1; k < tree.bands.length; k++) {
      assert.ok(!(isEmptyBand(tree.bands[k]) && isEmptyBand(tree.bands[k - 1])), `stacked empty bands for ${s}`);
    }
  }
});

test("fallback: exhausted sampling returns the blessed layout, correctly ordered", () => {
  const tree = plan("force-fallback", "desktop", MANIFEST, 5, 0);
  assert.equal(tree.fallback, true);
  assert.deepEqual(
    tree.bands.flatMap((b) => b.cells).filter((c) => c.section).map((c) => c.section),
    MANIFEST.map((m) => m.id)
  );
  const hsum = tree.bands.reduce((a, b) => a + b.hFrac, 0);
  assert.ok(Math.abs(hsum - 1) < 1e-9, "fallback heights normalized");
});

test("no seed in a large sweep ever needs the fallback", () => {
  for (let i = 0; i < 400; i++) {
    const tree = plan(`sweep-${i}`, "desktop", MANIFEST);
    assert.ok(!tree.fallback, `seed sweep-${i} fell back`);
  }
});
