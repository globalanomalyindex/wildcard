# wildcard v2 - two-mode draw + safe open-scope concepts

**Date:** 2026-06-11
**Status:** Approved (design); pre-implementation
**Scope:** Expand the `wildcard` skill with a second draw mode (general concepts) and a
documented offline safety pipeline; add a loose-to-genuine refinement protocol; re-test;
update site + case study. (The structured academic test is a SEPARATE, later spec.)

---

## 1. Goal

Today wildcard draws one kind of thing: a hyper-specific specialist (one of 378 niche
disciplines). v2 adds a second kind: a **general concept** (flowers, adenosine, moire,
tides, sourdough fermentation). The seed picks the mode ~50/50, then draws from that pool.
Distant concepts are connected to the user's problem through a bounded **refinement
search** (spreading activation gated by the structure-mapping bar) that ends in a genuine
connection or honest abstention. The concept corpus is sourced from Wikipedia, screened by
a documented offline safety filter, and committed - so the draw stays offline,
deterministic, reproducible (browser==shell parity), lightweight, and safe by construction.

Every property the current system guarantees is preserved: no runtime network, no model
calls for the draw, full seed reproducibility, tiny footprint.

## 2. Architecture - two pools, one mechanism

### 2.1 The draw (`plugin/scripts/draw.sh`)

Add a **mode stream** before the pool draw:

```
mode = cksum("mode:" + seed) % 2     # 0 -> specialist, 1 -> concept
```

- If `specialist`: draw from `references/domains.txt` (the existing `domain` stream + lens).
- If `concept`: draw from `references/concepts.txt` (a `concept` stream + lens).

Streams stay decorrelated by tag (`mode:`, `domain:`, `concept:`, `lens:`), exactly as
today. The `--seed`, `--file`, entropy fallback, and error handling are unchanged.

**Output** (new `mode=` line; one of `domain=`/`concept=` per mode):

```
mode=concept
concept=adenosine
lens=time-and-rhythm
```
```
mode=specialist
domain=varve chronology reading annual glacial-lake layers
lens=signals-and-noise
```

A `--mode specialist|concept` override is accepted for demos/tests (forces the pool,
bypasses the mode roll); default is the seeded roll.

### 2.2 Browser parity

`site/js/entropy.js` already mirrors `cksum`. Extend the generated data + demo:
- `gen_site_data.sh` emits `CONCEPTS` (from concepts.txt) alongside `DOMAINS`, plus
  `PROVENANCE` for both pools.
- The demo computes `mode = pickIndex("mode", seed, 2)` then draws from the matching array.
- The parity test asserts browser==shell for **mode + pick** across the seed set (the
  whole point: a visitor's draw, concept or specialist, reproduces in their terminal).

## 3. The concept corpus + safety pipeline (the showcase)

### 3.1 Source (real snapshot; network confirmed available)

Wikipedia **Vital Articles** (levels 3 + 4) - community-curated for importance and breadth,
CC BY-SA. We take **titles only** (article titles and the bare fact of a topic's existence
are not copyrightable; we cite source + license as good practice and use titles purely as
*inspiration pointers*, never reproducing article prose). Pulled once via the MediaWiki API
(main-namespace links from the Vital Articles list pages), saved as a raw candidate list
with the dump date. This is a committed, version-pinned snapshot - not a runtime call.

If a future re-pull is desired, the method is documented and re-runnable; the filter below
is source-agnostic, so any title list can be screened the same way.

### 3.2 Filter (`plugin/scripts/screen_concepts.sh`) - documented, runnable, auditable

Input: raw candidate titles. Output: `concepts.txt` (survivors, tagged) + a sampled
`rejection-log.txt` (what was dropped and which rule caught it). Stages:

1. **Denylist families** (regex/keyword + Wikipedia-category signals): living persons;
   contemporary politics/elections/parties; religious doctrine/figures; ethnic/national
   conflict; war/violence/weapons/terrorism; sexual content; self-harm/suicide;
   drugs-of-abuse; disasters-with-victims; diseases framed as tragedy; slurs/hate; and
   IP-heavy entities (brands, franchises, characters, trademarks). Anything matching is
   rejected with its rule logged.
2. **Allowlist bias / neutrality**: keep concrete, mechanism-rich, evergreen, "safe to
   freely associate from" concepts - natural phenomena, organisms, materials, processes,
   physical/biological/mathematical concepts, crafts, everyday objects, abstract-neutral
   ideas.
3. **Structural gates** (mirrors `audit_domains.sh`): dedup, min count, format, no empties,
   no pipe in the concept text.
4. **Abstraction-tier tag** (for breadth auditing, NOT draw weighting): `everyday |
   natural | scientific | abstract`, plus a coarse facet, appended as ` | tier | facet`
   like the domains axis tags. Lets `audit_concepts.sh` prove the corpus spans tiers.

### 3.3 Adversarial audit (workflow)

After filtering, an adversarial-review workflow (same method that hardened domains.txt):
reviewers try to find any survivor that still reads as sensitive/loaded, is a living
person, or is IP-heavy. Confirmed hits are removed; the removals are logged. This is the
"we didn't just trust the regex" step.

### 3.4 Provenance + legal stance

`concepts.txt` header stamps: source (Wikipedia Vital Articles L3+L4), dump date, filter
version, candidate/kept/rejected counts, CC BY-SA attribution, and the inspiration-only
principle: *titles are used as pointers to spark structural analogy; no article text is
reproduced; any IP-bearing entity is excluded at curation time, and if one ever surfaces it
is used only as abstract inspiration and named as such.* The same principle is stated in
SKILL.md so the runtime honors it.

## 4. The refinement protocol - "the web" (`plugin/references/connecting.md`)

Honest name: **spreading activation** (Collins & Loftus, 1975) gated by the structure-
mapping predicate. The skill follows it, especially in concept mode (specialists often map
more directly; distant concepts need the search):

1. From the drawn concept, cast **3-5 relational properties** - how it works, what it
   trades off, its dynamics, its failure modes. Relations, not nouns. (For "adenosine":
   accumulates while awake, is a rising pressure signal, is cleared/antagonized, gates a
   state transition.)
2. Probe each property against the project's **structural sketch**.
3. Keep only threads that pass the structure-mapping bar (relations map, not surface
   words). Refine a loose-but-promising thread by going **one association deeper** until it
   tightens into a genuine isomorphism or is dropped.
4. Terminate in **1-4 genuine connections OR honest abstention**. Refinement never licenses
   fabrication; it is a bounded search whose accept-test is the existing honesty bar.

Visibility: **internal by default** (present only the tightened threads - tight, token-
light output), with an offer: "want to see the threads I discarded?" This respects the
lightweight constraint; the web lives in the model's reasoning, surfaced minimally.

## 5. SKILL.md pipeline update

The five-stage pipeline becomes mode-aware:
- **1 Detect** - unchanged (structural sketch of the project).
- **2 Draw** - run `draw.sh`; read `mode=` and the `domain=`/`concept=` + `lens=`.
- **3 Embody or explore** - specialist: grow the niche practitioner (`specializing.md`).
  concept: load the concept's relational properties (`connecting.md` step 1).
- **4 Connect (honestly)** - specialist: notice via structure-mapping. concept: run the
  refinement search (`connecting.md`). Both end in genuine connections or abstention.
- **5 Present seeds** - unchanged three-beat shape; explicitly optional; offer the
  discarded threads or to pull one further.

The three guarantees (no fabrication, no derailment, no favoritism) are unchanged and now
explicitly cover both modes. `specializing.md` also gains more niche-generation axes ("more
criteria for more specialist possibilities") without bloating the file.

## 6. Lightweight / storage / tokens

- Flat text + shell + the tiny JS parity layer. No runtime network, no model calls for the
  draw. `concepts.txt` is expected < ~150 KB. Plugin footprint stays small.
- The refinement search runs in the model's own reasoning and surfaces only final threads,
  so it does not bleed tokens.

## 7. Re-test with true randomization

The no-seed draw already uses `/dev/urandom`. "Re-test" means re-validate over the expanded
system and re-measure every cited figure:
- **mode balance**: `cksum("mode:"+seed) % 2` is ~50/50 over N seeds (new test).
- **concept diversity**: wide spread over concepts.txt (mirrors test_diversity for domains).
- **concept audit**: `audit_concepts.sh` gate (format, dedup, min count, tier spanning,
  zero denylist hits) - runs in CI before deploy.
- **parity**: browser==shell for mode + both pools across seeds (extended parity test).
- **figures re-measured**: pool counts, the mode split, concept screened/kept/rejected
  counts. The site's figures panel and case study are updated to the new, honest numbers.

## 8. Site + case study

- **Figures panel**: add the two-mode split, concept count, and the safety-filter stats
  (candidates screened / kept / rejected); keep the parity figure. All regenerable.
- **Live demo**: the seeded draw now sometimes shows a concept (with `mode=`), so visitors
  see both kinds; still reproducible + parity-checked.
- **New case-study section "open scope, safely"**: the Wikipedia-tension -> why offline
  curation -> the filter stages -> the rejection log -> the legal-inspiration stance ->
  the spreading-activation refinement. This is the resourcefulness/guardrail showcase.
- Lowercase everywhere; zero em/en dashes; honest small-n caveats retained.

## 9. File plan

```
plugin/
├── SKILL.md                       # mode-aware pipeline + both guarantees
├── references/
│   ├── domains.txt                # specialists (existing, lightly grown)
│   ├── concepts.txt               # NEW: screened, tagged, provenance-stamped
│   ├── specializing.md            # + more niche axes
│   ├── structure-mapping.md       # the honesty bar (unchanged core)
│   └── connecting.md              # NEW: the refinement / spreading-activation protocol
└── scripts/
    ├── draw.sh                    # + mode stream, concept pool, --mode override
    ├── audit_domains.sh           # existing
    ├── screen_concepts.sh         # NEW: source-agnostic safety filter -> concepts.txt + rejection-log
    └── audit_concepts.sh          # NEW: format/dedup/min/tier-spanning/zero-denylist gate
docs/
├── concepts-sourcing.md           # NEW: exact API method + filter doc (reproducible)
└── case-study.md                  # + "open scope, safely" section
site/                              # figures + demo + case-study page updated; gen_site_data emits CONCEPTS
tests/ + site/tests/               # + mode-balance, concept-diversity, concept-audit, extended parity
```

## 10. Out of scope (this spec)

- The structured academic test (separate, later spec - only PREP after this lands).
- Any runtime network call (explicitly rejected: breaks reproducibility/parity/offline/safety).
- Weighting the draw by tier or facet (tags are for auditing breadth, not for biasing the
  draw - same principle as domains axis tags).

## 11. Success criteria

- A seeded draw reproduces browser==shell including the mode pick, for concept and
  specialist alike.
- `audit_concepts.sh` passes: zero denylist hits, spans all tiers, deduped, >= min count.
- The adversarial audit finds no sensitive/IP survivor after remediation.
- Concept-mode output shows real refinement: genuine structural connections or honest
  abstention, never a forced noun-match.
- Footprint stays small; no runtime network; figures on the site all regenerate from tests.
