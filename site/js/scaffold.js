// In-engine scaffolding: the grid is DRAWN from the measured constants, not rendered
// from the reference image. Horizontal rules at the H fractions span the band; vertical
// rules at the V fractions span the band height; edge rules close the frame - the same
// structure the chickpea reference carries, now generated.
import { V, H } from "./grid-cells.js";

export function renderScaffold(mount) {
  mount.replaceChildren();
  const line = (cls, style) => {
    const el = document.createElement("div");
    el.className = `rule ${cls}`;
    Object.assign(el.style, style);
    mount.appendChild(el);
  };
  for (const h of H) line("rule-h", { top: `${h * 100}%` });
  line("rule-h", { top: "100%" });
  for (const v of V) line("rule-v", { left: `${v * 100}%` });
  line("rule-v", { left: "0%" });
  // registration ticks at every real V x H intersection (they rotate while the
  // mechanism re-seats - see #scaffold.shuffling)
  for (const v of V) {
    for (const h of H) {
      const t = document.createElement("div");
      t.className = "tick";
      t.style.left = `${v * 100}%`;
      t.style.top = `${h * 100}%`;
      mount.appendChild(t);
    }
  }
}
