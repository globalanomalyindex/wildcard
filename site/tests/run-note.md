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

## v6 figma redesign + case study (2026-06-11)

New flat-orange design (no glass/deck/parallax; those modules + tests retired, in git
history). Tokens: orange #eb8853, pale #ced9f7, ink #1e1e1e. Layout matches Figma node
1:2: top-left lede, giant bottom-anchored pale wordmark (boyers blur), top-right pale
panel ("figures & stuff here") holding REAL regenerable data, big "install > > >" CTA
that css-:target-flips the panel to the one-command plugin install (no-js friendly),
seeded digital ASCII drift in the two small cells (the only motion; ~12fps; reduced-motion
static), and the live seeded typewriter draw (doubles as the parity figure). all rendered
copy lowercase (verified by a browser textContent A-Z scan = 0 on both pages). zero
em/en dashes (grep). no body scroll at 1440x1024; no horizontal scroll at 380px; install
flip + back verified. figures panel data is honest and caveated (small-n flagged) and
every number regenerates from tests. full case study at docs/case-study.md and the live
page site/case-study/ (linked from the panel). node suite 8/8, shell suite ALL GREEN.

## v7 demo + install tweaks (2026-06-11)

draw demo no longer flashes: reserved heights (demo box a steady 194px through a full
cycle, measured), the previous note stays in place dimmed while the next draw loads, and a
subtle pulse bar under the label shows the loading (breathes when idle, sweeps when
loading; reduced-motion static). install > > > no longer flips the panel (that swap
shifted page alignment); it now links to case-study/#install, which lands on the
highlighted install heading with the plugin commands below. dead install-flip css/markup
removed. node suite 8/8, shell ALL GREEN, zero em dashes, all lowercase.

## v8 concepts mode (2026-06-12)

second draw mode shipped end-to-end. draw.sh now rolls a mode first via
cksum("mode:"+seed)%2 (0=specialist from the 378-discipline map, 1=concept from a new
461-concept pool) and emits mode= + domain=|concept= + lens=; the specialist tag stays
"domain" so prior parity holds by construction. concept pool sourced offline (frozen,
not a live api call): wikipedia vital articles l3+l4 (7291 candidates, people+history
excluded at source) -> screen_concepts.sh mechanical denylist with logged drops (7115
kept, 176 rejected: 142 names/15 person/9 toolong/6 ip/4 meta) -> multi-agent curate +
adversarial pass -> 461 final, gated by audit_concepts.sh (re-runs the denylist).
measured: mode split 296/600 (49.3%) via test_mode_balance.sh; specialist diversity 152
distinct/200 (max 6); concept diversity 160 distinct/200 (max 3). all numbers in
docs/measurements.md, regenerable.

site: domains.js now exports DOMAINS(378) + CONCEPTS(461) + LENSES + PROVENANCE; the live
demo is mode-aware (specialist -> "what a <x> specialist would notice"; concept -> "what a
professor of <x> would notice, or what <x> has in common"); parity.test.js checks mode +
pick + lens against the real draw.sh over 6 seeds incl. a concept seed and string seeds;
concept-diversity.test.js added. figures panel gains two figures (two-modes coin-flip;
concept-pool safety pipeline). case study + its hand-maintained html gain an "open scope,
safely" section (why an offline snapshot beats a live wikipedia call; the logged screen;
concept-as-professor framing so concept mode keeps the "summon an expert" quality) plus an
honest concept-pool limitation. concept connection uses spreading activation (collins &
loftus 1975) gated by the same structure-mapping bar; documented in connecting.md.

browser smoke: index + case study render at 1440 and 380px; index single-viewport at
desktop; concept mode surfaces in the live demo (302/600 in-browser over 1..600); live
parity exact (seed 1 -> concept/bell, seed 2 -> specialist/shielded-cell); console 0/0;
no mobile horizontal page overflow (rejection-log pre scrolls internally by design). node
suite 9/9, shell ALL GREEN, zero em/en dashes, all-lowercase voice.
