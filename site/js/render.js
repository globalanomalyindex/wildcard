// Place the deal: build slot divs in the card field, move the authored card nodes into
// their slots, wire stack cycling. Decorative sub-cells get the ratio annotations the
// reference image itself carries.
const RATIO_LABEL = { "0.382": "1-1/φ 0.382", "0.236": "0.236", "1.000": "1:1 1.000" };

export function renderDeal(field, deck, d) {
  field.replaceChildren();
  const zoneW = 1 - 0.618; // slot fractions arrive in page space; normalize to the zone
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
      const cards = stack.map((id) => deck.querySelector(`[data-card="${id}"]`));
      cards.forEach((c, k) => { if (k > 0) c.hidden = true; el.appendChild(c); });
      if (cards.length > 1) {
        let cur = 0;
        const chip = document.createElement("button");
        chip.className = "stack-chip";
        chip.type = "button";
        const setLabel = () => {
          chip.textContent = `${cur + 1}/${cards.length} ↻`;
          chip.setAttribute("aria-label", `card ${cur + 1} of ${cards.length} in this cell, press to cycle`);
        };
        setLabel();
        chip.addEventListener("click", () => {
          cards[cur].hidden = true;
          cur = (cur + 1) % cards.length;
          cards[cur].hidden = false;
          cards[cur].classList.remove("swap-in");
          void cards[cur].offsetWidth;
          cards[cur].classList.add("swap-in");
          setLabel();
        });
        el.appendChild(chip);
      }
    }
    field.appendChild(el);
  });
  document.documentElement.classList.add("dealt");
  field.dataset.seed = d.seed;
  if (d.fallback) field.dataset.fallback = "true";
}
