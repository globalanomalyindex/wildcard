import { deal } from "./deal.js";
import { renderDeal } from "./render.js";
import { renderScaffold } from "./scaffold.js";
import { initParallax } from "./parallax.js";
import { freshSeed } from "./entropy.js";
import { initDemo, initRecordings } from "./draw-demo.js";
import { initParticles } from "./particles.js";

function currentSeed() {
  const u = new URLSearchParams(location.search);
  return u.get("seed") || freshSeed();
}

const seed = currentSeed();

// Below 1100px (and with JS off) the authored deck flow in index.html IS the page -
// readability over theater on small screens.
if (window.matchMedia("(min-width: 1100px)").matches) {
  renderScaffold(document.getElementById("scaffold"));
  renderDeal(document.getElementById("cardfield"), document.getElementById("deck"), deal(seed));
}

initDemo(document.querySelector("#card-demo .demo-mount"), seed);
initRecordings(document.querySelector("#card-recordings .rec-mount"));
initParticles(document.querySelector(".page"), seed);
initParallax(document.querySelector(".page"));

// Reroll: press "r" to re-deal the page from a fresh seed. The seed lands in the URL
// first, so every deal you see is shareable and reproducible.
addEventListener("keydown", (e) => {
  if (e.key.toLowerCase() !== "r" || e.metaKey || e.ctrlKey || e.altKey) return;
  const t = e.target;
  if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
  const s = freshSeed();
  history.replaceState(null, "", `?seed=${s}`);
  location.reload();
});
