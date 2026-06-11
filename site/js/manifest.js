// Ordered content sections. Reading order is THIS order, always. The engine only varies
// which cells carry them; it can never reorder, drop, or duplicate a section.
// minColFrac: minimum fraction of the content column a cell for this section may occupy.
export const MANIFEST = [
  { id: "thesis",             kind: "text",    minColFrac: 0.5,   minRowPx: 220 },
  { id: "how-it-works",       kind: "text",    minColFrac: 0.5,   minRowPx: 240 },
  { id: "honesty",            kind: "text",    minColFrac: 0.5,   minRowPx: 220 },
  { id: "nature",             kind: "text",    minColFrac: 0.5,   minRowPx: 240 },
  { id: "reference-organism", kind: "image",   minColFrac: 0.382, minRowPx: 300 },
  { id: "install",            kind: "compact", minColFrac: 0.382, minRowPx: 160 },
];

// The only ratios the engine may cut with — the three values in the chickpea grid legend.
export const RATIOS = [0.382, 0.5, 0.618];
