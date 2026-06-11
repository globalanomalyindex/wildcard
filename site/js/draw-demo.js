import { DOMAINS, LENSES } from "./domains.js";
import { pickIndex, freshSeed } from "./entropy.js";

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function typeOut(el, text, done) {
  if (reduce) { el.textContent = text; done && done(); return; }
  el.textContent = "";
  let i = 0;
  const tick = () => {
    el.textContent = text.slice(0, ++i);
    if (i < text.length) el._t = setTimeout(tick, 24);
    else done && done();
  };
  clearTimeout(el._t);
  tick();
}

// A fresh real-entropy draw every 5-7s, typewritten. This is the one live element, and
// it doubles as the parity figure: the seed it shows reproduces in your shell.
export function initDemo(pageSeed) {
  const out = document.getElementById("draw-out");
  const note = document.getElementById("draw-note");
  const bar = document.getElementById("draw-bar");

  function noteHTML(d, seed) {
    return `now imagine what a <b>${d}</b> specialist would notice about your project. ` +
      `that part happens in claude code. ` +
      `<span class="seed-tag">seed ${seed} · reproduce: draw.sh --seed ${seed}</span>`;
  }

  // The next draw loads with the previous note still in place (dimmed) and the bar
  // pulsing, so the area stays filled and formatted instead of flashing empty.
  function draw(seed, isFirst) {
    const d = DOMAINS[pickIndex("domain", seed, DOMAINS.length)];
    const l = LENSES[pickIndex("lens", seed, LENSES.length)];
    if (!isFirst) note.classList.add("is-stale");
    if (bar) bar.classList.add("is-loading");
    typeOut(out, `domain=${d}\nlens=${l}`, () => {
      note.innerHTML = noteHTML(d, seed);
      note.classList.remove("is-stale");
      if (bar) bar.classList.remove("is-loading");
    });
  }

  draw(pageSeed, true);
  if (reduce) return;
  let timer = null;
  const cycle = () => { draw(freshSeed(), false); schedule(); };
  const schedule = () => { timer = setTimeout(cycle, 5000 + Math.random() * 2000); };
  schedule();
  document.addEventListener("visibilitychange", () => {
    clearTimeout(timer);
    if (!document.hidden) schedule();
  });
}
