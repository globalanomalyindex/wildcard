import { deal } from "./deal.js";
import { renderDeal } from "./render.js";
import { renderScaffold } from "./scaffold.js";
import { initParallax } from "./parallax.js";
import { freshSeed } from "./entropy.js";
import { initDemo, initRecordings } from "./draw-demo.js";
import { initParticles } from "./particles.js";
import { V, H } from "./grid-cells.js";
import { PROVENANCE } from "./domains.js";

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
const scaffold = document.getElementById("scaffold");
const heroInner = document.querySelector(".hero-inner");
const zones = { home: document.getElementById("zone-home"), install: document.getElementById("install") };

// The instrument line: live engine state, every value real and reproducible.
const readout = document.createElement("p");
readout.className = "readout";
readout.setAttribute("aria-hidden", "true");
document.querySelector(".page").appendChild(readout);

function runDeal(animate) {
  const d = deal(seed);
  renderDeal(field, deck, d, { animate });
  const cards = d.stacks.flat().length;
  readout.textContent =
    `seed ${d.seed} · ${cards} cards / ${d.slots.length} cells · ` +
    `cuts ${V.join(" ")} × ${H.join(" ")} · ` +
    `${PROVENANCE.count} domains @ ${PROVENANCE.commit} · r to reshuffle`;
  if (animate && !reduceMotion) {
    scaffold.classList.add("shuffling");
    setTimeout(() => scaffold.classList.remove("shuffling"), 700);
  }
}

const currentView = () => (location.hash === "#install" ? "install" : "home");

// Navigation IS reshuffling: changing view swaps the hero zone and re-seats the panels
// on a fresh seed, so the whole page visibly reorganizes around the new focus.
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
    runDeal(true);
  }
}

if (dealMedia.matches) {
  renderScaffold(scaffold);
  runDeal(false);
}
applyView(currentView());

initDemo(document.querySelector("#card-demo .demo-mount"), seed);
initRecordings(document.querySelector("#card-recordings .rec-mount"));
initParticles(document.querySelector(".page"), seed);
initParallax(document.querySelector(".page"));

window.addEventListener("hashchange", () => applyView(currentView(), { reshuffle: true }));

// Reroll: press "r" to re-seat the panels from a fresh seed. The seed lands in the URL
// first, so every deal you see is shareable and reproducible.
addEventListener("keydown", (e) => {
  if (e.key.toLowerCase() !== "r" || e.metaKey || e.ctrlKey || e.altKey) return;
  const t = e.target;
  if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
  if (!dealMedia.matches) return;
  seed = freshSeed();
  history.replaceState(null, "", `?seed=${seed}${location.hash}`);
  runDeal(true);
});
