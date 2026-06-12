import { DOMAINS, CONCEPTS, LENSES } from "./domains.js";
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

  function noteHTML(mode, pick, seed) {
    const lead = mode === "specialist"
      ? `now imagine what a <b>${pick}</b> specialist would notice about your project. `
      : `now imagine what <b>${pick}</b> has in common with your problem. `;
    return lead +
      `that part happens in claude code. ` +
      `<span class="seed-tag">seed ${seed} · reproduce: draw.sh --seed ${seed}</span>`;
  }

  // The next draw loads with the previous note still in place (dimmed) and the bar
  // pulsing, so the area stays filled and formatted instead of flashing empty.
  // The mode is rolled the same way draw.sh does it: cksum("mode:"+seed) % 2.
  function draw(seed, isFirst) {
    const mode = pickIndex("mode", seed, 2) === 0 ? "specialist" : "concept";
    const pool = mode === "specialist" ? DOMAINS : CONCEPTS;
    const key = mode === "specialist" ? "domain" : "concept";
    const pick = pool[pickIndex(key, seed, pool.length)];
    const l = LENSES[pickIndex("lens", seed, LENSES.length)];
    if (!isFirst) note.classList.add("is-stale");
    if (bar) bar.classList.add("is-loading");
    typeOut(out, `mode=${mode}\n${key}=${pick}\nlens=${l}`, () => {
      note.innerHTML = noteHTML(mode, pick, seed);
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
