import { plan } from "./phi-grid.js";
import { MANIFEST } from "./manifest.js";
import { render } from "./render.js";
import { freshSeed } from "./entropy.js";
import { initDemo } from "./draw-demo.js";
import { initParticles } from "./particles.js";
import { initReveals } from "./reveals.js";

function currentSeed() {
  const u = new URLSearchParams(location.search);
  return u.get("seed") || freshSeed();
}

function layout(seed) {
  // Below 760px the authored single-column flow in index.html IS the layout —
  // readability over theater on small screens.
  if (window.matchMedia("(max-width: 760px)").matches) return;
  render(document.getElementById("field"), plan(seed, "desktop", MANIFEST));
}

const seed = currentSeed();
layout(seed);
initReveals();
initDemo(document.getElementById("demo"), seed);
initParticles(document.querySelector(".hero"), seed);

// Reroll: press "r" to grow the page again from a fresh seed. The seed lands in the URL
// first, so every layout you see is shareable and reproducible.
addEventListener("keydown", (e) => {
  if (e.key.toLowerCase() !== "r" || e.metaKey || e.ctrlKey || e.altKey) return;
  const t = e.target;
  if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
  const s = freshSeed();
  history.replaceState(null, "", `?seed=${s}`);
  location.reload();
});
