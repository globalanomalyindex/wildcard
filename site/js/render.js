// The visible mechanism. Slot panels PERSIST across deals: on a reshuffle each panel
// glides to its new measured geometry (CSS transitions on the real fractions), settles,
// and locks with a seat click. Nothing is staged for looks - the motion you see is the
// actual slot geometry changing, and every label is live engine data (slot row and
// x-extent, stack contents, seed).
const RATIO_LABEL = { "0.382": "1-1/φ 0.382", "0.236": "0.236", "1.000": "1:1 1.000" };
const ZONE_X0 = 0.618;
const ZONE_W = 1 - ZONE_X0;

function blobLayer(i) {
  const layer = document.createElement("div");
  layer.className = "blob-layer";
  layer.dataset.depth = "8";
  for (let k = 0; k < 3; k++) {
    const b = document.createElement("div");
    b.className = `blob blob-${k} hue-${(i + k) % 3}`;
    b.style.setProperty("--phase", `${((i * 7 + k * 11) % 20) - 10}s`);
    layer.appendChild(b);
  }
  return layer;
}

function buildInterior(el, slot, stack, cardEls, i) {
  el.replaceChildren();
  el.classList.toggle("slot-decor", stack.length === 0 && !slot.wide);
  if (stack.length === 0) {
    if (!slot.wide) {
      const rel = ((slot.x1 - slot.x0) / ZONE_W).toFixed(3);
      const label = document.createElement("span");
      label.className = "decor-label";
      label.textContent = RATIO_LABEL[rel] || rel;
      el.appendChild(label);
    }
    return;
  }
  const frame = document.createElement("div");
  frame.className = "frame";
  frame.dataset.depth = "2";
  frame.appendChild(blobLayer(i));
  const pane = document.createElement("div");
  pane.className = "glass-pane";
  frame.appendChild(pane);
  const content = document.createElement("div");
  content.className = "frame-content";
  const cards = stack.map((id) => cardEls.get(id));
  cards.forEach((c, k) => { if (k > 0) c.hidden = true; content.appendChild(c); });
  frame.appendChild(content);
  if (cards.length > 1) {
    let cur = 0;
    const cta = document.createElement("button");
    cta.className = "stack-cta";
    cta.type = "button";
    const setLabel = () => {
      cta.innerHTML = `next card <span class="cta-count">${cur + 1}/${cards.length}</span> <span class="cta-arrow" aria-hidden="true">→</span>`;
      cta.setAttribute("aria-label", `show next card, ${cur + 1} of ${cards.length} in this cell`);
    };
    setLabel();
    cta.addEventListener("click", () => {
      cards[cur].hidden = true;
      cur = (cur + 1) % cards.length;
      cards[cur].hidden = false;
      cards[cur].classList.remove("swap-in");
      void cards[cur].offsetWidth;
      cards[cur].classList.add("swap-in");
      setLabel();
    });
    frame.appendChild(cta);
  }
  // live cell schematic: the slot's real row and x-extent on the measured grid
  const meta = document.createElement("span");
  meta.className = "slot-meta";
  meta.textContent = `r${slot.row + 1} · x ${slot.x0.toFixed(3)}→${slot.x1.toFixed(3)}`;
  el.appendChild(meta);
  el.appendChild(frame);
}

export function renderDeal(field, deck, d, { animate = false } = {}) {
  if (!animate) field.replaceChildren();

  // Panels are reconciled by CONTENT, not position: a panel keeps carrying whatever of
  // its cargo survives the deal and physically glides to wherever the dealer seats it.
  // Greedy best-overlap matching, so motion is the real mechanism, not a crossfade.
  const existing = [...field.querySelectorAll(".slot:not(.slot-out)")];
  const carriers = existing.filter((el) => el._cards && el._cards.length);
  const spare = existing.filter((el) => !el._cards || !el._cards.length);
  const claimed = new Set();
  const overlap = (a, b) => a.filter((x) => b.includes(x)).length;

  // Park only the cards whose panels will be rebuilt; kept panels keep their cards.
  const cardEls = new Map(
    [...document.querySelectorAll("[data-card]")].map((el) => [el.dataset.card, el])
  );

  // Match the biggest stacks first so they get first pick of their old panels.
  const order = d.stacks.map((s, i) => i).sort((a, b) => d.stacks[b].length - d.stacks[a].length);
  const assigned = new Array(d.slots.length).fill(null);
  for (const i of order) {
    const stack = d.stacks[i];
    if (!stack.length) continue;
    let best = null, bestN = 0;
    for (const el of carriers) {
      if (claimed.has(el)) continue;
      const n = overlap(el._cards, stack);
      if (n > bestN) { best = el; bestN = n; }
    }
    if (best) { claimed.add(best); assigned[i] = best; }
  }

  d.slots.forEach((slot, i) => {
    const stack = d.stacks[i];
    let el = assigned[i];
    let kept = false;
    if (el) {
      kept = el._stack === stack.join("|");
    } else {
      el = spare.find((s) => !claimed.has(s)) || carriers.find((s) => !claimed.has(s));
      if (el) claimed.add(el);
      else {
        el = document.createElement("div");
        el.className = "slot";
        field.appendChild(el);
      }
    }
    el.classList.remove("lock");
    el.style.setProperty("--x0", (slot.x0 - ZONE_X0) / ZONE_W);
    el.style.setProperty("--x1", (slot.x1 - ZONE_X0) / ZONE_W);
    el.style.setProperty("--y0", slot.y0);
    el.style.setProperty("--y1", slot.y1);
    el.style.setProperty("--i", i);
    el._cards = [...stack];
    el._stack = stack.join("|");
    if (animate && el.isConnected && existing.includes(el)) {
      el.style.transitionDelay = `${i * 45}ms`;
      clearTimeout(el._lockTimer);
      el._lockTimer = setTimeout(() => {
        el.style.transitionDelay = "";
        el.classList.add("lock");
      }, 500 + i * 45);
    }
    if (kept) {
      // same panel, same cargo: only its live schematic needs refreshing
      const meta = el.querySelector(".slot-meta");
      if (meta) meta.textContent = `r${slot.row + 1} · x ${slot.x0.toFixed(3)}→${slot.x1.toFixed(3)}`;
    } else {
      for (const id of stack) {
        const card = cardEls.get(id);
        card.hidden = false;
        deck.appendChild(card);
      }
      buildInterior(el, slot, stack, cardEls, i);
    }
  });

  for (const el of existing) {
    if (claimed.has(el)) continue;
    for (const card of el.querySelectorAll("[data-card]")) { card.hidden = false; deck.appendChild(card); }
    el._cards = null;
    el.classList.add("slot-out");
    setTimeout(() => el.remove(), 340);
  }

  document.documentElement.classList.add("dealt");
  field.dataset.seed = d.seed;
  if (d.fallback) field.dataset.fallback = "true"; else delete field.dataset.fallback;
}
