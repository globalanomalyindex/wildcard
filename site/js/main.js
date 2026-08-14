import { freshSeed } from "./entropy.js";
import { PROVENANCE } from "./domains.js";
import { initDemo } from "./draw-demo.js";
import { renderFigures } from "./figures.js";
import { initAscii } from "./ascii.js";

const seed = new URLSearchParams(location.search).get("seed") || freshSeed();

renderFigures(document.getElementById("figures"));
initDemo(seed);
initAscii(document.getElementById("ascii-a"), seed);
initAscii(document.getElementById("ascii-b"), `${seed}-b`);

document.getElementById("readout-text").textContent =
  `seed ${seed} · ${PROVENANCE.count} disciplines + ${PROVENANCE.concepts} concepts ` +
  `@ ${PROVENANCE.stamp} · the ascii is seeded, not random ·`;

// reroll: a fresh seed in the url, then reload, so any view is shareable and reproducible
function reshuffle() {
  const s = freshSeed();
  history.replaceState(null, "", `?seed=${s}${location.hash}`);
  location.reload();
}

document.getElementById("reshuffle").addEventListener("click", reshuffle);

// the r key stays as the fast path, but it is no longer the only one: it used to be the
// sole way to re-deal the page and it was announced inside an aria-hidden line, so touch
// and screen-reader users had no route to it at all.
addEventListener("keydown", (e) => {
  if (e.key.toLowerCase() !== "r" || e.metaKey || e.ctrlKey || e.altKey) return;
  const t = e.target;
  if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
  reshuffle();
});
