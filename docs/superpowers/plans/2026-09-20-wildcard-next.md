# Wildcard implementation plan

**Goal:** ship an inspectable creative-transfer tool, completed controlled benchmark and research/design case study.

**Architecture:** preserve historical artifacts; introduce versioned sampling and evidence layers; collect a separate experiment; publish a static evidence explorer. Independent agents own sampling, statistics and study assets while the primary agent owns acquisition, product integration and release.

**Tech stack:** Bash, Node 22 ES modules, Python 3 standard library, static HTML/CSS, existing fonts, authenticated Codex CLI for recorded research calls.

**Spec:** `docs/superpowers/specs/2026-09-20-wildcard-next-design.md`

## Global constraints

- GitHub repository: `globalanomalyindex/wildcard`; public byline: `christopher robin fiore`.
- Historical `experiment/` files remain unchanged.
- Record every scheduled call including failure. Do not invent missing data or metadata.
- Preserve source visual identity and lowercase editorial voice; no unsupported mechanism or safety guarantees.
- Research calls use public authored fixtures, fresh contexts, tools disabled, no outcome-dependent stopping or prompt selection.

## Review focus

Hostile Unicode/quote seeds must remain literal across HTML, URLs and shell. Legacy links must retain old draws. Duplicate grades must not silently become independent observations. Missing or malformed completions must not disappear from denominators. The evidence explorer must expose the actual selected artifact and source, including failures and negative comparisons.

## Work sequence

- [x] Establish clean source at audited commit, verify remote account, extract ZIP with path validation, run baseline suite.
- [x] Independently audit research, historical statistics, product, security and corpus; record accepted/rejected audit findings.
- [x] Implement and test versioned sampler, receipt, legacy replay, corpus failure handling and cross-runtime vectors.
- [x] Implement historical manifest, strict validation, corrected evidence data and robust statistical utilities with boundary tests.
- [x] Freeze 32 main briefs, grounded relation cards, four development tasks and separate counterfactual diagnostics. Review distinctness and prior-art positioning.
- [x] Build collector and deterministic schemas. Test malformed JSON, duplicate IDs, tool attempts, incomplete outputs, retries and restart idempotency on synthetic fixtures.
- [x] Verify transport and judge calibration on development/known-answer fixtures; freeze exact main manifests before acquisition.
- [ ] Commit and push preregistration with source hashes before main acquisition. Generate baseline bank before main conditions; mask/shuffle judgments with fixed seed; preserve all call artifacts.
- [ ] Analyze fixed primary and secondary contrasts, uncertainty, judge disagreement, task-level results, failures and actual usage. Independently review conclusions.
- [ ] Integrate safe interactive draws, evidence-driven case study and recorded comparison explorer. Correct README, plugin descriptions and theory language; publish authorship/contribution boundaries.
- [ ] Run complete tests and browser checks; review the branch; fix material issues; push reviewed release to main, wait for CI, verify live deployment.

## Interfaces

Sampler: `drawV2(seed, {mode?})` returns a promise for a versioned receipt including `mode`, `key`, `value`, `lens`, `seed`, `sampler`, `entryId`, `corpusSha256`. Browser and plugin engines are generated from one canonical implementation. `validateSeed` and `shellQuote` are shared helpers.

Statistics: `mean`, `pairedBootstrap(diffs,{seed,iterations})`, `signedRank(diffs)`, `signFlip(diffs)`, `holm(pvalues)`. Analysis unit is the problem, averaging judges within problem; model votes do not increase N.

Study assets: tasks contain `main` and `development` arrays; cards contain grounded label/relation/boundary records; diagnostics contain paired relation changes and expected action consequences. Collector owns exact prompt rendering, masking, schemas, call ledger and study manifest. Derived outputs never modify raw records.

## Execution log

2026-09-20: User authorized the full plan and execution in the initiating request. Implementation proceeds without repeated permission gates. Baseline suite: ALL GREEN. Authenticated research transport succeeds; provider-returned model snapshot is not exposed by CLI and will be recorded as unknown.

2026-09-20 19:54 UTC: Final development passes all 32 scheduled calls. The earlier complete development run and bank-only prefreeze run remain preserved. Materials commit 6ca0d76 precedes frozen main manifest d93831e, published to globalanomalyindex/wildcard before the first main bank call. Main acquisition is in progress; no main outcome claims are made yet.
