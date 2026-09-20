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
- [x] Commit and push preregistration with source hashes before main acquisition. Generate baseline bank before main conditions; mask/shuffle judgments with fixed seed; preserve all call artifacts.
- [x] Analyze fixed primary and secondary contrasts, uncertainty, judge disagreement, task-level results, failures and actual usage. Independently review conclusions.
- [x] Integrate safe interactive draws, evidence-driven case study and recorded comparison explorer. Correct README, plugin descriptions and theory language; publish authorship/contribution boundaries.
- [x] Run complete tests and browser checks; review the branch and fix material issues.
- [x] Push the reviewed release to main, wait for CI, and verify live deployment.

## Interfaces

Sampler: `drawV2(seed, {mode?})` returns a promise for a versioned receipt including `mode`, `key`, `value`, `lens`, `seed`, `sampler`, `entryId`, `corpusSha256`. Browser and plugin engines are generated from one canonical implementation. `validateSeed` and `shellQuote` are shared helpers.

Statistics: `mean`, `pairedBootstrap(diffs,{seed,iterations})`, `signedRank(diffs)`, `signFlip(diffs)`, `holm(pvalues)`. Analysis unit is the problem, averaging judges within problem; model votes do not increase N.

Study assets: tasks contain `main` and `development` arrays; cards contain grounded label/relation/boundary records; diagnostics contain paired relation changes and expected action consequences. Collector owns exact prompt rendering, masking, schemas, call ledger and study manifest. Derived outputs never modify raw records.

## Execution log

2026-09-20: The initiating request authorized the repository audit, research, implementation, and publication. This plan records the resulting execution choices. Baseline suite: ALL GREEN. Authenticated research transport succeeds; provider-returned model snapshot is not exposed by CLI and will be recorded as unknown.

2026-09-20 19:54 UTC: Final development passes all 32 scheduled calls. The earlier complete development run and bank-only prefreeze run remain preserved. Materials commit 6ca0d76 precedes frozen main manifest d93831e, published to globalanomalyindex/wildcard before the first main bank call. Main acquisition is in progress; no main outcome claims are made yet.

2026-09-20 20:30 UTC: All 64 bank and 128 main calls are valid. Original masked panel: 63/64 valid; i07-judge-2 used candidate IDs in two bank-reference fields. The frozen primary analyzer halts before scoring. Original records were committed as cb25d15 and published. The independent reviews support one prospectively frozen full-panel remeasurement with per-request identity enums, preserving the original primary halt and every raw artifact. See research/transfer-v1/amendment.md. Strict counterfactual diagnostics: 6/8 pairs, 12/16 variants.

2026-09-20: Amended freeze ca29d29 was published before any new judge calls; all 64 fresh blocks completed validly in one attempt each and raw records were committed as 36d7b58. The amended primary is inconclusive: LR minus R = -0.015625 QNM@4, 95% family-stratified bootstrap interval [-0.109375, 0.0625], mean sign-flip p = 1. Neither secondary passes Holm correction. An independent implementation reproduces the complete scores and inference. Runtime suite, 29 Python research tests, 10 Node research tests and exact three-artifact reproduction pass; final browser and publication checks follow.

### Final local release gate

The complete amended dataset passes 898 browser checks in each of Chromium, Firefox and WebKit. Rapid comparison changes are coalesced into address-bar updates without delaying visible selections. Runtime tests and raw-record reproduction pass; all 478 historical files remain unchanged. The 13-page research PDF was rendered and visually checked in full, including its final pagination. Public results preserve the original primary halt and identify the completed amended measurement.

The release merged through PR #1 as f84e341. GitHub Actions run 35538289076 passed validation and Pages deployment. Six live assets matched the reviewed bytes, 128 live browser checks passed, and a fresh GitHub plugin installation verified the exact merged source. The user subsequently authorized a separate working-solutions system and study; that follow-up does not alter this study’s finding.
