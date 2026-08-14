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

  // Both leads put the drawn string after a colon, and that is the whole trick. Any slot
  // that needs a determiner inherits the pool's grammar: "a <domain> specialist" printed
  // "a acid mine drainage..." on the 46 domains that start with a vowel, and "a professor
  // of <concept>" was worse - it invented people who do not exist ("a professor of
  // abrasive", "a professor of amber"). After a colon the slot is syntactically inert, so
  // every one of the 378 domains and 461 concepts reads correctly with no article logic.
  function noteHTML(mode, pick, seed) {
    const lead = mode === "specialist"
      ? `now imagine the specialist who does this all day: <b>${pick}</b>. what would they notice in your project? `
      : `now imagine an expert whose whole career is one subject: <b>${pick}</b>. what would they notice in your project, and what does that subject have in common with it? `;
    return lead +
      `that part happens in claude code. ` +
      `<span class="seed-tag">seed ${seed} · reproduce: draw.sh --seed ${seed}</span>`;
  }

  // The next draw loads with the previous note still in place (dimmed) and the bar
  // pulsing, so the area stays filled and formatted instead of flashing empty.
  // The mode is rolled the same way draw.sh does it: cksum("mode:"+seed) % 2.
  function draw(seed, isFirst, done) {
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
      done && done();
    });
  }

  let timer = null;
  // The next delay is armed by the typewriter finishing, never in parallel with it.
  // Previously the 5-7s cycle ran on its own clock, so whenever a character took longer
  // than ~110ms the next draw restarted the typing before the note was ever written and
  // the caption stayed blank forever. Background tabs throttle timers to ~1s/tick, so a
  // page opened in a background tab hit exactly that and showed a stuck partial draw with
  // no caption at all. Chaining from the completion callback makes that unreachable.
  const schedule = () => {
    clearTimeout(timer);
    timer = setTimeout(cycle, 5000 + Math.random() * 2000);
  };
  const cycle = () => {
    if (document.hidden) return; // stay put; visibilitychange re-arms on return
    draw(freshSeed(), false, schedule);
  };

  draw(pageSeed, true, reduce ? null : schedule);
  if (reduce) return;
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) clearTimeout(timer);
    else schedule();
  });
}
