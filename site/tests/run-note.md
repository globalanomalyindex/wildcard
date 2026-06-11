# Verification record — 2026-06-11

## Node suite (machine-verified)
`cd site && node --test` → **17/17 pass**: scaffold smoke; domains count/order/lens guards;
cksum anchors (incl. empty string); pickIndex mirror; **browser==shell parity across 6 seeds
(execs the real draw.sh)**; engine order/closure/ratios/determinism/variety/fit/emptiness/
stacked-void invariants across 120 seeds; fallback correctness; 400-seed sweep with zero
fallbacks.

## Browser (playwright, 1440×1024)
- `?seed=42`: hero faithful (Boyers Blur wordmark, gold row, multiply-blend grid hairlines);
  draw shows `manuscript illumination laying burnished gold leaf on gesso` /
  `time-and-rhythm` — **identical to `bash scripts/draw.sh --seed 42`**. 6 bands, 8 cells,
  2 empties, reading order = manifest order, no fallback.
- `?seed=wildcard`: visibly different composition (leading empty band, 38.2/61.8 honesty
  cell, 50/50 reference+install band); draw = `pollinator hand-brushing of vanilla orchid
  flowers` — the skill's name seeds a pollination expert, reproducible in any terminal.
- Reveals: IntersectionObserver adds `.in` on scroll (verified live: opacity 0 → 1).
  Full-page screenshots show blanks only because screenshots don't scroll — expected.
- Figure: capped at 72vh (was 1986px tall before the fix → 737px).
- Console: 0 errors (inline SVG favicon added). 2 benign Chromium preload-timing warnings
  for fonts that are demonstrably in use (wordmark/body render in them).
- Mobile 380px: engine inactive (authored single-column), correct order, no horizontal
  scroll, wordmark 84px fluid.

## A11y (spot-checked)
- `aria-live="polite"` on the draw output; die is a real `<button>` with `aria-label` and
  `:focus-visible` ring; recordings are native `<details>/<summary>` (keyboard-operable).
- Body contrast #302e3a on #e5e0f6 ≈ 10:1 (AA/AAA); gold used only at display sizes/chips.
- Hero grid image `alt=""` (decorative); reference-organism figure has descriptive alt.

## By construction (not separately exercised)
- No-JS: index.html contains the full content in document order; `data-fallback` styles it
  readably; the engine is pure enhancement. The demo without JS shows the three recordings'
  markup only after `initDemo` — recordings are injected by JS, so no-JS visitors see the
  hero + full story but no demo column content. Accepted for v1 (the column is the demo).
- Reduced motion: `prefers-reduced-motion` kills reveals via CSS and gates particles +
  typed reveal in JS (`matchMedia` checks at module init).
- Reroll: `r` writes `?seed=` via replaceState then reloads — same path as a shared URL.
