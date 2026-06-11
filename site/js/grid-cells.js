// MEASURED from assets/chickpea-grid-display.png by a canvas alpha-scan (2026-06-11):
// vertical rules at 0.618 / 0.764 / 0.854 of width; horizontal rules at 0.382 / 0.618 /
// 0.764 of height (plus edge rules). Recursive golden sections - each cut splits its
// region at 1/phi. The Figma hero already sits on these cells (right column x=890 =
// 0.618 x 1440; description ends at the 0.382 row; closing statement starts at 0.764).
// If the reference image ever changes, re-run the scan (see tests/run-note.md) and
// update these constants; deal.test.js pins them.
export const V = [0.618, 0.764, 0.854];
export const H = [0.382, 0.618, 0.764];

// Right-zone slot geometry: 4 rows between the H cuts; each row is either one wide slot
// (x 0.618..1) or splits at the measured V cuts into three compact sub-slots.
export function rowSlots(row, split) {
  const top = row === 0 ? 0 : H[row - 1];
  const bottom = row === 3 ? 1 : H[row];
  if (!split) return [{ row, x0: V[0], x1: 1, y0: top, y1: bottom, wide: true }];
  return [
    { row, x0: V[0], x1: V[1], y0: top, y1: bottom, wide: false },
    { row, x0: V[1], x1: V[2], y0: top, y1: bottom, wide: false },
    { row, x0: V[2], x1: 1,    y0: top, y1: bottom, wide: false },
  ];
}
