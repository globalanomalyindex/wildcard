# Verification record

## v2 (2026-06-11) - single viewport, measured grid, card deck

Node suite: 15/15 (`cd site && node --test`) - cksum anchors, draw.sh parity over 6 seeds
(execs the real script), domains provenance, measured-grid constants pinned, dealer
invariants over 200 seeds (every card exactly once; demo pinned to row 1; cards only in
wide slots; text only in tall rows; max stack 3; deterministic; 56 distinct deals against
a ~60-signature ceiling; fallback valid; no fallback in sweep).

Engineering find of the build: deriving a random stream by hashing an incrementing
counter with CRC (cksum) mode-collapsed the deal to 6 distinct layouts in 200 seeds,
because CRC is GF(2)-linear and adjacent counters give correlated low bits. Fix: hash
once for identity, then mulberry32 for the sequence. Draw parity is unaffected (a draw
is a single direct hash, exactly like draw.sh).

Browser (playwright):
- 1440x1024 `?seed=42`: NO body scroll; hero matches the Figma frame (wordmark, gold
  row, lede and closing on the measured 0.382/0.764 rows, grid hairlines from the
  pre-rotated transparent PNG); draw = `manuscript illumination laying burnished gold
  leaf on gesso` / `time-and-rhythm`, identical to `bash scripts/draw.sh --seed 42`.
- All 7 cards reachable by cycling stack chips; after a copy trim + chrome tightening
  on the recordings card, ZERO cell overflows across all cards, all stack positions,
  and all three recording pages.
- `?seed=wildcard`: visibly different deal; decorative sub-cells appear with ratio
  annotations like the reference image; the draw is the vanilla-orchid pollination
  expert (the skill's name hashes to the project's own metaphor; verifiable in any
  terminal).
- 380px: deal inactive, authored stacked flow, demo and recordings pager fully
  functional, no horizontal scroll.
- Console: 0 errors; 2 benign Chromium font-preload timing warnings (fonts are
  demonstrably in use).
- Copy: `grep -rn "—" site/ scripts/` returns nothing. No em dashes anywhere.

By construction: no-JS and narrow viewports get the authored deck flow (page scrolls,
everything readable); reduced motion removes deal-in/fade animations, the typed reveal,
and the pollen canvas.

## v1 (2026-06-11, superseded by v2)

17/17 node suite (guillotine engine: order/closure/ratios/determinism/variety/fit
invariants over 120 seeds, 400-seed no-fallback sweep); browser-verified hero fidelity,
seed-42 parity, scroll reveals, mobile single column, a11y spot checks. The v1 guillotine
and its tests were removed in v2 (preserved in git history).
