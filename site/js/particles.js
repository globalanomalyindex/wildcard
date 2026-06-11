import { cksum } from "./entropy.js";

// Sparse pollen rising through the page - DOM dots on CSS animations, the same
// rendering paradigm as the blob layers. No canvas: a canvas beneath backdrop-filter
// panes invites compositing artifacts, and CSS animations run off the main thread.
// Seeded from the page seed (no Math.random theater); absent under reduced motion;
// background tabs throttle CSS animations on their own.
export function initParticles(page, seed) {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const layer = document.createElement("div");
  layer.className = "pollen";
  layer.dataset.depth = "10";
  layer.setAttribute("aria-hidden", "true");

  let s = cksum(`pollen:${seed}`) || 1;
  const rnd = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };

  const N = 22;
  for (let i = 0; i < N; i++) {
    const d = document.createElement("i");
    d.className = `mote ${rnd() > 0.6 ? "mote-gold" : "mote-blue"}`;
    const size = (1.5 + rnd() * 3).toFixed(1);
    const dur = (26 + rnd() * 30).toFixed(1);
    d.style.cssText =
      `left:${(rnd() * 100).toFixed(2)}%;` +
      `width:${size}px;height:${size}px;` +
      `--sway:${((rnd() - 0.5) * 90).toFixed(0)}px;` +
      `animation-duration:${dur}s;` +
      `animation-delay:-${(rnd() * dur).toFixed(1)}s;`;
    layer.appendChild(d);
  }
  page.prepend(layer);
}
