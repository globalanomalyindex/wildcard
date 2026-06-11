# DESIGN.md - wildcard

## Color
Base palette (from the user's Figma, file iqxNGyYx6eMbcPgWEPBKbu):
- seafoam field: #e5e0f6 (page background, light theme: daylight portfolio browsing)
- periwinkle: #77a0e4 (hero wordmark, card titles, primary accents)
- gold: #d0c382 (taglines, chips, decorative annotations)
- ink: #302e3a (body text), ink-soft: #6b6580
Depth extension (v4): deeper jewel tones live BEHIND the liquid glass only, so the page
keeps its daylight field while frames carry depth: deep indigo around oklch(0.45 0.09 280),
deep violet around oklch(0.42 0.1 300), deep teal-blue around oklch(0.5 0.08 250).
Never #000/#fff; neutrals tinted toward violet.
Strategy: Committed. Seafoam carries the surface; periwinkle and gold are identity;
deep jewel blobs give the glass its weight.

## Typography
- Boyers Blur (display): hero-position titles ONLY (the wordmark, and whichever title
  occupies the hero cell in the current view).
- Karrik (body): everything else, including all card titles. Lowercase preference.
- Body line-height ~1.45 in cards; hero copy tighter (1.06) per Figma.

## Layout
Measured golden-ratio grid (canvas-scanned from the chickpea reference):
vertical cuts 0.618/0.764/0.854 of width; horizontal cuts 0.382/0.618/0.764 of height;
band inset from viewport edges. Left zone: hero content. Right zone: dealt card frames.
Scaffold rules are DRAWN in-engine from these constants. One viewport at desktop;
authored single-column flow below 1100px wide or short viewports.

## Components
- Liquid glass frames: rounded 16px, hairline white border, backdrop-blur pane over
  slow-drifting deep-jewel blob gradients. Purposeful, never decorative sprinkle.
- Stack CTA: explicit labeled button (not an icon glyph), periwinkle, scale(0.97) active.
- Decorative sub-cells: hairline scaffold + tiny gold mono ratio annotations.

## Motion
- Custom curves: --ease-out: cubic-bezier(0.23, 1, 0.32, 1); UI under 300ms.
- Stagger 40-70ms on dealt frames. Blur-masked crossfades for card/view swaps.
- Cursor parallax three depths (blobs 14, frames 6, scaffold 2) via one lerped rAF.
- Blob drift 17-23s. Typewriter draw ~24ms/char, auto-shuffle every 5-7s.
- Everything gated by prefers-reduced-motion; hover effects gated by (hover:hover).
