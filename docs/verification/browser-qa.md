# Browser verification — 20 September 2026

The completed public artifact passed **898 checks in each of three browser engines**. This validates the interface against the amended measurement panel; it does not turn the halted original primary analysis into a completed test. No frozen research file was changed during this UI verification.

| Engine | Automation transport | Checks | Elapsed |
|---|---|---:|---:|
| Chromium 153.0.8010.48 | `@playwright/cli@0.1.21` | 898 passed | 41.96s |
| Firefox 156.0 | `@playwright/cli@0.1.21` | 898 passed | 43.86s |
| WebKit 26.6 | direct stable `playwright@1.63.0` | 898 passed | 38.56s |

The [portable machine-readable record](browser-qa.json) contains the full check list, source hashes, artifact hash, engine versions and scope limits. The tested data was complete, contained 32 tasks, identified `measurementPanel: remeasurement`, and retained `originalPrimaryStatus: halted`.

## Coverage

The driver selects every task and every arm in both comparison columns: **256 rendered arm sets**. It checks exact action titles and scores against the artifact, source-fact and source-note text, reference-bank action counts and eventual URL parity. It checks all eight diagnostic pairs' expected and observed traces, the recorded 6/8 summary, accessible result-chart text, all 32 task-effect buttons and navigation from an effect to its matching comparison.

Security and state probes cover hostile literal seeds under both motion preferences, exact browser/Node CLI receipt parity, legacy unversioned replay, escaped command export, JSON and URL export, autoplay pause and committed-state consistency, static decorative fields, overlong-input rejection and entropy failure. The final matrix recorded zero uncaught page errors, unexpected failed assets or CSP violations.

Responsive coverage includes 1440×1024, 1280×720, 390×844, 320×800, 640×360, 320×180 and 1280×500. CSSOM user-style emulation applies line height 1.5, letter spacing .12em, word spacing .16em and paragraph spacing 2em. Those changes preserve the page CSP. Tests verify document widths, reachable lower content, local navigation scrolling, keyboard focus and 44px mobile navigation targets. The 640×360 and 320×180 checks emulate reflow equivalent to 200% and 400% from 1280×720; they are not native browser zoom tests.

Desktop and mobile screenshots were reviewed for landing, overview, actual results, expanded methods and an expanded comparison with the longest serialized donor card. The source fact, authored-abstraction note and boundary remained readable at 320px. A separate 320px spot check opened the i07 reference bank and its first action, with no horizontal overflow. Another opened the i07/R second-judge explanation: it displayed “direct bank reference: none” together with the reason a match propagates across the judge's mechanism group. Recorded judge text remains as supplied; the UI does not invent an explanation for an opaque recorded reason.

## Fix verified during this pass

Unthrottled rapid selection exceeded WebKit's history replacement quota. This was reproduced during exhaustive selection, and can also affect rapid keyboard input. `selection-url.js` now coalesces writes behind one 150ms timer while rendering the current selection immediately. A pending write uses the latest task and arms and reads the current URL at commit time, preserving a newly selected section. Exceptions are not swallowed.

Two focused unit tests were first added, then passed with the implementation, including on Node 22. All 20 site unit tests pass. The browser regression sends 160 rapid selection events, verifies immediate latest content, switches sections while a write is pending, and checks bounded writes and final URL convergence. All three engines pass. Each exhaustive comparison waits for actual URL convergence; the final gate has no artificial pacing delay or history/CSP bypass.

The initial expanded driver also needed two harness corrections: wait for same-document hash navigation to reveal its requested view, and expand a disclosure only when it is closed. Those test-state failures were resolved before the final matrix.

## Reproduction and limits

Install the pinned engines, then run from the repository root:

```sh
npx --yes --package=@playwright/cli@0.1.21 playwright-cli install-browser chromium --with-deps
npx --yes --package=@playwright/cli@0.1.21 playwright-cli install-browser firefox --with-deps
npx --yes --package=playwright@1.63.0 playwright install webkit --with-deps
python3 scripts/test-browser.py --browsers chromium firefox webkit
node --test site/tests/*.test.js
```

The driver serves the actual `site/` directory through a temporary localhost HTTP server and writes screenshots and detailed records to `output/playwright/regression` by default. Each engine has an explicit 90-second bound. It makes no model calls and publishes no mock study data.

The CLI pin bundles Playwright `1.64.0-alpha-1789764292000`. Its alpha WebKit incorrectly applied document CSP to native select styling in a minimal reproduction. The same minimal self-only policy passed under stable Playwright 1.63.0/WebKit 26.6, which is why WebKit uses the direct API fallback. Playwright screenshot preparation separately injects an inert style, so WebKit functional assertions omit screenshots. The application's restrictive CSP is retained, with no style exception or console-error exemption.

Chromium exercises native clipboard read/write. Firefox and WebKit use a declared export-value shim, so their native OS clipboard integration is unverified. Browser checks supplement visual review; they do not certify assistive-technology behavior, native mobile devices, network performance, remote source-link availability or the final deployed site. Screenshot evidence remains local QA material rather than a published research observation.

## Supplement: final PDF link

After the full matrix, the only interface change was a PDF download link in the current-results card. A targeted Chromium 153.0.8010.48 check at widths 1440, 390 and 320 verified that the link remained readable, within the card and reachable without document overflow. Both mobile targets measured 44px high. The link returned HTTP 200 with `application/pdf`, 148,027 bytes and the `%PDF-` signature. An actual browser click downloaded `Wildcard_Research_Paper_2026-09-20.pdf` without error; its bytes matched the published file exactly.

The PDF parsed as 13 pages, and first-page text extraction recovered the manuscript title, author and amended-analysis status. This targeted local check does not repeat the full three-engine matrix or certify PDF accessibility. The supplement in `browser-qa.json` records the final PDF and HTML hashes.
