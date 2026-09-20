# wildcard

a small tool for thinking from somewhere else. wildcard is a Claude Code skill that samples an outside cue, explores what it brings to the problem, and offers concrete moves the user can accept or ignore.

the cue can be a niche specialist from a curated pool of 378 disciplines or a concept from a pool of 461. the skill first records the problem's structure, then uses the sampled cue and lens to explore possible transfers. it asks whether a useful action remains when the donor explanation is removed.

this is **inference-time context conditioning**: the model receives different text in its context. wildcard does not change model weights, access a parameter or token pool, retrieve identifiable training examples, or implement a neural default-mode network. the sampler selects a cue; the model generates the interpretation. those are separate operations.

by **christopher robin fiore**, developed with AI assistance across design, implementation and evaluation. [Try the draw](https://globalanomalyindex.github.io/wildcard/) · [Read the case study](https://globalanomalyindex.github.io/wildcard/case-study/) · [Download the paper](https://globalanomalyindex.github.io/wildcard/research-paper.pdf) · [Inspect the evidence audit](research/audit-2026-09/README.md).

## what has been measured

three historical studies record an iteration story: externally selected cues reached a broader range of labels, the first skill's distant mappings scored worse, and a rewritten skill improved some judged qualities while reducing novelty. the studies compare bundled prompt configurations, not isolated cognitive mechanisms.

in Study 3, the recorded Wildcard configuration scored **+0.725 novelty points** relative to one plain brainstorming prompt across ten problems. its original paired bootstrap 95% interval was **[+0.2167, +1.2083]**, and signed-rank p was **0.0371**. the point prediction and positive-interval decision rule were met; the result does not establish a minimum +0.30 effect with 95% confidence. usefulness and genuineness had negative point differences.

the later audit found a dependent legacy sampler, incomplete grading matrices, and a normalization change affecting a flagged output. plain brainstorming had six positive model-judge flags across two of thirty outputs; Wildcard had none in thirty outputs. these are observed flags, not proof of factual safety. the [dated audit](research/audit-2026-09/README.md) retains the historical analyses and reports the corrections and sensitivity checks.

the new [component study](research/transfer-v1/README.md) acquired four prompt conditions across 32 authored briefs using 16 curated relation cards. it asks whether an explicit donor name adds qualified mechanisms once the relation is already supplied. all 64 reference-bank calls and 128 candidate calls passed validation, but one of 64 judge blocks contained invalid reference identities. **the original primary analysis is halted.** a separate [measurement amendment](research/transfer-v1/amendment.md) completed one full new judge panel, with all 64 blocks valid. its [amended primary estimate](research/transfer-v1/results.json) was **−0.015625 qualified mechanisms absent from the bank per response**, with 95% interval **[−0.109375, 0.0625]** and p = **1.000**: inconclusive, not equivalent. neither secondary contrast met its corrected test threshold. the amended panel evaluates the same generated sample and does not restore the original primary. the separate operational diagnostics passed 6 of 8 pairs under their exact contract.

the current **v2 sampler and revised prompt have not inherited experimental effectiveness results**. the component study does not test the full 378-specialist/461-concept skill or sampler's creative benefit. the website's live interaction draws a cue locally; it does not run an AI model or demonstrate improved downstream work by itself.

## install

requires **Bash and Node.js 22 or newer on PATH**, plus a Claude Code version supporting plugins. install and generation use the host's normal network/model access; the cue sampler itself makes no network calls.

in Claude Code:

```text
/plugin marketplace add globalanomalyindex/wildcard
/plugin install wildcard@globalanomalyindex
/wildcard:wildcard
```

the repository uses the documented single-skill plugin layout, with `plugin/SKILL.md` at its root. see the official [plugin reference](https://code.claude.com/docs/en/plugins-reference) and [installation guide](https://code.claude.com/docs/en/discover-plugins) for host-specific installation scopes, updates and removal. a [recorded smoke test](docs/verification/claude-install-smoke.json) on Claude Code 2.1.228 for macOS used a new isolated configuration profile and a local marketplace source. marketplace/plugin validation, installation of version 2.0.0, skill recognition, a draw from the installed copy, an already-current update check, uninstallation, and marketplace removal passed. the normal profile was unchanged. this did not test a fresh GitHub download, a version migration, or model invocation; the test account was not signed in.

## use and replay

1. **freeze the brief.** record the goal, constraints and moving parts before drawing.
2. **draw a cue.** the script issues a fresh OS-backed seed and uses the versioned `sha256-counter-v2` sampler. a supplied seed replays the same versioned corpus.
3. **explore the relation.** use the cue's tools, constraints or behavior to look for a useful direction. distinguish donor facts from transfer hypotheses.
4. **check the move.** remove the donor explanation. does a concrete, relevant action remain? then check its factual dependencies and fit with the actual task.
5. **offer, then let the user choose.** fewer useful moves are better than a quota. abstain when none withstand review. implementing a suggestion is a separate task.

```bash
# fresh draw: three output lines on stdout, complete receipt on stderr
bash plugin/scripts/draw.sh

# deterministic v2 draw with a JSON receipt
bash plugin/scripts/draw.sh --sampler sha256-counter-v2 --seed '42' --json

# historical website/study replay
bash plugin/scripts/draw.sh --sampler legacy-crc-v1 --seed '42'
```

v2 preserves equal mode probability, then selects within the chosen pool. under the uniform-word model, the corresponding entry probabilities are 1/756 for a specialist and 1/922 for a concept. hash-derived selection is pseudorandom; arbitrary chosen seed banks are not guaranteed uniform. it is not uniform over all 839 entries or all possible ideas. see the [sampler contract](docs/sampler-v2.md) for framing, rejection, corpus identity and compatibility.

the prompt asks for grounded claims, relevant optional suggestions and bounded refinement. these are behavioral instructions, not guarantees of truth, originality or usefulness. a removability check is an actionability filter, not factual verification. the skill may offer to save an exact receipt and selected moves to `.wildcard/seedbank.md`; writing requires the user's authorization, and no source edits are part of a draw.

## verify and inspect

```bash
bash tests/run_all.sh
node scripts/verify-history.mjs
node scripts/build-evidence.mjs --check
bash scripts/gen_site_data.sh --check
```

tests establish the properties they check: deterministic replay, specified sampler behavior, corpus validation, source failures and historical artifact integrity. they do not make every prose claim true or establish creative benefit. current claims and limitations come from [the evidence audit](research/audit-2026-09/README.md); the [audit resolution ledger](docs/audit-resolution.md) separates implemented changes from outstanding work.

- `plugin/`: self-contained skill, runtime, corpus snapshot and reference instructions.
- `site/`: static draw interface and evidence presentation.
- `experiment/`, `experiment/v2/`, `experiment/v3/`: preserved historical studies.
- `research/audit-2026-09/`: new validation and post-hoc reanalysis of those observations.
- `research/transfer-v1/`: component-study protocol, preserved acquisition, original analysis halt, and measurement amendment.

existing license declarations and unresolved asset provenance are recorded in [the notices inventory](THIRD_PARTY_NOTICES.md). this README adds no license grant.
