import { DOMAINS, LENSES, PROVENANCE } from "./domains.js";
import { pickIndex, freshSeed } from "./entropy.js";
import { RECORDINGS } from "./recordings.js";

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

export function initDemo(mount, pageSeed) {
  mount.innerHTML = `
    <p class="demo-title">drawing wildcards</p>
    <p class="sr-note">a new expert is drawn automatically every few seconds; each draw is reproducible in a terminal with the shown seed</p>
    <pre class="draw-out"></pre>
    <p class="draw-note"></p>`;
  const out = mount.querySelector(".draw-out");
  const note = mount.querySelector(".draw-note");

  function draw(seed) {
    const domain = DOMAINS[pickIndex("domain", seed, DOMAINS.length)];
    const lens = LENSES[pickIndex("lens", seed, LENSES.length)];
    note.innerHTML = "";
    typeOut(out, `domain=${domain}\nlens=${lens}`, () => {
      note.innerHTML =
        `now imagine what a <b>${domain}</b> specialist would notice about your project - ` +
        `that part happens in claude code. <span class="seed-tag">seed ${seed} · same draw in your ` +
        `terminal: <code>draw.sh --seed ${seed}</code></span>`;
    });
  }

  draw(pageSeed); // first draw shares the page seed: one seed grows the deal AND the expert

  // The shuffle: a fresh real-entropy draw every ~6s, paused while the tab is hidden.
  // Reduced motion keeps the page-seed draw static instead of auto-cycling.
  if (reduce) return;
  let timer = null;
  const cycle = () => { draw(freshSeed()); schedule(); };
  const schedule = () => { timer = setTimeout(cycle, 5000 + Math.random() * 2000); };
  schedule();
  document.addEventListener("visibilitychange", () => {
    clearTimeout(timer);
    if (!document.hidden) schedule();
  });
}

export function initRecordings(mount) {
  let cur = 0;
  mount.innerHTML = `
    <div class="rec-view"></div>
    <div class="rec-pager">
      <button type="button" class="rec-prev" aria-label="previous recording">‹</button>
      <span class="rec-count"></span>
      <button type="button" class="rec-next" aria-label="next recording">›</button>
    </div>
    <p class="provenance">${PROVENANCE.count} disciplines · from ${PROVENANCE.source} @ ${PROVENANCE.commit} · real session outputs</p>`;
  const view = mount.querySelector(".rec-view");
  const count = mount.querySelector(".rec-count");
  const show = () => {
    const r = RECORDINGS[cur];
    view.innerHTML = `
      <div class="rec-head"><span class="rec-date">${r.date}</span>
        <span class="rec-expert">${r.expert}</span>
        <span class="rec-chip">${r.lens}</span></div>
      <p class="rec-proj">on ${r.project}:</p>
      <p class="rec-seed">${r.seed}</p>`;
    count.textContent = `${cur + 1}/${RECORDINGS.length}`;
  };
  mount.querySelector(".rec-prev").addEventListener("click", () => { cur = (cur + RECORDINGS.length - 1) % RECORDINGS.length; show(); });
  mount.querySelector(".rec-next").addEventListener("click", () => { cur = (cur + 1) % RECORDINGS.length; show(); });
  show();
}
