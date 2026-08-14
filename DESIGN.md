# DESIGN.md - wildcard

The design language of the shipped landing page and case study. Earlier drafts explored a
seafoam-and-periwinkle glass system; that was replaced and this file describes what is live.

## Color
Two colors carry the whole site, plus ink.
- orange field: `#eb8853` (the page ground, both pages)
- pale: `#ced9f7` (the wordmark, the figures panel, highlight backgrounds)
- ink: `#1e1e1e` (all body text), ink-soft: `rgba(30,30,30,0.80)` (mono labels, captions)

`--ink-soft` is set at 0.80, not lower, on purpose. It carries every 10-11px mono label on the
site, and below about 0.78 that type drops under the 4.5:1 AA floor on both grounds. Measured:
4.61:1 on orange, 7.01:1 on pale, against 6.49:1 for full ink. Regenerate with
`node tests/contrast.mjs`.

The wordmark and the case study's `h1` sit at pale-on-orange, which is 1.82:1. That is a
deliberate logotype exemption at display size, not an oversight, and the site claims no blanket
WCAG conformance because of it. Everything that carries meaning as prose is ink or ink-soft.

## Typography
- Boyers Blur (display): the wordmark only.
- Karrik (body): everything else, including headings. Lowercase throughout, set globally by
  `text-transform: lowercase` in tokens.css. The case study overrides this to `none` on `.wrap`
  so it can carry acronyms (OS, AI, LLM, CI), proper nouns, model names, and the verbatim epigraph.
- The lede's type scales on `min(2.05vw, 3.4vh)`. The height term is load-bearing: sized on width
  alone, the lede kept its full height as viewports got shorter while the demo block (`top: 44vh`)
  walked up to meet it, and every desktop between 701px and about 848px tall printed the two on
  top of each other.

## Layout
One viewport at desktop, no scroll. Absolute cells over a golden-ratio grid measured from the
Chickpea reference image, which ships as the faint background and *is* the layout, not decoration.
Below 1100px wide or 700px tall the cells become a single authored column, ordered lede ->
wordmark -> live draw -> figures -> install -> ascii -> provenance. The live draw sits high in
that order because it is the one element that demonstrates the thesis.

## Motion
- `--ease-out: cubic-bezier(0.23, 1, 0.32, 1)`; UI transitions under 300ms.
- The live draw types at ~24ms/char and re-draws 5-7s after the previous one finishes. The delay
  is armed by the typewriter's completion callback, never in parallel with it: on its own clock,
  any character slower than ~110ms restarted the typing before the caption was ever written, which
  is exactly what background-tab timer throttling does.
- Two seeded ascii cells, redrawn per seed.
- Everything is gated by `prefers-reduced-motion`; hover effects are gated by `(hover: hover)` so
  they do not latch after a tap.

## Rules that are not negotiable
- No em dashes or en dashes in any copy.
- Nothing "live" may be faked. Every number on the page regenerates from the repo, and the
  browser draw reproduces byte-for-byte in the shell, which CI gates.
- Every affordance has a pointer path, not only a keyboard shortcut.
