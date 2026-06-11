// Apply a {bands} tree to #field by moving the existing <section> templates into a
// generated band/cell structure. The real DOM nodes are reused — content is authored
// once in index.html (which is also the no-JS layout), never duplicated here.
export function render(field, tree) {
  const sections = new Map(
    [...field.querySelectorAll("[data-section]")].map((el) => [el.dataset.section, el])
  );
  const frag = document.createDocumentFragment();
  for (const band of tree.bands) {
    const bandEl = document.createElement("div");
    bandEl.className = "band";
    bandEl.style.setProperty("--h", band.hFrac);
    for (const cell of band.cells) {
      const cellEl = document.createElement("div");
      cellEl.className = cell.empty ? "cell cell-empty" : "cell";
      cellEl.style.setProperty("--w", cell.wFrac);
      if (cell.section) cellEl.appendChild(sections.get(cell.section));
      bandEl.appendChild(cellEl);
    }
    frag.appendChild(bandEl);
  }
  field.replaceChildren(frag);
  field.removeAttribute("data-fallback");
  field.dataset.seed = tree.seed;
  if (tree.fallback) field.dataset.fallback = "true";
}
