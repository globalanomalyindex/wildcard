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

// The deal needs width for the grid AND height for the cells: below either floor the
// authored single-column flow is the more readable page, and it may scroll freely.
const dealMedia = window.matchMedia("(min-width: 1100px) and (min-height: 760px)");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

let seed = currentSeed();
const field = document.getElementById("cardfield");
const deck = document.getElementById("deck");
const heroInner = document.querySelector(".hero-inner");
const zones = { home: document.getElementById("zone-home"), install: document.getElementById("install") };

const currentView = () => (location.hash === "#install" ? "install" : "home");

// Navigation IS reshuffling: changing view swaps the hero zone and re-deals the field
// from a fresh seed, so the whole page reshapes around the new focus.
function applyView(view, { reshuffle = false } = {}) {
  zones.home.hidden = view !== "home";
  zones.install.hidden = view !== "install";
  if (!reduceMotion) {
    heroInner.classList.remove("swap");
    void heroInner.offsetWidth;
    heroInner.classList.add("swap");
  }
  if (reshuffle && dealMedia.matches) {
    seed = freshSeed();
    history.replaceState(null, "", `?seed=${seed}${view === "install" ? "#install" : ""}`);
    renderDeal(field, deck, deal(seed));
  }
}

if (dealMedia.matches) {
  renderScaffold(document.getElementById("scaffold"));
  renderDeal(field, deck, deal(seed));
}
applyView(currentView());

initDemo(document.querySelector("#card-demo .demo-mount"), seed);
initRecordings(document.querySelector("#card-recordings .rec-mount"));
initParticles(document.querySelector(".page"), seed);
initParallax(document.querySelector(".page"));

window.addEventListener("hashchange", () => applyView(currentView(), { reshuffle: true }));

// Reroll: press "r" to re-deal from a fresh seed. The seed lands in the URL first, so
// every deal you see is shareable and reproducible.
addEventListener("keydown", (e) => {
  if (e.key.toLowerCase() !== "r" || e.metaKey || e.ctrlKey || e.altKey) return;
  const t = e.target;
  if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
  if (!dealMedia.matches) return;
  seed = freshSeed();
  history.replaceState(null, "", `?seed=${seed}${location.hash}`);
  renderDeal(field, deck, deal(seed));
});
