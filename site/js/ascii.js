import { cksum } from "./entropy.js";

// Intentionally-digital ASCII drift, in-palette, in the two small cells only. Seeded by
// the page seed via cksum -> mulberry32 (same discipline as the draw: not Math.random),
// so the field is reproducible. Deliberately low-fps (~12) for a digital, not-smooth
// cadence. Static single frame under reduced motion; paused while the tab is hidden.
const CHARS = "01/\\|<>=+*.:- ·01  ".split("");

function rng(seedNum) {
  let s = (seedNum >>> 0) || 1;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function initAscii(el, seed) {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const cw = 6.7, ch = 12; // approx mono metrics at 11px
  const cols = Math.max(8, Math.floor((el.clientWidth - 18) / cw));
  const rows = Math.max(4, Math.floor((el.clientHeight - 14) / ch));
  const r = rng(cksum(`ascii:${seed}`));
  const grid = new Array(cols * rows);
  for (let i = 0; i < grid.length; i++) grid[i] = CHARS[Math.floor(r() * CHARS.length)];

  const paint = () => {
    let out = "";
    for (let y = 0; y < rows; y++) out += grid.slice(y * cols, (y + 1) * cols).join("") + "\n";
    el.textContent = out;
  };
  paint();
  if (reduce) return;

  const churn = Math.max(1, Math.floor(grid.length * 0.08));
  let timer = null;
  const tick = () => {
    for (let k = 0; k < churn; k++) {
      const i = Math.floor(r() * grid.length);
      grid[i] = CHARS[Math.floor(r() * CHARS.length)];
    }
    paint();
  };
  const start = () => { timer = setInterval(tick, 84); };
  start();
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) { clearInterval(timer); timer = null; }
    else if (!timer) start();
  });
}
