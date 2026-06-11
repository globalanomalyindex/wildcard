// The phi-grid engine: a depth-bounded guillotine. The below-fold space is a vertical
// stack of bands; each band is one cell or one left/right split. Reading order and
// closure are true BY CONSTRUCTION (sections are consumed sequentially; fractions in a
// band always sum to 1), and the remaining invariants are enforced by validate() with
// rejection sampling. Pure data in, pure data out — no DOM, so node can property-test it.
import { cksum } from "./entropy.js";
import { RATIOS } from "./manifest.js";

// A deterministic stream driven by the seed via cksum — the same hash the draw uses,
// so one seed reproduces both the expert and the layout, in browser and shell alike.
function stream(seed) {
  let n = 0;
  return {
    next: () => cksum(`layout:${seed}:${n++}`),
    pick: (arr) => arr[cksum(`layout:${seed}:${n++}`) % arr.length],
    chance: (num, den) => cksum(`layout:${seed}:${n++}`) % den < num,
  };
}

// Walk sections in manifest order. Each becomes a full-width band, shares a band with the
// next section (one split), or takes an empty "shoulder" cell beside it.
function buildBands(seed, manifest, maxEmpty) {
  const rng = stream(seed);
  const bands = [];
  let empties = 0;
  let i = 0;
  while (i < manifest.length) {
    const sec = manifest[i];
    const nextSec = manifest[i + 1];
    const canSplit =
      nextSec &&
      sec.minColFrac <= 0.618 &&
      nextSec.minColFrac <= 0.618 &&
      rng.chance(2, 5);
    if (canSplit) {
      const r = rng.pick(RATIOS);
      const leftFits = sec.minColFrac <= r;
      const rightFits = nextSec.minColFrac <= 1 - r;
      if (leftFits && rightFits) {
        bands.push({ hFrac: 0, cells: [
          { wFrac: r, section: sec.id },
          { wFrac: 1 - r, section: nextSec.id },
        ]});
        i += 2;
        continue;
      }
    }
    if (empties < maxEmpty && sec.kind !== "image" && rng.chance(1, 3)) {
      const r = rng.pick([0.618, 0.382]);
      if (sec.minColFrac <= r) {
        const left = rng.chance(1, 2);
        bands.push({ hFrac: 0, cells: left
          ? [{ wFrac: 1 - r, empty: true }, { wFrac: r, section: sec.id }]
          : [{ wFrac: r, section: sec.id }, { wFrac: 1 - r, empty: true }],
        });
        empties++;
        i += 1;
        continue;
      }
    }
    bands.push({ hFrac: 0, cells: [{ wFrac: 1, section: sec.id }] });
    i += 1;
  }
  // breathe: standalone empty bands until the airy minimum is met
  while (empties < 2) {
    const at = bands.length ? (stream(`e:${seed}:${empties}`).next() % (bands.length + 1)) : 0;
    bands.splice(at, 0, { hFrac: 0, cells: [{ wFrac: 1, empty: true }] });
    empties++;
  }
  return bands;
}

// Heights: each band gets a phi-ratio weight, normalized — the vertical rhythm is
// phi-related rather than uniform. Renderer treats hFrac as a min-height proportion.
function assignHeights(seed, bands) {
  const rng = stream(`h:${seed}`);
  const weights = bands.map((b) => {
    const w = rng.pick(RATIOS);
    return b.cells.length === 1 && b.cells[0].empty ? w * 0.382 : w; // empty bands stay slim
  });
  const total = weights.reduce((a, b) => a + b, 0);
  bands.forEach((b, k) => (b.hFrac = weights[k] / total));
}

function isEmptyBand(b) {
  return b.cells.length === 1 && b.cells[0].empty;
}

function validate(tree, manifest) {
  const cells = tree.bands.flatMap((b) => b.cells);
  const ids = cells.filter((c) => c.section).map((c) => c.section);
  if (ids.join("|") !== manifest.map((m) => m.id).join("|")) return false;
  const empties = cells.filter((c) => c.empty).length;
  if (empties < 2 || empties > 5) return false;
  const byId = Object.fromEntries(manifest.map((m) => [m.id, m]));
  for (const c of cells) {
    if (!c.section) continue;
    const spec = byId[c.section];
    if (spec.kind !== "image" && c.wFrac + 1e-9 < spec.minColFrac) return false;
  }
  for (const b of tree.bands) {
    const wsum = b.cells.reduce((a, c) => a + c.wFrac, 0);
    if (Math.abs(wsum - 1) > 1e-9) return false;
  }
  // no two stacked full-width empty bands — a void that large reads as a broken page
  for (let k = 1; k < tree.bands.length; k++) {
    if (isEmptyBand(tree.bands[k]) && isEmptyBand(tree.bands[k - 1])) return false;
  }
  return true;
}

// Inlined blessed layout (validated by the same tests) so the engine never depends on
// fetch() and node tests need no fixtures. Returned when rejection sampling is exhausted.
function FALLBACK() {
  return {
    bands: [
      { hFrac: 0.22, cells: [{ wFrac: 1, section: "thesis" }] },
      { hFrac: 0.18, cells: [{ wFrac: 0.618, section: "how-it-works" }, { wFrac: 0.382, empty: true }] },
      { hFrac: 0.18, cells: [{ wFrac: 1, section: "honesty" }] },
      { hFrac: 0.16, cells: [{ wFrac: 0.382, empty: true }, { wFrac: 0.618, section: "nature" }] },
      { hFrac: 0.16, cells: [{ wFrac: 1, section: "reference-organism" }] },
      { hFrac: 0.10, cells: [{ wFrac: 0.618, section: "install" }, { wFrac: 0.382, empty: true }] },
    ],
  };
}

export function plan(seed, viewportClass, manifest, maxEmpty = 5, maxAttempts = 32) {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const variantSeed = attempt === 0 ? String(seed) : `${seed}#${attempt}`;
    const bands = buildBands(variantSeed, manifest, maxEmpty);
    assignHeights(variantSeed, bands);
    const tree = { bands, seed: String(seed), viewportClass };
    if (validate(tree, manifest)) return tree;
  }
  const fb = FALLBACK();
  return { bands: fb.bands, seed: String(seed), viewportClass, fallback: true };
}
