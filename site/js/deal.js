// The dealer: assigns the card deck to right-zone slots, seeded. Pure data in/out so
// node can property-test the invariants. Same cksum streams as the draw, so one seed
// reproduces the whole page (layout deal + expert) in browser and shell alike.
import { cksum } from "./entropy.js";
import { rowSlots, H } from "./grid-cells.js";

// kind: "text" needs a wide slot in a tall-enough row; "compact" fits sub-slots;
// "demo" is pinned alone to the row-1 wide slot (the draw is the page's hook).
export const CARDS = [
  { id: "demo",         kind: "demo" },
  { id: "thesis",       kind: "text" },
  { id: "how-it-works", kind: "text" },
  { id: "honesty",      kind: "text" },
  { id: "nature",       kind: "text" },
  { id: "recordings",   kind: "text" },
  { id: "install",      kind: "compact" },
];

const MIN_TEXT_ROW = 0.2; // a text card needs a row at least this tall (fraction of zone)

// cksum is a hash, not a PRNG: hashing an incrementing counter gives linearly-correlated
// low bits (CRC is GF(2)-linear), which mode-collapsed the deal. So: hash ONCE for
// identity, then run a real small PRNG (mulberry32) for the sequence.
function stream(seed) {
  let s = cksum(`deal:${seed}`) || 1;
  const rnd = () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  return {
    pick: (arr) => arr[Math.floor(rnd() * arr.length)],
    chance: (num, den) => rnd() < num / den,
  };
}

function rowHeight(row) {
  const top = row === 0 ? 0 : H[row - 1];
  const bottom = row === 3 ? 1 : H[row];
  return bottom - top;
}

function attempt(seed) {
  const rng = stream(seed);
  const slots = [...rowSlots(0, false)];
  const stacks = [["demo"]];
  const rest = CARDS.filter((c) => c.id !== "demo");
  const rows = [[], [], []]; // rows 2..4 (indices 1..3 of the zone)
  for (const c of rest) {
    if (c.kind === "text") {
      const tall = [0, 1, 2].filter((r) => rowHeight(r + 1) >= MIN_TEXT_ROW);
      rows[rng.pick(tall)].push(c);
    } else {
      rows[rng.pick([0, 1, 2])].push(c);
    }
  }
  for (let r = 0; r < 3; r++) {
    const cards = rows[r];
    // Cards always get the wide slot; only empty rows may split into the narrow
    // sub-cells, which stay decorative (hairlines + ratio annotations, like the
    // reference image's own empty cells).
    const split = cards.length === 0 && rng.chance(1, 2);
    const rs = rowSlots(r + 1, split);
    const base = slots.length;
    slots.push(...rs);
    for (let i = 0; i < rs.length; i++) stacks.push([]);
    cards.forEach((c) => stacks[base].push(c.id));
  }
  return { slots, stacks };
}

function validate({ slots, stacks }) {
  const dealt = stacks.flat();
  if (dealt.length !== CARDS.length) return false;
  if (new Set(dealt).size !== CARDS.length) return false;
  if (stacks[0].length !== 1 || stacks[0][0] !== "demo" || !slots[0].wide || slots[0].row !== 0) return false;
  const kind = Object.fromEntries(CARDS.map((c) => [c.id, c.kind]));
  for (let i = 0; i < slots.length; i++) {
    for (const id of stacks[i]) {
      if (!slots[i].wide) return false; // cards live in wide slots, sub-cells stay decorative
      if (kind[id] === "text" && (slots[i].y1 - slots[i].y0) < MIN_TEXT_ROW) return false;
    }
    if (stacks[i].length > 3) return false; // no slot hoards the deck
  }
  return true;
}

export function deal(seed, maxAttempts = 32) {
  for (let a = 0; a < maxAttempts; a++) {
    const t = attempt(a === 0 ? String(seed) : `${seed}#${a}`);
    if (validate(t)) return { ...t, seed: String(seed) };
  }
  // Deterministic last resort: everything in reading order, one card per wide row,
  // overflow stacked on the last tall row. Validated by the test suite.
  const slots = [rowSlots(0, false)[0], rowSlots(1, false)[0], rowSlots(2, false)[0], rowSlots(3, false)[0]];
  const stacks = [["demo"], ["thesis", "how-it-works", "honesty"], ["install"], ["nature", "recordings"]];
  return { slots, stacks, seed: String(seed), fallback: true };
}
