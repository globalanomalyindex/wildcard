// Place the deal: slots hold liquid-glass frames. Each frame layers slow blob gradients
// (behind), a backdrop-blur glass pane (middle), and the card content (front). Blob
// layers and frames carry data-depth so the cursor parallax can move them at different
// rates. Decorative sub-cells stay plain scaffold with their ratio annotation.
const RATIO_LABEL = { "0.382": "1-1/φ 0.382", "0.236": "0.236", "1.000": "1:1 1.000" };

function blobLayer(i) {
  const layer = document.createElement("div");
  layer.className = "blob-layer";
  layer.dataset.depth = "14";
  for (let k = 0; k < 3; k++) {
    const b = document.createElement("div");
    b.className = `blob blob-${k} hue-${(i + k) % 3}`;
    b.style.setProperty("--phase", `${((i * 7 + k * 11) % 20) - 10}s`);
    layer.appendChild(b);
  }
  return layer;
}

export function renderDeal(field, deck, d) {
  // Cards may currently live inside the field from a previous deal (view changes
  // re-deal). Collect them document-wide BEFORE clearing, so the nodes survive.
  const cardEls = new Map(
    [...document.querySelectorAll("[data-card]")].map((el) => { el.hidden = false; return [el.dataset.card, el]; })
  );
  field.replaceChildren();
  const zoneW = 1 - 0.618;
  d.slots.forEach((slot, i) => {
    const el = document.createElement("div");
    el.className = "slot";
    el.style.setProperty("--x0", (slot.x0 - 0.618) / zoneW);
    el.style.setProperty("--x1", (slot.x1 - 0.618) / zoneW);
    el.style.setProperty("--y0", slot.y0);
    el.style.setProperty("--y1", slot.y1);
    el.style.setProperty("--i", i);
    const stack = d.stacks[i];
    if (stack.length === 0) {
      if (!slot.wide) {
        el.classList.add("slot-decor");
        const rel = ((slot.x1 - slot.x0) / zoneW).toFixed(3);
        const label = document.createElement("span");
        label.className = "decor-label";
        label.textContent = RATIO_LABEL[rel] || rel;
        el.appendChild(label);
      }
    } else {
      const frame = document.createElement("div");
      frame.className = "frame";
      frame.dataset.depth = "6";
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
      el.appendChild(frame);
    }
    field.appendChild(el);
  });
  document.documentElement.classList.add("dealt");
  field.dataset.seed = d.seed;
  if (d.fallback) field.dataset.fallback = "true";
}
