# wildcard Landing Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the no-build vanilla landing page in `site/` — Figma-faithful hero, a generative φ-grid engine that re-deals the below-fold content per seed, and an honest seed-parity draw demo.

**Architecture:** Pure ES modules with a tested seam: `entropy.js` (POSIX-cksum CRC, byte-for-byte parity with `scripts/draw.sh`) and `phi-grid.js` (a **depth-bounded guillotine** engine — a vertical stack of bands, each a single cell or one left/right split — so reading-order and closure invariants hold *by construction*). DOM-touching code (`render.js`, `draw-demo.js`, `particles.js`) is thin and browser-verified. Data (`domains.js`) is generated from `references/domains.txt`, never hand-typed. Tests run under `node --test` (node 26).

**Tech Stack:** HTML + CSS + browser ES modules, no bundler. `node --test` for the pure modules. Fonts served as OTF (BoyersBlur 30KB, Karrik 80KB — no conversion needed).

---

## File Structure

```
site/
├── index.html              # semantic skeleton; hero authored; below-fold sections in DOM order (no-JS renders here)
├── package.json            # {"type":"module"} so node + browser share ESM
├── css/
│   ├── tokens.css          # palette, type scale, hairline language, @font-face
│   ├── hero.css            # authored hero viewport fidelity (Figma 1:2)
│   └── cells.css           # engine grid, empty-cell hairlines, reveals, demo column
├── js/
│   ├── entropy.js          # PURE: cksum CRC-32 + stream-tagged pick (parity with draw.sh)
│   ├── phi-grid.js         # PURE: plan(seed, viewport, manifest) → {bands}
│   ├── manifest.js         # PURE: ordered section specs (ids, min sizes, kinds)
│   ├── render.js           # {bands} → DOM (reads #section-<id> templates)
│   ├── draw-demo.js        # die, typed reveal, recordings expanders
│   ├── particles.js        # hero pollen canvas (reduced-motion aware)
│   ├── main.js             # wires it together on DOMContentLoaded
│   ├── domains.js          # GENERATED — provenance stamp; never hand-edited
│   └── fallback-layout.json# blessed-seed {bands} for exhausted rejection sampling
├── fonts/                  # BoyersBlur-Regular.otf, Karrik-Regular.otf
├── assets/chickpea-grid.png
└── tests/
    ├── entropy.test.js     # cksum anchors + pick logic
    ├── parity.test.js      # JS pick == draw.sh pick (child_process)
    ├── domains.test.js     # generated data count/order/provenance guard
    └── phi-grid.test.js    # engine invariants, property over many seeds
scripts/gen_site_data.sh    # domains.txt + draw.sh LENSES → site/js/domains.js
```

**Manifest section order (locked — reading order never varies, only cells do):**
`thesis, how-it-works, honesty, nature, reference-organism, install`

---

## Task 1: Scaffold + tokens + fonts + node test harness

**Files:**
- Create: `site/package.json`, `site/css/tokens.css`, `site/fonts/` (copied), `site/assets/chickpea-grid.png` (copied), `site/tests/smoke.test.js`

- [ ] **Step 1: Copy fonts and the grid asset, create dirs**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
mkdir -p site/css site/js site/fonts site/assets site/tests
cp ~/Library/Fonts/BoyersBlur-Regular.otf site/fonts/BoyersBlur-Regular.otf
cp ~/Library/Fonts/Karrik-Regular.otf site/fonts/Karrik-Regular.otf
cp docs/design-assets/chickpea-grid.png site/assets/chickpea-grid.png
ls -la site/fonts site/assets
```
Expected: both OTFs (~30KB, ~80KB) and the PNG present.

- [ ] **Step 2: Write `site/package.json`**

```json
{
  "name": "wildcard-site",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test tests/"
  }
}
```

- [ ] **Step 3: Write `site/css/tokens.css`**

```css
@font-face {
  font-family: "Boyers Blur";
  src: url("../fonts/BoyersBlur-Regular.otf") format("opentype");
  font-weight: 400; font-display: swap;
}
@font-face {
  font-family: "Karrik";
  src: url("../fonts/Karrik-Regular.otf") format("opentype");
  font-weight: 400; font-display: swap;
}
:root {
  --seafoam: #e5e0f6;
  --periwinkle: #77a0e4;
  --gold: #d0c382;
  --ink: #302e3a;
  --ink-soft: #6b6580;
  --cell-line: rgba(48, 46, 58, 0.14);
  --cell-fill: #efeaf9;
  --r-phi: 0.618;
  --r-inv: 0.382;
  --r-half: 0.5;
  --measure-min: 38ch;
  --measure-max: 70ch;
  --font-display: "Boyers Blur", system-ui, sans-serif;
  --font-body: "Karrik", system-ui, sans-serif;
}
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--seafoam); color: var(--ink); font-family: var(--font-body); }
a { color: var(--gold); }
```

- [ ] **Step 4: Write a harness smoke test `site/tests/smoke.test.js`**

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");

test("scaffold: fonts and tokens exist", () => {
  assert.ok(readFileSync(join(root, "fonts/Karrik-Regular.otf")).length > 1000);
  const css = readFileSync(join(root, "css/tokens.css"), "utf8");
  assert.match(css, /--periwinkle: #77a0e4/);
});
```

- [ ] **Step 5: Run it**

Run: `cd site && node --test tests/`
Expected: 1 test, pass.

- [ ] **Step 6: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add site/
git commit -m "feat(site): scaffold, design tokens, fonts, node test harness"
```

---

## Task 2: Generated domains data + provenance guard

**Files:**
- Create: `scripts/gen_site_data.sh`, `site/js/domains.js` (generated), `site/tests/domains.test.js`

- [ ] **Step 1: Write the failing test `site/tests/domains.test.js`**

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { DOMAINS, LENSES, PROVENANCE } from "../js/domains.js";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");

test("domains.js count matches the source map exactly", () => {
  const src = readFileSync(join(repo, "references/domains.txt"), "utf8");
  const lines = src.split("\n").filter((l) => l.trim() && !l.trim().startsWith("#"));
  assert.equal(DOMAINS.length, lines.length);
  assert.equal(DOMAINS.length, PROVENANCE.count);
});

test("domains are tag-stripped and ordered (index parity with draw.sh)", () => {
  assert.equal(DOMAINS[0], "drilling-mud rheology testing with Marsh funnel and rotational viscometer");
  assert.ok(DOMAINS.every((d) => !d.includes("|")));
});

test("lenses parsed from draw.sh (8, includes structure-and-form)", () => {
  assert.equal(LENSES.length, 8);
  assert.equal(LENSES[5], "structure-and-form");
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd site && node --test tests/domains.test.js`
Expected: FAIL — cannot import `../js/domains.js` (does not exist).

- [ ] **Step 3: Write the generator `scripts/gen_site_data.sh`**

```bash
#!/usr/bin/env bash
# Generate site/js/domains.js from references/domains.txt (tag-stripped, order-preserved)
# and the LENSES set from scripts/draw.sh. Never hand-edit the output.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/references/domains.txt"
DRAW="$ROOT/scripts/draw.sh"
OUT="$ROOT/site/js/domains.js"
COMMIT="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"

domains_json="$(grep -vE '^[[:space:]]*($|#)' "$SRC" \
  | sed -E 's/[[:space:]]*\|.*$//' \
  | awk 'BEGIN{ORS=""} {gsub(/\\/,"\\\\"); gsub(/"/,"\\\""); printf "%s\"%s\"", (NR>1?",\n  ":""), $0}')"
count="$(grep -vcE '^[[:space:]]*($|#)' "$SRC")"
lenses="$(sed -n 's/^LENSES="\(.*\)"$/\1/p' "$DRAW")"
lenses_json="$(printf '%s' "$lenses" | awk '{for(i=1;i<=NF;i++) printf "%s\"%s\"", (i>1?", ":""), $i}')"

{
  echo "// GENERATED by scripts/gen_site_data.sh — do not edit by hand."
  echo "export const PROVENANCE = { source: \"references/domains.txt\", count: $count, commit: \"$COMMIT\" };"
  echo "export const LENSES = [$lenses_json];"
  echo "export const DOMAINS = ["
  echo "  $domains_json"
  echo "];"
} > "$OUT"
echo "wrote $OUT ($count domains)"
```

- [ ] **Step 4: Generate and run**

Run:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
chmod +x scripts/gen_site_data.sh && bash scripts/gen_site_data.sh
cd site && node --test tests/domains.test.js
```
Expected: generator prints "wrote … (344 domains)"; all 3 tests pass.

- [ ] **Step 5: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add scripts/gen_site_data.sh site/js/domains.js site/tests/domains.test.js
git commit -m "feat(site): generate domains.js from the map with a provenance guard"
```

---

## Task 3: entropy.js — POSIX cksum CRC with seed parity

**Files:**
- Create: `site/js/entropy.js`, `site/tests/entropy.test.js`

- [ ] **Step 1: Write the failing test `site/tests/entropy.test.js`**

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { cksum, pickIndex } from "../js/entropy.js";

// Anchors measured from the real `cksum` binary — algorithm properties, data-independent.
test("cksum matches POSIX cksum byte-for-byte", () => {
  assert.equal(cksum("abc"), 1219131554);
  assert.equal(cksum("domain:1"), 3264583362);
  assert.equal(cksum("lens:1"), 2936984613);
  assert.equal(cksum("domain:42"), 1314043712);
});

test("pickIndex mirrors draw.sh modulo (seed 1 lens -> index 5)", () => {
  assert.equal(pickIndex("lens", "1", 8), 5); // structure-and-form
});

test("pickIndex streams are independent", () => {
  // domain and lens streams use different tags, so they decorrelate
  assert.notEqual(pickIndex("domain", "7", 344), pickIndex("lens", "7", 344) % 344);
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd site && node --test tests/entropy.test.js`
Expected: FAIL — cannot import `../js/entropy.js`.

- [ ] **Step 3: Write `site/js/entropy.js`**

```js
// POSIX cksum CRC-32 (polynomial 0x04C11DB7, non-reflected, init 0, length appended,
// final XOR). This is the SAME algorithm `cksum` uses, so picks match scripts/draw.sh.
const TABLE = (() => {
  const t = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i << 24;
    for (let k = 0; k < 8; k++) c = (c & 0x80000000) ? ((c << 1) ^ 0x04c11db7) : (c << 1);
    t[i] = c >>> 0;
  }
  return t;
})();

export function cksum(str) {
  const bytes = new TextEncoder().encode(str);
  let crc = 0;
  for (let i = 0; i < bytes.length; i++) {
    crc = ((crc << 8) ^ TABLE[((crc >>> 24) ^ bytes[i]) & 0xff]) >>> 0;
  }
  for (let len = bytes.length; len > 0; len = Math.floor(len / 256)) {
    crc = ((crc << 8) ^ TABLE[((crc >>> 24) ^ (len & 0xff)) & 0xff]) >>> 0;
  }
  return (~crc) >>> 0;
}

// Mirror of draw.sh: index = cksum("<tag>:<seed>") % modulus.
export function pickIndex(tag, seed, modulus) {
  return cksum(`${tag}:${seed}`) % modulus;
}

// Browser-only: a fresh true-entropy seed (string, so it round-trips through cksum).
export function freshSeed() {
  const u = new Uint32Array(1);
  crypto.getRandomValues(u);
  return String(u[0]);
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd site && node --test tests/entropy.test.js`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add site/js/entropy.js site/tests/entropy.test.js
git commit -m "feat(site): cksum CRC-32 entropy with byte-for-byte draw.sh parity"
```

---

## Task 4: Parity test — JS pick == draw.sh pick

**Files:**
- Create: `site/tests/parity.test.js`

- [ ] **Step 1: Write the test (it should pass immediately — it verifies a property of Tasks 2+3)**

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { DOMAINS, LENSES } from "../js/domains.js";
import { pickIndex } from "../js/entropy.js";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");

function shellDraw(seed) {
  const out = execFileSync("bash", ["scripts/draw.sh", "--seed", seed, "--file", "references/domains.txt"], { cwd: repo, encoding: "utf8" });
  const domain = out.match(/^domain=(.*)$/m)[1];
  const lens = out.match(/^lens=(.*)$/m)[1];
  return { domain, lens };
}

test("browser pick equals draw.sh pick for many seeds", () => {
  for (const seed of ["1", "42", "7", "review-101", "wildcard", "999"]) {
    const shell = shellDraw(seed);
    const jsDomain = DOMAINS[pickIndex("domain", seed, DOMAINS.length)];
    const jsLens = LENSES[pickIndex("lens", seed, LENSES.length)];
    assert.equal(jsDomain, shell.domain, `domain parity for seed ${seed}`);
    assert.equal(jsLens, shell.lens, `lens parity for seed ${seed}`);
  }
});
```

- [ ] **Step 2: Run it**

Run: `cd site && node --test tests/parity.test.js`
Expected: PASS — the browser and the shell agree on every sampled seed. (If a lens mismatches, the bug is a sign/overflow error in `cksum`; if a domain mismatches, `domains.js` order drifted from `domains.txt` — regenerate with `bash scripts/gen_site_data.sh`.)

- [ ] **Step 3: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add site/tests/parity.test.js
git commit -m "test(site): prove browser draw == draw.sh draw (the falsifiable claim)"
```

---

## Task 5: manifest.js + phi-grid.js engine (order, closure, ratios)

**Files:**
- Create: `site/js/manifest.js`, `site/js/phi-grid.js`, `site/tests/phi-grid.test.js`

- [ ] **Step 1: Write `site/js/manifest.js`**

```js
// Ordered content sections. Reading order is THIS order, always. The engine only varies cells.
// minColFrac: minimum fraction of the content column a text cell may occupy (fit invariant).
export const MANIFEST = [
  { id: "thesis",             kind: "text",    minColFrac: 0.5, minRowPx: 220 },
  { id: "how-it-works",       kind: "text",    minColFrac: 0.5, minRowPx: 240 },
  { id: "honesty",            kind: "text",    minColFrac: 0.5, minRowPx: 220 },
  { id: "nature",             kind: "text",    minColFrac: 0.5, minRowPx: 240 },
  { id: "reference-organism", kind: "image",   minColFrac: 0.382, minRowPx: 300 },
  { id: "install",            kind: "compact", minColFrac: 0.382, minRowPx: 160 },
];
export const RATIOS = [0.382, 0.5, 0.618];
```

- [ ] **Step 2: Write the failing test `site/tests/phi-grid.test.js`**

```js
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

test("ratios: every split width is an allowed ratio", () => {
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
```

- [ ] **Step 3: Run to verify it fails**

Run: `cd site && node --test tests/phi-grid.test.js`
Expected: FAIL — cannot import `../js/phi-grid.js`.

- [ ] **Step 4: Write `site/js/phi-grid.js`**

```js
import { cksum } from "./entropy.js";
import { RATIOS } from "./manifest.js";

// A small deterministic PRNG stream driven by the seed via cksum (browser/shell agnostic).
function stream(seed) {
  let n = 0;
  return {
    next: () => cksum(`layout:${seed}:${n++}`),
    pick: (arr) => arr[cksum(`layout:${seed}:${n++}`) % arr.length],
    chance: (num, den) => cksum(`layout:${seed}:${n++}`) % den < num,
  };
}

// Build the band sequence: walk sections in order; each becomes a full-width band OR shares a
// band with the next section as a left/right split; empty cells are interspersed within bounds.
// Reading order == manifest order BY CONSTRUCTION (we consume sections sequentially).
function buildBands(seed, manifest, maxEmpty) {
  const rng = stream(seed);
  const bands = [];
  let empties = 0;
  let i = 0;
  while (i < manifest.length) {
    const sec = manifest[i];
    const nextSec = manifest[i + 1];
    // Decide split: only if this and next are both text/compact and both fit side-by-side.
    const canSplit =
      nextSec &&
      sec.minColFrac <= 0.618 &&
      nextSec.minColFrac <= 0.618 &&
      rng.chance(2, 5); // ~40% of eligible pairs share a band
    if (canSplit) {
      const r = rng.pick(RATIOS.filter((x) => x !== 1)); // 0.382 | 0.5 | 0.618
      const leftFrac = r;
      // place wider section on the larger side if its minColFrac demands it
      const leftFits = sec.minColFrac <= leftFrac;
      const rightFits = nextSec.minColFrac <= 1 - leftFrac;
      if (leftFits && rightFits) {
        bands.push({ hFrac: 0, cells: [{ wFrac: leftFrac, section: sec.id }, { wFrac: 1 - leftFrac, section: nextSec.id }] });
        i += 2;
        continue;
      }
    }
    // full-width band, optionally with a trailing empty cell as a "shoulder"
    if (empties < maxEmpty && sec.kind !== "image" && rng.chance(1, 3)) {
      const r = rng.pick([0.618, 0.382]);
      bands.push({ hFrac: 0, cells: [{ wFrac: r, section: sec.id }, { wFrac: 1 - r, empty: true }] });
      empties++;
    } else {
      bands.push({ hFrac: 0, cells: [{ wFrac: 1, section: sec.id }] });
    }
    i += 1;
  }
  // standalone empty bands to reach >= 2 empties (airy look) if we are short
  while (empties < 2) {
    const at = (rng.next() % (bands.length + 1));
    bands.splice(at, 0, { hFrac: 0, cells: [{ wFrac: 1, empty: true }] });
    empties++;
  }
  return { bands, empties };
}

// Assign band heights via repeated phi partitions of the vertical extent, so the rhythm is
// phi-related rather than uniform. (Heights are visual targets; render uses them as min-heights.)
function assignHeights(seed, bands) {
  const rng = stream(`h:${seed}`);
  const weights = bands.map(() => rng.pick(RATIOS)); // 0.382 | 0.5 | 0.618 weight each
  const total = weights.reduce((a, b) => a + b, 0);
  bands.forEach((b, k) => (b.hFrac = weights[k] / total));
}

export function plan(seed, viewportClass, manifest, maxEmpty = 5) {
  const { bands, empties } = buildBands(seed, manifest, maxEmpty);
  assignHeights(seed, bands);
  return { bands, empties, seed: String(seed), viewportClass };
}
```

- [ ] **Step 5: Run to verify it passes**

Run: `cd site && node --test tests/phi-grid.test.js`
Expected: PASS (3 tests across 120 seeds each).

- [ ] **Step 6: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add site/js/manifest.js site/js/phi-grid.js site/tests/phi-grid.test.js
git commit -m "feat(site): depth-bounded guillotine engine (order/closure/ratios by construction)"
```

---

## Task 6: Engine fit + bounded-emptiness invariants + fallback

**Files:**
- Modify: `site/js/phi-grid.js` (add validation + fallback)
- Modify: `site/tests/phi-grid.test.js` (add fit + emptiness tests)
- Create: `site/js/fallback-layout.json`

- [ ] **Step 1: Add failing tests (append to `site/tests/phi-grid.test.js`)**

```js
import { MANIFEST as M2 } from "../js/manifest.js";

test("fit: every text/compact content cell meets its minColFrac", () => {
  const byId = Object.fromEntries(M2.map((m) => [m.id, m]));
  for (const s of SEEDS) {
    const tree = plan(s, "desktop", M2);
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

test("bounded emptiness: between 2 and 5 empty cells", () => {
  for (const s of SEEDS) {
    const tree = plan(s, "desktop", M2);
    const empty = tree.bands.flatMap((b) => b.cells).filter((c) => c.empty).length;
    assert.ok(empty >= 2 && empty <= 5, `empty=${empty} for ${s}`);
  }
});

test("fallback layout is valid and used when sampling is exhausted", () => {
  const tree = plan("force-fallback", "desktop", M2, /*maxEmpty*/ 5, /*maxAttempts*/ 0);
  assert.equal(tree.fallback, true);
  assert.deepEqual(
    tree.bands.flatMap((b) => b.cells).filter((c) => c.section).map((c) => c.section),
    M2.map((m) => m.id)
  );
});
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `cd site && node --test tests/phi-grid.test.js`
Expected: FAIL — `plan` ignores the `maxAttempts` arg and never sets `tree.fallback`; emptiness may exceed 5.

- [ ] **Step 3: Add validation, rejection sampling, and fallback to `site/js/phi-grid.js`**

Replace the exported `plan` function with:

```js
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
  return true;
}

export function plan(seed, viewportClass, manifest, maxEmpty = 5, maxAttempts = 32) {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const variantSeed = attempt === 0 ? seed : `${seed}#${attempt}`;
    const { bands } = buildBands(variantSeed, manifest, maxEmpty);
    assignHeights(variantSeed, bands);
    const tree = { bands, seed: String(seed), viewportClass };
    if (validate(tree, manifest)) return tree;
  }
  // exhausted — return the committed blessed layout, re-tagged with this seed.
  const fb = FALLBACK();
  return { bands: fb.bands, seed: String(seed), viewportClass, fallback: true };
}
```

Add near the top of the file (after imports):

```js
// Inlined blessed layout so the engine never depends on fetch() and tests run in node.
// Mirrors the structure of a known-good plan() output (validated by the fit/order/closure tests).
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
```

Also write `site/js/fallback-layout.json` (the same data, for documentation/runtime parity; render.js does not need it but it records the blessed layout):

```json
{
  "bands": [
    { "hFrac": 0.22, "cells": [{ "wFrac": 1, "section": "thesis" }] },
    { "hFrac": 0.18, "cells": [{ "wFrac": 0.618, "section": "how-it-works" }, { "wFrac": 0.382, "empty": true }] },
    { "hFrac": 0.18, "cells": [{ "wFrac": 1, "section": "honesty" }] },
    { "hFrac": 0.16, "cells": [{ "wFrac": 0.382, "empty": true }, { "wFrac": 0.618, "section": "nature" }] },
    { "hFrac": 0.16, "cells": [{ "wFrac": 1, "section": "reference-organism" }] },
    { "hFrac": 0.10, "cells": [{ "wFrac": 0.618, "section": "install" }, { "wFrac": 0.382, "empty": true }] }
  ]
}
```

- [ ] **Step 4: Run to verify all pass**

Run: `cd site && node --test tests/phi-grid.test.js`
Expected: PASS (6 tests). The fallback test confirms `maxAttempts: 0` yields the blessed layout with correct section order.

- [ ] **Step 5: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add site/js/phi-grid.js site/js/fallback-layout.json site/tests/phi-grid.test.js
git commit -m "feat(site): fit + bounded-emptiness invariants, rejection sampling, blessed fallback"
```

---

## Task 7: index.html skeleton + hero fidelity (no-JS renders fully here)

**Files:**
- Create: `site/index.html`, `site/css/hero.css`

- [ ] **Step 1: Write `site/index.html`**

The hero is authored to Figma node 1:2. Below-fold sections are present in DOM order (the no-JS / mobile layout) and double as the templates the engine clones.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>wildcard — a skill for Claude Code</title>
  <meta name="description" content="An experimental Claude Code skill that introduces a random expert from an unrelated field to seed non-linear creative thinking." />
  <link rel="preload" href="fonts/BoyersBlur-Regular.otf" as="font" type="font/otf" crossorigin />
  <link rel="stylesheet" href="css/tokens.css" />
  <link rel="stylesheet" href="css/hero.css" />
  <link rel="stylesheet" href="css/cells.css" />
</head>
<body>
  <header class="hero">
    <img class="hero-grid" src="assets/chickpea-grid.png" alt="" aria-hidden="true" />
    <div class="hero-inner">
      <h1 class="wordmark">wildcard</h1>
      <div class="hero-row">
        <span class="tagline">skill for claude code</span>
        <a class="install-link" href="#install">install</a>
      </div>
      <p class="lede">wildcard is an experimental skill for claude code that, at random, introduces an unrelated expert to your current task or project. in doing so, the token pool is seeded with unorthodox directions for standard chain-of-thought systems to work with — influencing more creative thinking, problem-solving, and idea generation in large language models.</p>
      <p class="closing">this project is an experiment in introducing and emulating non-linear creative thinking in artificial intelligence systems, without straying away from current artificial intelligence technology and capabilities.</p>
    </div>
    <aside class="demo" id="demo" aria-label="draw a wildcard"></aside>
  </header>

  <main id="field" class="field" data-fallback>
    <section class="section" id="section-thesis" data-section="thesis">
      <h2>a synthetic default-mode network</h2>
      <p>An LLM's chain of thought has no default mode. It is relentlessly task-locked — it never wanders, never lets something irrelevant surface, because every token is conditioned on staying on-task. So it can't have the "pop-in"; the architecture forbids it. wildcard externalizes the one faculty the architecture is missing — a synthetic default-mode network that injects the remote associate the on-task reasoner would never wander to.</p>
      <p class="aside">Not higher temperature (which only flattens the distribution into noise) but different conditioning — a specific expert persona translates the model's high-probability mass to a distant, still-coherent region. Structured divergence, never randomness.</p>
    </section>

    <section class="section" id="section-how-it-works" data-section="how-it-works">
      <h2>how it works</h2>
      <ol class="pipeline">
        <li><b>detect</b> — distill the structural sketch of your project: moving parts, flows, tensions. Structure, not stack.</li>
        <li><b>draw</b> — a shell script picks one of 344 niche disciplines with real entropy, outside the model, so no field is favored.</li>
        <li><b>specialize</b> — the coordinate grows into a hyper-specific practitioner with a real toolkit, steered by a drawn lens.</li>
        <li><b>notice</b> — only genuine relational matches surface; honest abstention when little maps.</li>
        <li><b>seed</b> — 2–4 optional provocations, yours to plant or discard.</li>
      </ol>
    </section>

    <section class="section" id="section-honesty" data-section="honesty">
      <h2>map relations, not nouns</h2>
      <p>A bad connection shares a surface feature ("your code has 'cells,' I study biological cells!"). A real one maps relational structure: "your retry backoff and a predator–prey cycle are the same oscillation — and ecologists found stochastic jitter stops the populations from synchronizing into a crash; have you considered jitter in your backoff?" Same relations, different domain. Encoding that bar is how "doesn't lie for the sake of a connection" becomes a checkable property instead of a vibe.</p>
    </section>

    <section class="section" id="section-nature" data-section="nature">
      <h2>looking to nature for the mechanism</h2>
      <ul class="nature">
        <li><b>cross-pollination</b> — a pollinator carries genes between species without choosing which; the draw is the undirected carrier.</li>
        <li><b>seed dispersal &amp; germination</b> — most seeds never germinate, and that's the honest hit rate; you decide which provocations take root.</li>
        <li><b>outbreeding</b> — a distant cross escapes the inbreeding depression of a closed gene pool, the way a foreign field escapes mode collapse.</li>
        <li><b>stochastic resonance</b> — in a nonlinear system, the right noise amplifies a weak signal rather than drowning it.</li>
      </ul>
    </section>

    <section class="section" id="section-reference-organism" data-section="reference-organism">
      <figure>
        <img src="assets/chickpea-grid.png" alt="A golden-ratio modular grid generated by the Chickpea system, used as the structural reference for this page." />
        <figcaption>the reference organism — the φ-grid this page's cells are grown from.</figcaption>
      </figure>
    </section>

    <section class="section" id="section-install" data-section="install">
      <h2>install</h2>
      <pre><code>ln -s "$(pwd)" ~/.claude/skills/wildcard</code></pre>
      <p>Then run <code>/wildcard</code> in any Claude Code session. <a href="https://github.com/" class="repo-link">source &amp; the 344-domain map →</a></p>
    </section>
  </main>

  <script type="module" src="js/main.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write `site/css/hero.css` (Figma-faithful)**

```css
.hero { position: relative; min-height: 100vh; overflow: hidden; }
.hero-grid {
  position: absolute; inset: 0; width: 100%; height: 100%;
  object-fit: cover; opacity: 0.5; pointer-events: none;
}
.hero-inner { position: relative; max-width: 890px; padding: 33px 0 0 50px; }
.wordmark {
  font-family: var(--font-display); font-weight: 400;
  font-size: 200px; line-height: 1; letter-spacing: -4px;
  color: var(--periwinkle); margin: 0;
}
.hero-row { display: flex; justify-content: space-between; max-width: 789px; margin-top: 27px; }
.tagline, .install-link {
  font-family: var(--font-body); font-size: 40px; letter-spacing: -0.8px; color: var(--gold);
  text-decoration: none;
}
.install-link:hover { text-decoration: underline; }
.lede, .closing {
  font-family: var(--font-body); font-size: 32px; line-height: 1.0006; letter-spacing: -0.64px;
  color: var(--ink); max-width: 822px;
}
.lede { margin-top: 40px; }
.closing { text-align: right; margin-top: 120px; }
.demo {
  position: absolute; top: 35px; right: 0; width: 550px; min-height: 957px;
}
@media (max-width: 1100px) {
  .wordmark { font-size: 22vw; }
  .demo { position: static; width: auto; margin: 24px 16px; min-height: 0; }
  .hero-inner { padding: 24px 16px 0; }
  .closing { text-align: left; margin-top: 48px; }
}
```

- [ ] **Step 3: Verify it loads (manual)**

Run a static server and open it:
```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard/site && python3 -m http.server 8765 &
```
Open `http://localhost:8765/`. Expected: seafoam page, blobby periwinkle "wildcard" at ~200px, gold tagline/install row, dark lede, faint grid backdrop, all six below-fold sections readable in order (no JS yet). Stop the server when done: `kill %1`.

- [ ] **Step 4: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add site/index.html site/css/hero.css
git commit -m "feat(site): figma-faithful hero + full no-JS content (reading-order source)"
```

---

## Task 8: render.js + cells.css + main wiring (engine drives the DOM)

**Files:**
- Create: `site/js/render.js`, `site/js/main.js`, `site/css/cells.css`

- [ ] **Step 1: Write `site/js/render.js`**

```js
// Apply a {bands} tree to #field by reordering the existing <section> templates into a
// generated band/cell structure. Reuses the real DOM nodes (no re-authoring of content).
export function render(field, tree) {
  const sections = new Map(
    [...field.querySelectorAll("[data-section]")].map((el) => [el.dataset.section, el])
  );
  const frag = document.createDocumentFragment();
  for (const band of tree.bands) {
    const bandEl = document.createElement("div");
    bandEl.className = "band";
    bandEl.style.setProperty("--h", band.hFrac);
    for (const cell of band.cells) {
      const cellEl = document.createElement("div");
      cellEl.className = cell.empty ? "cell cell-empty" : "cell";
      cellEl.style.setProperty("--w", cell.wFrac);
      if (cell.section) cellEl.appendChild(sections.get(cell.section));
      bandEl.appendChild(cellEl);
    }
    frag.appendChild(bandEl);
  }
  field.replaceChildren(frag);
  field.removeAttribute("data-fallback");
  field.dataset.seed = tree.seed;
  if (tree.fallback) field.dataset.fallback = "true";
}
```

- [ ] **Step 2: Write `site/css/cells.css`**

```css
.field { display: flex; flex-direction: column; }
.field[data-fallback] { /* no-JS / pre-hydration: plain stacked sections */ }
.band { display: flex; min-height: calc(var(--h, 0.16) * 88vh); }
.cell { flex: 0 0 calc(var(--w, 1) * 100%); padding: clamp(24px, 4vw, 72px); border-top: 1px solid var(--cell-line); }
.cell + .cell { border-left: 1px solid var(--cell-line); }
.cell-empty { background: transparent; }
.section h2 { font-family: var(--font-display); font-size: clamp(28px, 4vw, 56px); color: var(--periwinkle); letter-spacing: -1.5px; margin: 0 0 16px; font-weight: 400; }
.section p, .section li { font-size: clamp(16px, 1.4vw, 20px); line-height: 1.55; max-width: var(--measure-max); }
.section p.aside { color: var(--ink-soft); }
.pipeline, .nature { padding-left: 1.2em; }
.pipeline li, .nature li { margin: 10px 0; }
.section pre { background: var(--cell-fill); padding: 14px 16px; border-radius: 8px; overflow-x: auto; }
.section code { font-family: var(--font-mono, monospace); }
figure { margin: 0; }
figure img { width: 100%; height: auto; display: block; border: 1px solid var(--cell-line); }
figcaption { font-size: 14px; color: var(--ink-soft); margin-top: 8px; font-style: italic; }
.reveal { opacity: 0; transform: translateY(14px); transition: opacity .7s ease, transform .7s ease; }
.reveal.in { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .reveal { opacity: 1; transform: none; transition: none; } }
@media (max-width: 760px) {
  .band { flex-direction: column; min-height: 0; }
  .cell { flex-basis: auto; }
  .cell-empty { display: none; }
  .cell + .cell { border-left: none; }
}
```

- [ ] **Step 3: Write `site/js/main.js`**

```js
import { plan } from "./phi-grid.js";
import { MANIFEST } from "./manifest.js";
import { render } from "./render.js";
import { freshSeed } from "./entropy.js";
import { initDemo } from "./draw-demo.js";
import { initParticles } from "./particles.js";
import { initReveals } from "./reveals.js";

function currentSeed() {
  const u = new URLSearchParams(location.search);
  return u.get("seed") || freshSeed();
}

function layout(seed) {
  const field = document.getElementById("field");
  const narrow = window.matchMedia("(max-width: 760px)").matches;
  if (narrow) return; // keep the authored single-column flow on mobile
  render(field, plan(seed, "desktop", MANIFEST));
}

const seed = currentSeed();
layout(seed);
initReveals();
initDemo(document.getElementById("demo"), seed);
initParticles(document.querySelector(".hero"), seed);
```

(Reveals module is small — create `site/js/reveals.js`:)

```js
export function initReveals() {
  const els = document.querySelectorAll(".section");
  els.forEach((el) => el.classList.add("reveal"));
  if (!("IntersectionObserver" in window)) { els.forEach((el) => el.classList.add("in")); return; }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
  }, { rootMargin: "0px 0px -10% 0px" });
  els.forEach((el) => io.observe(el));
}
```

- [ ] **Step 4: Verify in the browser (manual)**

Serve and open as in Task 7. Expected: below-fold now renders as irregular φ-bands (varied heights, some side-by-side, some empty cells with hairline borders), content still in order. Append `?seed=wildcard` — layout changes and is stable on reload. Resize below 760px — single column, empty cells gone.

- [ ] **Step 5: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add site/js/render.js site/js/main.js site/js/reveals.js site/css/cells.css
git commit -m "feat(site): render engine output to DOM; ?seed reproducible; mobile single-column"
```

---

## Task 9: draw-demo.js — die, typed reveal, field recordings

**Files:**
- Create: `site/js/draw-demo.js`, `site/js/recordings.js`

- [ ] **Step 1: Write the recordings content `site/js/recordings.js`**

```js
// Abridged from the three real validated sessions (2026-06-10). Real outputs, not simulated.
export const RECORDINGS = [
  {
    date: "2026-06-10", expert: "rush-light dipper", domain: "rush-light dipping reeds in tallow for period stage lamps", lens: "time-and-rhythm",
    project: "a rate limiter (thundering herd)",
    seed: "Synchronized guttering — a draught makes every flame dip on the same beat — is your thundering herd. The fix isn't a steadier flame; it's per-reed coat-thickness variance baked in so no shared shock can phase-lock the rack. Give each client a persistent, identity-tied phase offset under the per-retry jitter — structural variance that survives across cycles.",
  },
  {
    date: "2026-06-10", expert: "vellum preparer", domain: "vellum preparation — liming and scudding calfskin for scribes", lens: "signals-and-noise",
    project: "a three-timeline novel converging on one house",
    seed: "Over-liming is the failure I fear: scrub the skin so clean the ink has nothing to bite. Foreshadowing has the same edge — a beat smoothed so far below notice it does nothing on first read and has nothing to resurface at the reveal. You might check planted beats against that quiet edge too, not only the loud one.",
  },
  {
    date: "2026-06-10", expert: "pointe-shoe fitter", domain: "ballet pointe-shoe fitting and darning for professional dancers", lens: "materials",
    project: "a CSV-to-JSON converter",
    seed: "Most of my craft doesn't reach your tool — I'm leaving the lifecycle apparatus on the shelf. What rhymes: failures cluster at seams. The drawstring-channel stitch vs the satin stitch are identical on the surface, one structural and one decorative — exactly your quoted-comma vs delimiter-comma. Centralize the quoted-state decision; weight tests toward the seams.",
  },
];
```

- [ ] **Step 2: Write `site/js/draw-demo.js`**

```js
import { DOMAINS, LENSES, PROVENANCE } from "./domains.js";
import { pickIndex, freshSeed } from "./entropy.js";
import { RECORDINGS } from "./recordings.js";

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function typeOut(el, text, done) {
  if (reduce) { el.textContent = text; done && done(); return; }
  el.textContent = "";
  let i = 0;
  const tick = () => { el.textContent = text.slice(0, ++i); if (i < text.length) setTimeout(tick, 28); else done && done(); };
  tick();
}

export function initDemo(root, pageSeed) {
  root.innerHTML = `
    <div class="demo-card">
      <button class="die" type="button" aria-label="draw a wildcard">
        <i class="die-face">⚄</i><span>draw a wildcard</span>
      </button>
      <pre class="draw-out" aria-live="polite"></pre>
      <p class="draw-note"></p>
    </div>
    <div class="recordings"><h3>field recordings</h3></div>`;
  const out = root.querySelector(".draw-out");
  const note = root.querySelector(".draw-note");

  function draw(seed) {
    const domain = DOMAINS[pickIndex("domain", seed, DOMAINS.length)];
    const lens = LENSES[pickIndex("lens", seed, LENSES.length)];
    typeOut(out, `domain=${domain}\nlens=${lens}`, () => {
      note.innerHTML = `now imagine what a <b>${domain}</b> specialist would notice about your project — that's the part that happens in Claude Code. <span class="seed-tag">seed ${seed} · reproduce with <code>draw.sh --seed ${seed}</code></span>`;
    });
  }

  root.querySelector(".die").addEventListener("click", () => draw(freshSeed()));
  draw(pageSeed); // first draw uses the page seed (so ?seed= ties layout + expert together)

  const rec = root.querySelector(".recordings");
  for (const r of RECORDINGS) {
    const d = document.createElement("details");
    d.innerHTML = `<summary><span class="rec-date">${r.date}</span> ${r.expert} <span class="rec-chip">${r.lens}</span></summary>
      <p class="rec-proj">on ${r.project}:</p><p class="rec-seed">${r.seed}</p>`;
    rec.appendChild(d);
  }
  const prov = document.createElement("p");
  prov.className = "provenance";
  prov.textContent = `${PROVENANCE.count} disciplines · generated from references/domains.txt @ ${PROVENANCE.commit}`;
  rec.appendChild(prov);
}
```

- [ ] **Step 3: Add demo styles to `site/css/cells.css`**

```css
.demo-card { background: var(--cell-fill); border: 1px solid var(--cell-line); border-radius: 12px; padding: 18px; }
.die { display: flex; align-items: center; gap: 10px; font-family: var(--font-body); font-size: 18px; color: var(--ink); background: var(--periwinkle); border: none; border-radius: 10px; padding: 12px 16px; cursor: pointer; }
.die:hover { filter: brightness(1.05); }
.die-face { font-style: normal; font-size: 22px; }
.draw-out { font-family: var(--font-mono, monospace); font-size: 13px; background: #fff; border-radius: 8px; padding: 12px; margin: 14px 0 8px; white-space: pre-wrap; min-height: 3em; }
.draw-note { font-size: 14px; color: var(--ink); }
.seed-tag { display: block; margin-top: 8px; font-size: 12px; color: var(--ink-soft); }
.recordings { margin-top: 20px; }
.recordings h3 { font-family: var(--font-display); font-weight: 400; color: var(--periwinkle); font-size: 22px; margin: 0 0 10px; }
.recordings details { border-top: 1px solid var(--cell-line); padding: 10px 0; }
.recordings summary { cursor: pointer; font-size: 14px; }
.rec-date { font-family: var(--font-mono, monospace); font-size: 12px; color: var(--periwinkle); }
.rec-chip { background: var(--gold); color: #4d431a; font-size: 11px; padding: 1px 8px; border-radius: 10px; }
.rec-proj { font-size: 13px; color: var(--ink-soft); margin: 8px 0 4px; }
.rec-seed { font-size: 14px; line-height: 1.5; }
.provenance { font-size: 11px; color: var(--ink-soft); margin-top: 12px; }
```

Add the Tabler-free die: the `⚄` glyph is used (no icon font dependency). Ensure `--font-mono` falls back to `monospace` (already done inline).

- [ ] **Step 4: Verify in browser (manual)**

Serve and open. Expected: the right column shows the die; clicking it draws a real domain+lens with a typed reveal and a "reproduce with draw.sh --seed …" note; three expandable recordings below; a provenance line. Cross-check honesty: copy the shown seed, run `bash scripts/draw.sh --seed <seed>` in the terminal, confirm the domain+lens match exactly.

- [ ] **Step 5: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add site/js/draw-demo.js site/js/recordings.js site/css/cells.css
git commit -m "feat(site): honest draw demo (real entropy, draw.sh parity) + field recordings"
```

---

## Task 10: particles.js — hero pollen drift (reduced-motion aware)

**Files:**
- Create: `site/js/particles.js`

- [ ] **Step 1: Write `site/js/particles.js`**

```js
import { cksum } from "./entropy.js";

// Sparse drifting pollen/seed dots on a canvas behind the hero text. Seeded (not Math.random),
// fully disabled under reduced-motion or when the tab is hidden. Decorative only.
export function initParticles(hero, seed) {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const canvas = document.createElement("canvas");
  canvas.className = "pollen";
  Object.assign(canvas.style, { position: "absolute", inset: "0", width: "100%", height: "100%", pointerEvents: "none", zIndex: "0" });
  hero.prepend(canvas);
  const ctx = canvas.getContext("2d");
  let w, h, raf, running = true;
  const N = 28;
  // seed a tiny PRNG from cksum
  let s = cksum(`pollen:${seed}`) || 1;
  const rnd = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  const dots = Array.from({ length: N }, () => ({ x: rnd(), y: rnd(), r: 1 + rnd() * 3, vx: (rnd() - 0.5) * 0.0006, vy: -0.0003 - rnd() * 0.0006, gold: rnd() > 0.6 }));
  function resize() { w = canvas.width = hero.clientWidth; h = canvas.height = hero.clientHeight; }
  resize(); window.addEventListener("resize", resize);
  function frame() {
    if (!running) return;
    ctx.clearRect(0, 0, w, h);
    for (const d of dots) {
      d.x += d.vx; d.y += d.vy;
      if (d.y < -0.02) { d.y = 1.02; d.x = rnd(); }
      if (d.x < 0) d.x = 1; if (d.x > 1) d.x = 0;
      ctx.beginPath(); ctx.arc(d.x * w, d.y * h, d.r, 0, Math.PI * 2);
      ctx.fillStyle = d.gold ? "rgba(208,195,130,0.5)" : "rgba(119,160,228,0.5)";
      ctx.fill();
    }
    raf = requestAnimationFrame(frame);
  }
  frame();
  document.addEventListener("visibilitychange", () => {
    running = !document.hidden;
    if (running) frame(); else cancelAnimationFrame(raf);
  });
}
```

- [ ] **Step 2: Verify in browser (manual)**

Serve and open. Expected: a few faint periwinkle/gold dots drift upward behind the wordmark; they never sit above the text legibly (z-index 0, text is in `.hero-inner` which is `position: relative`). Toggle OS reduced-motion → no canvas at all. Switch tabs → animation pauses.

- [ ] **Step 3: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add site/js/particles.js
git commit -m "feat(site): seeded hero pollen drift, reduced-motion and tab-visibility aware"
```

---

## Task 11: Full verification — tests, browser smoke, a11y, no-JS

**Files:**
- Create: `site/tests/run-note.md` (records the manual verification checklist results)

- [ ] **Step 1: Run the full node suite**

Run: `cd site && node --test tests/`
Expected: all suites pass (smoke, domains, entropy, parity, phi-grid). Note the total count.

- [ ] **Step 2: Browser smoke via Claude Preview MCP (or manual)**

Start the preview and exercise the page:
- Load `/` — hero faithful, below-fold φ-bands render.
- `?seed=wildcard` and `?seed=42` — two visibly different layouts; each stable on reload.
- Click the die ~5 times — real varied domains, typed reveal, seed-reproduce note.
- Verify parity live: for the displayed seed, run `bash scripts/draw.sh --seed <seed>` and confirm the domain+lens match.
- Resize to 380px — single column, ordered, no empty cells, demo column flows under the lede.
- DevTools: emulate `prefers-reduced-motion` — no pollen, instant reveals, instant draw text.
- Disable JS — full content present and readable in document order; demo shows the three recordings statically.

Record pass/fail for each in `site/tests/run-note.md`.

- [ ] **Step 3: Accessibility checks**

- Tab through: install link, die button, each `<details>` — all reachable, visible focus.
- `aria-live="polite"` on `.draw-out` announces new draws.
- Grid image has empty alt in hero (decorative) and descriptive alt in the reference-organism figure.
- Contrast: body `--ink` (#302e3a) on `--seafoam` (#e5e0f6) ≥ 4.5:1 (verify with DevTools); gold is used only for ≥40px hero type and chips, never body text.

Record results in `site/tests/run-note.md`.

- [ ] **Step 4: Commit**

```bash
cd /Users/chrisfiore/Documents/Claude/Projects/wildcard
git add site/tests/run-note.md
git commit -m "test(site): full verification pass — node suite, browser smoke, a11y, no-JS"
```

---

## Self-Review (completed by plan author)

**Spec coverage:**
- §1 page-is-a-draw → Tasks 5,6,8. ✓
- §3.1 hero fidelity (fonts/sizes/tracking/positions/copy) → Task 7 hero.css with exact Figma values. ✓
- §3.1 chickpea backdrop layer → Task 7 `.hero-grid`. ✓
- §3.2 below-fold sections in order + empty cells → Task 7 (content) + Tasks 5/6 (engine) + Task 8 (render). ✓
- §4.1 pure module seam `plan(seed,viewport,manifest)→tree` → Task 5. ✓
- §4.2 invariants (order/fit/closure/ratios/bounded-emptiness) → Tasks 5+6 tests. ✓
- §4.2 rejection sampling + committed fallback → Task 6. ✓
- §4.3 seeds, ?seed override, reroll, stream separation → Tasks 5 (stream tags) + 8 (?seed). NOTE: an explicit reroll *button* is not in the tasks; `?seed=` + reload covers reproducibility. Added as nice-to-have in Task 8 if desired — not a spec blocker since spec lists reroll under "seeds and streams" as a control; **added explicitly below.**
- §4.4 narrow + no-JS → Task 7 (no-JS source) + Task 8 (mobile guard) + Task 11 (verify). ✓
- §5.1 honest draw (domain+lens, no fake persona) → Task 9. ✓
- §5.2 generated data + provenance + count guard → Task 2. ✓
- §5.3 cksum parity + parity test → Tasks 3,4. ✓
- §5.4 three field recordings → Task 9. ✓
- §6 motion (pollen, reveals, typed draw, reduced-motion) → Tasks 8 (reveals),9 (typed),10 (pollen). ✓
- §7 a11y/contrast → Task 11. ✓
- §8 files → all created. ✓
- §9 success criteria → Task 11 checklist. ✓

**Gap found & fixed inline:** the reroll control (§4.3) wasn't a discrete step. Add to Task 8 Step 3 `main.js` a minimal reroll: append to `main.js`:
```js
addEventListener("keydown", (e) => { if (e.key.toLowerCase() === "r" && !e.metaKey && !e.ctrlKey) { const s = freshSeed(); history.replaceState(null, "", `?seed=${s}`); location.reload(); } });
```
(Keyboard "r" rerolls and writes `?seed=` — shareable, reproducible. A visible button can wrap this later; out of scope for v1 minimalism.)

**Placeholder scan:** none. Every code step is complete.

**Type/name consistency:** `plan(seed, viewportClass, manifest, maxEmpty, maxAttempts)` consistent across Tasks 5/6/8. `pickIndex(tag, seed, modulus)` consistent across entropy/parity/demo. `{bands:[{hFrac,cells:[{wFrac,section?,empty?}]}]}` consistent across engine/render/fallback. `PROVENANCE.count`, `DOMAINS`, `LENSES` consistent across Tasks 2/3/4/9. Manifest ids (`thesis,how-it-works,honesty,nature,reference-organism,install`) match `data-section` attributes in Task 7. ✓
