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
    if (i < text.length) el._t = setTimeout(tick, 28);
    else done && done();
  };
  clearTimeout(el._t);
  tick();
}

export function initDemo(root, pageSeed) {
  root.innerHTML = `
    <div class="demo-card">
      <button class="die" type="button" aria-label="draw a wildcard">
        <span class="die-face" aria-hidden="true">⚄</span><span>draw a wildcard</span>
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
    note.innerHTML = "";
    typeOut(out, `domain=${domain}\nlens=${lens}`, () => {
      note.innerHTML =
        `now imagine what a <b>${domain}</b> specialist would notice about your project — ` +
        `that part happens in Claude Code. <span class="seed-tag">seed ${seed} · same draw in your ` +
        `terminal: <code>draw.sh --seed ${seed}</code></span>`;
    });
  }

  root.querySelector(".die").addEventListener("click", () => draw(freshSeed()));
  draw(pageSeed); // first draw shares the page seed: one seed grows the layout AND the expert

  const rec = root.querySelector(".recordings");
  for (const r of RECORDINGS) {
    const d = document.createElement("details");
    const sum = document.createElement("summary");
    sum.innerHTML = `<span class="rec-date">${r.date}</span> ${r.expert} <span class="rec-chip">${r.lens}</span>`;
    const proj = document.createElement("p");
    proj.className = "rec-proj";
    proj.textContent = `on ${r.project}:`;
    const seedP = document.createElement("p");
    seedP.className = "rec-seed";
    seedP.textContent = r.seed;
    d.append(sum, proj, seedP);
    rec.appendChild(d);
  }
  const prov = document.createElement("p");
  prov.className = "provenance";
  prov.textContent = `${PROVENANCE.count} disciplines · generated from ${PROVENANCE.source} @ ${PROVENANCE.commit} · real session outputs above`;
  rec.appendChild(prov);
}
