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
- Copy: grepping site/ and scripts/ for the em-dash character returns nothing.

By construction: no-JS and narrow viewports get the authored deck flow (page scrolls,
everything readable); reduced motion removes deal-in/fade animations, the typed reveal,
and the pollen canvas.

## v1 (2026-06-11, superseded by v2)

17/17 node suite (guillotine engine: order/closure/ratios/determinism/variety/fit
invariants over 120 seeds, 400-seed no-fallback sweep); browser-verified hero fidelity,
seed-42 parity, scroll reveals, mobile single column, a11y spot checks. The v1 guillotine
and its tests were removed in v2 (preserved in git history).

## v3 notes pass (2026-06-11)

Auto-shuffle replaces the die: a fresh real-entropy draw every 5-7s with the typewriter
effect, paused on hidden tabs, static under reduced motion (machine-verified: two
different draws 8s apart). Closing statement left-aligned. Karrik on all card titles;
Boyers Blur only on the wordmark. The reference image is no longer rendered: scaffold.js
DRAWS the grid from the measured constants (8 rules), and content sits in liquid-glass
frames (backdrop-blur panes over per-frame drifting blob gradients, periwinkle/gold/
violet). Cursor parallax moves blobs (14px), frames (6px), and scaffold (2px) through
one lerped rAF loop; disabled for reduced motion and coarse pointers. Verified: no body
scroll, zero card overflows, 15/15 node suite.

## v4 design pass (2026-06-11)

Guided by emil-design-eng + impeccable. Install link now navigates: clicking it reshuffles
the entire page (fresh seed, re-dealt field), install takes the hero cell (Boyers Blur,
gold-numbered steps), the wordmark moves to a glass frame at the bottom as the way back;
hash deep-links work and a CSS :target fallback covers no-JS. Stack chip became a labeled
CTA ("next card 1/3" pill, scale-on-press, custom ease-out). Deeper jewel blobs
(indigo/gold/violet) behind the glass plus a page-wide ambient wash for coherence. Band
gets bottom air (91.5vh); dealt-mode type scales with viewport height (root cause of the
near-cutoff). Pollen canvas replaced with CSS-animated DOM motes after the canvas was
caught corrupting compositing beneath backdrop-filter panes (black band in captures);
alpha-oklch inside gradients pre-resolved to rgba for the same reason. Verified at
1440x900: no body scroll, zero overflows across all stacks and recordings pages, install
flow round-trips with reshuffles, 22 seeded motes, console clean. 15/15 node suite.

## v5 mechanical skeleton (2026-06-11)

The exposed-internals pass: utilitarian Swiss, and everything shown is real. Panels are
persistent objects reconciled by CARGO (greedy best-overlap matching): on every reshuffle
they glide to their new measured geometry over 480ms (mechanical in-out curve, 45ms
stagger) and seat with a lock click; measured 0-3 panels physically moving per round with
panels surviving across rounds and the demo's timers never disturbed. Scaffold rules
became dashed seams with registration ticks at the 9 real intersections (ticks rotate 45
degrees while the mechanism re-seats). Every label is live engine data: per-panel cell
schematics (row + x-extent on the measured grid) and a bottom instrument line (seed,
cards/cells, the phi cuts, domain count @ generating commit). De-polished: radius 8,
seam-colored borders, blur 24 to 12, parallax depths 14/6/2 to 8/5/2/1. Install hero in
Karrik (Boyers Blur is wordmark-only). Blinking dot removed. Ghost-navigation candidate
investigated: five reshuffles under capture-phase click+hashchange instrumentation showed
zero spurious events; deliberate install/back flows correct both directions. 15/15 suite,
zero overflows, no body scroll.
