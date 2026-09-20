# DESIGN.md - wildcard

The source identity is an orange field, pale highlights and ink type, composed on the measured Chickpea grid. Keep this character while making the draw and evidence easier to inspect. This file states the current design contract; it is not a blanket accessibility certification.

## Color

- Orange field: `#eb8853`.
- Pale wordmark/evidence surface: `#ced9f7`.
- Ink: `#1e1e1e`; secondary ink: `rgba(30,30,30,0.80)`.

The existing palette test measures full ink on orange at about 6.49:1 and secondary ink on orange/pale at about 4.61:1/7.01:1. Regenerate with `node tests/contrast.mjs`. These token pairs do not certify all rendered states, composited backgrounds, disabled controls or text sizes.

Pale on orange is about 1.82:1. The decorative brand wordmark can retain that identity treatment; an ordinary heading such as “case study” cannot claim a logotype exception. Meaningful headings should use ink or another tested color, with at least 3:1 for qualifying large text and 4.5:1 for normal text.

## Typography

Boyers Blur is reserved for the wordmark. Karrik carries headings and prose; system monospace carries short commands and receipts. Font names are existing asset metadata, not proof of redistribution rights; see `THIRD_PARTY_NOTICES.md`.

Use the lowercase voice for authored labels, not to corrupt copied values. Seeds, JSON, identifiers and code must retain their exact content. Keep long prose near 65 characters per line where practical. Do not depend on 10px captions to communicate essential uncertainty or primary actions.

## Composition and reading order

Keep a compact desktop composition with an expressive wordmark, live draw cell, evidence area and a clear route to installation or methods. The measured reference grid is part of the source identity. The current breakpoint converts the composition to a column below 1100px width or at 700px height and below. Semantic DOM order should match the meaningful reading sequence, even when desktop placement differs.

Long seeds and receipts wrap without widening the page. Expanded content remains reachable. A desktop poster arrangement is not a reason to clip prose under zoom, text-spacing overrides or short viewports. Test mobile reflow and actual keyboard order; CSS breakpoints alone do not establish usability.

## Draw interaction

The first completed draw is stable and complete. Draw another is a real button. If automatic draws are available, they begin only after an explicit action, have a pause control and respect reduced-motion preference. Copy command, copy receipt and copy link use the current completed receipt. The URL changes only when that state is ready.

Use text nodes for URL/corpus values and shell-safe quoting for copied commands. Show a clear failure state when input, runtime, entropy or corpus validation fails. Announce a completed user-requested result coherently; do not announce a character-by-character animation. Decoration remains hidden from assistive technology.

Use visible keyboard focus and comfortable pointer targets, aiming for at least 44px on touch layouts. A global single-letter reload shortcut is not part of the design contract. Focus, receipt inspection and copy actions must not be disrupted by a timer.

## Evidence presentation

Keep the three historical questions and the audit corrections close to the result. Numerical displays need units, denominators, confidence intervals and source links. A study selector or disclosure can reduce density inside the pale panel. A recorded example needs a problem, cue, move, provenance and limitation, plus an explicit recorded label.

The case study needs stable anchors and understandable tables with captions, header associations and accessible overflow. New study plans must not visually resemble completed results. The public byline is christopher robin fiore, with AI assistance described honestly.

## Motion

Preserve `--ease-out: cubic-bezier(0.23, 1, 0.32, 1)` for short purposeful transitions. Animate opacity/transform rather than layout geometry. Gate hover effects for hover-capable devices and respect reduced motion. Seeded ASCII may carry character, but it must stay decorative and must not imply model activity.
