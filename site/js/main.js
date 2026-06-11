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

const readout = document.getElementById("readout");
readout.textContent =
  `seed ${seed} · ${PROVENANCE.count} disciplines @ ${PROVENANCE.commit} · ` +
  `the ascii is seeded, not random · press r to reshuffle`;

// reroll: a fresh seed in the url, then reload, so any view is shareable and reproducible
addEventListener("keydown", (e) => {
  if (e.key.toLowerCase() !== "r" || e.metaKey || e.ctrlKey || e.altKey) return;
  const t = e.target;
  if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
  const s = freshSeed();
  history.replaceState(null, "", `?seed=${s}${location.hash}`);
  location.reload();
});
