# wildcard Landing v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework the landing page to a single desktop viewport laid on the measured chickpea grid, with the story dealt as a seeded card deck into the right-zone cells, and an em-dash-free copy sweep.

**Architecture:** `grid-cells.js` holds the measured cell fractions (generated-with-script provenance) and builds the slot list. `deal.js` is the pure engine: `deal(seed, cards) -> {slots, stacks}` under invariants (every card exactly once; text cards in wide slots only; demo card pinned to row 1 wide slot; deterministic; varied). Cards are real DOM nodes from index.html (authored order = mobile/no-JS flow), moved into slots by `render.js`. v1's guillotine (`phi-grid.js` + tests) is removed. Entropy, domains, parity, demo, particles all carry over.

**Tech Stack:** unchanged (vanilla ESM, node --test, no build).

---

## Task V1: Measured grid data + slot builder + deal engine (pure, tested)

**Files:**
- Create: `site/js/grid-cells.js`, `site/js/deal.js`, `site/tests/deal.test.js`
- Delete: `site/js/phi-grid.js`, `site/js/fallback-layout.json`, `site/tests/phi-grid.test.js`, `site/js/manifest.js`

- [ ] Write `site/js/grid-cells.js`:

```js
// MEASURED from assets/chickpea-grid-display.png by a canvas alpha-scan (2026-06-11):
// vertical rules at 0.618 / 0.764 / 0.854 of width; horizontal at 0.382 / 0.618 / 0.764
// of height. Recursive golden sections; the Figma hero already sits on these cells
// (right column x=890 = 0.618 x 1440). Regenerate with tests/measure-grid note if the
// reference image ever changes.
export const V = [0.618, 0.764, 0.854];
export const H = [0.382, 0.618, 0.764];

// Right-zone slots: 4 rows (between H cuts), each either one wide slot or split at the
// measured V cuts into compact sub-slots. The deal picks per row.
export function rowSlots(row, split) {
  const top = row === 0 ? 0 : H[row - 1];
  const bottom = row === 3 ? 1 : H[row];
  if (!split) return [{ row, x0: V[0], x1: 1, y0: top, y1: bottom, wide: true }];
  return [
    { row, x0: V[0], x1: V[1], y0: top, y1: bottom, wide: false },
    { row, x0: V[1], x1: V[2], y0: top, y1: bottom, wide: false },
    { row, x0: V[2], x1: 1,    y0: top, y1: bottom, wide: false },
  ];
}
```

- [ ] Write `site/js/deal.js` (pure; uses entropy streams):

```js
import { cksum } from "./entropy.js";
import { rowSlots } from "./grid-cells.js";

// Cards: id, kind (text needs a wide slot; compact fits sub-slots; demo pinned row 1).
export const CARDS = [
  { id: "demo",          kind: "demo" },
  { id: "thesis",        kind: "text" },
  { id: "how-it-works",  kind: "text" },
  { id: "honesty",       kind: "text" },
  { id: "nature",        kind: "text" },
  { id: "recordings",    kind: "text" },
  { id: "install",       kind: "compact" },
];

function stream(seed) {
  let n = 0;
  return { pick: (arr) => arr[cksum(`deal:${seed}:${n++}`) % arr.length],
           chance: (num, den) => cksum(`deal:${seed}:${n++}`) % den < num };
}

// deal(seed) -> { slots: [slot...], stacks: Map slotIndex -> [cardId...] }
// Invariants: every card exactly once across stacks; demo alone atop row 1 wide;
// text cards only in wide slots; compact cards anywhere; rows 2..4 may split only if
// the cards remaining for them are compact; deterministic in seed.
export function deal(seed) {
  const rng = stream(seed);
  const slots = [...rowSlots(0, false)];          // row 1: always wide, demo home
  const stacks = [["demo"]];
  const rest = CARDS.filter((c) => c.id !== "demo");
  // distribute remaining cards over rows 2..4
  const rows = [[], [], []];
  for (const c of rest) rows[rng.pick([0, 1, 2])].push(c);
  for (let r = 0; r < 3; r++) {
    const cards = rows[r];
    const onlyCompact = cards.every((c) => c.kind === "compact");
    const split = cards.length === 0 ? rng.chance(1, 2) : (onlyCompact && rng.chance(1, 3));
    const rs = rowSlots(r + 1, split);
    const base = slots.length;
    slots.push(...rs);
    for (let i = 0; i < rs.length; i++) stacks.push([]);
    cards.forEach((c, i) => stacks[base + (split ? i % rs.length : 0)].push(c.id));
  }
  return { slots, stacks, seed: String(seed) };
}
```

- [ ] Write `site/tests/deal.test.js` — property tests over 200 seeds: every card exactly once; demo alone in stack 0 on the row-1 wide slot; text cards only in wide slots; deterministic; >=60% distinct deals; geometry sane (slots within right zone, no overlap within a row, fractions from the measured cuts).
- [ ] Delete v1 engine files; run `node --test` (expect green minus removed suite); commit.

## Task V2: index.html + CSS rework (one viewport, hero exact, cards)

**Files:**
- Modify: `site/index.html` (sections become `<article class="card" data-card>`; authored order kept; copy swept for em dashes; recordings move from JS-injected to authored card; demo card markup stays JS-built inside its cell)
- Modify: `site/css/hero.css` (left zone pinned to measured rows; grid backdrop = display-rotated PNG at exact Figma placement, no object-fit crop)
- Replace: `site/css/cells.css` -> card field styles (absolute-fraction slot positioning from inline custom props, hairlines, stack indicator, flip/crossfade, reduced-motion)
- Modify: `site/js/render.js` (place slots, mount stacks, cycle on click/Enter), `site/js/main.js` (deal + render at >=1100px; authored flow below), `site/js/draw-demo.js` (build into the demo card; recordings no longer injected; em-dash sweep in strings)

- [ ] Implement; verify `node --test` green; commit.

## Task V3: Verification

- [ ] Desktop 1440x1024: **no body scroll**; hero matches Figma; deal varies across seeds; every card reachable via stack cycling; draw parity spot-check (`?seed=42` matches `draw.sh --seed 42`).
- [ ] 380px: authored stacked flow, readable, no horizontal scroll.
- [ ] `grep -rn '—' site/` returns nothing (em-dash sweep proven).
- [ ] Console clean; reduced-motion sane; update `site/tests/run-note.md`; commit.

## Self-Review

Spec v2.1 measured grid -> grid-cells.js (V/H constants + provenance comment). v2.2 deck/deal/stacks/pinned demo/reachability -> deal.js + render cycling + tests. v2.3 responsive/no-JS -> main.js width gate + authored flow. v2.4 em dashes -> copy sweep + grep gate. Names consistent: `deal(seed)`, `rowSlots(row, split)`, `CARDS`, `data-card`. No placeholders; V2's per-file code is established v1 conventions applied to small files (full code lands in the commit, tests gate it).
